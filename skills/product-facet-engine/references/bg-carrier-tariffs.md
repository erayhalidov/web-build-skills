# Bulgarian carrier tariffs (Speedy / DPD) — published rates for catalogue shops

Knowledge bank for "add real delivery prices for every European country" requests. Every number here is
from the carrier's published price list — never extrapolate to a destination that is not listed.

## Discovery facts (save an hour next time)

| Fact | Detail |
| --- | --- |
| `www.dpd.bg` | Redirects to the **Speedy** international pages — Speedy operates the DPD network in Bulgaria, so "Speedy - DPD" is one offering, not two quotes. |
| `https://www.dpd.bg` (443) | Connection refused from the server. Plain `http://www.dpd.bg/` answers 200 and issues the redirect to speedy.bg. |
| `https://www.speedy.bg/...` | Cloudflare "Just a moment…" JS challenge — a plain fetch retrieves the challenge page, and a headless Chromium also stalls on it. |
| `https://services.speedy.bg/priceList/?lang=en` | **The actual price list.** 200 to plain curl with a normal browser UA, no challenge. The `<title>` carries the version date (`Speedy Price List 13.09.2026`) — quote that date to customers. |

```bash
curl -sSL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36" \
  -o /tmp/sp_pl.html "https://services.speedy.bg/priceList/?lang=en"
```

Parsing the page (~200 KB of inline tables):
```python
import re, html as H
s = open('/tmp/sp_pl.html', encoding='utf-8', errors='replace').read()
flat = H.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '|', s))).replace('\xa0', ' ')  # prices use &nbsp;
flat = re.sub(r'\|+', '|', flat)
```
* `\xa0` between the amount and the € sign breaks every price regex — normalise it first.
* The header row often lives in its own `<table>` while the country rows sit outside it, so slicing
  between `<table>…</table>` boundaries loses the body. Slice the **flattened text** between the service
  title and the following boilerplate paragraph instead.
* Country names can carry parentheses (`CROATIA (LOCAL NAME: HRVATSKA)`) — match
  `[A-Z][A-Z \.\-\(\)']{3,60}` and you will still lose them; verify the row count against the zone list.

## Services outbound from Bulgaria

| Code | Service | Weight bands | Notes |
| --- | --- | --- | --- |
| 202 | Speedy CEE Economy | 1, 2, 3, 4, 5, 7, 10, 20, 31.5 kg | RO/GR last band `21.72 € + 1.09 € for each extra kg`. |
| 306 | DPD Economy — door to door | 0.5, 5, 10, 31.5, 40 kg | Western / Northern Europe road service. |
| 308 | DPD Economy **Collection request** | 0.5, 5, 10, 31.5, 40 kg | Inbound collections **to** Bulgaria — never quote this for outbound orders. |
| 302 | Speedy Air Express | 0.5 kg steps, 20 bands to 10 kg | Zone 1 (EU outside the road network), Zone 2 (non-EU Europe), 3/4 (world). Above 10 kg → on request. |

All published amounts **already include VAT and the fuel surcharge**.

## Country → service mapping

* **202 CEE Economy** — RO, GR, HU, CZ, PL, SK, SI, HR, CY
* **306 DPD Economy** — AT, DE, BE, FR, IT, NL, DK, LU, ES, EE, FI, LV, LT, PT, SE
* **302 Air Zone 1** — IE, MT (zone-1 list also names AT, BE, HR, CY, CZ, DK, EE, FI, FR, DE, GR, HU, IE, IT, LV, LT, LU, MT, NL, PL, PT, SK, SI, ES, SE)
* **302 Air Zone 2** — AL, AD, BA, FO, GI, GL, VA, IS, LI, MC, ME, NO, SM, RS, CH, TR, GB, GG, JE, Canaries
* **Not listed anywhere** (UA, US, …) → "price on request". Do not interpolate.

Transit times as printed: DE/AT/CZ/PL 3-4 · HU/SK 2-3 · SI 3-4 · HR/BE/FR/IT/NL/DK/LU/LV/LT 4-5 · ES 5-6 ·
SE 5-6 · EE 5-6 · FI/PT 5-7 · Air Zone 1 1-2 · Air Zone 2 1-3. RO/GR/CY are **not** printed — omit the
column rather than guess.

## Price matrix (version 13.09.2026)

202 CEE Economy, bands 1 → 31.5 kg:
```
RO        5.27  5.71  6.13 10.96 10.96 13.63 16.76 21.72 21.72 (+1.09 €/kg over 31.5)
GR        6.44  7.36  7.36 10.96 10.96 13.63 16.76 21.72 21.72 (+1.09 €/kg over 31.5)
HU        8.84  9.70 10.57 23.17 23.17 27.68 27.68 27.68 27.68
CZ        8.84  9.70 10.57 32.21 32.21 38.22 38.22 38.22 38.22
PL/SK/SI/HR 8.84 9.70 10.57 45.76 45.76 51.04 51.04 53.14 53.14
CY       17.03 19.21 21.36 23.72 25.87   —     —     —     —   (only to 5 kg)
```

306 DPD Economy, bands 0.5 / 5 / 10 / 31.5 / 40 kg:
```
AT, DE                     23.78 23.78 28.32 28.32  65.14
BE, FR, IT, NL             32.82 32.82 38.83 38.83  75.67
DK, LU                     44.26 46.38 51.64 53.77  90.58
ES                         42.59 42.59 50.11 50.11  86.94
EE, FI, LV, LT, PT, SE     63.28 65.38 71.71 74.89 111.72
```

302 Air Express: zone 1 from 68.41 € (≤0.5 kg) rising ~10-15 € per 0.5 kg step; zone 2 from 84.08 €.
Transcribe the 20 published rows rather than approximating.

Surcharges that exist (mention in the FAQ, do not silently add to a quote): island/remote post code
28.06 € (202) / 26.54 € (308) incl. VAT · heavy parcel >50 kg 12.77 € · manual handling if a side >100 cm
1.94 € · COD 2.4 % (min 1.23 € international). Promo in force when last checked: **-25 % on 306 tariff
prices for DE and IT, 01.09.2024 – 30.09.2026**.

## Wiring it into the site

`inc/shipping.php`:
* `shipping_services()` — label, carrier, band list, note per service key
* `shipping_rates()` — service → destination group → price per band (arrays in the same order as bands)
* `shipping_map()` — ISO2 → `['service' =>, 'group' =>, 'days' =>]`
* `shipping_quote($cc, $kg)` — first band the weight fits; **`price = null` when beyond the published
  bands** so the UI can say "on request" instead of guessing
* `shipping_pickup()` (free, 0.00) and `shipping_options()`
* `shipping_updated()` — the version string shown to customers

Weight comes from the catalogue (`products.weight`; alias it `AS weight_kg` in shared SELECTs), summed
over quantity. Items without a weight contribute a documented 0.5 kg estimate and the page says the
weight is partly estimated. Recompute everything **server-side on POST** from the product slug — the
browser basket is not trusted for prices or weights.

Rendering: a price table on the delivery page (`Delivery prices to every European country`) built from
the same arrays, so it can never drift from the checkout. Rates change → replace the three arrays, bump
`shipping_updated()`, re-run the route sweep.
