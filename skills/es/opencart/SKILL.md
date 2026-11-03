---
name: opencart
description: Opera tiendas OpenCart 2.x (temas, limpieza, debug).
---

# Operaciones OpenCart 2.x

## Cuándo usarla
- Trabajar en un sitio OpenCart 2.x: temas, layout, módulos de portada, bloat en disco, debug.
- Quitar un tema — especialmente un Journal2/Journal3 nulled — y cambiar a un tema nativo limpio.
- Construir/personalizar el tema de una tienda.

## Hechos de arquitectura (OpenCart 2.3.x)
- Las plantillas son `.tpl` = PHP crudo renderizado por `Template\PHP` (`require($file)` + `extract($data)`), NO Twig. `system/library/template/tiwg.php` existe pero el loader hardcodea `$route . '.tpl'`; el motor es PHP. No escribas `.twig` para 2.3.
- Resolución del tema activo en `catalog/controller/event/theme.php`:
  - `config_theme == 'theme_default'` → dir del tema = ajuste `theme_default_directory`.
  - si no → usa `config_theme` (Journal3 añade un remap OCMOD `theme_journal3` → `journal3`).
  - Plantilla ausente cae a `default/template/<view>` (mantén el dir de tema "default" como fallback para plantillas de módulos de terceros).
- El tema vive en `catalog/view/theme/<name>/template/` (archivos `.tpl`) + `stylesheet/`.
- Dos archivos de config: `catalog/config.php` (DIR_APPLICATION=catalog) y `admin/config.php` (DIR_APPLICATION=admin, DIR_CATALOG=catalog, DIR_MODIFICATION=system/storage/modification/). Ambos llevan credenciales de BD.

## Cambiar a un tema custom (lo más seguro, reversible)
1. Copia el tema en `catalog/view/theme/<name>/`.
2. BD:
   `UPDATE oc_setting SET value='theme_default' WHERE \`key\`='config_theme';`
   `UPDATE oc_setting SET value='<name>' WHERE \`key\`='theme_default_directory';`
   Asegúrate de que `theme_default_status` = 1.
3. Revertir = un único UPDATE de BD. Verifica con curl antes de cualquier limpieza destructiva.

## Menú de categorías (tema nativo)
El menú de portada nativo solo muestra categorías con `top=1` AND `status=1`. Los temas Journal usaban su propio menú e ignoraban esta flag, así que tras el cambio el menú parece vacío. Arreglo:
`UPDATE oc_category SET top=1 WHERE category_id IN (<top-level ids>);`

## Módulos de portada (nativo)
- Los módulos están en `oc_module` (`setting` es un string JSON); la asignación en `oc_layout_module` (`code` = `<modulecode>.<id>`, `position`, `sort_order`).
- `featured` necesita `"product":["id1","id2",...]`; `latest`/`special`/`bestseller` solo necesitan `limit`/`width`/`height`/`status`.
- Entradas huérfanas del tema antiguo: `DELETE FROM oc_layout_module WHERE code LIKE 'journal2\_%' OR code LIKE 'journal3\_%' OR code='0';`
- Las descripciones de producto viven por idioma en `oc_product_description`; los datos demo de OpenCart están en language_id=1, los datos reales en el id de idioma de la tienda (p. ej. 2 = bg).

## Construir un tema nativo limpio
- Copia el tema default de serie (`upload/catalog/view/theme/default`) del tarball de GitHub que coincida con `VERSION` (index.php) → dir del tema nuevo. Base garantizada compatible.
- Personaliza `stylesheet/stylesheet.css` + `common/header.tpl`, `footer.tpl`, `home.tpl`. El tema de serie es Bootstrap 3 — sobrescríbelo a fondo en CSS.

## Pitfalls (sufridos de verdad)
- `$home` NO está definido en `home.tpl` (solo en header.tpl). Usa URLs relativas (el `<base href>` está puesto) o enlaces `index.php?route=...`.
- Borrar `image/cache/*` como root y recrearlo → dirs propiedad de root; OpenCart (usuario del sitio) recibe luego `imagepng(): Permission denied`. Arreglo: `chown -R <siteuser>:<siteuser> image/cache/`.
- Las cachés CDN/Varnish cachean el CSS con agresividad. Tras cambiar la hoja de estilos, rompe la caché del `<link>`: `stylesheet.css?v=2`, y pasa `?v=$(date +%s)` en las URLs de screenshot/curl.
- Especificidad CSS: `.product-thumb .caption p` (0,2,1) gana a `.product-thumb .price` (0,2,0) — acota las reglas de precio a `.product-thumb .caption .price`.

## Quitar un tema Journal2/Journal3 nulled
La parte difícil: se integran a la vez por OCMOD Y por ediciones directas de archivos del core. Ver `references/journal3-removal.md` para rutas/pasos exactos y `scripts/ocmod_refresh.php` para el refresh independiente.

## Verificación
- `curl -s -o /dev/null -w "%{http_code}"` en cada ruta (home/category/product/cart/account).
- Screenshot headless: el chromium incluido de Playwright en `/root/.cache/ms-playwright/chromium-*/chrome-linux64/chrome --headless --disable-gpu --no-sandbox --hide-scrollbars --window-size=W,H --virtual-time-budget=9000 --screenshot=/tmp/x.png URL`. Confirma el tema con el RGB medio de PIL (oscuro ≈ <60).
- Confirma que el CSS se aplicó de verdad vía `browser_console` con estilos computados (ojo con la caché CDN vieja — compara los bytes servidos, añade `?v=`).
