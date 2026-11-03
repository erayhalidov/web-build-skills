# Design d'après une référence avec design-extract MCP

Procédure complète pour reproduire un design tiers avec des tokens exacts, pas à l'œil.

## 1. Extrais les tokens

```
mcp__design_extract__extract_design(url="https://target.com")
→ job_id
mcp__design_extract__get_job_status(job_id)
→ { status: "done", summary: { primary, fonts, colorCount, accessibilityScore } }
```

Ensuite :
- `get_colors(job_id)` — palette avec rampes (50-950), backgrounds, text, contrast pairs
- `get_typography(job_id)` — families, scale (size/weight/lineHeight/letterSpacing), **roleScale** (display/h1/h2/body), ratio
- `get_components(job_id)` — button variants, cards, inputs, radius, shadows
- `get_tokens(job_id)` — tokens W3C DTCG, prêts pour les variables CSS

## 2. Vérifie comment le site est construit

```bash
curl -s -A "Mozilla/5.0" "https://target.com" -o page.html
grep -oP 'href="[^"]*\.css[^"]*"' page.html      # fichiers CSS
grep -oE '/_astro/[^"]*' page.html                # Astro ?
grep -oP '\-\-prefix_[a-z-]+:[^;}]*' css          # variables CSS du site
grep -oP 'border-radius:[^;}]*' css | sort -u     # formes
grep -oP 'transition:[^;}]*' css | sort -u        # animations
```

Ricola par exemple est en Astro + tokens `--ric_*`, radius 4/8/16/9999, easing `cubic-bezier(.39,.575,.565,1)`, duration `.25s`.

## 3. Police

Si la référence utilise une police **propriétaire** (`url(/fonts/Brand-Bold.woff2)`), tu ne peux pas l'utiliser.
Choisis une police gratuite au caractère similaire :
- gras + arrondi + amical → **Figtree**, Nunito, Outfit
- géométrique moderne → Outfit, Bricolage Grotesque
- accent serif → Fraunces, Cormorant Garamond

Vérifie la disponibilité : `curl -o /dev/null -w "%{http_code}" "https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap"`

## 4. Construis le design system

Copie les **rampes** de `get_colors().ramps`, pas seulement la primary :
```css
--green-50: #ddffe8;  ... --green-700: #286140;  --green-950: #0a2516;
```

Respecte la hiérarchie des tokens : primitive → semantic → component.

## 5. Vérifie visuellement

```python
from playwright.sync_api import sync_playwright
# scroll par étapes (images lazy) → screenshot full_page=True → vision_analyze
```

## Pièges

1. **Lazy-load dans le screenshot** — des blocs noirs dans un screenshot ne sont PAS un bug. Scroll par étapes de 800px, attends 300ms, puis screenshot.
2. **`naturalWidth === 0` avec `complete: false`** — course. Attends 2 s après scrollIntoView avant de vérifier.
3. **Débordement horizontal sur mobile** — vérifie toujours. Coupables : enfants grid/flex sans `min-width: 0`, `max-width` sans `overflow: hidden`, `<picture>` sans `display: block`.
4. **`u(lang, "path?query")` place un `/` à la fin** → `/knives/?cat=x/`. La query doit être passée séparément.
5. **Polices propriétaires de la référence** — elles ne sont pas publiques, ne les cherche pas.
