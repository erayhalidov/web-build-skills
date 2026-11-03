# Sidebar de filtres qui se rafraîchit sans recharger la page

Exigence du propriétaire : *« cliquer un filtre ne doit pas recharger la page, pour que je puisse ajouter plusieurs filtres d'un coup »*
— avec **un seul** bouton `Filter` et aucun toggle Afficher/Masquer. Vérifié sur un catalogue de 38 k produits en PHP 8.4 + SQLite
(example-shop.com), 2026-09.

## Forme de la solution

| Fichier | Rôle |
| --- | --- |
| `inc/listing.php` → `listing_context(array $CTX, array &$PAGE): array` | construit le scope, les filtres, la page de résultats, les groupes de facettes, les compteurs live, le SEO. Utilisé par **les deux** vues ci-dessous. |
| `views/listing.php` | page complète : page-head, bandes de sous-catégories, `partials/filters.php` + `partials/results.php` dans `<div class="listing" data-listing>`. |
| `views/api_listing.php` | même contexte, n'émet que du JSON. |
| `views/partials/filters.php` / `results.php` | les deux blocs remplaçables (`results` porte `data-results`). |
| `assets/js/site.js` | `showListing()` + `applyFacetCounts()`. |

Routage : chaque branche de listing (rayon / catégorie / sous-catégorie / marque / recherche) rend
`$LISTING_VIEW = !empty($_GET['frag']) ? 'api_listing' : 'listing'` au lieu d'un nom de vue codé en dur, donc
l'URL AJAX est simplement l'URL de la page plus `&frag=1` — pas de seconde route à garder synchronisée.

`render()` doit sauter le layout pour celles-ci : `if (str_starts_with($view, 'api_')) { echo $content; return; }`
(voir le piège dans SKILL.md — sinon le JSON arrive à l'intérieur d'un document HTML complet).

## Contrat JSON

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

`filters` (le HTML de la sidebar) ne fait **plus** partie du contrat : l'envoyer invite à un re-render,
et le re-render est le bug (voir plus bas).

## Compteurs live — une requête par groupe, sa propre dimension relâchée

```php
function facet_live_counts(array $f, array $groups): array
{
    $out = [];
    foreach ($groups as $g) {
        $scope = $f;
        $scope['spec'] = is_array($f['spec'] ?? null) ? $f['spec'] : [];
        unset($scope['spec'][$g['name']], $scope['page'], $scope['per_page'], $scope['sort']);
        [$from, $whereSql, $params, ] = scope_sql($scope, true);      // constructeur de scope partagé
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

Marques : `brand_facets($f, 60)` relâche déjà la sélection de marques ; transforme-la en map slug → compteur.

Ne lance ça que quand quelque chose est sélectionné — sans sélection, le scan de scope mis en cache est identique et bien
moins cher :

```php
$__active = !empty($filters['brand']) || (string)$filters['min'] !== '' || (string)$filters['max'] !== ''
    || !empty($filters['spec']) || !empty($filters['with_image']);
$CTX['facet_counts'] = $__active ? facet_live_counts($filters, $CTX['spec_facets']) : [];
```

Mesuré sur le site en production : 17 ms page non filtrée, 49 ms page filtrée, 53 ms requête de fragment.

Règles de rendu (côté serveur, pour tenir aussi sans JS) :
* compteur 0 **et** non coché → ne rend pas le `<li>` du tout ;
* chaque valeur cochée est injectée de force dans la liste de valeurs de son groupe (les facettes top-N peuvent la retirer) ;
* un groupe sans valeur visible ne rend rien.

## Côté client

`showListing(path, opts)` :

1. construit les params depuis le formulaire live (`new FormData(document.querySelector('[data-filter-form]'))`, en sautant les
   valeurs vides et le `sort=relevance` par défaut) — **cherche le formulaire à chaque appel**, il est remplacé par
   le rafraîchissement des résultats dans l'ancienne implémentation et une référence en cache devient périmée (ce mode de panne a coûté
   une heure : la seconde coche ne faisait silencieusement rien) ;
2. `opts.resetPage` → retire `page` (changement de filtre/tri) ; les liens gardent ce que leur propre query dit ;
3. `fetch(path + '?' + params + '&frag=1')`, puis remplace `[data-results]` et appelle `applyFacetCounts(data.counts)` ;
4. `history.pushState` avec `data.url`, `popstate` refait le fetch avec `push:false` ;
5. classe `.is-loading` pendant la requête ; en cas d'erreur, fallback sur `window.location.href`.

`applyFacetCounts(counts)` — la partie qui corrige « je coche un filtre et un autre se retrouve coché » :

```js
// les inputs portent data-facet="<group>" data-facet-value="<value>"; le <em> porte data-facet-count
const n = (group === 'brand' ? counts.brand : counts.groups[group])?.[value] ?? 0;
li.hidden = (n <= 0 && !input.checked);           // ne touche jamais le nœud lui-même
if (!li.hidden && n > 0) em.textContent = fmtd(n);
```

* Pas de `innerHTML`, pas de remplacement du `<aside>` — la case cochée doit rester le même nœud DOM.
* Badges de groupe (`data-facet-badge`) = nombre d'inputs cochés ; masque le badge à 0.
* Un groupe dont tous les items sont cachés et qui n'a rien de coché reçoit `grp.hidden = true`.
* Badge du bouton `Filter` = facettes cochées + champs de prix remplis.

## Tester que le « pas de rechargement » est réel

Pose un marqueur sur `window` avant d'interagir ; il ne survit que si le document n'est jamais remplacé :

```js
await js(`window.__mark = 1; 1`);
// clique / coche, attends le fetch
const reloaded = await js(`window.__mark !== 1`);   // doit être false
```

Asserte aussi, dans la même passe :
* `visibleFacets` baisse et `zeroCounts === 0` ;
* la case cochée est toujours cochée, toujours visible, et `sameNode` — tague-la (`box.__id = 'TICKED'`) et cherche
  cette propriété à nouveau après le rafraîchissement ;
* deux filtres se combinent (l'URL porte les deux params, chips = 2, le compteur baisse) ;
* `location.search` n'a pas de `frag`, pas de `sort=relevance`, pas de `min=/max=` vides ;
* la pagination garde `page=2` alors qu'un changement de filtre la remet à 1 ;
* le chemin sans JS : `curl` la query exacte que le formulaire enverrait et asserte 200 + le compteur attendu.
