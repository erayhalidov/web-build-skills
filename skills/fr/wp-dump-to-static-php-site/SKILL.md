---
name: wp-dump-to-static-php-site
description: "Reconstruire un WordPress mort depuis son dump .sql."
---

# Dump SQL WordPress → site en PHP simple

À utiliser quand tu reçois un dump WordPress `*.sql` (ou un site CloudPanel vide + un dump) et que l'objectif est un
site moderne et rapide **sans** WordPress : contenu dans un fichier de données PHP généré, URL propres, bilingue.

## 1. Importer & inventorier le dump
```bash
clpctl db:show:master-credentials                 # identifiants root MySQL CloudPanel
export MYSQL_PWD='<pass>'; M="mariadb -h127.0.0.1 -uroot"
$M -e "CREATE DATABASE IF NOT EXISTS src_tmp CHARACTER SET utf8mb4;"
$M src_tmp < dump.sql
$M src_tmp -e "SELECT post_type,post_status,COUNT(*) FROM wp_posts GROUP BY 1,2 ORDER BY 3 DESC;"
$M src_tmp -e "SELECT option_name,LEFT(option_value,120) FROM wp_options
  WHERE option_name IN ('siteurl','home','blogname','WPLANG','template','page_on_front');"
```
Exporte les posts en XML (`mariadb --xml`) et parse avec `xml.etree` — ça évite les cassures sur tabulations/retours à la ligne de `-N`.

## 2. Récupérer les images (la partie difficile)
Le dump ne contient que des lignes de DB ; `wp-content/uploads` a généralement disparu. Échelle de récupération :
1. `grep -oE 'https?://[^"]+\.(jpg|jpeg|png|webp)'` sur `post_content` — **les hôtes externes servent encore**
   (blogspot `*.bp.blogspot.com`, noms du CDN Facebook `NNN_NNN_NNN_n.jpg`).
2. Blogspot : remplace le segment de taille par la résolution max — `re.sub(r'/s\d+/','/s1600/',url)` ; fallback sur l'original.
3. `/wp-content/uploads/...` de ton propre domaine : essaie `https://web.archive.org/web/2022id_/<url>` — **souvent 404**
   (vérifie : une vraie image = HTTP 200 + `image/*` + >5 Ko ; un corps HTML de ~4,6 Ko est la page 404 de Wayback).
4. Ce qui manque → dis-le à l'utilisateur et conçois une carte placeholder intentionnelle. Ne fabrique jamais de fausses photos.

Normalise les suffixes de taille WP au matching des noms de fichiers : `re.sub(r'-\d+\.jpg$','.jpg', name)` (`foo-1024x683.jpg`).

## 3. Pipeline d'images (PIL, pas besoin d'ImageMagick)
Pour chaque image, émets `full` (≤1400w), `card` (≤760w), `thumb` (≤380w) en **JPEG + WebP**, sans jamais agrandir,
`ImageOps.exif_transpose` d'abord, puis `jpegoptim --strip-all -m86`. Écris un manifest JSON avec
`w/h/ratio` par image pour que PHP puisse émettre `width`/`height` (pas de décalage de layout).

## 4. Générer le fichier de données, ne pas l'écrire à la main
`gen_data.py` contient un dictionnaire curaté à la main par enregistrement (specs, copie EN/BG) + le manifest d'images et
imprime `inc/data.php` (`<?php return [...];`). La régénération est idempotente ; `php -l` dessus ensuite.
Garde l'ancien slug WP (`post_name`, `urllib.parse.unquote`) dans chaque enregistrement pour les 301.
**N'inclus que les faits énoncés dans le dump** — omets une clé de spec plutôt que d'inventer une valeur.

## 5. Squelette du site (PHP simple)
```
index.php          front controller : route sur trim(parse_url(REQUEST_URI))
inc/config.php     constantes, cache buster ASSET_V, $LANG depuis le préfixe /bg/, t()/u()/f()/pic()
inc/layout.php     page_head() + site_header() + site_footer()
inc/parts.php      renderers de cartes/partials
pages/*.php        home, list, detail, gallery, about, contact, 404
assets/{css,js,img}
```
- nginx (CloudPanel par défaut) fait déjà `try_files $uri $uri/ /index.php?$args` → les URL propres fonctionnent.
- Langue par **préfixe d'URL** (`/bg/...`), jamais par cookie — reste cache-friendly derrière Varnish/Cloudflare.
- 301 des anciens permaliens dans la branche `default:` : `strtolower(rawurldecode($seg[0]))` contre le slug WP stocké.
- Formulaire de contact : `mail()` + ajout à un log **hors** du webroot (`__DIR__.'/../../data/'`), champ honeypot.
  Vérifie d'abord `dig MX` — un domaine sans MX signifie que l'adresse publiée est morte ; dis-le.

## 6. Déployer sur CloudPanel
```bash
DEST=/home/<user>/htdocs/<domain>
rsync -a --delete --exclude dev-router.php /root/build/ "$DEST/"
chown -R <user>:<user> "$DEST"
find "$DEST" -type d -exec chmod 755 {} \; ; find "$DEST" -type f -exec chmod 644 {} \;
varnishadm "ban req.url ~ ."          # CloudPanel proxifie :8080 via Varnish
```

## 7. Vérifier pour de vrai (sans besoin de regarder à l'œil)
```bash
php -S 127.0.0.1:8099 dev-router.php   # dev-router : return false pour les fichiers existants, sinon index.php
for u in / /list /list/slug /gallery /about /contact /bg/ /nope; do curl -so /dev/null -w "$u %{http_code}\n" "http://127.0.0.1:8099$u"; done
```
Puis dans l'outil navigateur lance une sonde JS : `fontFamily`/couleur d'accent calculés, `document.documentElement.scrollWidth`
vs `innerWidth` (débordement), `images.filter(i=>i.naturalWidth===0)` (cassées), `document.fonts.status`.
Des screenshots sans modèle de vision : Chromium headless est déjà sur le disque via Playwright —
`~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome --headless=new --no-sandbox --hide-scrollbars
--window-size=1440,1700 --virtual-time-budget=9000 --screenshot=out.png <url>` — puis envoie-les à
l'utilisateur en `MEDIA:/path.jpg` et contrôle avec PIL (luminosité moyenne, couleurs uniques, nombre de pixels d'accent).

## Proposer des directions de design
Construis la couche données + images une fois, puis 2–3 **pages variantes autonomes** (inline `<style>`, polices propres)
routées sur `/v2`, `/v3` avec un sélecteur flottant, et laisse l'utilisateur choisir avant de thèmer tout le site.
Une fois le choix fait : réécris `assets/css/site.css` en gardant tous les noms de classes, déplace la structure de la page gagnante dans
le shell partagé, puis `rm` les pages variantes + le sélecteur (ne laisse aucun résidu).

## Pièges
- **Bumpe `ASSET_V` à chaque changement de CSS/JS.** Même `?v=` = Cloudflare/Varnish/navigateur servent l'ancien fichier et
  tu vas « vérifier » un design périmé. Ça mord à chaque fois.
- **Google Fonts est un bloqueur de rendu** — mesuré 5 205 ms d'écran blanc sur un vrai site alors que chaque
  asset self-hosted prenait 20–50 ms. Héberge les woff2 toi-même (`fonts.googleapis.com/css2?...` avec un UA desktop
  renvoie des URL de police variable par sous-ensemble), `@font-face` + `font-display:swap`, `<link rel=preload>` sur le sous-ensemble
  correspondant à la langue de la page. Le premier rendu est passé de 5516 → 440 ms. Ajoute `font/woff2 woff2;` à
  `/etc/nginx/mime.types` (nginx ne livre que `woff`) sinon les polices sont servies en octet-stream.
- **`hidden` perd contre n'importe quel `display` auteur.** `<div class="mnav" hidden>` + `.mnav{display:flex}` = le panneau
  mobile est visible en permanence, sur desktop aussi. Accompagne toujours avec `.mnav[hidden]{display:none!important}`.
- **Les animations de scroll-reveal en opacity-0 vont CACHER du contenu.** Avec `threshold:0.06` + un `rootMargin`
  inférieur négatif, une première ligne juste sous la ligne de flottaison n'intersecte jamais et toute la grille reste invisible
  (un screenshot headless sort noir — c'est le signe). Utilise `threshold:0`, un rootMargin
  inférieur *positif*, ré-ajoute `.in` chaque fois qu'un filtre affiche un élément, plus un filet sur `load` et un
  `setTimeout(revealAll, 2500)` en dur, plus `<noscript><style>.rv{opacity:1}</style></noscript>`.
  Vérifie avec `getComputedStyle(card).opacity`, jamais en faisant confiance au HTML.
- Du CSS coûteux au rendu fait saccader le scroll : `filter:` sur de grandes images (intègre le traitement dans le fichier
  au build à la place), `backdrop-filter:blur()` sur un header fixe, et `transition:all` (anime le layout).
- N'utilise pas `z-index:-1` sur un remplissage `::after` dans un bouton — il passe derrière le fond de la section.
  Anime `background-color` à la place.
- Les formes plurielles ont besoin d'un helper (`1 cuchillo` / `7 cuchillos`), pas de `"$n " . t('word')`.
- Dérive un libellé de regroupement court (style `steel_key`) pour les chips/filtres ; ordonne les règles de correspondance pour que
  le cas spécifique gagne (`laminate` avant `1.2210` dans « san-mai laminate, 1.2210 core »).
- Polices Google compatibles cyrillique : Oswald, Inter, Manrope, Lora, Playfair Display, PT Serif, Montserrat.
  Cormorant/Fraunces/Spectral retombent silencieusement pour le texte BG. Note que `№` (U+2116) vit dans le sous-ensemble
  *cyrillique* — une page anglaise qui l'utilise télécharge quand même le woff2 cyrillique.
- Quand tu normalises des noms de fichiers d'upload WordPress, retire **uniquement** `-<W>x<H>` (`re.sub(r'-\d+x\d+(?=\.\w+$)','')`).
  Un `-\\d+\\.jpg$` naïf écrase `Picture-001.jpg`, `Picture-045.jpg`… en un seul nom et fait silencieusement disparaître des photos.
- Avant de déclarer des images irrécupérables, demande à l'utilisateur — un ancien dossier `wp-content/uploads/<year>/<month>`
  traînant sur le serveur a battu blogspot ET la Wayback Machine pour 37 fichiers ici.
- `php -l` chaque fichier généré/édité avant de déployer.
