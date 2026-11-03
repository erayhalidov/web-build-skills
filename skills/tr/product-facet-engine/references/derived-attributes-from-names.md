# Ürün adlarından filtrelenebilir özellikler türetme

Teknik özelliği olmayan beslemeler için (ERP/Icecat tarzı CSV'ler: yalnızca ad + EAN + ağırlık + fiyat).
Türetilen değerler içe aktarma anında normal `product_properties` tablosuna yazılır, böylece facet
motoru, filtre SQL'i ve spec tablosu değişmeden çalışmaya devam eder.

## Özellik kataloğu ve gerçekten işe yarayan kural

| Özellik | Kural taslağı | Normalleştirme |
| --- | --- | --- |
| `Colour` | kelime listesi: black, white, silver, grey/gray, blue, red, green, yellow, pink, purple, orange, brown, gold, transparent, beige | `gray→Grey`; iki renk → `Black / White` |
| `Memory type` | `DDR[2345]L?` | ad söylüyorsa + ` SODIMM` / ` RDIMM` / ` UDIMM` |
| `Capacity` | `(\d+(?:[.,]\d+)?)\s*(TB|GB)` **ve** ad SSD/HDD/tape/flash/NVMe/microSD geçiriyor | `1024 GB → 1 TB`; iki değer → `1 TB + 512 GB` |
| `Memory size` | aynı sayısal yakalama, ad DDR/RAM/memory module/SODIMM geçiriyor | yukarıdaki gibi |
| `Storage capacity` | aynı yakalama, ad notebook/desktop/server/tablet/phone geçiriyor | yukarıdaki gibi |
| `Interface` | NVMe, PCIe, SATA, M.2, Thunderbolt, USB-C, USB 3.x, USB 2.0, HDMI, DisplayPort, DVI, VGA, RJ45, SAS, Fibre Channel, Serial içinde ilk eşleşme | ilk eşleşme kazanır, özgüllüğe göre sıralı |
| `Screen size` | `(\d{2}(?:[.,]\d)?)\s?("|inch|in|')`, sınır **10–120** | sondaki sıfırları kırp → `27 inch` |
| `Resolution` | `4K|UHD|QHD|WQHD|UWQHD|Full HD|FHD|WUXGA|XGA|HD`, yoksa `W x H` → eşlenmiş | `UHD → 4K UHD`, `1920x1080 → Full HD` |
| `Wi-Fi` | `Wi-?Fi ?[4567E]` veya `802.11(ax|ac|be|n)` | `802.11ax → Wi-Fi 6`, `802.11ac → Wi-Fi 5` |
| `Speed` | `(\d+(?:[.,]\d+)?)\s*(Gbit|Gbps|GbE|igabit)`, sınır **1–400**; `\d{2,4}\s?Mbit` | `rtrim(rtrim($v,'0'),'.').' Gbit'` |
| `PoE` | düz `PoE`'den önce `PoE\+` | `PoE+` / `PoE` |
| `Ports` | `\b(\d{1,3})[-\s]?port` veya `\b(\d{1,2})\s?x\s?(RJ-?45|LAN|Gigabit|GE)` | `8 ports` |
| `Power` / `Capacity (VA)` | `(\d{3,4})\s?W(?:att)?` sınır 45–4000; `(\d{2,4})\s?VA` | `650 W`, `1000 VA` |
| `Length` | `(\d+(?:[.,]\d+)?)\s?(m|mm|cm)` sınır 0.1–100 m | cm → m, `2 m` |
| `Form factor` | `2.5"/3.5" HDD/SSD/drive` veya `M.2 (2230/2242/2280/22110)` veya `\b[124]U\b` | büyük harf |
| `Print colour` | black/cyan/magenta/yellow toner/cartridge/ink **yakınında** | `Black` |
| `Paper size` | `A3|A4|A5|A6` **ve** ad içinde paper/print/photo/label/film/designjet | olduğu gibi tut |

## Sınırlar ve son ek gereksinimi neden önemli

Bunlar üretimde gerçekten ortaya çıkan yanlış pozitifler ve nasıl kaldırıldıkları:

* LTE yönlendiricilerde `Speed = 4 Gbit` — regex mobil nesil `4G` ile eşleşti. Düzeltme: açık bir
  hız son eki (`Gbit|Gbps|GbE|igabit`) **ve** 1–400 aralığı gerektir.
* `Screen size = 1 inch` — sınırsız ikinci desenden geldi. Düzeltme: yalnızca ilk dalda değil,
  her dalda aynı 10–120 sınırı.
* Ağ ekipmanlarında `Screen size = 45 inch` — raf rayları için `19 inch` doğrudur, 45 değildir; yine de
  üst sınırı koru.
* Monitörlerde `Paper size = A5` — `A3`/`A5` parça numaralarının içinde geçiyor. Düzeltme: paper/print bağlamı gerektir.
* `Speed = 83 Gbit` — regex `G` ile takip edilen rastgele bir sayı yakaladı. Aynı aralık düzeltmesi.

## Sıralama ve birleştirme kuralları

1. Yalnızca satırın kendi beslemesinde böyle bir özellik yoksa çıkar (XML beslemesi `Memory type`,
   `Screen size`, … zaten sağlıyor) — yoksa gerçek tedarikçi verisini bir regex tahminiyle düşürürsün.
2. Spec tablosunun önce besleme özelliklerini göstermesi için yüksek bir `sort` değeriyle sakla.
3. Kural değişikliklerinden sonra içe aktarıcıyı yeniden çalıştır; facet önbelleği `built_at` anahtarlıdır,
   dolayısıyla sayılar yenilenir.

## Bunların hepsini bulan doğrulama döngüsü

```php
// print the top facet values per big category and eyeball them
foreach (['networking','monitors-accessories','computer-components','notebooks-tablets'] as $cat) {
    foreach (spec_facets(['cat' => $cat], 6, 8) as $g) {
        printf("%-22s cov=%-5d %s\n", $g['name'], $g['cov'],
            implode(' | ', array_map(fn($v) => $v['value'] . ' (' . $v['n'] . ')', array_slice($g['values'], 0, 4))));
    }
}
```

Anlamsız okunan değerler (monitörlerde `1 inch`, `4 Gbit`, `A5`) her zaman bir sınır, bir son ek ya da
bir bağlam anahtar kelimesi gerektiren kuraldır. Kataloğun ~%70–80'ine ulaşan facet kapsaması sağlıklı bir
sonuçtur; eşleşmeyen kalan kısım gerçektir (beslemelerde gerçekten bu veri yoktur) ve bir kovaya zorlanmamalıdır.
