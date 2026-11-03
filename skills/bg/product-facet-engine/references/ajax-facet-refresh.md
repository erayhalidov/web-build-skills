# Filter sidebar that refreshes without reloading the page

Owner requirement: *"clicking a filter must not reload the page, so I can add several filters at once"*
— with **one** `Filter` button and no Show/Hide toggles. Verified on a 38 k-product PHP 8.4 + SQLite
catalogue (example-shop.com), 2026-09.

## Shape of the solution

| File | Role |
| --- | --- |
| `inc/listing.php` → `listing_context(array $CTX, array &$PAGE): array` | builds scope, filters, result page, facet groups, live counts, SEO. Used by **both** views below. |
| `views/listing.php` | full page: page-head, sub-category strips, `partials/filters.php` + `partials/results.php` inside `<div class="listing" data-listing>`. |
| `views/api_listing.php` | same context, emits JSON only. |
| `views/partials/filters.php` / `results.php` | the two replaceable blocks (`results` carries `data-results`). |
| `assets/js/site.js` | `showListing()` + `applyFacetCounts()`. |

Routing: every listing branch (department / category / sub-category / brand / search) renders
`$LISTING_VIEW = !empty($_GET['frag']) ? 'api_listing' : 'listing'` instead of a hard-coded view name, so
the AJAX URL is simply the page URL plus `&frag=1` — no second route to keep in sync.

`render()` must skip the layout for these: `if (str_starts_with($view, 'api_')) { echo $content; return; }`
(see the pitfall in SKILL.md — otherwise the JSON arrives inside a full HTML document).

## JSON contract

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

`filters` (the sidebar HTML) is **not** part of the contract any more: sending it invites a re-render,
and re-rendering is the bug (see below).

## Live counts — one query per group, own dimension relaxed

```php
function facet_live_counts(array $f, array $groups): array
{
    $out = [];
    foreach ($groups as $g) {
        $scope = $f;
        $scope['spec'] = is_array($f['spec'] ?? null) ? $f['spec'] : [];
        unset($scope['spec'][$g['name']], $scope['page'], $scope['per_page'], $scope['sort']);
        [$from, $whereSql, $params, ] = scope_sql($scope, true);      // shared scope builder
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

Brands: `brand_facets($f, 60)` already relaxes the brand selection; turn it into a slug → count map.

Only run this when something is selected — with no selection the cached scope scan is identical and much
cheaper:

```php
$__active = !empty($filters['brand']) || (string)$filters['min'] !== '' || (string)$filters['max'] !== ''
    || !empty($filters['spec']) || !empty($filters['with_image']);
$CTX['facet_counts'] = $__active ? facet_live_counts($filters, $CTX['spec_facets']) : [];
```

Measured on the live site: 17 ms unfiltered page, 49 ms filtered page, 53 ms fragment request.

Rendering rules (server side, so it also holds without JS):
* count 0 **and** not ticked → do not render the `<li>` at all;
* every ticked value is force-injected into its group's value list (top-N facets can drop it);
* a group with no visible values renders nothing.

## Client side

`showListing(path, opts)`:

1. build params from the live form (`new FormData(document.querySelector('[data-filter-form]'))`, skipping
   empty values and the default `sort=relevance`) — **look the form up on every call**, it is replaced by
   the results refresh in the old implementation and a cached reference goes stale (that failure mode cost
   an hour: the second tick silently did nothing);
2. `opts.resetPage` → drop `page` (filter/sort change); links keep whatever their own query says;
3. `fetch(path + '?' + params + '&frag=1')`, then replace `[data-results]` and call `applyFacetCounts(data.counts)`;
4. `history.pushState` with `data.url`, `popstate` re-fetches with `push:false`;
5. `.is-loading` class while in flight; on any error fall back to `window.location.href`.

`applyFacetCounts(counts)` — the part that fixes "I tick one filter and a different one gets marked":

```js
// inputs carry data-facet="<group>" data-facet-value="<value>"; the <em> carries data-facet-count
const n = (group === 'brand' ? counts.brand : counts.groups[group])?.[value] ?? 0;
li.hidden = (n <= 0 && !input.checked);           // never touch the node itself
if (!li.hidden && n > 0) em.textContent = fmtd(n);
```

* No `innerHTML`, no replacing the `<aside>` — the ticked checkbox must stay the same DOM node.
* Group badges (`data-facet-badge`) = number of ticked inputs; hide the badge at 0.
* A group whose items are all hidden and which has nothing ticked gets `grp.hidden = true`.
* The `Filter` button badge = ticked facets + filled price fields.

## Testing that "no reload" is real

Set a marker on `window` before interacting; it only survives if the document is never replaced:

```js
await js(`window.__mark = 1; 1`);
// click / tick, wait for the fetch
const reloaded = await js(`window.__mark !== 1`);   // must be false
```

Also assert, in the same run:
* `visibleFacets` drops and `zeroCounts === 0`;
* the ticked box is still checked, still visible, and `sameNode` — tag it (`box.__id = 'TICKED'`) and look
  for that property again after the refresh;
* two filters combine (URL carries both params, chips = 2, count drops);
* `location.search` has no `frag`, no `sort=relevance`, no empty `min=/max=`;
* pagination keeps `page=2` while a filter change resets it;
* the no-JS path: `curl` the exact query the form would send and assert 200 + the expected count.
