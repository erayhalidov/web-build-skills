# Diseño por referencia con design-extract MCP

Procedimiento completo para recrear un diseño ajeno con tokens exactos, no a ojo.

## 1. Extrae los tokens

```
mcp__design_extract__extract_design(url="https://target.com")
→ job_id
mcp__design_extract__get_job_status(job_id)
→ { status: "done", summary: { primary, fonts, colorCount, accessibilityScore } }
```

Después:
- `get_colors(job_id)` — paleta con rampas (50-950), backgrounds, text, contrast pairs
- `get_typography(job_id)` — families, scale (size/weight/lineHeight/letterSpacing), **roleScale** (display/h1/h2/body), ratio
- `get_components(job_id)` — variantes de botón, cards, inputs, radius, shadows
- `get_tokens(job_id)` — tokens W3C DTCG, listos para variables CSS

## 2. Comprueba cómo está hecho el sitio

```bash
curl -s -A "Mozilla/5.0" "https://target.com" -o page.html
grep -oP 'href="[^"]*\.css[^"]*"' page.html      # archivos CSS
grep -oE '/_astro/[^"]*' page.html                # ¿Astro?
grep -oP '\-\-prefix_[a-z-]+:[^;}]*' css          # variables CSS del sitio
grep -oP 'border-radius:[^;}]*' css | sort -u     # formas
grep -oP 'transition:[^;}]*' css | sort -u        # animaciones
```

Ricola por ejemplo es Astro + tokens `--ric_*`, radius 4/8/16/9999, easing `cubic-bezier(.39,.575,.565,1)`, duration `.25s`.

## 3. Fuente

Si la referencia usa una fuente **propia** (`url(/fonts/Brand-Bold.woff2)`), no puedes usarla.
Elige una gratuita con carácter parecido:
- gruesa + redondeada + amigable → **Figtree**, Nunito, Outfit
- geométrica moderna → Outfit, Bricolage Grotesque
- acento serif → Fraunces, Cormorant Garamond

Comprueba la disponibilidad: `curl -o /dev/null -w "%{http_code}" "https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap"`

## 4. Construye el design system

Copia las **rampas** de `get_colors().ramps`, no solo el primary:
```css
--green-50: #ddffe8;  ... --green-700: #286140;  --green-950: #0a2516;
```

Respeta la jerarquía de tokens: primitive → semantic → component.

## 5. Verifica visualmente

```python
from playwright.sync_api import sync_playwright
# scroll por pasos (imágenes lazy) → screenshot full_page=True → vision_analyze
```

## Pitfalls

1. **Lazy-load en el screenshot** — los bloques negros en el screenshot NO son un bug. Scroll por pasos de 800px, espera 300ms, luego screenshot.
2. **`naturalWidth === 0` con `complete: false`** — carrera. Espera 2 segundos tras scrollIntoView antes de comprobar.
3. **Desbordamiento horizontal en móvil** — compruébalo siempre. Culpables: hijos grid/flex sin `min-width: 0`, `max-width` sin `overflow: hidden`, `<picture>` sin `display: block`.
4. **`u(lang, "path?query")` pone `/` al final** → `/knives/?cat=x/`. El query tiene que ir aparte.
5. **Fuentes propias de la referencia** — no son públicas, no las busques.
