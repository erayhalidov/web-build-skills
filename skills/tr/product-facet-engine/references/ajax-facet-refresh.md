# Sayfayı yeniden yüklemeden yenilenen filtre yan çubuğu

Sahibin gereksinimi: *"bir filtreye tıklamak sayfayı yeniden yüklememeli, böylece birkaç filtreyi aynı
anda ekleyebilirim"* — **tek** bir `Filter` düğmesiyle ve Show/Hide anahtarları olmadan. 38 bin ürünlü bir PHP 8.4 + SQLite
kataloğunda (example-shop.com) doğrulandı, 2026-09.

## Çözümün şekli

| Dosya | Rol |
| --- | --- |
| `inc/listing.php` → `listing_context(array $CTX, array &$PAGE): array` | kapsamı, filtreleri, sonuç sayfasını, facet gruplarını, canlı sayıları, SEO'yu kurar. Aşağıdaki **iki** görünüm de kullanır. |
| `views/listing.php` | tam sayfa: sayfa başı, alt kategori şeritleri, `<div class="listing" data-listing>` içinde `partials/filters.php` + `partials/results.php`. |
| `views/api_listing.php` | aynı bağlam, yalnızca JSON üretir. |
| `views/partials/filters.php` / `results.php` | değiştirilebilir iki blok (`results` `data-results` taşır). |
| `assets/js/site.js` | `showListing()` + `applyFacetCounts()`. |

Yönlendirme: her listeleme dalı (departman / kategori / alt kategori / marka / arama) sabit kodlanmış bir görünüm
adı yerine `$LISTING_VIEW = !empty($_GET['frag']) ? 'api_listing' : 'listing'` render eder, böylece
AJAX URL'si basitçe sayfa URL'si artı `&frag=1` olur — senkron tutulacak ikinci bir rota yok.

`render()` bunlar için düzeni atlamalı: `if (str_starts_with($view, 'api_')) { echo $content; return; }`
(SKILL.md'deki tuzağa bakın — yoksa JSON tam bir HTML belgesinin içinde gelir).

## JSON sözleşmesi

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

`filters` (yan çubuk HTML'i) artık sözleşmenin parçası **değil**: onu göndermek yeniden render'ı davet eder,
ve yeniden render hatanın ta kendisidir (aşağıya bakın).

## Canlı sayılar — grup başına bir sorgu, kendi boyutu gevşetilmiş

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

Markalar: `brand_facets($f, 60)` marka seçimini zaten gevşetir; onu slug → sayı haritasına çevir.

Bunu yalnızca bir şey seçiliyken çalıştır — seçim yokken önbelleğe alınmış kapsam taraması aynıdır ve çok
daha ucuzdur:

```php
$__active = !empty($filters['brand']) || (string)$filters['min'] !== '' || (string)$filters['max'] !== ''
    || !empty($filters['spec']) || !empty($filters['with_image']);
$CTX['facet_counts'] = $__active ? facet_live_counts($filters, $CTX['spec_facets']) : [];
```

Canlı sitede ölçüldü: filtresiz sayfa 17 ms, filtreli sayfa 49 ms, parça isteği 53 ms.

Render kuralları (sunucu tarafında, böylece JS olmadan da geçerli):
* sayı 0 **ve** işaretli değil → `<li>` hiç render edilmez;
* her işaretli değer kendi grubunun değer listesine zorla eklenir (top-N facet'ler onu düşürebilir);
* görünür değeri olmayan bir grup hiçbir şey render etmez.

## İstemci tarafı

`showListing(path, opts)`:

1. parametreleri canlı formdan kur (`new FormData(document.querySelector('[data-filter-form]'))`, boş
   değerleri ve varsayılan `sort=relevance`'ı atlayarak) — **formu her çağrıda yeniden ara**, eski uygulamada
   sonuç yenilemesi onu değiştirir ve önbelleğe alınmış referans bayatlar (bu hata modu bir saate mal oldu:
   ikinci işaretleme sessizce hiçbir şey yapmadı);
2. `opts.resetPage` → `page`'i düşür (filtre/sıralama değişikliği); bağlantılar kendi sorgularının söylediğini korur;
3. `fetch(path + '?' + params + '&frag=1')`, ardından `[data-results]`'ı değiştir ve `applyFacetCounts(data.counts)` çağır;
4. `data.url` ile `history.pushState`, `popstate` `push:false` ile yeniden getirir;
5. istek sürerken `.is-loading` sınıfı; herhangi bir hatada `window.location.href`'e düş.

`applyFacetCounts(counts)` — "bir filtreyi işaretliyorum ve başka biri işaretlenmiş görünüyor" sorununu çözen kısım:

```js
// inputs carry data-facet="<group>" data-facet-value="<value>"; the <em> carries data-facet-count
const n = (group === 'brand' ? counts.brand : counts.groups[group])?.[value] ?? 0;
li.hidden = (n <= 0 && !input.checked);           // never touch the node itself
if (!li.hidden && n > 0) em.textContent = fmtd(n);
```

* `innerHTML` yok, `<aside>`'ı değiştirmek yok — işaretli onay kutusu aynı DOM düğümü olarak kalmalı.
* Grup rozetleri (`data-facet-badge`) = işaretli girdi sayısı; 0'da rozeti gizle.
* Tüm öğeleri gizli ve hiçbir şeyi işaretli olmayan bir grup `grp.hidden = true` alır.
* `Filter` düğmesi rozeti = işaretli facet'ler + doldurulmuş fiyat alanları.

## "Yeniden yükleme yok"un gerçek olduğunu test etme

Etkileşimden önce `window` üzerine bir işaret koy; yalnızca belge hiç değiştirilmezse hayatta kalır:

```js
await js(`window.__mark = 1; 1`);
// click / tick, wait for the fetch
const reloaded = await js(`window.__mark !== 1`);   // must be false
```

Ayrıca aynı çalıştırmada şunları doğrula:
* `visibleFacets` düşer ve `zeroCounts === 0`;
* işaretli kutu hâlâ işaretli, hâlâ görünür ve `sameNode` — etiketle (`box.__id = 'TICKED'`) ve yenilemeden
  sonra o özelliği yeniden ara;
* iki filtre birleşir (URL her iki parametreyi taşır, çipler = 2, sayı düşer);
* `location.search` içinde `frag` yok, `sort=relevance` yok, boş `min=/max=` yok;
* sayfalama `page=2`'yi korur, filtre değişikliği ise sıfırlar;
* JS'siz yol: formun göndereceği sorguyu tam olarak `curl` et ve 200 + beklenen sayıyı doğrula.
