# design-extract MCP ile referansa göre tasarım

Yabancı bir tasarımı göz kararıyla değil, tam tokenlarla yeniden üretmek için tam prosedür.

## 1. Tokenları çıkar

```
mcp__design_extract__extract_design(url="https://target.com")
→ job_id
mcp__design_extract__get_job_status(job_id)
→ { status: "done", summary: { primary, fonts, colorCount, accessibilityScore } }
```

Ardından:
- `get_colors(job_id)` — ramplar (50-950) ile palet, arka planlar, metin, kontrast çiftleri
- `get_typography(job_id)` — font aileleri, ölçek (boyut/kalınlık/satır yüksekliği/harf aralığı), **roleScale** (display/h1/h2/body), oran
- `get_components(job_id)` — düğme varyantları, kartlar, girdiler, yarıçap, gölgeler
- `get_tokens(job_id)` — W3C DTCG tokenları, CSS değişkenlerine hazır

## 2. Sitenin nasıl yapıldığını incele

```bash
curl -s -A "Mozilla/5.0" "https://target.com" -o page.html
grep -oP 'href="[^"]*\.css[^"]*"' page.html      # CSS dosyaları
grep -oE '/_astro/[^"]*' page.html                # Astro?
grep -oP '\-\-prefix_[a-z-]+:[^;}]*' css          # sitenin CSS değişkenleri
grep -oP 'border-radius:[^;}]*' css | sort -u     # biçimler
grep -oP 'transition:[^;}]*' css | sort -u        # animasyonlar
```

Örneğin Ricola Astro + `--ric_*` tokenları, radius 4/8/16/9999, easing `cubic-bezier(.39,.575,.565,1)`, duration `.25s`.

## 3. Font

Referans **kendi** fontunu kullanıyorsa (`url(/fonts/Brand-Bold.woff2)`), onu kullanamazsın.
Benzer karakterde ücretsiz bir tane seç:
- kalın + yuvarlak + dostane → **Figtree**, Nunito, Outfit
- geometrik modern → Outfit, Bricolage Grotesque
- serif vurgu → Fraunces, Cormorant Garamond

Erişilebilirliği kontrol et: `curl -o /dev/null -w "%{http_code}" "https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap"`

## 4. Design system kur

`get_colors().ramps` içindeki **rampları** kopyala, yalnızca primary'yi değil:
```css
--green-50: #ddffe8;  ... --green-700: #286140;  --green-950: #0a2516;
```

Token hiyerarşisine uy: primitive → semantic → component.

## 5. Görsel olarak doğrula

```python
from playwright.sync_api import sync_playwright
# adım adım kaydır (lazy görseller) → screenshot full_page=True → vision_analyze
```

## Tuzaklar

1. **Screenshot'ta lazy-load** — screenshot'taki siyah bloklar hata DEĞİLDİR. 800px'lik adımlarla kaydır, 300ms bekle, sonra screenshot al.
2. **`complete: false` iken `naturalWidth === 0`** — yarış durumu. Kontrol etmeden önce scrollIntoView sonrası 2 saniye bekle.
3. **Mobilde yatay taşma** — her zaman kontrol et. Suçlular: `min-width: 0` olmayan grid/flex çocukları, `overflow: hidden` olmayan `max-width`, `display: block` olmayan `<picture>`.
4. **`u(lang, "path?query")` sona `/` ekler** → `/knives/?cat=x/`. Query ayrı verilmeli.
5. **Referansın kendi fontları** — herkese açık değiller, aramaya kalkma.
