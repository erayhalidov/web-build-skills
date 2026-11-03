---
name: static-product-shop
description: "Build static shops/catalogs (HTML+JS+PHP) from CSV/JSON."
---

# Static Product Shop / Catalog Frontend

Construis une boutique ou un catalogue autonome (catégories + filtres + formulaire de commande) à partir d'un
fichier de données produit existant (export CSV/JSON), hébergé en fichiers statiques simples sur n'importe quel hébergeur.
Les points d'entrée typiques sont `catalog.html` (listing) et `index.html` (landing).

Déclencheur : l'utilisateur demande de « faire une boutique en ligne / un catalogue à partir de ce CSV/fichier, avec toutes les catégories
et les filtres produit » pour un site qui lui appartient déjà.

## Architecture (multi-pages, sans framework)

1. `build_products.py` — parse la donnée source → `products.json` (source de vérité unique)
2. `style.css` + `common.js` — styles partagés + utilitaires partagés : panier en **localStorage**
   (`getCart/saveCart/addToCart/changeQty/removeItem/cartCount/cartTotal`), renderer du header
   (`renderHeader(active)`), `productCard(p)`, `fmt/esc/toast`, `loadData()` avec cache.
3. `index.html` — catalogue : arbre de catégories + dropdowns de filtres + recherche + tri + grille de produits.
   Les cartes pointent vers `product.html?id=X`.
4. `product.html?id=X` — une page par produit (image, tableau de specs, description, produits liés).
5. `order.html` — checkout : articles du panier depuis localStorage + formulaire de livraison.
6. `order.php` — accepte un POST JSON, ajoute à `orders.json` + écrit `orders.log`.

**L'utilisateur préfère des PAGES SÉPARÉES (catalog / product / order), pas une single-page app avec
des modales.** Si tu livres d'abord une modale + un mini-panier dans une seule page, attends-toi à ce qu'on te demande de la découper
en pages plus tard. Commence multi-pages.

## Étapes

1. **Inspecte d'abord les colonnes source** — `head -5` plus une passe rapide en Python avec `collections.Counter`
   pour énumérer catégories, filtres, fabricants, plage de prix, répartition du stock. N'écris jamais le
   générateur à l'aveugle.
2. **Normalise en products.json** avec un objet plat par produit :
   `id, name, manufacturer, price, special, image, stock, description, categories[] (chemins complets), filters{} (groupe→[valeurs]), related[]`.
3. **Génère l'arbre de catégories** à partir des chaînes de chemin (split sur le séparateur de hiérarchie,
   ex. `>`), puis assigne chaque produit à tous ses chemins de catégorie ; matche une catégorie avec la
   règle de préfixe `c === path || c.startsWith(path + '>')`.
4. **Construis index.html** — arbre dans la sidebar avec compteurs, un `<select>` par groupe de filtres, recherche,
   tri (prix asc/desc, nom), grille de cartes. Les cartes pointent vers `product.html?id=<id>` ; le
   bouton « add to cart » appelle `addToCartById(id)`. Supporte les query params `?q=` et `?cat=` pour que
   la recherche et les breadcrumbs produit puissent deep-linker.
5. **Construis product.html** — lis `?id=`, rends image / tableau de specs / description / produits liés,
   breadcrumb pointant vers `index.html?cat=<path>`. Boutons : « add to cart » + « buy now » (ajoute
   puis `location.href='order.html'`).
6. **Construis order.html** — lis le panier depuis localStorage, steppers de quantité + suppression, total, formulaire de
   livraison. Submit → order.php ; en cas de succès `saveCart([])` et affiche l'id de commande retourné.
7. **order.php** — valide nom/téléphone/adresse, ajoute à `orders.json` (JSON_PRETTY_PRINT |
   JSON_UNESCAPED_UNICODE) et ajoute une ligne lisible à `orders.log`. Retourne `{ok:true, order_id}`.
8. **`chown -R <webuser>:<webuser>` le dossier de la boutique** — des fichiers écrits en root cassent les écritures PHP
   et les lectures PHP-FPM. (Les sites CloudPanel tournent sous l'utilisateur du site, ex. `oem`.)
9. **Vérifie en live** — `curl` l'URL (attends 200), `curl -X POST` une commande de test, confirme l'écriture du
   fichier, puis supprime la commande de test pour que la boutique démarre vide.

## Pièges

- **Aligne-toi sur le thème existant du site** : extrais les hex dominants de la feuille de style du site
  (`grep -oiE '#[0-9a-f]{6}' .../stylesheet.css | sort | uniq -c | sort -rn`) et réutilise-les comme
  variables CSS. Deux combinaisons qui marchent bien : navy sombre `#0D1322` + orange `#FF7A00`, ou quasi-noir
  `#0e0f12` + rouge `#e30613`.
- **Ne code JAMAIS en dur téléphone / email / livraison gratuite de mémoire.** Lis-les dans les réglages DB de la
  boutique (voir `references/opencart-csv.md`). Un numéro copié d'une boutique sur une autre est
  un vrai bug embarrassant — interroge toujours `oc_setting`.
- **`onerror` d'image dans des handlers inline** : écris exactement `onerror="this.style.display='none'"`.
  Les variantes avec backslash échappé tuent silencieusement tout le bloc `<script>`.
- **Devise/locale** : affiche l'argent avec le séparateur décimal de la locale (virgule pour BG/DE, point pour EN)
  (`n.toFixed(2).replace('.', ',') + ' €'`). Ne suppose pas BGN sans qu'on te le dise.
- **Override du prix `special`** : n'utilise `price_special` que s'il est défini ET `> 0` ET `< price`.
- **Ajout au panier asynchrone** : `addToCart` a besoin d'un objet produit. Sur les boutons de carte appelle
  `addToCartById(id)` (qui fait `findProduct(id).then(addToCart)`) plutôt que d'inliner
  `JSON.stringify(product)` dans le onclick — inliner l'objet complet (y compris la description HTML)
  alourdit la page et risque de casser les quotes/HTML. Note que `findProduct` retourne une
  promesse, donc une lecture synchrone de `getCart()` juste après `addToCartById()` dans un test montre encore
  vide — `await` la promesse d'abord.
- **Renommage de marque (« change X→Y partout »)** : le CSV *source* peut encore contenir le texte de l'ancienne
  marque dans des colonnes que tu ne rends pas (ex. une colonne `store` inutilisée). Grep uniquement les
  fichiers rendus (`grep -rliE "X" --include="*.html" --include="*.js" --include="*.css"
  --include="*.json" --include="*.php" .`), pas le fichier de données brut, pour confirmer le renommage.
  Renomme aussi l'email visible si l'utilisateur dit « tout », mais signale-le pour qu'il puisse revenir en arrière
  si cette boîte n'est pas réelle.
- **Chemin servi** : un sous-dossier comme `/shop/` est pris par la directive nginx existante du site
  `try_files ... index.php` uniquement parce que `index.html` existe et que `.json` reçoit `application/json`.
  Vérifie le mime type du JSON avec `curl -sI` (certaines configs n'ont besoin de rien, mais vérifie).

## Références

- `references/opencart-csv.md` — colonnes d'export produit OpenCart 2.x, parsing des chaînes
  catégorie/filtre, et lecture des réglages boutique dans la table `oc_setting`.
