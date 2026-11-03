---
name: opencart
description: Operate OpenCart 2.x stores (themes, cleanup, debugging).
---

# OpenCart 2.x Operations

## When to use
- Working on an OpenCart 2.x site: themes, layout, homepage modules, disk bloat, debugging.
- Removing a theme — especially a nulled Journal2/Journal3 — and switching to a clean native theme.
- Building/customizing a storefront theme.

## Architecture facts (OpenCart 2.3.x)
- Templates are `.tpl` = raw PHP rendered by `Template\PHP` (`require($file)` + `extract($data)`), NOT Twig. `system/library/template/tiwg.php` exists but the loader hardcodes `$route . '.tpl'`; engine is PHP. Do not write `.twig` for 2.3.
- Active theme resolution in `catalog/controller/event/theme.php`:
  - `config_theme == 'theme_default'` → theme dir = `theme_default_directory` setting.
  - otherwise → uses `config_theme` (Journal3 adds an OCMOD remap `theme_journal3` → `journal3`).
  - Missing template falls back to `default/template/<view>` (keep the "default" theme dir as fallback for third-party module templates).
- Theme lives at `catalog/view/theme/<name>/template/` (`.tpl` files) + `stylesheet/`.
- Two config files: `catalog/config.php` (DIR_APPLICATION=catalog) and `admin/config.php` (DIR_APPLICATION=admin, DIR_CATALOG=catalog, DIR_MODIFICATION=system/storage/modification/). Both carry DB creds.

## Switch to a custom theme (safest, reversible)
1. Drop theme into `catalog/view/theme/<name>/`.
2. DB:
   `UPDATE oc_setting SET value='theme_default' WHERE \`key\`='config_theme';`
   `UPDATE oc_setting SET value='<name>' WHERE \`key\`='theme_default_directory';`
   Ensure `theme_default_status` = 1.
3. Revert = one DB update back. Verify with curl before any destructive cleanup.

## Category menu (native theme)
The native header menu only shows categories with `top=1` AND `status=1`. Journal themes used their own menu and ignored this flag, so after switching the menu looks empty. Fix:
`UPDATE oc_category SET top=1 WHERE category_id IN (<top-level ids>);`

## Homepage modules (native)
- Modules in `oc_module` (`setting` is a JSON string); assignment in `oc_layout_module` (`code` = `<modulecode>.<id>`, `position`, `sort_order`).
- `featured` needs `"product":["id1","id2",...]`; `latest`/`special`/`bestseller` need only `limit`/`width`/`height`/`status`.
- Orphaned old-theme entries: `DELETE FROM oc_layout_module WHERE code LIKE 'journal2\_%' OR code LIKE 'journal3\_%' OR code='0';`
- Product descriptions live per-language in `oc_product_description`; OpenCart demo data sits in language_id=1, real data in the store language id (e.g. 2 = bg).

## Building a clean native theme
- Copy the stock default theme (`upload/catalog/view/theme/default`) from the GitHub tarball matching `VERSION` (index.php) → new theme dir. Guaranteed-compatible base.
- Customize `stylesheet/stylesheet.css` + `common/header.tpl`, `footer.tpl`, `home.tpl`. Stock theme is Bootstrap 3 — override heavily in CSS.

## Pitfalls (hit for real)
- `$home` is NOT defined in `home.tpl` (only in header.tpl). Use relative URLs (the `<base href>` is set) or `index.php?route=...` links.
- Deleting `image/cache/*` as root then recreating → dirs owned by root; OpenCart (site user) then gets `imagepng(): Permission denied`. Fix: `chown -R <siteuser>:<siteuser> image/cache/`.
- CDN/Varnish caches CSS aggressively. After changing the stylesheet, cache-bust the `<link>`: `stylesheet.css?v=2`, and pass `?v=$(date +%s)` on screenshot/curl URLs.
- CSS specificity: `.product-thumb .caption p` (0,2,1) beats `.product-thumb .price` (0,2,0) — scope price rules to `.product-thumb .caption .price`.

## Removing a nulled Journal2/Journal3 theme
The hard part: they integrate via BOTH OCMOD AND direct edits to core files. See `references/journal3-removal.md` for exact paths/steps and `scripts/ocmod_refresh.php` for the standalone refresh.

## Verification
- `curl -s -o /dev/null -w "%{http_code}"` each route (home/category/product/cart/account).
- Headless screenshot: Playwright's bundled chromium at `/root/.cache/ms-playwright/chromium-*/chrome-linux64/chrome --headless --disable-gpu --no-sandbox --hide-scrollbars --window-size=W,H --virtual-time-budget=9000 --screenshot=/tmp/x.png URL`. Confirm theme via PIL average RGB (dark ≈ <60).
- Confirm CSS actually applied via `browser_console` computed styles (watch for stale CDN cache — compare served bytes, add `?v=`).
