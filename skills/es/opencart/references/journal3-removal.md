# Quitar un tema Journal2/Journal3 nulled (OpenCart 2.3)

Journal2 y Journal3 NO son solo temas — modifican archivos del core de DOS formas, y ambas hay que deshacerlas:

1. **OCMOD** — `system/journal3.ocmod.xml`, `system/da_journal2.ocmod.xml` (84 operaciones de archivo para J3). Cacheados en `system/storage/modification/`.
2. **Ediciones directas de archivos** — el instalador de Journal2 reescribe archivos del core directamente (NO vía OCMOD). Confírmalo comparando con el tarball de serie que coincida.

## Secuencia de eliminación segura (cambiar primero, verificar, luego borrar)

### 1. Cambiar de tema (reversible)
```
UPDATE oc_setting SET value='theme_default' WHERE `key`='config_theme';
UPDATE oc_setting SET value='<newtheme>' WHERE `key`='theme_default_directory';
```
Verifica que la tienda funciona (curl 200) ANTES de quitar nada. Los archivos de Journal se quedan en disco pero son inertes una vez cambiado el tema.

### 2. Encontrar los archivos del core modificados directamente (diff vs serie)
Descarga el tarball de la `VERSION` que coincida: `https://github.com/opencart/opencart/archive/<VERSION>.tar.gz`.
```
for f in system/engine/front.php system/engine/loader.php system/engine/router.php \
         system/engine/action.php system/engine/event.php system/framework.php \
         system/library/template.php system/library/template/php.php system/startup.php; do
  diff -q /tmp/oc<v>/upload/$f $f >/dev/null 2>&1 || echo "DIFFERS: $f";
done
```
La prueba irrefutable de esta sesión: `system/engine/front.php` tenía `require_once(DIR_SYSTEM . 'journal2/startup.php')` incrustado (línea ~48), lo que produce un fatal con HTTP 500 tras quitar el dir de journal. Restaura esos archivos desde el tarball de serie. Las diferencias en `system/framework.php` y `system/engine/router.php` eran shims de compatibilidad inertes (protegidos por `version_compare(VERSION,'2.3','<')`) — verifica antes de revertir.

### 3. Quitar los XML de OCMOD + reconstruir la caché
- `mv system/journal3.ocmod.xml system/da_journal2.ocmod.xml <backup>/` (NO borres hasta verificar; conserva `universal_import_pro.ocmod.xml` si existe).
- Ejecuta `scripts/ocmod_refresh.php`. Verifica `grep -c journal2 system/storage/modification/system/engine/front.php` → 0 (o que el archivo ya no exista en la caché).

### 4. Mover los dirs de tema/código fuera del webroot (conservar como backup)
Directorios + archivos dispersos (mover, no borrar en plano, hasta verificar):
- `catalog/view/theme/journal3`, `catalog/view/theme/journal2`
- `system/library/journal3`, `system/library/journal3.php`, `system/journal2`
- `catalog/model/journal3`, `catalog/model/journal2`
- `catalog/controller/journal3`, `catalog/controller/journal2`
- `catalog/controller/module/journal2_*.php` (muchos)
- `admin/view/template/journal3`, `admin/view/template/journal2`, `admin/view/javascript/journal3`, `admin/view/journal2`
- `admin/model/journal3`, `admin/model/journal2`, `admin/controller/journal3`, `admin/controller/journal2`
- `admin/language/en-gb/journal3`, `admin/language/en-gb/journal2`
- `admin/controller/extension/theme/theme_journal3.php`, `admin/controller/module/journal2.php`
- `admin/language/*/module/journal2.php`, `admin/language/*/extension/theme/theme_journal3.php`
- `admin/view/image/journal3`, `admin/view/stylesheet/journal3`

Cuidado: `mv` a un dir de backup plano colisiona en subdirs con el mismo nombre (`journal3`/`journal2` se repiten). Usa nombres de destino por ruta (`$(echo "$p" | tr '/' '_')`).

### 5. Limpiar la BD
```
DELETE FROM oc_layout_module WHERE code LIKE 'journal2\_%' OR code LIKE 'journal3\_%' OR code='0';
DELETE FROM oc_setting WHERE `key` LIKE 'journal2\_%' OR `key` LIKE 'theme_journal3%' OR `key` LIKE '%journal3%';
DELETE FROM oc_extension WHERE type='theme' AND code='theme_journal3';
```
`oc_event` normalmente no tiene entradas de journal — verifícalo.

### 6. Verificación final
curl a todas las rutas (home/category/product/cart/account) → 200; limpia `system/storage/cache/*`; revisa `system/storage/logs/error.log` en busca de errores nuevos.
