# Removing a nulled Journal2/Journal3 theme (OpenCart 2.3)

Journal2 and Journal3 are NOT just themes — they modify core files TWO ways, and both must be undone:

1. **OCMOD** — `system/journal3.ocmod.xml`, `system/da_journal2.ocmod.xml` (84 file operations for J3). Cached into `system/storage/modification/`.
2. **Direct file edits** — Journal2's installer directly rewrites core files (NOT via OCMOD). Confirm by diffing against the matching stock tarball.

## Safe removal sequence (switch first, verify, then delete)

### 1. Switch theme away (reversible)
```
UPDATE oc_setting SET value='theme_default' WHERE `key`='config_theme';
UPDATE oc_setting SET value='<newtheme>' WHERE `key`='theme_default_directory';
```
Verify storefront works (curl 200) BEFORE removing anything. Journal files stay on disk but are inert once the theme is switched.

### 2. Find directly-modified core files (diff vs stock)
Download matching `VERSION` tarball: `https://github.com/opencart/opencart/archive/<VERSION>.tar.gz`.
```
for f in system/engine/front.php system/engine/loader.php system/engine/router.php \
         system/engine/action.php system/engine/event.php system/framework.php \
         system/library/template.php system/library/template/php.php system/startup.php; do
  diff -q /tmp/oc<v>/upload/$f $f >/dev/null 2>&1 || echo "DIFFERS: $f";
done
```
The smoking gun this session: `system/engine/front.php` had `require_once(DIR_SYSTEM . 'journal2/startup.php')` baked in (line ~48), which fatals with HTTP 500 after the journal dir is removed. Restore such files from the stock tarball. `system/framework.php` and `system/engine/router.php` differences were inert compat shims (guarded by `version_compare(VERSION,'2.3','<')`) — verify before reverting.

### 3. Remove OCMOD XMLs + rebuild cache
- `mv system/journal3.ocmod.xml system/da_journal2.ocmod.xml <backup>/` (do NOT delete until verified; keep `universal_import_pro.ocmod.xml` if present).
- Run `scripts/ocmod_refresh.php`. Verify `grep -c journal2 system/storage/modification/system/engine/front.php` → 0 (or the file no longer exists in the cache).

### 4. Move theme/code dirs out of webroot (preserve as backup)
Directories + scattered files (move, don't flat-delete, until verified):
- `catalog/view/theme/journal3`, `catalog/view/theme/journal2`
- `system/library/journal3`, `system/library/journal3.php`, `system/journal2`
- `catalog/model/journal3`, `catalog/model/journal2`
- `catalog/controller/journal3`, `catalog/controller/journal2`
- `catalog/controller/module/journal2_*.php` (many)
- `admin/view/template/journal3`, `admin/view/template/journal2`, `admin/view/javascript/journal3`, `admin/view/journal2`
- `admin/model/journal3`, `admin/model/journal2`, `admin/controller/journal3`, `admin/controller/journal2`
- `admin/language/en-gb/journal3`, `admin/language/en-gb/journal2`
- `admin/controller/extension/theme/theme_journal3.php`, `admin/controller/module/journal2.php`
- `admin/language/*/module/journal2.php`, `admin/language/*/extension/theme/theme_journal3.php`
- `admin/view/image/journal3`, `admin/view/stylesheet/journal3`

Caveat: `mv` into a flat backup dir collides on same-named subdirs (`journal3`/`journal2` recur). Use per-path dest names (`$(echo "$p" | tr '/' '_')`).

### 5. Clean the DB
```
DELETE FROM oc_layout_module WHERE code LIKE 'journal2\_%' OR code LIKE 'journal3\_%' OR code='0';
DELETE FROM oc_setting WHERE `key` LIKE 'journal2\_%' OR `key` LIKE 'theme_journal3%' OR `key` LIKE '%journal3%';
DELETE FROM oc_extension WHERE type='theme' AND code='theme_journal3';
```
`oc_event` typically has no journal entries — verify.

### 6. Final verify
curl all routes (home/category/product/cart/account) → 200; clear `system/storage/cache/*`; tail `system/storage/logs/error.log` for fresh errors.
