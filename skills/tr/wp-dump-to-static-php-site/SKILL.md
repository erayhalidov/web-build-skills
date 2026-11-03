---
name: wp-dump-to-static-php-site
description: Ölü bir WordPress sitesini .sql dökümünden yeniden kurun.
---

# WordPress SQL dökümü → saf PHP site

Elinde bir `*.sql` WordPress dökümü (ya da boş bir CloudPanel sitesi + döküm) olduğunda ve amaç
WordPress **olmadan** modern, hızlı bir site olduğunda kullanın: içerik üretilmiş bir PHP veri
dosyasında, temiz URL'ler, iki dilli.

## 1. Dökümü içe aktar ve envanterini çıkar
```bash
clpctl db:show:master-credentials                 # CloudPanel MySQL root creds
export MYSQL_PWD='<pass>'; M="mariadb -h127.0.0.1 -uroot"
$M -e "CREATE DATABASE IF NOT EXISTS src_tmp CHARACTER SET utf8mb4;"
$M src_tmp < dump.sql
$M src_tmp -e "SELECT post_type,post_status,COUNT(*) FROM wp_posts GROUP BY 1,2 ORDER BY 3 DESC;"
$M src_tmp -e "SELECT option_name,LEFT(option_value,120) FROM wp_options
  WHERE option_name IN ('siteurl','home','blogname','WPLANG','template','page_on_front');"
```
Yazıları XML olarak dışa aktarın (`mariadb --xml`) ve `xml.etree` ile ayrıştırın — `-N` kaynaklı
sekme/satır sonu bozulmalarını önler.

## 2. Görselleri kurtar (zor kısım)
Dökümde yalnızca DB satırları vardır; `wp-content/uploads` genellikle yoktur. Kurtarma merdiveni:
1. `post_content` üzerinde `grep -oE 'https?://[^"]+\.(jpg|jpeg|png|webp)'` — **harici sunucular hâlâ sunuyor**
   (blogspot `*.bp.blogspot.com`, Facebook CDN adları `NNN_NNN_NNN_n.jpg`).
2. Blogspot: boyut parçasını maksimum çözünürlükle değiştirin — `re.sub(r'/s\d+/','/s1600/',url)`; olmazsa orijinaline düşün.
3. Kendi alan adı `/wp-content/uploads/...`: `https://web.archive.org/web/2022id_/<url>` deneyin — **genellikle 404**
   (doğrulama: gerçek görsel = HTTP 200 + `image/*` + >5 KB; ~4.6 KB'lik bir HTML gövdesi Wayback 404 sayfasıdır).
4. Eksik olan ne varsa → kullanıcıya söyleyin ve bilinçli bir yer tutucu kart tasarlayın. Asla sahte fotoğraf koymayın.

Dosya adlarını eşleştirirken WP boyut eklerini normalize edin: `re.sub(r'-\d+\.jpg$','.jpg', name)` (`foo-1024x683.jpg`).

## 3. Görsel hattı (PIL, ImageMagick gerekmez)
Görsel başına `full` (≤1400w), `card` (≤760w), `thumb` (≤380w) **JPEG + WebP** olarak üretin, asla büyütmeyin,
önce `ImageOps.exif_transpose`, sonra `jpegoptim --strip-all -m86`. PHP'nin `width`/`height` yazabilmesi için
görsel başına `w/h/ratio` içeren bir manifest JSON yazın (düzen kayması olmasın).

## 4. Veri dosyasını üretin, elle yazmayın
`gen_data.py` her kayıt için elle düzenlenmiş bir sözlük (özellikler, EN/BG metin) + görsel manifesti tutar ve
`inc/data.php` (`<?php return [...];`) yazdırır. Yeniden üretmek idempotenttir; sonrasında `php -l` ile kontrol edin.
301'ler için her kayıtta eski WP slug'ını (`post_name`, `urllib.parse.unquote`) saklayın.
**Yalnızca dökümde belirtilen olguları ekleyin** — değer uydurmak yerine özellik anahtarını atlayın.

## 5. Site iskeleti (saf PHP)
```
index.php          front controller: routes on trim(parse_url(REQUEST_URI))
inc/config.php     constants, ASSET_V cache buster, $LANG from /bg/ prefix, t()/u()/f()/pic()
inc/layout.php     page_head() + site_header() + site_footer()
inc/parts.php      card/partial renderers
pages/*.php        home, list, detail, gallery, about, contact, 404
assets/{css,js,img}
```
- nginx (CloudPanel varsayılanı) zaten `try_files $uri $uri/ /index.php?$args` yapar → temiz URL'ler çalışır.
- Dil **URL öneki** ile (`/bg/...`), asla çerezle — Varnish/Cloudflare arkasında önbellek dostu kalır.
- Eski kalıcı bağlantıları `default:` dalında 301'leyin: `strtolower(rawurldecode($seg[0]))` ile saklanan WP slug'ı karşılaştırın.
- İletişim formu: `mail()` + webroot **dışında** bir günlüğe ekleme (`__DIR__.'/../../data/'`), honeypot alanı.
  Önce `dig MX` kontrol edin — MX'i olmayan bir alan adı, yayınlanan adresin ölü olduğu anlamına gelir; bunu söyleyin.

## 6. CloudPanel'e yayınla
```bash
DEST=/home/<user>/htdocs/<domain>
rsync -a --delete --exclude dev-router.php /root/build/ "$DEST/"
chown -R <user>:<user> "$DEST"
find "$DEST" -type d -exec chmod 755 {} \; ; find "$DEST" -type f -exec chmod 644 {} \;
varnishadm "ban req.url ~ ."          # CloudPanel proxies :8080 through Varnish
```

## 7. Gerçekten doğrulayın (göz kararı gerekmez)
```bash
php -S 127.0.0.1:8099 dev-router.php   # dev-router: return false for existing files, else index.php
for u in / /list /list/slug /gallery /about /contact /bg/ /nope; do curl -so /dev/null -w "$u %{http_code}\n" "http://127.0.0.1:8099$u"; done
```
Ardından tarayıcı aracında tek bir JS sondası çalıştırın: hesaplanmış `fontFamily`/vurgu rengi, `document.documentElement.scrollWidth`
vs `innerWidth` (taşma), `images.filter(i=>i.naturalWidth===0)` (bozuk), `document.fonts.status`.
Görüntü modeli olmadan ekran görüntüsü: headless Chromium Playwright'tan zaten diskte —
`~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome --headless=new --no-sandbox --hide-scrollbars
--window-size=1440,1700 --virtual-time-budget=9000 --screenshot=out.png <url>` — sonra bunları kullanıcıya
`MEDIA:/path.jpg` olarak gönderin ve PIL ile mantık kontrolü yapın (ortalama parlaklık, benzersiz renkler, vurgu piksel sayısı).

## Tasarım yönleri sunma
Veri + görsel katmanını bir kez kurun, ardından 2–3 **kendi kendine yeten varyant sayfa** (satır içi `<style>`, kendi fontları)
`/v2`, `/v3` yollarında yüzen bir değiştiriciyle yayınlayın ve tüm siteyi temalı hale getirmeden önce kullanıcı seçsin.
Seçim yapıldıktan sonra: tüm sınıf adlarını koruyarak `assets/css/site.css` dosyasını yeniden yazın, kazanan sayfa yapısını
paylaşılan kabuğa taşıyın, sonra varyant sayfaları + değiştiriciyi `rm` ile silin (artık bırakmayın).

## Tuzaklar
- **Her CSS/JS değişikliğinde `ASSET_V`'yi artırın.** Aynı `?v=` = Cloudflare/Varnish/tarayıcı eski dosyayı sunar ve
  bayat bir tasarımı "doğrularsınız". Bu her seferinde ısırır.
- **Google Fonts bir render engelleyicisidir** — gerçek bir sitede boş ekranın 5 205 ms sürdüğü ölçüldü, hâlbuki her
  kendi barındırılan varlık 20–50 ms sürüyordu. woff2'leri kendi sunucunuzda barındırın (`fonts.googleapis.com/css2?...` masaüstü UA ile
  alt küme başına değişken font URL'leri döndürür), `@font-face` + `font-display:swap`, sayfa diliyle eşleşen alt kümeyi
  `<link rel=preload>` ile ön yükleyin. İlk boyama 5516 → 440 ms'ye indi. `/etc/nginx/mime.types` dosyasına `font/woff2 woff2;` ekleyin
  (nginx yalnızca `woff` ile gelir) yoksa fontlar octet-stream olarak sunulur.
- **`hidden`, herhangi bir yazar `display` kuralına yenilir.** `<div class="mnav" hidden>` + `.mnav{display:flex}` = mobil
  panel masaüstünde de kalıcı olarak görünür. Her zaman `.mnav[hidden]{display:none!important}` ile eşleştirin.
- **Opaklık-0 kaydırma ile açılma animasyonları içeriği KESİNLİKLE gizler.** `threshold:0.06` + negatif alt
  `rootMargin` ile katlanma çizgisinin hemen altındaki ilk satır hiç kesişmez ve tüm ızgara görünmez kalır
  (headless ekran görüntüsü siyah çıkar — ipucu budur). `threshold:0`, *pozitif* alt
  rootMargin kullanın, bir filtre bir öğe gösterdiğinde `.in` sınıfını yeniden ekleyin, ayrıca bir `load` ağı ve sert bir
  `setTimeout(revealAll, 2500)`, artı `<noscript><style>.rv{opacity:1}</style></noscript>` ekleyin.
  `getComputedStyle(card).opacity` ile doğrulayın, HTML'e asla güvenmeyin.
- Boya ağırlıklı CSS kaydırmayı takılır hale getirir: büyük görsellerde `filter:` (bunun yerine işlemeyi derleme
  sırasında dosyaya pişirin), sabit başlıkta `backdrop-filter:blur()` ve `transition:all` (düzeni animasyonlar).
- Bir düğme içindeki `::after` dolgusunda `z-index:-1` kullanmayın — bölüm arka planının arkasına batar.
  Bunun yerine `background-color` animasyonu yapın.
- Çoğul biçimler bir yardımcı gerektirir (`1 cuchillo` / `7 cuchillos`), `"$n " . t('word')` değil.
- Çipler/filtreler için kısa bir gruplama etiketi (`steel_key` tarzı) türetin; eşleştirme kurallarını
  özgül durum kazanacak şekilde sıralayın ("san-mai laminate, 1.2210 core" içinde `laminate` `1.2210`'dan önce).
- Kiril güvenli Google fontları: Oswald, Inter, Manrope, Lora, Playfair Display, PT Serif, Montserrat.
  Cormorant/Fraunces/Spectral BG metin için sessizce yedek fonta düşer. Not: `№` (U+2116) *cyrillic*
  alt kümesinde yaşar — onu kullanan bir İngilizce sayfa yine de cyrillic woff2'yi çeker.
- WordPress yükleme dosya adlarını normalize ederken **yalnızca** `-<W>x<H>` kısmını çıkarın (`re.sub(r'-\d+x\d+(?=\.\w+$)','')`).
  Naif bir `-\d+\.jpg$` kuralı `Picture-001.jpg`, `Picture-045.jpg` … dosyalarını tek ada çökertir ve fotoğrafları sessizce düşürür.
- Görselleri kurtarılamaz ilan etmeden önce kullanıcıya sorun — sunucuda duran eski bir `wp-content/uploads/<year>/<month>` klasörü
  burada 37 dosya için blogspot'u da Wayback Machine'i de yendi.
- Yayınlamadan önce her üretilen/düzenlenen dosyayı `php -l` ile kontrol edin.
