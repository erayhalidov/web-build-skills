---
name: static-product-shop
description: "CSV/JSON'dan statik mağaza/katalog (HTML+JS+PHP) kurun."
---

# Statik Ürün Mağazası / Katalog Ön Yüzü

Mevcut bir ürün veri dosyasından (CSV/JSON dışa aktarımı) kendi kendine yeten bir çevrimiçi
mağaza veya katalog (kategoriler + filtreler + sipariş formu) kurun ve herhangi bir web
sunucusunda düz statik dosyalar olarak barındırın. Tipik giriş noktaları `catalog.html` (listeleme)
ve `index.html` (açılış sayfası).

Tetikleyici: kullanıcı, zaten sahip olduğu bir site için "bu CSV/dosyadan tüm kategoriler ve ürün
filtreleriyle bir çevrimiçi mağaza / katalog yap" der.

## Mimari (çok sayfalı, çerçevesiz)

1. `build_products.py` — kaynak veriyi ayrıştır → `products.json` (tek doğruluk kaynağı)
2. `style.css` + `common.js` — paylaşılan stiller + paylaşılan yardımcılar: sepet **localStorage**'da
   (`getCart/saveCart/addToCart/changeQty/removeItem/cartCount/cartTotal`), başlık render edici
   (`renderHeader(active)`), `productCard(p)`, `fmt/esc/toast`, önbelleğe alınmış `loadData()`.
3. `index.html` — katalog: kategori ağacı + filtre açılır menüleri + arama + sıralama + ürün ızgarası.
   Kartlar `product.html?id=X` bağlantısı verir.
4. `product.html?id=X` — ürün başına bir sayfa (görsel, özellik tablosu, açıklama, ilgili ürünler).
5. `order.html` — ödeme: localStorage'dan sepet öğeleri + teslimat formu.
6. `order.php` — JSON POST kabul eder, `orders.json` dosyasına ekler + `orders.log` yazar.

**Kullanıcı AYRI SAYFALARI (katalog / ürün / sipariş) tercih eder, modallı tek sayfa uygulamasını
değil.** İlk seferde tek sayfada modal + mini sepet çıkarırsanız, sonradan sayfalara bölmeniz
isteneceğini bekleyin. Çok sayfalı başlayın.

## Adımlar

1. **Önce kaynak sütunları inceleyin** — `head -5` artı hızlı bir Python `collections.Counter`
   geçişiyle kategorileri, filtreleri, üreticileri, fiyat aralığını, stok dağılımını listeleyin.
   Üreteci asla körlemesine yazmayın.
2. **products.json içine normalleştirin**, ürün başına tek düz nesne:
   `id, name, manufacturer, price, special, image, stock, description, categories[] (tam yollar), filters{} (grup→[değerler]), related[]`.
3. **Kategori ağacını** yol dizelerinden üretin (hiyerarşi ayırıcısından bölün, örn. `>`), sonra her
   ürünü tüm kategori yollarına atayın; kategoriyi `c === path || c.startsWith(path + '>')` önek
   kuralıyla eşleştirin.
4. **index.html oluşturun** — sayılı yan çubuk ağacı, filtre grubu başına bir `<select>`, arama,
   sıralama (fiyat artan/azalan, ad), kart ızgarası. Kartlar `product.html?id=<id>` bağlantısı verir;
   "sepete ekle" düğmesi `addToCartById(id)` çağırır. `?q=` ve `?cat=` sorgu parametrelerini destekleyin ki
   arama ve ürün kırıntı yolları derin bağlantı kurabilsin.
5. **product.html oluşturun** — `?id=` okuyun, görsel / özellik tablosu / açıklama / ilgili ürünleri render edin,
   `index.html?cat=<path>` bağlantılı kırıntı yolu. Düğmeler: "sepete ekle" + "hemen al" (ekle
   sonra `location.href='order.html'`).
6. **order.html oluşturun** — sepeti localStorage'dan okuyun, adet artırıcılar + kaldır, toplam, teslimat
   formu. Gönder → order.php; başarıda `saveCart([])` ve dönen sipariş id'sini göster.
7. **order.php** — ad/telefon/adres doğrula, `orders.json` dosyasına ekle (JSON_PRETTY_PRINT |
   JSON_UNESCAPED_UNICODE) ve `orders.log` dosyasına okunur bir satır ekle. `{ok:true, order_id}` döndür.
8. **Mağaza dizinine `chown -R <webuser>:<webuser>`** — root olarak yazılan dosyalar PHP yazmalarını
   ve PHP-FPM okumalarını bozar. (CloudPanel siteleri site kullanıcısı olarak çalışır, örn. `oem`.)
9. **Canlıda doğrulayın** — URL'yi `curl` edin (200 beklersiniz), bir test siparişi `curl -X POST` edin, dosya
   yazımını onaylayın, sonra mağaza boş başlasın diye test siparişini silin.

## Tuzaklar

- **Sitenin mevcut temasıyla eşleşin**: sitenin stil dosyasından ana hex renkleri çıkarın
  (`grep -oiE '#[0-9a-f]{6}' .../stylesheet.css | sort | uniq -c | sort -rn`) ve bunları
  CSS değişkeni olarak yeniden kullanın. İyi çalışan iki şekil: koyu lacivert `#0D1322` + turuncu `#FF7A00`, ya da neredeyse siyah
  `#0e0f12` + kırmızı `#e30613`.
- **Telefon / e-posta / ücretsiz kargo bilgisini ASLA hafızadan sabit kodlamayın.** Bunları mağazanın DB
  ayarlarından okuyun (`references/opencart-csv.md` dosyasına bakın). Bir mağazadan diğerine kopyalanan numara
  gerçek ve utanç verici bir hatadır — her zaman `oc_setting` sorgulayın.
- **Satır içi işleyicilerde görsel `onerror`**: tam olarak `onerror="this.style.display='none'"` yazın.
  Kaçışlı ters bölü varyantları tüm `<script>` bloğunu sessizce öldürür.
- **Para birimi/yerel ayar**: parayı yerel ayarın ondalık ayırıcısıyla gösterin (BG/DE için virgül, EN için nokta)
  (`n.toFixed(2).replace('.', ',') + ' €'`). Aksi söylenmedikçe BGN varsaymayın.
- **`special` fiyat geçersiz kılma**: `price_special` yalnızca ayarlıysa VE `> 0` VE `< price` ise kullanılır.
- **Asenkron sepete ekleme**: `addToCart` bir ürün nesnesi ister. Kart düğmelerinde onclick içine
  `JSON.stringify(product)` gömmek yerine `addToCartById(id)` çağırın (`findProduct(id).then(addToCart)` yapar) —
  tüm nesneyi (HTML açıklaması dahil) gömmek sayfayı şişirir ve tırnak/HTML bozulma riski taşır. Not: `findProduct`
  bir promise döndürür, dolayısıyla bir testte `addToCartById()` hemen ardından senkron `getCart()` okuması hâlâ
  boş görünür — önce promise'ı `await` edin.
- **Marka adı değişikliği ("X→Y her yerde değiştir")**: *kaynak* CSV, render etmediğiniz sütunlarda (örn. kullanılmayan bir `store` sütunu)
  hâlâ eski marka metnini içerebilir. Değişikliği onaylamak için yalnızca render edilen dosyaları grep'leyin
  (`grep -rliE "X" --include="*.html" --include="*.js" --include="*.css"
  --include="*.json" --include="*.php" .`), ham veri dosyasını değil. Kullanıcı "her şey" derse görünen e-postayı da
  yeniden adlandırın, ama o posta kutusu gerçek değilse geri alabilsinler diye bunu belirtin.
- **Sunum yolu**: `/shop/` gibi bir alt klasör, sitenin mevcut nginx `try_files ... index.php` kuralına yalnızca
  `index.html` var olduğu ve `.json` `application/json` aldığı için yakalanır.
  JSON mime türünü `curl -sI` ile doğrulayın (bazı kurulumlarda yapılandırma gerekmez, ama kontrol edin).

## Referanslar

- `references/opencart-csv.md` — OpenCart 2.x ürün dışa aktarım sütunları, kategori/filtre dize
  ayrıştırması ve `oc_setting` tablosundan mağaza ayarlarını okuma.
