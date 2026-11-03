---
name: product-facet-engine
description: Katalog filtreleri seyrek besleme verisinden gelmeli.
---

# Ürün facet motoru — seyrek tedarikçi verisi üzerinde gerçek filtreler

Bir mağaza/kataloğun (PHP+SQLite, OpenCart, Medusa, statik HTML) **gerçek filtrelere** ihtiyacı
olduğunda ama:
* müşteri "filtreyi *<büyük distribütör>* gibi yap" diyorsa (sayılı spec facet'leri,
  seçili filtre çipleri, çoklu seçim, daha fazla göster kastediyordur), veya
* tedarikçi beslemesi çok az ya da hiç teknik veri göndermiyorsa (ERP/Icecat tarzı CSV'ler için tipik:
  ad, EAN, ağırlık, fiyat ve başka hiçbir şey), veya
* alt kategoriler, özellik değerleri veya teslimat ağırlıkları beslemede hiç yoksa.

Gösterdiğin her değer için katı kural: besleme verisine veya **addan türetilmiş bir çıkarıma**
kadar izlenebilir olmalı. Asla bir spec değeri, sayı veya fiyat uydurma. Bilinmiyor → facet'i atla
ya da "talep üzerine" göster.

## 1. Her filtrenin nereden geldiğine karar ver

| Kaynak | Örnekler | Notlar |
| --- | --- | --- |
| Besleme özellikleri | XML beslemelerinden `product_properties(name,value)` | En zengini, önce kullan. |
| Adan türetilmiş | Renk, Kapasite, Bellek türü, Arayüz, Ekran boyutu, Wi-Fi, Portlar, Güç, Uzunluk | Sıfır özellikli beslemeler için çalışır — bkz. §3. |
| Yapısal | marka, kategori, alt kategori, fiyat aralığı, "fotoğrafı var" | Her zaman mevcut. |
| Ağırlık | `products.weight` (kg) | Teslimat fiyatlamasını besler, facet değil. |

Bir besleme genellikle özellik içerir, diğeri hiç içermez: yalnızca beslemesinde bunlar eksik olan
ürünler için çıkarım yap, böylece gerçek tedarikçi değerlerinin üzerine asla yazmazsın.

## 2. Beslemede alt seviye yokken alt kategoriler

Sıralı kural tablosu, ilk eşleşme kazanır, **içe aktarma anında** uygulanır (`inc/taxonomy.php` →
`catalogue_subcategory_rules()`: kategori adı → `[[sub_name, regex], …]`). Tabloyu, herhangi bir
"temiz bölme" eşlemesinden sonraki tam kategori adına anahtarla — bir büyük/küçük harf farkı
(`Junction boxes` vs `Junction Boxes`) sessizce sıfır eşleşme verir, bu yüzden gerçek kategori adlarını
dök ve kural anahtarlarıyla karşılaştır.

* Eşleşmeyen ürünler `subcategory_id = NULL` kalır — bunları "Diğer" kovasına **sokmayın**.
* Slug'ları içe aktarıcı üretir; aynı kod yolu ardından alt kategori sayfalarını, facet'leri,
  kırıntı yollarını ve site haritasını bedavaya besler.
* Gerçekçi sonuç: beslemeden gelen 195 alt kategori → türetmeden sonra 365, 38 bin ürünün %76'sı yerleştirildi.
* Arayüz görünürlüğü veri kadar önemli: kategori sayfasının üstünde sayılı bir çip şeridi,
  departman sayfasında bir "Categories in <department>" dizini. **Bu kullanıcı departman dizininde yalnızca
  ana kategorileri ister (orada alt bağlantı yok) ve tam alt kategori şeridini
  kategori sayfasında ister** — aynı listeyi yan çubukta da çoğaltma.

## 3. Özellikleri ürün adlarından türet, gerçek özellik olarak sakla

Bütün hüner: türetilmiş değerleri içe aktarmada `product_properties` içine yazmak, böylece facet motoru,
filtre SQL'i, site haritası ve spec tablosu paralel bir "türetilmiş" kod yolu yerine **tek** bir
mekanizmayla çalışır.

* Türetilmiş satırlar için `sort = 1200` (ya da herhangi bir yüksek değer) kullan ve beslemenin zaten
  sağladığı adı atla.
* Kurallar tek dosyada yaşar (`inc/attributes.php` → `extract_attributes($name, $category)`), geriye
  `['Interface' => 'HDMI', …]` döndürür — yalnızca gerçekten bulunan özellikler.
* Sınırlı sayısal değerler ve açık son ekler, kullanışlı bir facet ile gürültü arasındaki farktır:
  * hız `Gbit|Gbps|GbE|igabit` **ve** 1–400 gerektirir → yoksa "4G/5G" LTE yönlendiricileri "4 Gbit" olur;
  * ekran boyutu 10–120 inç, güç 45–4000 W, kablo uzunluğu 0.1–100 m ile sınırlı;
  * `Paper size` yalnızca ad ayrıca paper/print/photo/label geçirdiğinde (yoksa bir parça numarasından gelen `A3` sızar);
  * `1024 GB → 1 TB`, `gray → Grey`, `802.11ax → Wi-Fi 6` normalleştir, iki rengi `Black / White` olarak birleştir.
* Yanlış pozitifleri facet dışında tutmak için ayırt edici olmayan grupları at (§4).
* Tam kural kataloğu ve ayrıştırıcı tuzakları: `references/derived-attributes-from-names.md`.

## 4. Facet keşif motoru

Tek bir **paylaşılan kapsam oluşturucu** hem listeleme sorgusunu hem facet sorgularını besler —
join/WHERE kopyalamak, listeleme sayıları ile facet sayılarının birbirinden kopmasının yoludur.

```php
function scope_sql(array $f, bool $withSpec = true): array   // [from, whereSql, params, joinFts]
```

İstek başına keşif:
1. Bu kapsamdaki en güçlü aday özellik adları: `SELECT pp.name, COUNT(DISTINCT pp.product_id) cov …
   GROUP BY pp.name HAVING cov >= 3 ORDER BY cov DESC LIMIT 40`, bir **kara liste** çıkarılarak
   (`Vendor_url`, `Dimensions`, `Weight`, `EAN`, `Part number`, `Warranty`, `Model`, `Other`, …).
2. Ad başına, sayılarıyla en güçlü ~26 değerini getir.
3. Bir adı yalnızca 2–24 değeri varsa, en az 8 ürünü varsa ve en güçlü değeri grubun ≤ %85'ini
   kapsıyorsa tut (her şeyi kapsayan bir değer ayırt edici değildir).
4. Grupları ham kapsama yerine açık bir **öncelik listesine** göre sırala (önce donanım özellikleri,
   `Colour` en sonda) — kapsama tek başına `Audio` ve `Pen`'i pekâlâ `Screen size`'ın önüne koyar.
5. ~6 grup × 8 değer al.

Filtreleme: özellik grubu başına bir `EXISTS` (gruplar arasında AND, grup içinde OR), parametreler
sırayla eklenir:
```sql
EXISTS (SELECT 1 FROM product_properties x WHERE x.product_id = p.id AND x.name = ? AND x.value IN (?,?))
```
İndeksle: `CREATE INDEX idx_pp_name_value ON product_properties(name, value)`.

Facet toplamlarını `md5(scope) + built_at` anahtarlı ve 1 saatlik TTL'li bir dosya önbelleğinde sakla —
soğuk ≈ 230 ms, sıcak ≈ 30–40 ms. **`built_at` meta verisi anahtarın parçası olmalı**, yoksa yeniden
içe aktarma ekranda bir saat boyunca bayat sayılar bırakır. Yazma sırasında ~7 günden eski önbellek
dosyalarını temizle.

## 5. Filtre arayüzü ve URL sözleşmesi

* Çoklu seçim, radyo değil: `?brand[]=hp&brand[]=lenovo` (ve `?spec[Screen size][]=27 inch`), böylece
  filtre sorgusu grup başına bir dizi alır; sıralama/sayfa başına formları dizi parametrelerini gizli
  girdi olarak yeniden yaymalı, yoksa sıralama filtreleri sessizce düşürür.
* Sonuçların üstünde **seçili filtre çipleri**, her biri tam olarak o değeri kaldıran bir ✕ ile
  (`url_without_value($key,$value)`, `url_without_spec($name,$value)`) artı "Clear all".
* **Yan çubukta tam olarak tek düğme — etiketi `Filter`.** Yanında "Filters" başlık metni yok,
  Show/Hide panel anahtarı yok, grup başına "Show N more" yok: sahibi hepsini açıkça kaldırdı. Uzun
  değer listeleri kendi kutularında kaydırılır (`max-height` + `overflow-y:auto`, `.fopts-scroll`); düğme
  kompakt kalır (`~72×37 px`, `btn-sm`, `width:auto` — masaüstünde de, telefonda da tam genişlik değil) ve
  etkin filtre sayısını küçük bir rozet olarak taşır. Telefonlarda o tek düğme (daraltılmış)
  listeyi açar / kapatır — filtreler işaretledikçe uygulanır, dolayısıyla "Apply" adımı yoktur.
* Grup başına: seçili sayı rozeti ve sağa hizalı sayılar. Sayfa başına: 24/48/96.
* Filtrelenmiş/sayfalanmış URL'ler: `noindex, follow` + temiz URL'ye canonical (besleme sitesi
  temel çizgisinden değişmedi).
* Sahibi "her şey mevcut" diye zorluyorsa, **stok durumu facet'ini kaldır** — tek kovası toplama eşit
  olan bir filtre gürültüdür.

### 5a. Filtreleme sayfayı yeniden yüklememeli (ve sayılar yerinde güncellenmeli)

Sahibin düz sözlerle gereksinimi: *"bir filtreye tıklamak sayfayı yeniden yüklememeli, böylece birkaç
filtreyi aynı anda ekleyebilirim"*. Çalışan PHP + JS tarifi, JSON sözleşmesi ve test yöntemi:
`references/ajax-facet-refresh.md`.

* Tek bir JSON parça endpoint'i her listeleme rotasını besler (`…?<filters>&frag=1` → `{results, counts, total,
  url, title}`); sayfa görünümü ve parça endpoint'i durumlarını **tek paylaşılan
  `listing_context()`** üzerinden kurar, yoksa sayfa ve parçalar birbirinden kopar.
* **Sonuçları yenile, asla yan çubuk HTML'ini değil.** İmlecin altında yan çubuğu yeniden render etmek,
  sahibin *"bir filtreyi işaretliyorum ve başka biri işaretlenmiş görünüyor"* şikâyetinin ta kendisidir —
  liste tıklamanın etrafında yeniden sıralanır. Yalnızca sonuç bloğunu değiştir ve yan çubuğu **yerinde**
  yamala (sayı metni + öğeleri gizle/göster): işaretli kutu aynı DOM düğümü olarak, işaretli, parmağın
  bıraktığı yerde kalır.
* **Canlı sayılar, sıfır değerler gitti.** Her grubu diğer tüm filtreler uygulanmış ve *kendi
  seçimi gevşetilmiş* halde say (`facet_live_counts()`), sayısı 0 olan değerleri işaretli olmadıkça gizle ve
  içinde hiçbir şey kalmadığında tüm grubu gizle. İşaretli değerleri değer listesine zorla ekle — top-N
  facet'ler aksi halde onları düşürür ve alışverişçi işareti kaldıramaz. Bunu yalnızca bir filtre
  etkinken hesapla: seçim yokken önbelleğe alınmış kapsam taraması aynı sayıları çok daha ucuza verir
  (burada ölçüldü: filtresiz sayfa 17 ms, filtreli sayfa 49 ms, parça 53 ms).
* Her değişiklikte `history.pushState` artı geri düğmesi için `popstate`; filtre/sıralama değişikliğinde
  `page`'i 1'e sıfırla ama sayfalama ve sayfa başına bağlantılarında **koru**; temiz URL için tarayıcının
  kendi sorgu dizesini yeniden kullan (`frag`'ı ve varsayılan sıralamayı düşür, boş `min=`/`max=`'ı atla) —
  `http_build_query` ile yeniden serileştirme yapma, o `spec[Socket][]=LGA1700`'i
  `spec[Socket][0]=LGA1700`'e çevirir.
* Aşamalı iyileştirme isteğe bağlı değildir: aynı form JS olmadan da normal bir GET yapar, bu yüzden bir
  test formun göndereceği sorguyu tam olarak `curl` etmelidir.

## 6. Ağırlık tabanlı teslimat fiyatlaması (aynı veri kümesi, aynı dürüstlük kuralı)

Teslimat maliyeti bir katalog özelliğidir: gerçek ürün ağırlıklarından ve **yayınlanmış taşıyıcı
tarifelerinden** hesapla, asla tahminden değil.

**Ağırlık bir beslemenin tamamında eksik olabilir.** XML beslemesinde hiç ağırlık sütunu yoktu, dolayısıyla 5 400 ürün
"tahmini 0.5 kg" ile gönderilecekti. Değeri bunun yerine içe aktarmada beslemenin kendi özelliklerinden
çıkar: `Weight: "1.70 kg"`, `"Starting at 1.38 kg"`, `"450 g"` → `products.weight` (ayrıştırıcı = ilk
sayı + birim, `g` → /1000, sınır 0–200 kg, yalnızca sütunun boş olduğu yere yazılır). 1 713 ürün bu şekilde
gerçek bir ağırlık kazandı ve teslimat bandı tahmin olmaktan çıktı. Ağırlığı asla tahmin etme —
bilinmeyen bilinmeyen kalır ve özet bunu söyler. Bulgaristan (Speedy orada DPD ağını işletir; `www.dpd.bg` speedy.bg'ye
yönlendirir), resmî fiyat listesi, hizmet kodları, ülke grubu başına fiyatlar ve getirme tarifi
`references/bg-carrier-tariffs.md` içinde. Yayınlanan tarifenin dışındaki varış noktaları → "fiyat talep üzerine".

## 7. Veri boşluklarını uydurmadan doldurma (aynı dürüstlük kuralı)

Boşluk ne olursa olsun — facet'ler, ağırlıklar, fotoğraflar — cevap *gerçek veriden türet, tahmini
etiketle ya da hiçbir şey gösterme*.

* **Fotoğraflar:** bir besleme sıfır görsel verisi gönderebilir (her satırda boş `Images` sütunu, dosyada hiçbir yerde
  URL yok — söz vermeden önce kontrol et). O zaman: fotoğrafı *olan* beslemenin fotoğrafını **yalnızca**
  aynı normalize edilmiş parça numarası için yeniden kullan (`/EXP` veya `GIFT` gibi varyant satırları aynı fiziksel
  öğedir — pratikte 38 binde 242), geri kalanı *tasarlanmış* bir yer tutucuyla değiştir (gri "fotoğraf yok" kutusu yerine
  departman + marka + parça numarası başına satır içi SVG çizgi grafiği, 24 departmanı kapsayan ~20 glif),
  ürün sayfasında dürüst bir satır tut ("üretici fotoğraf yayınlamıyor — bize sorun") ve sahibine
  gerçek bir görsel beslemesinin ne gerektireceğini söyle. Asla bir rakibi kazıma ya da ilgisiz bir marka fotoğrafı ödünç alma.
* **Ağırlıklar:** tahmine düşmeden önce bunları beslemenin kendi özellik dizelerinden çıkar (§6);
  müşterinin toplamına ulaşan bir tahmin tahmin olarak etiketlenmelidir.
* **Özellikler/alt kategoriler:** addan türetilmiş kurallar (§2/§3) boş bir filtre panelini yener — ama
  beslemeye ya da ürün adına geri izlenemeyen bir değer dışarıda kalır.

## 8. Bayi kataloglarında görülen sahip talebi kalıpları

* **"Tüm ürünler mevcut olmalı."** Besleme verisini yeniden yazma. Gerçek stok durumunu DB'de tut
  ve görüntüleme katmanının, JSON-LD'nin (`InStock`), facet sayılarının ve stok durumu filtresinin
  hepsinin okuduğu tek bir yapılandırma bayrağı ekle (`force_availability = 'in_stock'`) — tek satırda geri alınabilir.
  Artık anlamsız hale gelen stok durumu facet'ini kaldır ve yerel stok iddia eden her cümleyi yumuşat
  ("Siparişe açık — teslim süresi siparişle birlikte teyit edilir").
* **"Bunu bir talep değil sipariş sayfası yap."** O halde gerçek bir ödeme akışı ver: toplamlı sipariş özeti,
  teslimat fiyatı, bir **Place order** düğmesi, onayda gösterilen bir sipariş referansı (`ERP-2026-00001`,
  satır sırasından), ve POST'ta ürün slug'ından sunucu tarafında yeniden hesaplanan toplamlar/ağırlık.
  Talep/teklif akışını kendi sayfasında tut — bu kullanıcının kalıcı tercihi, yeni bir işlevin
  **kendi URL'si ve kendi SEO'su** olması, mevcut bir sayfaya eklenmiş bir bölüm asla değil.
* **Koşullu zorunlu alanlar (şirket vs birey).** Her zaman zorunlu alanları yıldızla; türe bağlı olanları
  `[data-business-only]` içine sar ve JS'te hem `hidden` hem `required` durumunu değiştir — sonra
  **aynı kuralı sunucu tarafında yeniden doğrula**, çünkü gizli bir `required` girdi basitçe gönderilmez.
  Saklamadan önce seçilen türe uymayan veriyi boşalt.
* **Fiyatlar KDV'li ve KDV'siz gösterilmeli, tür modu seçmeli.** Bireysel müşteri: mal, teslimat ve
  toplam **KDV dahil**. Şirket / bayi: aynı üç satır **KDV hariç** (taşıyıcı fiyatları KDV dahil
  yayınlanır, dolayısıyla net teslimat = brüt / 1.2). Varış noktasına göre oranlar: BG'de yerel KDV;
  VIES'te KDV numarası verildiğinde %0 topluluk içi; AB bireysel alıcısı için varış ülkesi standart oranı;
  AB dışı ihracatta %0 — artı faturanın yetkili belge olduğuna dair bir satır.
  Ayrıntılı dökümü tek kutuda, kompakt 3 satırlık toplamı ise doğrudan gönder düğmesinin üstünde tut.
* **Metin hijyeni — bu sahip tedarikçiye dönük her şeyi müşteri arayüzünden budar.** Oturumlar boyunca
  talep üzerine kaldırılanlar: üst banner, teslimat seçenekleri altındaki not, alt bilgi uyarı çifti
  ("Ürün verileri tedarikçi kataloglarımızdan otomatik güncellenir (son içe aktarma …)" / "Ürün adları
  ve markalar ilgili sahiplerinin mülkiyetindedir…"), "tesisimizde kendi taşıyıcınızla teslim alma"
  seçeneği ve ürün sayfasındaki `Second supplier price: 111.17 € net` satırı. Fiyatları, etiketleri ve alanları gönder;
  açıklamaları SSS/statik sayfalara koy. Bir fiyat/alan arayüzden çıktığında artık ölü olan CSS
  sınıfını ve kullanılmayan değişkeni de sil, DB sütununu tut (tek satırda geri gelebilsin). Burada müşteriye dönük
  taşıyıcı markası **DPD**'dir; kaynak yorumları kodda yaşar, asla sayfada değil.
* **Geniş fiyat/facet tabloları telefondan sağ çıkmalı.** 10+ sütunla, `≤760px`'te yığılmış kartlara
  geç: `thead`'i gizle, satırlarda `display: block`, her hücrede `data-label` ve
  `td::before { content: attr(data-label) }`. Gözle değil, CDP kontrolüyle doğrula (`scripts/` bölümüne bakın).
* **Asla kaynak gösterilmemiş bir fiyat, ağırlık veya teslim süresi yok.** Bilinmiyor → "talep üzerine",
  sahibi tarafından teyit edildi; bu kullanıcı uydurulmuş sayıları kesinlikle reddeder ve teslimattan hemen sonra siteyi canlı kontrol eder.

## Tuzaklar

* **Paylaşılan bir `SELECT` sabitinde var olmayan bir sütun canlı siteyi 500'e götürür.** Gerçek vaka:
  şema sütunu `weight` iken `p.weight_kg` — düzeltilene kadar her listeleme sayfası 500 döndü.
  Önce `.schema` kontrol et, sabitte takma ad ver (`p.weight AS weight_kg`) ve paylaşılan bir
  sorgu sabitine/yardımcısına dokunduktan sonra her rota türünü yeniden tara (`curl` her rota, 200 + `Warning:`/`Fatal` yok doğrula).
* **PHP: art arda satırlarda iki dize sabiti ayrıştırma hatasıdır.** Uzun SSS/dizi dizileri açık bir
  `.` birleştirmesi gerektirir; `php -l` bunu yalnızca gerçekten lint yaparsan yakalar (`for f in $(find . -name
  '*.php'); do php -l $f; done`).
* **`[$a, $b] = $assocRow` sessizce `null` verir.** Bir ilişkisel diziyi yapı bozumuna uğratmak hatasız
  boş tablo hücreleri / eksik satırlar üretir. Adlandırılmış anahtarlar kullan (`$row['service']`). Hatırlanacak belirti:
  tablo başlıkları render edilir, gövde satırları boştur.
* Türetilmiş özellikler beslemenin sağladığı özelliklerin üzerine yazmamalı; kaç satır atladığını günlüğe yaz.
* Facet sayıları listeleme ile aynı kapsam oluşturucu kullanılarak hesaplanmalı ve `built_at` üzerinde önbelleğe alınmalı.
* "Türetilmiş" filtreler için ikinci bir giriş noktası eklemeyin — bunları mevcut özellik tablosuna yazın.
* **Betikle yapılan bir "tümünü değiştir" düzenlemesi bir dizi anahtarını çoğaltabilir.** Aynı bloğu iki PHP
  işlevine eklemek (`shipping_services()` ve `shipping_rates()` ikisi de `'cee202' => [` ile başlar) bir hizmet
  tanımını bir fiyat dizisinin yerine koydu; PHP sessizce **son** anahtarı tutar, dolayısıyla seçenek
  hiçbir yerde hata olmadan "talep üzerine" olarak render edildi. Veri tablolarını `str.replace(..., -1)` ile
  düzenledikten sonra yapıyı yeniden doğrula (`php -r 'print_r(array_keys(...))'`) ve bir ülkenin teklifini birim olarak yazdır.
* **Çok adımlı akışları uzun tek satırlık bir komuttan değil bir betik dosyasından doğrula.** Karmaşık zincirleme komutlar
  shell guard tarafından reddedilir; site araçlarının yanına `verify_<area>.sh` / `<area>_flow_test.sh` yaz,
  `bash` ile çalıştır ve yeniden kullanılabilir olanları becerinin `scripts/` dizininde tut.
* **`Secure` bir oturum çerezi yerel-HTTP testini bozuk gösterir.** Cloudflare arkasında uygulama
  `X-Forwarded-Proto: https` görür, dolayısıyla PHP oturum çerezini `Secure` yapar; bir `curl http://127.0.0.1:8080`
  testi onu asla geri göndermez, CSRF tokenları hiç eşleşmez ve her hesap işlemi `err=csrf` döndürür.
  Çerez/hesap akışı testlerini **genel HTTPS kaynağına** karşı çalıştır, yerel vhost'u ise
  anonim sayfa taramaları için tut. Ayrıntılar: `customer-accounts-and-sessions` becerisi.
* **Satır içi bir `onchange="this.form.submit()"` yeniden yüklemesiz davranışı öldürür.** `form.submit()` hiçbir
  `submit` olayı tetiklemez, dolayısıyla submit'i preventDefault eden bir dinleyici onu asla görmez ve sayfa yine yeniden yüklenir
  (belirti: sıralama/sayfa başına "çalışır" ama tüm sayfa zıplar). Satır içi işleyiciyi kaldır, `change`
  olayını select'e (`[data-sort]`) bağla ve JS kapalı durumu için bir `<noscript>` gönder düğmesi ekle.
* **Bir JSON parça görünümü asla sayfa düzeniyle sarılmamalı.** `render()` görünümü ister ardından
  `views/layout.php`'yi çağırır; parça bu yüzden JSON'un içine gömüldüğü tam bir HTML belgesi olarak döndü
  (doğru `Content-Type`, ayrıştırılamaz gövde). Her rota imzası aynı kalır — renderer'ın içinde dallan:
  `if (str_starts_with($view, 'api_')) { echo $content; return; }`.
* **Okuma bağlantısında `PRAGMA query_only = ON` her CLI yazmasını başarısız kılar.** Uygulamanın `db()`'si
  sağlamlaştırılmış salt-okunur bir tutamaçtır, dolayısıyla `qexec()`'i yeniden kullanan bir bakım betiği
  `SQLSTATE[HY000]: General error: 8 attempt to write a readonly database` ile ölür; buna karşılık kendi
  yazma tutamacını açan web yolu sorunsuzdur. Yazma yoluna kendi bağlantısını ver (`db_write()` yardımcısının
  arkasında `db_open_rw()`) ve yönetim/CLI güncellemelerini onun üzerinden yönlendir.
* **Paylaşılan bir bağlam yardımcısı + `extract($arr, EXTR_SKIP)` çağıranın `$CTX`'ini bayat bırakır.** Yardımcı
  `$CTX`'i değer olarak alır, kendi kopyasını zenginleştirir (filters/result/facets) ve döndürür; `EXTR_SKIP` ise
  görünüm kapsamında zaten bulunan *orijinal* `$CTX`'i korur, dolayısıyla parçalar tanımsız
  `$CTX['filters']` ile çalışır (uyarılar, boş filtreler, ürün yok). Extract etmeden önce açıkça ata
  (`$CTX = $__L['CTX'] ?? $CTX;`) ve referansla geçen `$PAGE` ezilmesin diye
  `unset($__L['CTX'], $__L['PAGE'])` yap.
* **Form/yan çubuk öğesini asla bir JS değişkeninde önbelleğe alma.** Yüklemede yakalanan
  `var form = document.querySelector('[data-filter-form]')`, parça endpoint'i işaretlemeyi değiştirir değiştirmez
  **ayrılmış bir düğümü** gösterir: ilk işaretleme çalışır, sonraki her işaretleme *eski* değerleri yeniden gönderir ve sayfa
  tıklamaları yok sayıyor görünür (belirti: "ikinci filtreyi eklemek hiçbir şey yapmıyor, URL asla değişmiyor").
  Öğeyi her seferinde işleyicinin içinde ara — ve yan çubuğu herhangi bir şekilde değiştiriyorsan işaretli girdilerin
  DOM düğümlerini canlı tut (§5a'ya bakın).
* **Bir satır aralığını yiyen büyük bir `str.replace()` bir başlığı çoğaltabilir.** Bir görünümü index→index dilimleyerek
  yeniden yazmak eski veri hazırlama bloğunu yenisinin üstünde bıraktı; yine de ayrıştı, ama sayfa anlamsız
  render etti. Bir görünüm üzerinde ameliyattan sonra `php -l` **ve** birleştirilen bölgeyi geri oku, sonra devam et.

## Doğrulama

* `scripts/mobile-overflow-check.mjs` (npm bağımlılığı yok, Playwright Chromium üzerinden CDP) —
  `scrollWidth` ile `clientWidth`'i ölçer, sağ kenarı aşan her öğeyi listeler ve
  `--selector ".ship-table"` ile geniş bir tablonun yığılmış kart düzenine geçip geçmediğini bildirir. Kategori, ürün, sepet/sipariş ve fiyat tablosu olan her sayfada
  360/390/414 px'te çalıştır.
* Kuralları değiştirdikten sonra kategori başına facet gruplarını karşılaştır (render edilen yan çubukta `fgroup-title` grep'le).
* Bir kategori için en güçlü 5 facet değerinin makul olduğunu nokta kontrolüyle doğrula; 19 inç raflarda `1 inch`
  ya da LTE yönlendiricilerde `4 Gbit` gibi bir değer, bir kuralın sınıra ya da son eke ihtiyacı olduğunu gösterir.
* Çiplerin gidiş-dönüşünü onayla: iki marka + bir spec değeri seç, ardından sonuç sayısının düştüğünü ve
  her iki çipin de tam olarak bir filtreyi kaldıran bir URL'ye bağlandığını doğrula.
