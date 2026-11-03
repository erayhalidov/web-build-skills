# Дизайн по референс с design-extract MCP

Пълна процедура за пресъздаване на чужд дизайн с точни токени, не на око.

## 1. Извлечи токените

```
mcp__design_extract__extract_design(url="https://target.com")
→ job_id
mcp__design_extract__get_job_status(job_id)
→ { status: "done", summary: { primary, fonts, colorCount, accessibilityScore } }
```

След това:
- `get_colors(job_id)` — палитра с рампи (50-950), backgrounds, text, contrast pairs
- `get_typography(job_id)` — families, scale (size/weight/lineHeight/letterSpacing), **roleScale** (display/h1/h2/body), ratio
- `get_components(job_id)` — button variants, cards, inputs, radius, shadows
- `get_tokens(job_id)` — W3C DTCG токени, готови за CSS променливи

## 2. Провери как е направен сайтът

```bash
curl -s -A "Mozilla/5.0" "https://target.com" -o page.html
grep -oP 'href="[^"]*\.css[^"]*"' page.html      # CSS файлове
grep -oE '/_astro/[^"]*' page.html                # Astro?
grep -oP '\-\-prefix_[a-z-]+:[^;}]*' css          # CSS променливи на сайта
grep -oP 'border-radius:[^;}]*' css | sort -u     # форми
grep -oP 'transition:[^;}]*' css | sort -u        # анимации
```

Ricola например е Astro + `--ric_*` токени, radius 4/8/16/9999, easing `cubic-bezier(.39,.575,.565,1)`, duration `.25s`.

## 3. Шрифт

Ако референсът ползва **собствен** шрифт (`url(/fonts/Brand-Bold.woff2)`), не можеш да го ползваш.
Избери безплатен с подобен характер:
- дебел + закръглен + приятелски → **Figtree**, Nunito, Outfit
- геометричен модерен → Outfit, Bricolage Grotesque
- серифен акцент → Fraunces, Cormorant Garamond

Провери достъпността: `curl -o /dev/null -w "%{http_code}" "https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap"`

## 4. Изгради design system

Копирай **рампите** от `get_colors().ramps`, не само primary:
```css
--green-50: #ddffe8;  ... --green-700: #286140;  --green-950: #0a2516;
```

Спазвай йерархията на токените: primitive → semantic → component.

## 5. Провери визуално

```python
from playwright.sync_api import sync_playwright
# скрол на стъпки (lazy снимки) → screenshot full_page=True → vision_analyze
```

## Pitfalls

1. **Lazy-load в screenshot** — черни блокове в screenshot НЕ са бъг. Скрол на стъпки по 800px, изчакай 300ms, после screenshot.
2. **`naturalWidth === 0` при `complete: false`** — състезание. Изчакай 2 сек след scrollIntoView, преди да проверяваш.
3. **Horizontal overflow на мобилно** — винаги проверявай. Виновници: grid/flex деца без `min-width: 0`, `max-width` без `overflow: hidden`, `<picture>` без `display: block`.
4. **`u(lang, "path?query")` слага `/` накрая** → `/knives/?cat=x/`. Query-то трябва отделно.
5. **Собствени шрифтове на референса** — не са публични, не ги търси.
