# Supprimer un thème Journal2/Journal3 nulled (OpenCart 2.3)

Journal2 et Journal3 ne sont PAS de simples thèmes — ils modifient les fichiers du core de DEUX façons, et les deux doivent être annulées :

1. **OCMOD** — `system/journal3.ocmod.xml`, `system/da_journal2.ocmod.xml` (84 opérations de fichiers pour J3). Mis en cache dans `system/storage/modification/`.
2. **Éditions directes de fichiers** — l'installeur de Journal2 réécrit directement les fichiers du core (PAS via OCMOD). Confirme en comparant avec le tarball d'origine correspondant.

## Séquence de suppression sûre (changer d'abord, vérifier, puis supprimer)

### 1. Changer de thème (réversible)
```
UPDATE oc_setting SET value='theme_default' WHERE `key`='config_theme';
UPDATE oc_setting SET value='<newtheme>' WHERE `key`='theme_default_directory';
```
Vérifie que le storefront fonctionne (curl 200) AVANT de supprimer quoi que ce soit. Les fichiers Journal restent sur le disque mais sont inertes une fois le thème changé.

### 2. Trouver les fichiers du core modifiés directement (diff vs original)
Télécharge le tarball `VERSION` correspondant : `https://github.com/opencart/opencart/archive/<VERSION>.tar.gz`.
```
for f in system/engine/front.php system/engine/loader.php system/engine/router.php \
         system/engine/action.php system/engine/event.php system/framework.php \
         system/library/template.php system/library/template/php.php system/startup.php; do
  diff -q /tmp/oc<v>/upload/$f $f >/dev/null 2>&1 || echo "DIFFERS: $f";
done
```
La preuve flagrante de cette session : `system/engine/front.php` avait `require_once(DIR_SYSTEM . 'journal2/startup.php')` incrusté (ligne ~48), ce qui provoque une fatale HTTP 500 après la suppression du dossier journal. Restaure ces fichiers depuis le tarball d'origine. Les différences dans `system/framework.php` et `system/engine/router.php` étaient des shims de compatibilité inertes (protégés par `version_compare(VERSION,'2.3','<')`) — vérifie avant de revenir en arrière.

### 3. Supprimer les XML OCMOD + reconstruire le cache
- `mv system/journal3.ocmod.xml system/da_journal2.ocmod.xml <backup>/` (ne supprime PAS avant vérification ; garde `universal_import_pro.ocmod.xml` s'il est présent).
- Lance `scripts/ocmod_refresh.php`. Vérifie `grep -c journal2 system/storage/modification/system/engine/front.php` → 0 (ou le fichier n'existe plus dans le cache).

### 4. Déplacer les dossiers de thème/code hors du webroot (conservés en sauvegarde)
Dossiers + fichiers dispersés (déplace, ne supprime pas à plat, avant vérification) :
- `catalog/view/theme/journal3`, `catalog/view/theme/journal2`
- `system/library/journal3`, `system/library/journal3.php`, `system/journal2`
- `catalog/model/journal3`, `catalog/model/journal2`
- `catalog/controller/journal3`, `catalog/controller/journal2`
- `catalog/controller/module/journal2_*.php` (nombreux)
- `admin/view/template/journal3`, `admin/view/template/journal2`, `admin/view/javascript/journal3`, `admin/view/journal2`
- `admin/model/journal3`, `admin/model/journal2`, `admin/controller/journal3`, `admin/controller/journal2`
- `admin/language/en-gb/journal3`, `admin/language/en-gb/journal2`
- `admin/controller/extension/theme/theme_journal3.php`, `admin/controller/module/journal2.php`
- `admin/language/*/module/journal2.php`, `admin/language/*/extension/theme/theme_journal3.php`
- `admin/view/image/journal3`, `admin/view/stylesheet/journal3`

Attention : un `mv` vers un dossier de sauvegarde à plat entre en collision sur les sous-dossiers de même nom (`journal3`/`journal2` se répètent). Utilise des noms de destination par chemin (`$(echo "$p" | tr '/' '_')`).

### 5. Nettoyer la DB
```
DELETE FROM oc_layout_module WHERE code LIKE 'journal2\_%' OR code LIKE 'journal3\_%' OR code='0';
DELETE FROM oc_setting WHERE `key` LIKE 'journal2\_%' OR `key` LIKE 'theme_journal3%' OR `key` LIKE '%journal3%';
DELETE FROM oc_extension WHERE type='theme' AND code='theme_journal3';
```
`oc_event` n'a généralement aucune entrée journal — vérifie.

### 6. Vérification finale
curl sur toutes les routes (home/category/product/cart/account) → 200 ; vide `system/storage/cache/*` ; regarde la fin de `system/storage/logs/error.log` pour de nouvelles erreurs.
