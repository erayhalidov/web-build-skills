---
name: wp-dump-to-static-php-site
description: Reconstruye un WordPress muerto desde su dump .sql.
---

# Dump SQL de WordPress → sitio en PHP plano

Úsala cuando tengas un dump `*.sql` de WordPress (o un sitio CloudPanel vacío + dump) y el objetivo sea un sitio
moderno y rápido **sin** WordPress: contenido en un archivo PHP de datos generado, URLs limpias, bilingüe.

## 1. Importa e inventaría el dump
```bash
clpctl db:show:master-credentials                 # credenciales root de MySQL en CloudPanel
export MYSQL_PWD='<pass>'; M="mariadb -h127.0.0.1 -uroot"
$M -e "CREATE DATABASE IF NOT EXISTS src_tmp CHARACTER SET utf8mb4;"
$M src_tmp < dump.sql
$M src_tmp -e "SELECT post_type,post_status,COUNT(*) FROM wp_posts GROUP BY 1,2 ORDER BY 3 DESC;"
$M src_tmp -e "SELECT option_name,LEFT(option_value,120) FROM wp_options
  WHERE option_name IN ('siteurl','home','blogname','WPLANG','template','page_on_front');"
```
Exporta los posts como XML (`mariadb --xml`) y parsea con `xml.etree` — evita la rotura por tabuladores/saltos de línea de `-N`.

## 2. Recupera las imágenes (la parte difícil)
El dump solo tiene filas de BD; `wp-content/uploads` normalmente ya no existe. Escalera de recuperación:
1. `grep -oE 'https?://[^"]+\.(jpg|jpeg|png|webp)'` sobre `post_content` — **los hosts externos aún sirven**
   (blogspot `*.bp.blogspot.com`, nombres del CDN de Facebook `NNN_NNN_NNN_n.jpg`).
2. Blogspot: cambia el segmento de tamaño por la resolución máxima — `re.sub(r'/s\d+/','/s1600/',url)`; si falla, usa la original.
3. Dominio propio `/wp-content/uploads/...`: prueba `https://web.archive.org/web/2022id_/<url>` — **normalmente 404**
   (verifica: imagen real = HTTP 200 + `image/*` + >5 KB; un cuerpo HTML de ~4.6 KB es la página 404 de Wayback).
4. Lo que falte → díselo al usuario y diseña una tarjeta placeholder intencionada. Nunca fotos falsas.

Normaliza los sufijos de tamaño de WP al comparar nombres de archivo: `re.sub(r'-\d+\.jpg$','.jpg', name)` (`foo-1024x683.jpg`).

## 3. Pipeline de imágenes (PIL, sin necesidad de ImageMagick)
Por imagen emite `full` (≤1400w), `card` (≤760w), `thumb` (≤380w) como **JPEG + WebP**, nunca reescales hacia arriba,
`ImageOps.exif_transpose` primero, luego `jpegoptim --strip-all -m86`. Escribe un manifiesto JSON con
`w/h/ratio` por imagen para que PHP pueda emitir `width`/`height` (sin layout shift).

## 4. Genera el archivo de datos, no lo escribas a mano
`gen_data.py` contiene un dict curado a mano por registro (specs, textos EN/BG) + el manifiesto de imágenes y
imprime `inc/data.php` (`<?php return [...];`). Regenerar es idempotente; pásale `php -l` después.
Guarda el slug antiguo de WP (`post_name`, `urllib.parse.unquote`) en cada registro para los 301.
**Incluye solo hechos declarados en el dump** — omite una clave de spec en vez de inventar un valor.

## 5. Esqueleto del sitio (PHP plano)
```
index.php          front controller: enruta sobre trim(parse_url(REQUEST_URI))
inc/config.php     constantes, cache buster ASSET_V, $LANG desde el prefijo /bg/, t()/u()/f()/pic()
inc/layout.php     page_head() + site_header() + site_footer()
inc/parts.php      renderizadores de card/partials
pages/*.php        home, list, detail, gallery, about, contact, 404
assets/{css,js,img}
```
- nginx (por defecto en CloudPanel) ya hace `try_files $uri $uri/ /index.php?$args` → las URLs limpias funcionan.
- Idioma por **prefijo de URL** (`/bg/...`), nunca cookie — se mantiene cacheable tras Varnish/Cloudflare.
- 301 de los permalinks antiguos en la rama `default:`: `strtolower(rawurldecode($seg[0]))` contra el slug de WP guardado.
- Formulario de contacto: `mail()` + anexar a un log **fuera** del webroot (`__DIR__.'/../../data/'`), campo honeypot.
  Comprueba `dig MX` primero — un dominio sin MX significa que la dirección publicada está muerta; dilo.

## 6. Despliegue en CloudPanel
```bash
DEST=/home/<user>/htdocs/<domain>
rsync -a --delete --exclude dev-router.php /root/build/ "$DEST/"
chown -R <user>:<user> "$DEST"
find "$DEST" -type d -exec chmod 755 {} \; ; find "$DEST" -type f -exec chmod 644 {} \;
varnishadm "ban req.url ~ ."          # CloudPanel proxya :8080 a través de Varnish
```

## 7. Verifica de verdad (sin necesidad de mirar a ojo)
```bash
php -S 127.0.0.1:8099 dev-router.php   # dev-router: return false para archivos existentes, si no index.php
for u in / /list /list/slug /gallery /about /contact /bg/ /nope; do curl -so /dev/null -w "$u %{http_code}\n" "http://127.0.0.1:8099$u"; done
```
Luego en la herramienta de navegador ejecuta una sonda JS: `fontFamily`/color de acento computados, `document.documentElement.scrollWidth`
vs `innerWidth` (desbordamiento), `images.filter(i=>i.naturalWidth===0)` (rotas), `document.fonts.status`.
Screenshots sin modelo de visión: Chromium headless ya está en disco desde Playwright —
`~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome --headless=new --no-sandbox --hide-scrollbars
--window-size=1440,1700 --virtual-time-budget=9000 --screenshot=out.png <url>` — luego envíalos al
usuario como `MEDIA:/path.jpg` y sanéalos con PIL (brillo medio, colores únicos, número de píxeles de acento).

## Ofrecer direcciones de diseño
Construye la capa de datos + imágenes una vez, luego 2–3 **páginas variante autocontenidas** (con `<style>` inline, fuentes propias)
enrutadas en `/v2`, `/v3` con un conmutador flotante, y deja que el usuario elija antes de tematizar todo el sitio.
Una vez elegido: reescribe `assets/css/site.css` conservando todos los nombres de clase, mueve la estructura de la página ganadora al
shell compartido, y luego `rm` las páginas variante + el conmutador (no dejes restos).

## Pitfalls
- **Sube `ASSET_V` en cada cambio de CSS/JS.** Mismo `?v=` = Cloudflare/Varnish/navegador sirven el archivo antiguo y
  "verificarás" un diseño obsoleto. Esto muerde siempre, sin excepción.
- **Google Fonts es un bloqueador de render** — medido 5 205 ms de pantalla en blanco en un sitio real mientras cada
  asset autoalojado tardaba 20–50 ms. Autoaloja los woff2 (`fonts.googleapis.com/css2?...` con un UA de escritorio
  devuelve URLs de fuente variable por subset), `@font-face` + `font-display:swap`, `<link rel=preload>` del subset
  que corresponde al idioma de la página. El primer pintado pasó de 5516 → 440 ms. Añade `font/woff2 woff2;` a
  `/etc/nginx/mime.types` (nginx solo trae `woff`) o las fuentes se sirven como octet-stream.
- **`hidden` pierde contra cualquier `display` de autor.** `<div class="mnav" hidden>` + `.mnav{display:flex}` = el panel
  móvil queda permanentemente visible también en desktop. Empareja siempre con `.mnav[hidden]{display:none!important}`.
- **Las animaciones de scroll-reveal con opacity-0 SÍ esconden contenido.** Con `threshold:0.06` + `rootMargin`
  inferior negativo, una primera fila justo bajo el pliegue nunca intersecta y toda la rejilla queda invisible
  (un screenshot headless sale negro — esa es la señal). Usa `threshold:0`, un rootMargin inferior *positivo*,
  vuelve a añadir `.in` siempre que un filtro muestre un elemento, más una red en `load` y un
  `setTimeout(revealAll, 2500)` duro, más `<noscript><style>.rv{opacity:1}</style></noscript>`.
  Verifica con `getComputedStyle(card).opacity`, nunca confiando en el HTML.
- El CSS con mucho coste de pintado hace que el scroll tartamudee: `filter:` en imágenes grandes (hornea el tratamiento en el archivo en
  tiempo de build en su lugar), `backdrop-filter:blur()` en un header fijo, y `transition:all` (anima layout).
- No uses `z-index:-1` en un relleno `::after` dentro de un botón — se hunde detrás del fondo de la sección.
  Anima `background-color` en su lugar.
- Las formas plurales necesitan un helper (`1 cuchillo` / `7 cuchillos`), no `"$n " . t('word')`.
- Deriva una etiqueta corta de agrupación (estilo `steel_key`) para chips/filtros; ordena las reglas de match para que
  gane el caso específico (`laminate` antes que `1.2210` en "san-mai laminate, 1.2210 core").
- Google fonts seguras con cirílico: Oswald, Inter, Manrope, Lora, Playfair Display, PT Serif, Montserrat.
  Cormorant/Fraunces/Spectral caen al fallback en silencio para texto BG. Ojo: `№` (U+2116) vive en el subset
  *cyrillic* — una página en inglés que lo use sigue descargando el woff2 cirílico.
- Al normalizar nombres de archivo de uploads de WordPress, quita **solo** `-<W>x<H>` (`re.sub(r'-\d+x\d+(?=\.\w+$)','')`).
  Un `-\d+\.jpg$` ingenuo colapsa `Picture-001.jpg`, `Picture-045.jpg` … en un solo nombre y descarta fotos en silencio.
- Antes de declarar imágenes irrecuperables, pregunta al usuario — una carpeta antigua `wp-content/uploads/<year>/<month>`
  olvidada en el servidor superó a blogspot y a la Wayback Machine para 37 archivos aquí.
- `php -l` a cada archivo generado/editado antes de desplegar.
