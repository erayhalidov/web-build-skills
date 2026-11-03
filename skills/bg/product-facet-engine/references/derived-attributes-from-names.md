# Deriving filterable attributes from product names

For feeds with no technical properties (ERP/Icecat-style CSVs: name + EAN + weight + price only).
The derived values are written into the normal `product_properties` table at import time, so the facet
engine, the filter SQL and the spec table all keep working unchanged.

## Attribute catalogue and the rule that actually worked

| Attribute | Rule sketch | Normalisation |
| --- | --- | --- |
| `Colour` | word list: black, white, silver, grey/gray, blue, red, green, yellow, pink, purple, orange, brown, gold, transparent, beige | `gray→Grey`; two colours → `Black / White` |
| `Memory type` | `DDR[2345]L?` | + ` SODIMM` / ` RDIMM` / ` UDIMM` when the name says so |
| `Capacity` | `(\d+(?:[.,]\d+)?)\s*(TB|GB)` **and** the name mentions SSD/HDD/tape/flash/NVMe/microSD | `1024 GB → 1 TB`; two values → `1 TB + 512 GB` |
| `Memory size` | same numeric capture, name mentions DDR/RAM/memory module/SODIMM | as above |
| `Storage capacity` | same capture, name mentions notebook/desktop/server/tablet/phone | as above |
| `Interface` | first hit of NVMe, PCIe, SATA, M.2, Thunderbolt, USB-C, USB 3.x, USB 2.0, HDMI, DisplayPort, DVI, VGA, RJ45, SAS, Fibre Channel, Serial | first match wins, ordered by specificity |
| `Screen size` | `(\d{2}(?:[.,]\d)?)\s?("|inch|in|')`, bound **10–120** | trim trailing zeros → `27 inch` |
| `Resolution` | `4K|UHD|QHD|WQHD|UWQHD|Full HD|FHD|WUXGA|XGA|HD`, else `W x H` → mapped | `UHD → 4K UHD`, `1920x1080 → Full HD` |
| `Wi-Fi` | `Wi-?Fi ?[4567E]` or `802.11(ax|ac|be|n)` | `802.11ax → Wi-Fi 6`, `802.11ac → Wi-Fi 5` |
| `Speed` | `(\d+(?:[.,]\d+)?)\s*(Gbit|Gbps|GbE|igabit)`, bound **1–400**; `\d{2,4}\s?Mbit` | `rtrim(rtrim($v,'0'),'.').' Gbit'` |
| `PoE` | `PoE\+` before plain `PoE` | `PoE+` / `PoE` |
| `Ports` | `\b(\d{1,3})[-\s]?port` or `\b(\d{1,2})\s?x\s?(RJ-?45|LAN|Gigabit|GE)` | `8 ports` |
| `Power` / `Capacity (VA)` | `(\d{3,4})\s?W(?:att)?` bound 45–4000; `(\d{2,4})\s?VA` | `650 W`, `1000 VA` |
| `Length` | `(\d+(?:[.,]\d+)?)\s?(m|mm|cm)` bound 0.1–100 m | cm → m, `2 m` |
| `Form factor` | `2.5"/3.5" HDD/SSD/drive` or `M.2 (2230/2242/2280/22110)` or `\b[124]U\b` | uppercase |
| `Print colour` | black/cyan/magenta/yellow **near** toner/cartridge/ink | `Black` |
| `Paper size` | `A3|A4|A5|A6` **and** paper/print/photo/label/film/designjet in the name | keep as-is |

## Why the bounds and the suffix requirement matter

These are the false positives that actually appeared in production and how they were removed:

* `Speed = 4 Gbit` on LTE routers — the regex matched the mobile generation `4G`. Fix: require an
  explicit rate suffix (`Gbit|Gbps|GbE|igabit`) **and** a 1–400 range.
* `Screen size = 1 inch` — came from the un-bounded second pattern. Fix: the same 10–120 bound in every
  branch, not just the first.
* `Screen size = 45 inch` on networking gear — `19 inch` for rack rails is correct, 45 is not; keep the
  upper bound anyway.
* `Paper size = A5` on monitors — `A3`/`A5` appear inside part numbers. Fix: require paper/print context.
* `Speed = 83 Gbit` — regex picked a random number followed by `G`. Same range fix.

## Ordering and merge rules

1. Extract only when the row's own feed has no such property (the XML feed provides `Memory type`,
   `Screen size`, … already) — otherwise you downgrade real supplier data with a regex guess.
2. Store with a high `sort` value so the spec table shows feed properties first.
3. Re-run the importer after rule changes; the facet cache keys on `built_at`, so counts refresh.

## Verification loop that found every one of these

```php
// print the top facet values per big category and eyeball them
foreach (['networking','monitors-accessories','computer-components','notebooks-tablets'] as $cat) {
    foreach (spec_facets(['cat' => $cat], 6, 8) as $g) {
        printf("%-22s cov=%-5d %s\n", $g['name'], $g['cov'],
            implode(' | ', array_map(fn($v) => $v['value'] . ' (' . $v['n'] . ')', array_slice($g['values'], 0, 4))));
    }
}
```

Values that read as nonsense (`1 inch`, `4 Gbit`, `A5` on monitors) are always a rule that needs a bound,
a suffix or a context keyword. Facet coverage of ~70–80 % of the catalogue is a healthy result; the
unmatched remainder is real (feeds genuinely lack the data) and must not be forced into a bucket.
