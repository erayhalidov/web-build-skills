---
name: product-facet-engine
description: Úsala si los filtros salen de datos de feed escasos.
---

# Motor de facetas de producto — filtros reales sobre datos de proveedor escasos

Úsala cuando una tienda/catálogo (PHP+SQLite, OpenCart, Medusa, HTML estático) necesita **filtros reales**, pero:
* el cliente dice "haz el filtro como *<gran distribuidor>*" (quiere decir facetas de especificaciones con contadores,
  chips de filtros seleccionados, selección múltiple, ver más), o
* el feed del proveedor trae pocos o ningún dato técnico (típico de CSVs tipo ERP/Icecat: nombre, EAN,
  peso, precio y nada más), o
* las subcategorías, los valores de atributo o los pesos de envío simplemente no existen en el feed.

Regla dura para cada valor que muestres: debe remontarse a datos del feed o a una **extracción derivada del nombre**.
Nunca inventes un valor de especificación, un contador ni un precio. Desconocido → omite la faceta, o muestra "a consultar".

## 1. Decide de dónde sale cada filtro

| Origen | Ejemplos | Notas |
| --- | --- | --- |
| Propiedades del feed | `product_properties(name,value)` de feeds XML | Lo más rico, úsalo primero. |
| Derivado del nombre | Color, Capacidad, Tipo de memoria, Interfaz, Tamaño de pantalla, Wi-Fi, Puertos, Potencia, Longitud | Funciona con feeds sin propiedades — ver §3. |
| Estructural | marca, categoría, subcategoría, rango de precio, "tiene foto" | Siempre disponible. |
| Peso | `products.weight` (kg) | Alimenta el precio de envío, no es una faceta. |

A menudo un feed tiene propiedades y el otro ninguna: extrae solo para los productos cuyo feed carece de ellas
para no sobrescribir nunca valores reales del proveedor.

## 2. Subcategorías cuando el feed no tiene subnivel

Tabla ordenada de reglas, gana la primera coincidencia, aplicada **en el momento de la importación** (`inc/taxonomy.php` →
`catalogue_subcategory_rules()`: nombre de categoría → `[[sub_name, regex], …]`). Indexa la tabla por el nombre
exacto de categoría tras cualquier mapeo de "división limpia" — una diferencia de mayúsculas (`Junction boxes` vs `Junction Boxes`)
da cero coincidencias en silencio, así que vuelca los nombres reales de categoría y compáralos con las claves de las reglas.

* Los productos sin coincidencia quedan `subcategory_id = NULL` — **no** los embudes en un cajón "Otros".
* Los slugs los genera el importador; ese mismo código sirve después las páginas de subcategoría, facetas,
  breadcrumbs y el sitemap gratis.
* Resultado realista: 195 subcategorías del feed → 365 tras la derivación, 76 % de 38 k productos colocados.
* La visibilidad en la UI importa tanto como el dato: una tira de chips con contadores en la parte superior de la página de categoría,
  un índice "Categorías en <departamento>" en la página de departamento. **Este usuario quiere solo las categorías
  principales en el índice de departamento (sin subenlaces ahí) y la tira completa de subcategorías en la
  página de categoría** — no dupliques la misma lista también en la barra lateral.

## 3. Deriva atributos de los nombres de producto y guárdalos como propiedades reales

Todo el truco: escribe los valores derivados en `product_properties` en la importación, así el motor de facetas, el
SQL de filtros, el sitemap y la tabla de especificaciones funcionan con **un** mecanismo en vez de una ruta de código
"derivada" paralela.

* Usa `sort = 1200` (o cualquier valor alto) para las filas derivadas, y salta un nombre que el feed ya proporcionaba.
* Las reglas viven en un solo archivo (`inc/attributes.php` → `extract_attributes($name, $category)`), devolviendo
  `['Interface' => 'HDMI', …]` — solo los atributos realmente encontrados.
* Los numéricos acotados y los sufijos explícitos son la diferencia entre una faceta útil y ruido:
  * la velocidad requiere `Gbit|Gbps|GbE|igabit` **y** 1–400 → si no, los routers LTE "4G/5G" se convierten en "4 Gbit";
  * tamaño de pantalla acotado 10–120 pulgadas, potencia 45–4000 W, longitud de cable 0.1–100 m;
  * `Paper size` solo cuando el nombre menciona además papel/impresión/foto/etiqueta (si no, un `A3` de un número de pieza se cuela);
  * normaliza `1024 GB → 1 TB`, `gray → Grey`, `802.11ax → Wi-Fi 6`, une dos colores como `Black / White`.
* Mantén los falsos positivos fuera de la faceta descartando los grupos que no son discriminadores (§4).
* Catálogo completo de reglas y trampas del parser: `references/derived-attributes-from-names.md`.

## 4. Motor de descubrimiento de facetas

Un **constructor de scope compartido** alimenta tanto la consulta del listado como las consultas de facetas — duplicar
los joins/WHERE es cómo los contadores del listado y los de las facetas se desincronizan.

```php
function scope_sql(array $f, bool $withSpec = true): array   // [from, whereSql, params, joinFts]
```

Descubrimiento, por petición:
1. Nombres de propiedad candidatos principales en este scope: `SELECT pp.name, COUNT(DISTINCT pp.product_id) cov …
   GROUP BY pp.name HAVING cov >= 3 ORDER BY cov DESC LIMIT 40`, menos una **lista negra**
   (`Vendor_url`, `Dimensions`, `Weight`, `EAN`, `Part number`, `Warranty`, `Model`, `Other`, …).
2. Por nombre, trae sus ~26 valores principales con contadores.
3. Conserva un nombre solo si tiene 2–24 valores, al menos 8 productos, y su valor principal cubre ≤ 85 % del
   grupo (un valor que lo cubre todo no es un discriminador).
4. Ordena los grupos por una **lista de prioridad** explícita (primero especificaciones de hardware, `Colour` al final) en vez de por
   cobertura bruta — la cobertura sola pone encantada `Audio` y `Pen` por delante de `Screen size`.
5. Toma ~6 grupos × 8 valores.

Filtrado: un `EXISTS` por grupo de propiedades (AND entre grupos, OR dentro de un grupo), params añadidos en
orden:
```sql
EXISTS (SELECT 1 FROM product_properties x WHERE x.product_id = p.id AND x.name = ? AND x.value IN (?,?))
```
Indéxalo: `CREATE INDEX idx_pp_name_value ON product_properties(name, value)`.

Cachea los agregados de facetas en una caché de archivos con clave `md5(scope) + built_at` y TTL de 1 h — frío ≈ 230 ms,
caliente ≈ 30–40 ms. **El meta `built_at` debe formar parte de la clave**, si no una reimportación deja contadores
obsoletos en pantalla durante una hora. Purga los archivos de caché de más de ~7 días al escribir.

## 5. UI de filtros y contrato de URL

* Selección múltiple, no radio: `?brand[]=hp&brand[]=lenovo` (y `?spec[Screen size][]=27 inch`), así la
  consulta de filtros toma un array por grupo; los formularios de ordenación/por página deben reemitir los params de array como inputs
  ocultos o la ordenación descarta los filtros en silencio.
* **Chips de filtros seleccionados** sobre los resultados, cada uno con una ✕ que quita exactamente ese valor
  (`url_without_value($key,$value)`, `url_without_spec($name,$value)`) más "Limpiar todo".
* **Exactamente un botón en la barra lateral — con la etiqueta `Filter`.** Sin texto de encabezado "Filters" al lado, sin
  toggle de panel Mostrar/Ocultar, sin "Mostrar N más" por grupo: el propietario los quitó todos explícitamente. Las listas
  largas de valores hacen scroll dentro de su propia caja (`max-height` + `overflow-y:auto`, `.fopts-scroll`); el botón
  queda compacto (`~72×37 px`, `btn-sm`, `width:auto` — no a ancho completo ni en desktop *ni* en teléfono) y lleva
  el contador de filtros activos como pequeño badge. En teléfonos ese único botón abre / cierra la lista
  (colapsada) — los filtros se aplican al marcarlos, así que no hay paso de "Aplicar".
* Por grupo: badge con el número seleccionado y contadores alineados a la derecha. Por página: 24/48/96.
* URLs filtradas/paginadas: `noindex, follow` + canonical a la URL limpia (igual que la base del sitio de feed).
* Cuando el propietario fuerza "todo está disponible", **quita la faceta de disponibilidad** — un filtro cuyo
  único cubo iguala el total es ruido.

### 5a. El filtrado no debe recargar la página (y los contadores se actualizan en sitio)

Requisito del propietario en palabras llanas: *"al hacer clic en un filtro no debe recargarse la página, para poder añadir varios
filtros a la vez"*. Receta PHP + JS que funciona, contrato JSON y método de prueba:
`references/ajax-facet-refresh.md`.

* Un único endpoint de fragmento JSON sirve a todas las rutas de listado (`…?<filters>&frag=1` → `{results, counts, total,
  url, title}`); la vista de página y el endpoint de fragmento construyen su estado a través de **un
  `listing_context()` compartido**, si no la página y los fragmentos se desincronizan.
* **Refresca los resultados, nunca el HTML de la barra lateral.** Re-renderizar la barra lateral bajo el cursor *es* la
  queja del propietario *"marco un filtro y se marca otro"* — la lista se reordena alrededor del
  clic. Reemplaza solo el bloque de resultados y parchea la barra lateral **en sitio** (texto de contador + ocultar/mostrar ítems):
  la casilla marcada sigue siendo el mismo nodo DOM, marcada, donde el dedo la dejó.
* **Contadores en vivo, valores a cero fuera.** Cuenta cada grupo con todos los demás filtros aplicados y *su propia
  selección relajada* (`facet_live_counts()`), oculta los valores a 0 salvo que estén marcados, y oculta
  el grupo entero cuando no queda nada en él. Inyecta a la fuerza los valores marcados en la lista de valores — las facetas
  top-N los descartarían y el comprador no podría desmarcar. Calcula esto solo cuando hay un filtro
  activo: sin selección el escaneo de scope cacheado da los mismos números mucho más barato (medido aquí: 17 ms
  página sin filtrar, 49 ms página filtrada, 53 ms fragmento).
* `history.pushState` en cada cambio más `popstate` para el botón atrás; resetea `page` a 1 en un
  cambio de filtro/orden pero **consérvalo** para la paginación y los enlaces por página; reutiliza el query
  string del propio navegador para la URL limpia (quitando `frag` y la ordenación por defecto, omitiendo `min=`/`max=` vacíos) en vez de
  re-serializar con `http_build_query`, que reescribe `spec[Socket][]=LGA1700` como
  `spec[Socket][0]=LGA1700`.
* La mejora progresiva no es opcional: el mismo formulario sigue haciendo un GET normal sin JS, así que una
  prueba debe hacer `curl` exactamente del query que enviaría el formulario.

## 6. Precio de envío basado en peso (mismo dataset, misma regla de honestidad)

El coste de envío es una característica del catálogo: calcúlalo con pesos reales de producto y **tarifas publicadas
del transportista**, nunca a ojo.

**El peso puede faltar en un feed entero.** El feed XML no tenía columna de peso, así que 5 400 productos
se habrían enviado con un "estimado 0.5 kg". Extrae el valor de las propiedades del propio feed en la importación
en su lugar: `Weight: "1.70 kg"`, `"Starting at 1.38 kg"`, `"450 g"` → `products.weight` (parser = primer
número + unidad, `g` → /1000, acotado 0–200 kg, escrito solo donde la columna está vacía). 1 713 productos
ganaron un peso real así y la banda de envío dejó de ser una estimación. Nunca adivines un peso —
un desconocido sigue siendo desconocido y el resumen lo dice. Bulgaria (Speedy opera la red DPD allí; `www.dpd.bg` redirige a
speedy.bg), tarifa oficial, códigos de servicio, precios por grupo de país y la receta de obtención están en
`references/bg-carrier-tariffs.md`. Destinos fuera de la tarifa publicada → "precio a consultar".

## 7. Rellenar huecos de datos sin inventarlos (la misma regla de honestidad)

Sea cual sea el hueco — facetas, pesos, fotos — la respuesta es *derivar de datos reales, etiquetar la estimación o
no mostrar nada*.

* **Fotos:** un feed puede traer cero datos de imagen (columna `Images` vacía en todas las filas, ninguna URL en
  el archivo — compruébalo antes de prometer). Entonces: reutiliza la foto del feed que *sí* las tiene **solo** para el
  mismo número de pieza normalizado (las filas de variante como `/EXP` o `GIFT` son el mismo artículo físico — 242 de
  38 k en la práctica), sustituye el resto por un placeholder *diseñado* (glifo inline-SVG de línea por
  departamento + marca + número de pieza, ~20 glifos que cubren 24 departamentos) en vez de una caja gris "sin foto",
  mantén una línea honesta en la página de producto ("el fabricante no publica foto — pregúntanos"), y dile al propietario
  qué haría falta de un feed de imágenes real. Nunca hagas scraping a un competidor ni tomes prestada una foto de otra marca.
* **Pesos:** extráelos de las propias cadenas de propiedad del feed antes de recurrir a una estimación (§6);
  una estimación que llega al total del cliente debe ir etiquetada como tal.
* **Atributos/subcategorías:** las reglas derivadas del nombre (§2/§3) superan un panel de filtros vacío — pero un valor que
  no se pueda remontar al feed o al nombre del producto se queda fuera.

## 8. Patrones de petición vistos en catálogos de revendedor

* **"Todos los productos deben estar disponibles."** No reescribas los datos del feed. Mantén la disponibilidad real en la BD
  y añade una flag de config (`force_availability = 'in_stock'`) que lean la capa de presentación, el JSON-LD
  (`InStock`), los contadores de facetas y el filtro de disponibilidad — reversible en una línea. Quita la faceta de
  disponibilidad ahora sin sentido, y suaviza cualquier frase que afirmara stock local
  ("Disponible por encargo — plazo de entrega confirmado con el pedido").
* **"Hazlo una página de pedido, no una consulta."** Entonces entrega un checkout real: resumen del pedido con totales,
  el precio de envío, un botón **Realizar pedido**, una referencia de pedido (`ERP-2026-00001` de la secuencia de fila)
  mostrada en la confirmación, y totales/peso recalculados en servidor desde el slug del producto en
  el POST. Mantén el flujo de consulta/presupuesto en su propia página — la preferencia fija de este usuario es que una nueva
  función tenga **su propia URL con su propio SEO**, nunca una sección atornillada a una página existente.
* **Campos obligatorios condicionales (empresa vs particular).** Marca con asterisco los siempre obligatorios; envuelve
  los dependientes del tipo en `[data-business-only]` y alterna tanto `hidden` como `required` en JS — luego
  **revalida la misma regla en servidor**, porque un input `required` oculto simplemente no se envía.
  Vacía los datos que no aplican al tipo elegido antes de guardar.
* **Los precios deben mostrarse con y sin IVA, y el tipo elige el modo.** Cliente particular: mercancía,
  envío y total **con IVA**. Empresa / revendedor: las mismas tres líneas **sin IVA** (los precios de
  transportista se publican con IVA incluido, así que envío neto = bruto / 1.2). Tipos por destino: IVA local en
  BG; 0 % intracomunitario una vez dado un número de IVA (VIES); el tipo estándar del destino para un comprador particular
  de la UE; 0 % exportación fuera de la UE — más una línea de que la factura es el documento
  autoritativo. Mantén el desglose detallado en una caja y un total compacto de 3 líneas justo encima del botón de enviar.
* **Higiene de textos — este propietario poda de la UI de cliente todo lo que miran los proveedores.** Eliminado a petición
  en varias sesiones: el banner superior, la nota bajo las opciones de envío, el par de disclaimers del footer
  ("Los datos de producto se actualizan automáticamente desde nuestros catálogos de proveedor (última importación …)" / "Los nombres
  de producto y las marcas son propiedad de sus respectivos dueños…"), la opción "recogida / transportista propio en nuestras instalaciones",
  y la línea de página de producto `Price of second supplier: 111.17 € net`. Entrega precios, etiquetas y campos;
  pon las explicaciones en FAQ/páginas estáticas. Cuando un precio/campo sale de la UI, borra también la clase CSS
  ahora muerta y la variable sin uso, y conserva la columna de BD (para que pueda volver en una línea). La marca de
  transportista de cara al cliente aquí es **DPD**; los comentarios de procedencia viven en el código, nunca en la página.
* **Las tablas anchas de precios/facetas deben sobrevivir a un teléfono.** Con 10+ columnas, cambia a tarjetas apiladas a
  `≤760px`: oculta `thead`, `display: block` en las filas, `data-label` en cada celda y
  `td::before { content: attr(data-label) }`. Verifícalo con la comprobación CDP (ver `scripts/`), no a ojo.
* **Nunca un precio, peso o plazo que no esté documentado.** Desconocido → "a consultar", confirmado por el
  propietario; este usuario rechaza de plano los números inventados y comprueba el sitio en vivo justo después de la entrega.

## Pitfalls

* **Una columna que no existe en un `SELECT` constante compartido tumba el sitio en vivo con 500.** Caso real:
  `p.weight_kg` cuando la columna del esquema era `weight` — todas las páginas de listado devolvían 500 hasta arreglarlo.
  Comprueba primero el `.schema`, aliasa en la constante (`p.weight AS weight_kg`), y tras tocar una
  constante/helper de consulta compartida repasa cada tipo de ruta (`curl` por ruta, asegura 200 + sin `Warning:`/`Fatal`).
* **PHP: dos literales de string en líneas consecutivas es un error de parseo.** Las cadenas largas de FAQ/arrays necesitan
  una concatenación `.` explícita; `php -l` solo lo pilla si de verdad pasas el linter (`for f in $(find . -name
  '*.php'); do php -l $f; done`).
* **`[$a, $b] = $assocRow` da `null`s en silencio.** Desestructurar un array asociativo produce celdas de tabla vacías / filas
  ausentes sin ningún error. Usa claves con nombre (`$row['service']`). Síntoma que recordar:
  las cabeceras de tabla se renderizan, las filas del cuerpo están vacías.
* Los atributos derivados no deben sobrescribir propiedades del feed; registra cuántas filas saltaste.
* Los contadores de facetas deben calcularse con el mismo constructor de scope que el listado, y cachearse por `built_at`.
* No añadas un segundo punto de entrada para los filtros "derivados" — escríbelos en la tabla de propiedades existente.
* **Una edición scriptada de "reemplazar todo" puede duplicar una clave de array.** Insertar el mismo bloque en dos
  funciones PHP (`shipping_services()` y `shipping_rates()` ambas empiezan por `'cee202' => [`) puso una definición de servicio
  donde iba un array de precios; PHP conserva en silencio la **última** clave, así que la opción se renderizaba como
  "a consultar" sin ningún error. Tras editar tablas de datos con `str.replace(..., -1)`, comprueba
  la forma (`php -r 'print_r(array_keys(...))'`) e imprime la cotización de un país.
* **Verifica los flujos multipaso desde un archivo de script, no con una larga línea inline.** Los comandos encadenados complejos
  los rechaza el guard del shell; escribe `verify_<area>.sh` / `<area>_flow_test.sh` junto al tooling del sitio,
  ejecútalo con `bash`, y guarda los reutilizables en `scripts/` de la skill.
* **Una cookie de sesión `Secure` hace que las pruebas HTTP locales parezcan rotas.** Tras Cloudflare la app ve
  `X-Forwarded-Proto: https`, así que PHP pone la cookie de sesión `Secure`; una prueba `curl http://127.0.0.1:8080`
  entonces nunca la devuelve, los tokens CSRF nunca coinciden y toda acción de cuenta devuelve `err=csrf`.
  Ejecuta las pruebas de flujo de cookies/cuentas contra el **origen HTTPS público**, y mantén el vhost local para
  barridos de páginas anónimas. Detalles: skill `customer-accounts-and-sessions`.
* **Un `onchange="this.form.submit()"` inline mata el comportamiento sin recarga.** `form.submit()` no dispara el evento
  `submit`, así que un listener que hace preventDefault sobre el submit nunca lo ve y la página se recarga igual
  (síntoma: ordenación/por página "funcionan" pero la página entera salta). Quita el handler inline, engancha el evento
  `change` en el select (`[data-sort]`) y añade un botón de envío `<noscript>` para el caso JS-off.
* **Una vista de fragmento JSON nunca debe ir envuelta en el layout de página.** `render()` requiere la vista y luego
  `views/layout.php`; el fragmento volvía por tanto como un documento HTML completo con el JSON enterrado dentro
  (`Content-Type` correcto, cuerpo no parseable). Las firmas de ruta no cambian — ramifica dentro del
  renderer: `if (str_starts_with($view, 'api_')) { echo $content; return; }`.
* **`PRAGMA query_only = ON` en la conexión de lectura hace fallar toda escritura por CLI.** El `db()` de la app es un
  handle de solo lectura endurecido, así que un script de mantenimiento que reutilice `qexec()` muere con
  `SQLSTATE[HY000]: General error: 8 attempt to write a readonly database` mientras la ruta web (que abre
  su propio handle de escritura) está bien. Da a la ruta de escritura su propia conexión (`db_open_rw()` tras un
  helper `db_write()`) y enruta por ella las actualizaciones de admin/CLI.
* **Un helper de contexto compartido + `extract($arr, EXTR_SKIP)` deja el `$CTX` del llamador obsoleto.** El helper
  recibe `$CTX` por valor, enriquece su propia copia (filtros/resultado/facetas) y la devuelve; `EXTR_SKIP` entonces
  conserva el `$CTX` *original* ya presente en el scope de la vista, así que los parciales corren con un
  `$CTX['filters']` indefinido (warnings, filtros vacíos, sin productos). Asígnalo explícitamente
  (`$CTX = $__L['CTX'] ?? $CTX;`) antes de extraer, y haz `unset($__L['CTX'], $__L['PAGE'])` para que el
  `$PAGE` por referencia no se machaque.
* **Nunca caches el elemento de formulario/barra lateral en una variable JS.** `var form = document.querySelector('[data-filter-form]')`
  capturado al cargar apunta a un **nodo desacoplado** en cuanto el endpoint de fragmento cambia el markup: el
  primer tick funciona, todos los siguientes reenvían los valores *antiguos* y la página parece ignorar los clics
  (síntoma: "añadir un segundo filtro no hace nada, la URL nunca cambia"). Busca el elemento dentro del
  handler cada vez — y si reemplazas la barra lateral, mantén vivos los nodos DOM de los inputs marcados
  (ver §5a).
* **Un `str.replace()` grande que se come un rango de líneas puede duplicar una cabecera.** Reescribir una vista cortando
  índice→índice dejó el bloque viejo de preparación de datos encima del nuevo; seguía parseando, pero la página renderizaba
  basura. Tras una cirugía en una vista, `php -l` **y** relee la región ensamblada antes de seguir.

## Verificación

* `scripts/mobile-overflow-check.mjs` (sin dependencias npm, CDP sobre el Chromium de Playwright) — mide
  `scrollWidth` vs `clientWidth`, lista cada elemento que cruza el borde derecho, y con
  `--selector ".ship-table"` informa si una tabla ancha pasó al layout de tarjetas apiladas. Ejecútalo a
  360/390/414 px en la categoría, producto, carrito/pedido y cualquier página con tabla de precios.
* Compara los grupos de facetas por categoría tras cambiar reglas (`grep` la barra lateral renderizada buscando `fgroup-title`).
* Comprueba por muestreo que los 5 valores de faceta principales de una categoría son plausibles; un valor como `1 inch` en racks
  de 19 pulgadas o `4 Gbit` en routers LTE significa que una regla necesita un límite o un sufijo.
* Confirma el ida y vuelta de chips: selecciona dos marcas + un valor de especificación, luego asegura que el contador de resultados baja y
  que ambos chips enlazan de vuelta a una URL que quita exactamente un filtro.
