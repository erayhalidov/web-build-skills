# Uluslararası SEO: Kanıtlar ve Kaynaklar

SEO Denetimi becerisinin Uluslararası SEO ve Yerelleştirme bölümünü destekleyen ayrıntılı kanıtlar. Kaynak URL'leri ve kilit alıntılarla konuya göre düzenlenmiştir.

---

## Hreflang

### Yerleştirme Yöntemleri

Google üç eşdeğer yöntemi destekler: `<head>` içinde HTML `<link>`, HTTP `Link` başlıkları ve XML site haritası `<xhtml:link>` öğeleri. Google hiçbir yöntemin diğerine göre önceliklendirilmediğini doğruladı.

Google hem HTML hem site haritalarından gelen sinyalleri birleştirir. Aynı dil-bölge çifti yöntemler arasında farklı URL'lere işaret ediyorsa Google tahmin etmek yerine o çifti düşürür.

- [Google Search Central: Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [SEJ: Google Combines Hreflang Signals](https://www.searchenginejournal.com/google-combines-hreflang-signals-from-html-sitemaps/389219/)

### Karşılıklılık Gereği

Google'ın belgeleri: "X sayfası Y sayfasına bağlantı veriyorsa, Y sayfası da X sayfasına geri bağlantı vermelidir. Aksi halde bu açıklamalar yok sayılabilir veya doğru yorumlanmayabilir."

Her sayfa kendini hreflang kümesine eklemelidir (kendine referans). Kendine referansın eksikliği Semrush denetimlerinde bulunan 1 numaralı hatadır. 374.756 alan adı üzerinde yapılan bir çalışma hreflang uygulamalarının %67'sinde sorun olduğunu buldu.

- [Google Search Central: Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Semrush: 9 Common Hreflang Errors](https://www.semrush.com/blog/hreflang-errors/)
- [SE Land: 31% of International Websites Contain Hreflang Errors](https://searchengineland.com/study-31-of-international-websites-contain-hreflang-errors-395161)

### x-default

Nisan 2013'te tanıtıldı. Dil/bölgesi bildirilen hiçbir varyantla eşleşmeyen kullanıcılar için yedek sayfayı belirler. Dile özgü alternatiflerden biriyle aynı URL'ye işaret edebilir. Her varyant sayfasındaki tam açıklama kümesine dahil edilmelidir.

- [Google Blog: x-default hreflang](https://developers.google.com/search/blog/2013/04/x-default-hreflang-for-international-pages)
- [Google Blog: How x-default can help you (2023)](https://developers.google.com/search/blog/2023/05/x-default)

### Dil ve Bölge Kodları

Dil: ISO 639-1 (2 harf). Bölge: ISO 3166-1 Alpha 2 (2 harf). Biçim: `language[-script][-region]`.

Tek başına bölge kodu belirleyemezsin. Yaygın hatalar: `en-UK` (olması gereken `en-GB`), `es-419` (ISO 3166-1 değil). Bir çalışma hreflang kullanan sitelerin %8.9'unun geçersiz dil kodu içerdiğini buldu.

- [Google Search Central: Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [SE Land: 31% Study](https://searchengineland.com/study-31-of-international-websites-contain-hreflang-errors-395161)

### Ölçekte Hreflang (20+ yerel ayar)

20 yerel ayarla HTML `<head>` hreflang sayfa başına ~1.5KB ekler, kullanıcıya hiçbir faydası olmadan. Site haritası tabanlı hreflang'ın çalışma zamanı performans etkisi sıfırdır. `<xhtml:link>` alt öğeleri 50.000 URL'lik site haritası sınırına SAYILMAZ (yalnızca `<loc>` öğeleri sayılır).

John Mueller hreflang'ı her sayfa değil, yanlış dilde trafik alan sayfalara odaklamayı öneriyor: "Sitenin diğer sayfaları için yapmazdım çünkü çok karmaşık ve yönetimi zor."

- [SERoundtable: Child Elements Don't Count](https://www.seroundtable.com/google-child-elements-dont-count-towards-sitemap-url-limit-34377.html)
- [SERoundtable: Where To Focus Hreflang](https://www.seroundtable.com/using-hreflang-34127.html)
- [Yoast: hreflang Ultimate Guide](https://yoast.com/hreflang-ultimate-guide/)

### Google vs Bing

Bing hreflang'ı "zayıf sinyal" olarak değerlendirir. Bing `content-language` meta etiketine, HTML `lang` özniteliğine, ccTLD'lere ve sunucu konumuna dayanır. Yandex hreflang'ı Google gibi destekler.

Her iki motor için: hreflang (Google/Yandex) + `<html lang="...">` + `<meta http-equiv="content-language">` (Bing) uygula.

- [Digital Ready Marketing: Bing Doesn't Use Hreflang](https://digitalreadymarketing.com/bing-doesnt-use-hreflang-annotation-what-does-it-use/)
- [Yoast: hreflang Ultimate Guide](https://yoast.com/hreflang-ultimate-guide/)

---

## Canonicalleştirme ve i18n

### Kendine Referans Veren Canonical'lar

Her yerel ayar sayfası kendine canonical vermeli. John Mueller: "Diller/ülkeler arasında rel=canonical kullanmayın, yalnızca ülke/dil bazında kullanın."

Google'ın belgeleri: "Aynı dilde bir canonical sayfa belirtin, ya da aynı dil için canonical yoksa mümkün olan en iyi yedek dili belirtin."

- [John Mueller: hreflang canonical](https://johnmu.com/hreflang-canonical/)
- [Google: Consolidate Duplicate URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)

### Canonical Hreflang'ı Geçersiz Kılar

Mueller: "Canonical'ınız başka bir yeri gösteriyorsa, Google onu izler ve hreflang açıklamanızı yok sayar." Canonical URL hreflang kümesindeki URL'lerden biri olmalıdır, yoksa tüm hreflang işaretlemesi yok sayılır.

Google ayrıca şöyle der: "Google canonicalleştirme için hreflang kümelerinin parçası olan URL'leri tercih eder" -- sinyaller hizalandığında hreflang canonical seçimini güçlendirir.

- [John Mueller: hreflang canonical](https://johnmu.com/hreflang-canonical/)
- [SEJ: Hreflang Tags Are Hints](https://www.searchenginejournal.com/google-reminds-that-hreflang-tags-are-hints-not-directives/546428/)
- [Google: Consolidate Duplicate URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)

### Neredeyse Yinelenen Bölgesel Varyantlar

Mueller (2023 Ofis Saatleri): "İçerik tamamen aynıysa ve hiçbir farkı söyleyemiyorsak, basitlik ve kullanıcı deneyimi için yalnızca bir sürüm gösteririz -- hreflang mevcut olsa bile."

Google'ın yinelenen içerik tespiti hreflang değerlendirmesinden ÖNCE çalışır. Her iki sürümün de indekslenmesini korumak için para birimi sembollerinin ötesinde esaslı içerik farklarına ihtiyacın var.

- [International Web Mastery: Same-Language Duplicate Pages](https://internationalwebmastery.com/blog/how-google-handles-canonicalization-of-same-language-duplicate-near-duplicate-pages/)
- [Google: Managing Multi-Regional Sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)

### Yerel Ayarlar Arasında Sayfalama

Google: "Sayfalanmış bir dizinin ilk sayfasını canonical sayfa olarak kullanmayın. Bunun yerine her sayfaya kendi canonical URL'sini verin." Her yerel ayardaki her sayfalanmış sayfa kendine referans veren canonical alır. `rel="next/prev"` Mart 2019'da kullanımdan kaldırıldı.

- [Google: Pagination Best Practices](https://developers.google.com/search/docs/specialty/ecommerce/pagination-and-incremental-page-loading)

---

## Uluslararası Site Haritaları

### Yapı

Her `<url>` girişi her yerel ayar için `<xhtml:link>` alternatifleri içerir. `xmlns:xhtml="http://www.w3.org/1999/xhtml"` ad alanı gerektirir.

Site haritalarını yerel ayara göre değil içerik türüne göre bölün. Yerel ayara göre bölmek bakım sorunları yaratır çünkü her yerel ayar site haritası diğer tüm yerel ayarlara başvurmalıdır (karşılıklılık gereği).

- [Google Search Central: Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Lumar: How Google Handles Hreflang](https://www.lumar.io/office-hours/hreflang/)

### Boyut Sınırları

Site haritası başına 50.000 URL / 50MB sıkıştırılmamış. 50K sınırına yalnızca `<loc>` öğeleri sayılır. Ama giriş başına 20 hreflang alternatifiyle 50MB dosya boyutu sınırı darboğaz olur. Tam hreflang kullanırken site haritası başına 2.000-5.000 URL planla.

- [Google: Build and Submit a Sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [SERoundtable: Sitemap 50,000 Limit](https://www.seroundtable.com/google-sitemap-50-000-limit-based-on-location-urls-not-alternative-urls-33843.html)

### Gönderme

Site haritası dizinini Search Console'a gönder VE robots.txt içinde ona başvur. Tek tek alt site haritaları, site haritası başına raporlama için ayrıca gönderilebilir.

- [Google: Build and Submit a Sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)

### Next.js Uyarısı

Next.js `alternates.languages`, `<loc>` URL'si için kendine referans veren bir `<xhtml:link>`'i otomatik olarak içermez. `<loc>` URL'sinin kendi dilini `languages` nesnesine açıkça eklemelisin.

- [Next.js Docs: sitemap.xml](https://nextjs.org/docs/app/api-reference/file-conventions/metadata/sitemap)

---

## URL Yapısı

### Stratejilerin Karşılaştırması

Google alt dizinleri ve alt alan adlarını eşdeğer sayar. Mueller: "Bizim açımızdan... alt alan adları ve alt dizinler esasen eşdeğerdir diyorlar."

URL parametreleri (`?lang=en`) Google belgelerine göre açıkça "Önerilmez".

- [Google: Managing Multi-Regional Sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)

### Varsayılan Dil

Mueller öneriyor: `/`'ı x-default yap, her dili kendi önekine koy. `/`'ı x-default olarak işaretlemezsen, "Google için '/' diğerlerinden ayrı bir sayfa gibi görünebilir."

- [Google Blog: x-default](https://developers.google.com/search/blog/2023/05/x-default)
- [Google Blog: Creating the Right Homepage](https://developers.google.com/search/blog/2014/05/creating-right-homepage-for-your)

### İçerik Anlaşması / IP Yönlendirmeleri

Google yerel ayara uyarlanan sayfalara şiddetle karşı çıkar. Googlebot ABD IP'lerinden tarar ve Accept-Language başlıkları göndermez. Ayrı URL'ler + hreflang gereklidir.

- [Google: Locale-Adaptive Pages](https://developers.google.com/search/docs/specialty/international/locale-adaptive-pages)

### Sondaki Eğik Çizgi Tutarlılığı

Mueller: sondaki eğik çizgi "URL'nin önemli bir parçasıdır ve olup olmaması URL'yi değiştirir." Tüm yerel ayar yolları, iç bağlantılar, canonical'lar, hreflang ve site haritaları için tek bir biçim seç.

Mueller (2025): "Tutarlılık en büyük teknik SEO faktörüdür."

- [SERoundtable: Consistency Is The Biggest Technical SEO Factor](https://www.seroundtable.com/google-consistency-seo-40427.html)

### Search Console Coğrafi Hedefleme

Uluslararası Hedefleme raporu kullanımdan kaldırıldı. Google artık tamamen hreflang'a, içerik dili analizine ve bağlantı kalıplarına dayanır. Yerel ayar başına raporlama için alt dizin mülkleri ekleyebilirsin.

- [Google Support: International Targeting Deprecated](https://support.google.com/webmasters/answer/12474899?hl=en)

### Çerçeve Yerel Ayar Modları

`localePrefix: 'always'` (next-intl) ya da eşdeğerini kullan. Yerel ayarı asla URL'lerden saklama -- Google'ın her dil için benzersiz URL'lere ihtiyacı var. `'never'` modu alternatif bağlantıları tamamen devre dışı bırakır.

- [next-intl: Routing Configuration](https://next-intl.dev/docs/routing/configuration)
- [Next.js Discussion #18419](https://github.com/vercel/next.js/discussions/18419)

---

## Yerel Ayarlar Arasında İçerik Kalitesi

### Otomatik Çevrilmiş İçerik (2025 Duruşu)

Google 2025 ortasında otomatik çevrilmiş içeriğe karşı uzun süredir geçerli olan yönlendirmeyi kaldırdı. Mevcut duruş: "Politikalarımız AI ile çevrilmiş içeriği kesin olarak spam diye tanımlamaz." Ölçekli içerik kötüye kullanımı politikası çeviriyi olası bir vektör olarak anar ama yasaklamaz.

Reddit, AI çevirilerini Google'ın bilgisi dahilinde 35+ dile ölçekledi. Kilit ayrım yöntem değil niyet ve kalitedir.

- [Google Spam Policies](https://developers.google.com/search/docs/essentials/spam-policies)
- [Glenn Gabe: Auto-Translating Content](https://www.gsqi.com/marketing-blog/auto-translating-content-google-scaled-content-abuse/)
- [SE Land: Reddit AI Translations](https://searchengineland.com/google-comments-on-reddits-use-of-ai-to-translate-its-pages-456908)

### Zayıf Yerel Ayar Sayfaları

Google: "Bir sayfanın yerelleştirilmiş sürümleri, ancak sayfanın ana içeriği çevrilmeden kalırsa yinelenen sayılır." Yalnızca şablon metni çevrilmiş sayfalar yinelenen olarak kümelenir.

İstenmeyen yerel ayar sayfaları için noindex KULLANMA (tarama bütçesini boşa harcar). Diller arası canonical VERME (hreflang ile çelişir). En iyi yaklaşım: gerçekten yararlı hale getiremeyeceğin yerel ayar sayfaları oluşturma.

- [Google: Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Google: Crawl Budget Management](https://developers.google.com/search/docs/crawling-indexing/large-site-managing-crawl-budget)

### Yardımcı İçerik Sisteminin Etkisi

Mart 2024'te çekirdek sıralamaya birleştirildi. Site geneli sinyal: "genel olarak nispeten yüksek miktarda yardımcı olmayan içeriğe sahip olduğu belirlenen sitelerde, yalnızca yardımcı olmayan içerik değil, herhangi bir içerik Arama'da iyi performans gösterme olasılığı daha düşüktür."

Düşük kaliteli çevrilmiş sayfalar tüm siteyi aşağı çekebilir. Bu, gerçekten yararlı olmayan yerel ayar sayfaları yaratmaya karşı en güçlü argümandır.

- [Google Blog: Helpful Content Update](https://developers.google.com/search/blog/2022/08/helpful-content-update)
- [Amsive: What Changed in 2024](https://www.amsive.com/insights/seo/googles-helpful-content-update-ranking-system-what-happened-and-what-changed-in-2024/)

### Kısmi Çeviri

Google: "Sayfalarınızın yalnızca şablon metnini çevirip içeriğinizin büyük kısmını tek dilde tutmak... kötü bir kullanıcı deneyimi yaratabilir." Google sayfa dilini belirlemek için (lang özniteliği değil) görünür içeriği kullanır.

Bir yerel ayar sürümü oluşturuyorsan sayfadaki TÜM içeriği çevir. Yanlış dilde çevrilmemiş üst veri (başlık, açıklama) tıklama oranını düşürür.

- [Google: Managing Multi-Regional Sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)

### Tarama Bütçesi

Yalnızca 1M+ sayfası olan ya da günde 10K+ sayfası değişen siteler için endişe kaynağıdır. Ama alternatif URL'ler (hreflang hedefleri) tarama bütçesi tüketir. Bozuk hreflang bağlantıları bütçeyi boşa harcar VE sinyalleri geçersiz kılar.

- [Google: Crawl Budget Management](https://developers.google.com/search/docs/crawling-indexing/large-site-managing-crawl-budget)
- [Google Blog: Crawl Budget](https://developers.google.com/search/blog/2017/01/what-crawl-budget-means-for-googlebot)

### Yerel Ayara Özgü Sinyaller

Google hedef kitleyi şu yollarla belirler: "sayfalardaki yerel adresler ve telefon numaraları, yerel dil ve para birimi kullanımı, diğer yerel sitelerden gelen bağlantılar ya da Business Profile'ınızdan gelen sinyaller."

- [Google: Managing Multi-Regional Sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)
