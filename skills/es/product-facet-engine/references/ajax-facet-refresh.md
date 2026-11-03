# Barra lateral de filtros que se refresca sin recargar la página

Requisito del propietario: *"al hacer clic en un filtro no debe recargarse la página, para poder añadir varios filtros a la vez"*
— con **un** botón `Filter` y sin toggles Mostrar/Ocultar. Verificado en un catálogo de 38 k productos con PHP 8.4 + SQLite
(example-shop.com), 2026-09.

## Forma de la solución

| Archivo | Rol |
| --- | --- |
| `inc/listing.php` → `listing_context(array $CTX, array &$PAGE): array` | construye scope, filtros, página de resultados, grupos de facetas, contadores en vivo, SEO. Lo usan **ambas** vistas de abajo. |
| `views/listing.php` | página completa: page-head, tiras de subcategorías, `partials/filters.php` + `partials/results.php` dentro de `<div class="listing" data-listing>`. |
| `views/api_listing.php` | mismo contexto, emite solo JSON. |
| `views/partials/filters.php` / `results.php` | los dos bloques reemplazables (`results` lleva `data-results`). |
| `assets/js/site.js` | `showListing()` + `applyFacetCounts()`. |

Routing: cada rama de listado (departamento / categoría / subcategoría / marca / búsqueda) renderiza
`$LISTING_VIEW = !empty($_GET['frag']) ? 'api_listing' : 'listing'` en vez de un nombre de vista fijo, así
la URL AJAX es simplemente la URL de la página más `&frag=1` — sin una segunda ruta que mantener sincronizada.

`render()` debe saltarse el layout para estas: `if (str_starts_with($view, 'api_')) { echo $content; return; }`
(ver el pitfall en SKILL.md — si no, el JSON llega dentro de un documento HTML completo).

## Contrato JSON

```json
{
  "results": "<div class=\"results\" data-results>…</div>",
  "counts":  { "groups": { "<Property name>": { "<value>": 57, "…": 0 } },
               "brand":  { "gigabyte": 117 } },
  "total":   57,
  "perPage": 24,
  "url":     "/category/mainboards/?brand%5B%5D=gigabyte"
}
```

`filters` (el HTML de la barra lateral) **ya no** forma parte del contrato: enviarlo invita a un re-render,
y re-renderizar es el bug (ver abajo).

## Contadores en vivo — una consulta por grupo, con su propia dimensión relajada

```php
function facet_live_counts(array $f, array $groups): array
{
    $out = [];
    foreach ($groups as $g) {
        $scope = $f;
        $scope['spec'] = is_array($f['spec'] ?? null) ? $f['spec'] : [];
        unset($scope['spec'][$g['name']], $scope['page'], $scope['per_page'], $scope['sort']);
        [$from, $whereSql, $params, ] = scope_sql($scope, true);      // constructor de scope compartido
        $sql = 'SELECT pp.value, COUNT(DISTINCT pp.product_id) AS n ' . $from
             . ' JOIN product_properties pp ON pp.product_id = p.id'
             . $whereSql . ($whereSql !== '' ? ' AND' : ' WHERE')
             . ' pp.name = ? GROUP BY pp.value';
        foreach (qall($sql, array_merge($params, [(string)$g['name']])) as $r) {
            $out[(string)$g['name']][(string)$r['value']] = (int)$r['n'];
        }
    }
    return $out;
}
```

Marcas: `brand_facets($f, 60)` ya relaja la selección de marca; conviértelo en un mapa slug → contador.

Ejecuta esto solo cuando haya algo seleccionado — sin selección el escaneo de scope cacheado es idéntico y mucho
más barato:

```php
$__active = !empty($filters['brand']) || (string)$filters['min'] !== '' || (string)$filters['max'] !== ''
    || !empty($filters['spec']) || !empty($filters['with_image']);
$CTX['facet_counts'] = $__active ? facet_live_counts($filters, $CTX['spec_facets']) : [];
```

Medido en el sitio en vivo: 17 ms página sin filtrar, 49 ms página filtrada, 53 ms petición de fragmento.

Reglas de renderizado (en servidor, así que también valen sin JS):
* contador 0 **y** sin marcar → no renderices el `<li>` en absoluto;
* cada valor marcado se inyecta a la fuerza en la lista de valores de su grupo (las facetas top-N pueden descartarlo);
* un grupo sin valores visibles no renderiza nada.

## Lado cliente

`showListing(path, opts)`:

1. construye params desde el formulario vivo (`new FormData(document.querySelector('[data-filter-form]'))`, saltando
   valores vacíos y el `sort=relevance` por defecto) — **busca el formulario en cada llamada**, lo reemplaza el
   refresco de resultados en la implementación antigua y una referencia cacheada queda obsoleta (ese modo de fallo costó
   una hora: el segundo tick no hacía nada en silencio);
2. `opts.resetPage` → quita `page` (cambio de filtro/orden); los enlaces conservan lo que diga su propio query;
3. `fetch(path + '?' + params + '&frag=1')`, luego reemplaza `[data-results]` y llama `applyFacetCounts(data.counts)`;
4. `history.pushState` con `data.url`, `popstate` re-obtiene con `push:false`;
5. clase `.is-loading` mientras está en vuelo; ante cualquier error, cae a `window.location.href`.

`applyFacetCounts(counts)` — la parte que arregla "marco un filtro y se marca otro":

```js
// inputs llevan data-facet="<group>" data-facet-value="<value>"; el <em> lleva data-facet-count
const n = (group === 'brand' ? counts.brand : counts.groups[group])?.[value] ?? 0;
li.hidden = (n <= 0 && !input.checked);           // nunca toques el nodo en sí
if (!li.hidden && n > 0) em.textContent = fmtd(n);
```

* Sin `innerHTML`, sin reemplazar el `<aside>` — el checkbox marcado debe seguir siendo el mismo nodo DOM.
* Badges de grupo (`data-facet-badge`) = número de inputs marcados; oculta el badge a 0.
* Un grupo cuyos ítems están todos ocultos y que no tiene nada marcado recibe `grp.hidden = true`.
* Badge del botón `Filter` = facetas marcadas + campos de precio rellenos.

## Probar que "sin recarga" es real

Pon una marca en `window` antes de interactuar; solo sobrevive si el documento nunca se reemplaza:

```js
await js(`window.__mark = 1; 1`);
// clic / tick, espera el fetch
const reloaded = await js(`window.__mark !== 1`);   // debe ser false
```

Aserta también, en la misma pasada:
* `visibleFacets` baja y `zeroCounts === 0`;
* la casilla marcada sigue marcada, sigue visible y es `sameNode` — etiquétala (`box.__id = 'TICKED'`) y busca
  esa propiedad de nuevo tras el refresco;
* dos filtros se combinan (la URL lleva ambos params, chips = 2, el contador baja);
* `location.search` no tiene `frag`, ni `sort=relevance`, ni `min=/max=` vacíos;
* la paginación conserva `page=2` mientras un cambio de filtro lo resetea;
* la ruta sin JS: `curl` del query exacto que enviaría el formulario y asegura 200 + el contador esperado.
