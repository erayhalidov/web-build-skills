# Design from a reference with the design-extract MCP

Full procedure for recreating someone else's design with exact tokens, not by eye.

## 1. Extract the tokens

```
mcp__design_extract__extract_design(url="https://target.com")
→ job_id
mcp__design_extract__get_job_status(job_id)
→ { status: "done", summary: { primary, fonts, colorCount, accessibilityScore } }
```

Then:
- `get_colors(job_id)` — palette with ramps (50-950), backgrounds, text, contrast pairs
- `get_typography(job_id)` — families, scale (size/weight/lineHeight/letterSpacing), **roleScale** (display/h1/h2/body), ratio
- `get_components(job_id)` — button variants, cards, inputs, radius, shadows
- `get_tokens(job_id)` — W3C DTCG tokens, ready for CSS variables

## 2. Check how the site was built

```bash
curl -s -A "Mozilla/5.0" "https://target.com" -o page.html
grep -oP 'href="[^"]*\.css[^"]*"' page.html      # CSS files
grep -oE '/_astro/[^"]*' page.html                # Astro?
grep -oP '\-\-prefix_[a-z-]+:[^;}]*' css          # the site's CSS variables
grep -oP 'border-radius:[^;}]*' css | sort -u     # shapes
grep -oP 'transition:[^;}]*' css | sort -u        # animations
```

Ricola, for example, is Astro + `--ric_*` tokens, radius 4/8/16/9999, easing `cubic-bezier(.39,.575,.565,1)`, duration `.25s`.

## 3. Font

If the reference uses a **custom** font (`url(/fonts/Brand-Bold.woff2)`), you cannot use it.
Pick a free one with a similar character:
- bold + rounded + friendly → **Figtree**, Nunito, Outfit
- geometric modern → Outfit, Bricolage Grotesque
- serif accent → Fraunces, Cormorant Garamond

Check availability: `curl -o /dev/null -w "%{http_code}" "https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap"`

## 4. Build the design system

Copy the **ramps** from `get_colors().ramps`, not just the primary:
```css
--green-50: #ddffe8;  ... --green-700: #286140;  --green-950: #0a2516;
```

Follow the token hierarchy: primitive → semantic → component.

## 5. Check visually

```python
from playwright.sync_api import sync_playwright
# scroll in steps (lazy images) → screenshot full_page=True → vision_analyze
```

## Pitfalls

1. **Lazy-load in the screenshot** — black blocks in a screenshot are NOT a bug. Scroll in 800px steps, wait 300ms, then screenshot.
2. **`naturalWidth === 0` with `complete: false`** — a race. Wait 2s after scrollIntoView before checking.
3. **Horizontal overflow on mobile** — always check. Culprits: grid/flex children without `min-width: 0`, `max-width` without `overflow: hidden`, `<picture>` without `display: block`.
4. **`u(lang, "path?query")` appends a trailing `/`** → `/knives/?cat=x/`. The query must be passed separately.
5. **The reference's custom fonts** — they are not public, don't go looking for them.
