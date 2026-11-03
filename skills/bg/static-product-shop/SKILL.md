---
name: static-product-shop
description: "Build static shops/catalogs (HTML+JS+PHP) from CSV/JSON."
---

# Static Product Shop / Catalog Frontend

Build a self-contained online shop or catalog (categories + filters + order form) from an
existing product data file (CSV/JSON export), hosted as plain static files on any web host.
Typical entry points are `catalog.html` (listing) and `index.html` (landing).

Trigger: user asks to "make an online store / catalog from this CSV/file, with all categories
and product filters" for a site they already own.

## Architecture (multi-page, no framework)

1. `build_products.py` — parse the source data → `products.json` (single source of truth)
2. `style.css` + `common.js` — shared styles + shared utilities: cart in **localStorage**
   (`getCart/saveCart/addToCart/changeQty/removeItem/cartCount/cartTotal`), header renderer
   (`renderHeader(active)`), `productCard(p)`, `fmt/esc/toast`, cached `loadData()`.
3. `index.html` — catalog: category tree + filter dropdowns + search + sort + product grid.
   Cards link to `product.html?id=X`.
4. `product.html?id=X` — one page per product (image, specs table, description, related).
5. `order.html` — checkout: cart items from localStorage + delivery form.
6. `order.php` — accepts JSON POST, appends to `orders.json` + writes `orders.log`.

**The user prefers SEPARATE PAGES (catalog / product / order), not a single-page app with
modals.** If you first ship a modal + mini-cart in one page, expect to be asked to split it
into pages later. Start multi-page.

## Steps

1. **Inspect the source columns first** — `head -5` plus a quick Python `collections.Counter`
   pass to enumerate categories, filters, manufacturers, price range, stock split. Never write
   the generator blind.
2. **Normalize into products.json** with one flat object per product:
   `id, name, manufacturer, price, special, image, stock, description, categories[] (full paths), filters{} (group→[values]), related[]`.
3. **Generate the category tree** from the path strings (split on the hierarchy separator,
   e.g. `>`), then assign each product to all its category paths; match a category with the
   prefix rule `c === path || c.startsWith(path + '>')`.
4. **Build index.html** — sidebar tree with counts, one `<select>` per filter group, search,
   sort (price asc/desc, name), grid of cards. Cards link to `product.html?id=<id>`; the
   "add to cart" button calls `addToCartById(id)`. Support `?q=` and `?cat=` query params so
   the search and product breadcrumbs can deep-link.
5. **Build product.html** — read `?id=`, render image / specs table / description / related,
   breadcrumb linking to `index.html?cat=<path>`. Buttons: "add to cart" + "buy now" (add
   then `location.href='order.html'`).
6. **Build order.html** — read cart from localStorage, qty steppers + remove, total, delivery
   form. Submit → order.php; on success `saveCart([])` and show the returned order id.
7. **order.php** — validate name/phone/address, append to `orders.json` (JSON_PRETTY_PRINT |
   JSON_UNESCAPED_UNICODE) and append a human line to `orders.log`. Return `{ok:true, order_id}`.
8. **`chown -R <webuser>:<webuser>` the shop dir** — files written as root break PHP writes
   and PHP-FPM reads. (CloudPanel sites run as the site user, e.g. `oem`.)
9. **Verify live** — `curl` the URL (expect 200), `curl -X POST` a test order, confirm the file
   write, then delete the test order so the store starts empty.

## Pitfalls

- **Match the site's existing theme**: extract top hex colors from the site's stylesheet
  (`grep -oiE '#[0-9a-f]{6}' .../stylesheet.css | sort | uniq -c | sort -rn`) and reuse them as
  CSS vars. Two shapes that work well: dark navy `#0D1322` + orange `#FF7A00`, or near-black
  `#0e0f12` + red `#e30613`.
- **NEVER hardcode phone / email / free-shipping from memory.** Read them from the store's DB
  settings (see `references/opencart-csv.md`). A number copied from one shop onto another is
  a real, embarrassing bug — always query `oc_setting`.
- **Image `onerror` in inline handlers**: write `onerror="this.style.display='none'"` exactly.
  Escaped-backslash variants silently kill the whole `<script>` block.
- **Currency/locale**: display money with the locale's decimal separator (comma for BG/DE, dot for EN)
  (`n.toFixed(2).replace('.', ',') + ' €'`). Don't assume BGN unless told.
- **`special` price override**: only use `price_special` when it is set AND `> 0` AND `< price`.
- **Async add-to-cart**: `addToCart` needs a product object. On card buttons call
  `addToCartById(id)` (does `findProduct(id).then(addToCart)`) rather than inlining
  `JSON.stringify(product)` into the onclick — inlining the full object (incl. the HTML
  description) bloats the page and risks quote/HTML breakage. Note `findProduct` returns a
  promise, so a synchronous `getCart()` read right after `addToCartById()` in a test still
  shows empty — `await` the promise first.
- **Brand rename ("change X→Y everywhere")**: the *source* CSV may still contain the old
  brand text in columns you don't render (e.g. an unused `store` column). Grep only the
  rendered files (`grep -rliE "X" --include="*.html" --include="*.js" --include="*.css"
  --include="*.json" --include="*.php" .`), not the raw data file, to confirm the rename.
  Rename the visible email too if the user says "everything", but flag it so they can revert
  if that mailbox isn't real.
- **Serve path**: a subfolder like `/shop/` is picked up by the site's existing nginx
  `try_files ... index.php` only because `index.html` exists and `.json` gets `application/json`.
  Verify the JSON mime type with `curl -sI` (some setups need no config, but check).

## References

- `references/opencart-csv.md` — OpenCart 2.x product export columns, category/filter string
  parsing, and reading store settings from the `oc_setting` table.
