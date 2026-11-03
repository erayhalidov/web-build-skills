---
name: wp-dump-to-static-php-site
description: Rebuild a dead WordPress site from its .sql dump.
---

# WordPress SQL dump → plain-PHP site

Use when you get a `*.sql` WordPress dump (or an empty CloudPanel site + dump) and the goal is a
modern, fast site **without** WordPress: content in a generated PHP data file, clean URLs, bilingual.

## 1. Import & inventory the dump
```bash
clpctl db:show:master-credentials                 # CloudPanel MySQL root creds
export MYSQL_PWD='<pass>'; M="mariadb -h127.0.0.1 -uroot"
$M -e "CREATE DATABASE IF NOT EXISTS src_tmp CHARACTER SET utf8mb4;"
$M src_tmp < dump.sql
$M src_tmp -e "SELECT post_type,post_status,COUNT(*) FROM wp_posts GROUP BY 1,2 ORDER BY 3 DESC;"
$M src_tmp -e "SELECT option_name,LEFT(option_value,120) FROM wp_options
  WHERE option_name IN ('siteurl','home','blogname','WPLANG','template','page_on_front');"
```
Export posts as XML (`mariadb --xml`) and parse with `xml.etree` — avoids tab/newline breakage from `-N`.

## 2. Recover the images (the hard part)
The dump has DB rows only; `wp-content/uploads` is usually gone. Recovery ladder:
1. `grep -oE 'https?://[^"]+\.(jpg|jpeg|png|webp)'` over `post_content` — **external hosts still serve**
   (blogspot `*.bp.blogspot.com`, Facebook CDN names `NNN_NNN_NNN_n.jpg`).
2. Blogspot: swap the size segment for max res — `re.sub(r'/s\d+/','/s1600/',url)`; fall back to the original.
3. Own-domain `/wp-content/uploads/...`: try `https://web.archive.org/web/2022id_/<url>` — **usually 404**
   (verify: real image = HTTP 200 + `image/*` + >5 KB; a ~4.6 KB HTML body is the Wayback 404 page).
4. Whatever is missing → tell the user and design an intentional placeholder card. Never fake photos.

Normalise WP size suffixes when matching filenames: `re.sub(r'-\d+\.jpg$','.jpg', name)` (`foo-1024x683.jpg`).

## 3. Image pipeline (PIL, no ImageMagick needed)
Per image emit `full` (≤1400w), `card` (≤760w), `thumb` (≤380w) as **JPEG + WebP**, never upscale,
`ImageOps.exif_transpose` first, then `jpegoptim --strip-all -m86`. Write a manifest JSON with
`w/h/ratio` per image so PHP can emit `width`/`height` (no layout shift).

## 4. Generate the data file, don't hand-write it
`gen_data.py` holds a hand-curated dict per record (specs, EN/BG copy) + the image manifest and
prints `inc/data.php` (`<?php return [...];`). Regenerating is idempotent; `php -l` it after.
Keep the old WP slug (`post_name`, `urllib.parse.unquote`) in each record for 301s.
**Only include facts stated in the dump** — omit a spec key rather than inventing a value.

## 5. Site skeleton (plain PHP)
```
index.php          front controller: routes on trim(parse_url(REQUEST_URI))
inc/config.php     constants, ASSET_V cache buster, $LANG from /bg/ prefix, t()/u()/f()/pic()
inc/layout.php     page_head() + site_header() + site_footer()
inc/parts.php      card/partial renderers
pages/*.php        home, list, detail, gallery, about, contact, 404
assets/{css,js,img}
```
- nginx (CloudPanel default) already does `try_files $uri $uri/ /index.php?$args` → clean URLs work.
- Language by **URL prefix** (`/bg/...`), never cookie — stays cache-friendly behind Varnish/Cloudflare.
- 301 old permalinks in the `default:` branch: `strtolower(rawurldecode($seg[0]))` vs stored WP slug.
- Contact form: `mail()` + append to a log **outside** the webroot (`__DIR__.'/../../data/'`), honeypot field.
  Check `dig MX` first — a domain with no MX means the published address is dead; say so.

## 6. Deploy on CloudPanel
```bash
DEST=/home/<user>/htdocs/<domain>
rsync -a --delete --exclude dev-router.php /root/build/ "$DEST/"
chown -R <user>:<user> "$DEST"
find "$DEST" -type d -exec chmod 755 {} \; ; find "$DEST" -type f -exec chmod 644 {} \;
varnishadm "ban req.url ~ ."          # CloudPanel proxies :8080 through Varnish
```

## 7. Verify for real (no eyeballing required)
```bash
php -S 127.0.0.1:8099 dev-router.php   # dev-router: return false for existing files, else index.php
for u in / /list /list/slug /gallery /about /contact /bg/ /nope; do curl -so /dev/null -w "$u %{http_code}\n" "http://127.0.0.1:8099$u"; done
```
Then in the browser tool run one JS probe: computed `fontFamily`/accent colour, `document.documentElement.scrollWidth`
vs `innerWidth` (overflow), `images.filter(i=>i.naturalWidth===0)` (broken), `document.fonts.status`.
Screenshots without a vision model: headless Chromium is already on disk from Playwright —
`~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome --headless=new --no-sandbox --hide-scrollbars
--window-size=1440,1700 --virtual-time-budget=9000 --screenshot=out.png <url>` — then send them to the
user as `MEDIA:/path.jpg` and sanity-check with PIL (avg brightness, unique colours, accent-pixel count).

## Offering design directions
Build the data + image layer once, then 2–3 **self-contained variant pages** (inline `<style>`, own fonts)
routed at `/v2`, `/v3` with a floating switcher, and let the user pick before you theme the whole site.
Once picked: rewrite `assets/css/site.css` keeping every class name, move the winning page structure into
the shared shell, then `rm` the variant pages + switcher (leave no leftovers).

## Pitfalls
- **Bump `ASSET_V` on every CSS/JS change.** Same `?v=` = Cloudflare/Varnish/browser serve the old file and
  you will "verify" a stale design. This bites every single time.
- **Google Fonts is a render blocker** — measured 5 205 ms of blank screen on a real site while every
  self-hosted asset took 20–50 ms. Self-host the woff2s (`fonts.googleapis.com/css2?...` with a desktop UA
  returns per-subset variable-font URLs), `@font-face` + `font-display:swap`, `<link rel=preload>` the subset
  matching the page language. First paint went 5516 → 440 ms. Add `font/woff2 woff2;` to
  `/etc/nginx/mime.types` (nginx ships only `woff`) or fonts are served as octet-stream.
- **`hidden` loses to any author `display`.** `<div class="mnav" hidden>` + `.mnav{display:flex}` = the mobile
  panel is permanently visible on desktop too. Always pair with `.mnav[hidden]{display:none!important}`.
- **Opacity-0 scroll-reveal animations WILL hide content.** With `threshold:0.06` + negative bottom
  `rootMargin`, a first row sitting just below the fold never intersects and the whole grid stays invisible
  (a headless screenshot comes out black — that is the tell). Use `threshold:0`, a *positive* bottom
  rootMargin, re-add `.in` whenever a filter shows an element, plus a `load` net and a hard
  `setTimeout(revealAll, 2500)`, plus `<noscript><style>.rv{opacity:1}</style></noscript>`.
  Verify with `getComputedStyle(card).opacity`, never by trusting the HTML.
- Paint-heavy CSS makes scrolling stutter: `filter:` on large images (bake the treatment into the file at
  build time instead), `backdrop-filter:blur()` on a fixed header, and `transition:all` (animates layout).
- Don't use `z-index:-1` on a `::after` fill inside a button — it sinks behind the section background.
  Animate `background-color` instead.
- Plural forms need a helper (`1 нож` / `7 ножа`), not `"$n " . t('word')`.
- Derive a short grouping label (`steel_key`-style) for chips/filters; order the match rules so the
  specific case wins (`laminate` before `1.2210` in "san-mai laminate, 1.2210 core").
- Cyrillic-safe Google fonts: Oswald, Inter, Manrope, Lora, Playfair Display, PT Serif, Montserrat.
  Cormorant/Fraunces/Spectral silently fall back for BG text. Note `№` (U+2116) lives in the *cyrillic*
  subset — an English page using it still pulls the cyrillic woff2.
- When normalising WordPress upload filenames, strip **only** `-<W>x<H>` (`re.sub(r'-\d+x\d+(?=\.\w+$)','')`).
  A naive `-\d+\.jpg$` collapses `Picture-001.jpg`, `Picture-045.jpg` … into one name and silently drops photos.
- Before declaring images unrecoverable, ask the user — an old `wp-content/uploads/<year>/<month>` folder
  lying around on the server beat both blogspot and the Wayback Machine for 37 files here.
- `php -l` every generated/edited file before deploying.
