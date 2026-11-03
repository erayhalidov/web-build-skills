---
name: opencart
description: "Gérer des boutiques OpenCart 2.x (thèmes, nettoyage, debug)."
---

# Opérations OpenCart 2.x

## Quand l'utiliser
- Travail sur un site OpenCart 2.x : thèmes, layout, modules de la page d'accueil, gonflement du disque, debugging.
- Suppression d'un thème — surtout un Journal2/Journal3 nulled — et passage à un thème natif propre.
- Construction/personnalisation d'un thème de storefront.

## Faits d'architecture (OpenCart 2.3.x)
- Les templates sont des `.tpl` = du PHP brut rendu par `Template\PHP` (`require($file)` + `extract($data)`), PAS du Twig. `system/library/template/tiwg.php` existe mais le loader code en dur `$route . '.tpl'` ; le moteur est PHP. N'écris pas de `.twig` pour 2.3.
- Résolution du thème actif dans `catalog/controller/event/theme.php` :
  - `config_theme == 'theme_default'` → le dossier du thème = le réglage `theme_default_directory`.
  - sinon → utilise `config_theme` (Journal3 ajoute un remap OCMOD `theme_journal3` → `journal3`).
  - Un template manquant retombe sur `default/template/<view>` (garde le dossier de thème « default » comme fallback pour les templates de modules tiers).
- Le thème vit dans `catalog/view/theme/<name>/template/` (fichiers `.tpl`) + `stylesheet/`.
- Deux fichiers de config : `catalog/config.php` (DIR_APPLICATION=catalog) et `admin/config.php` (DIR_APPLICATION=admin, DIR_CATALOG=catalog, DIR_MODIFICATION=system/storage/modification/). Les deux contiennent les identifiants DB.

## Passer à un thème custom (le plus sûr, réversible)
1. Dépose le thème dans `catalog/view/theme/<name>/`.
2. DB :
   `UPDATE oc_setting SET value='theme_default' WHERE \`key\`='config_theme';`
   `UPDATE oc_setting SET value='<name>' WHERE \`key\`='theme_default_directory';`
   Assure-toi que `theme_default_status` = 1.
3. Retour arrière = une seule requête DB. Vérifie avec curl avant tout nettoyage destructif.

## Menu des catégories (thème natif)
Le menu natif du header n'affiche que les catégories avec `top=1` ET `status=1`. Les thèmes Journal utilisaient leur propre menu et ignoraient ce flag, donc après le changement le menu semble vide. Correctif :
`UPDATE oc_category SET top=1 WHERE category_id IN (<top-level ids>);`

## Modules de la page d'accueil (natif)
- Les modules sont dans `oc_module` (`setting` est une chaîne JSON) ; l'affectation dans `oc_layout_module` (`code` = `<modulecode>.<id>`, `position`, `sort_order`).
- `featured` a besoin de `"product":["id1","id2",...]` ; `latest`/`special`/`bestseller` n'ont besoin que de `limit`/`width`/`height`/`status`.
- Entrées orphelines de l'ancien thème : `DELETE FROM oc_layout_module WHERE code LIKE 'journal2\_%' OR code LIKE 'journal3\_%' OR code='0';`
- Les descriptions produit vivent par langue dans `oc_product_description` ; les données de démo OpenCart sont en language_id=1, les vraies données dans l'id de langue de la boutique (ex. 2 = bg).

## Construire un thème natif propre
- Copie le thème default d'origine (`upload/catalog/view/theme/default`) depuis le tarball GitHub correspondant à `VERSION` (index.php) → nouveau dossier de thème. Base garantie compatible.
- Personnalise `stylesheet/stylesheet.css` + `common/header.tpl`, `footer.tpl`, `home.tpl`. Le thème d'origine est Bootstrap 3 — surcharge massivement en CSS.

## Pièges (rencontrés pour de vrai)
- `$home` n'est PAS défini dans `home.tpl` (seulement dans header.tpl). Utilise des URL relatives (le `<base href>` est défini) ou des liens `index.php?route=...`.
- Supprimer `image/cache/*` en root puis recréer → dossiers appartenant à root ; OpenCart (utilisateur du site) reçoit alors `imagepng(): Permission denied`. Correctif : `chown -R <siteuser>:<siteuser> image/cache/`.
- CDN/Varnish cachent le CSS agressivement. Après avoir changé la feuille de style, cache-bust le `<link>` : `stylesheet.css?v=2`, et passe `?v=$(date +%s)` sur les URL de screenshot/curl.
- Spécificité CSS : `.product-thumb .caption p` (0,2,1) bat `.product-thumb .price` (0,2,0) — limite les règles de prix à `.product-thumb .caption .price`.

## Supprimer un thème Journal2/Journal3 nulled
La partie difficile : ils s'intègrent via OCMOD ET via des éditions directes des fichiers du core. Voir `references/journal3-removal.md` pour les chemins/étapes exacts et `scripts/ocmod_refresh.php` pour le refresh autonome.

## Vérification
- `curl -s -o /dev/null -w "%{http_code}"` sur chaque route (home/category/product/cart/account).
- Screenshot headless : le chromium fourni avec Playwright à `/root/.cache/ms-playwright/chromium-*/chrome-linux64/chrome --headless --disable-gpu --no-sandbox --hide-scrollbars --window-size=W,H --virtual-time-budget=9000 --screenshot=/tmp/x.png URL`. Confirme le thème via la moyenne RGB avec PIL (sombre ≈ <60).
- Confirme que le CSS est réellement appliqué via les styles calculés de `browser_console` (attention au cache CDN obsolète — compare les octets servis, ajoute `?v=`).
