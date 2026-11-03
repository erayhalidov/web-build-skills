---
name: opencart
description: OpenCart 2.x mağazalarını işletin (tema, temizlik, hata).
---

# OpenCart 2.x İşletimi

## Ne zaman kullanılır
- Bir OpenCart 2.x sitesi üzerinde çalışırken: temalar, düzen, ana sayfa modülleri, disk şişmesi, hata ayıklama.
- Bir temayı — özellikle nulled Journal2/Journal3'ü — kaldırıp temiz bir yerel temaya geçerken.
- Bir vitrin teması oluştururken/özelleştirirken.

## Mimari gerçekler (OpenCart 2.3.x)
- Şablonlar `.tpl` = `Template\PHP` tarafından render edilen ham PHP (`require($file)` + `extract($data)`), Twig DEĞİL. `system/library/template/tiwg.php` var ama yükleyici `$route . '.tpl'` yolunu sabit kodluyor; motor PHP. 2.3 için `.twig` yazmayın.
- `catalog/controller/event/theme.php` içinde etkin tema çözümlemesi:
  - `config_theme == 'theme_default'` → tema dizini = `theme_default_directory` ayarı.
  - aksi halde → `config_theme` kullanılır (Journal3 bir OCMOD yeniden eşlemesi ekler: `theme_journal3` → `journal3`).
  - Eksik şablon `default/template/<view>` yoluna düşer (üçüncü taraf modül şablonları için "default" tema dizinini yedek olarak koruyun).
- Tema `catalog/view/theme/<name>/template/` (`.tpl` dosyaları) + `stylesheet/` altında bulunur.
- İki yapılandırma dosyası: `catalog/config.php` (DIR_APPLICATION=catalog) ve `admin/config.php` (DIR_APPLICATION=admin, DIR_CATALOG=catalog, DIR_MODIFICATION=system/storage/modification/). İkisinde de DB kimlik bilgileri vardır.

## Özel bir temaya geçiş (en güvenli, geri alınabilir)
1. Temayı `catalog/view/theme/<name>/` içine bırakın.
2. DB:
   `UPDATE oc_setting SET value='theme_default' WHERE \`key\`='config_theme';`
   `UPDATE oc_setting SET value='<name>' WHERE \`key\`='theme_default_directory';`
   `theme_default_status` = 1 olduğundan emin olun.
3. Geri alma = tek bir DB güncellemesi. Yıkıcı temizlikten önce curl ile doğrulayın.

## Kategori menüsü (yerel tema)
Yerel başlık menüsü yalnızca `top=1` VE `status=1` olan kategorileri gösterir. Journal temaları kendi menülerini kullanıp bu bayrağı yok sayıyordu, dolayısıyla geçişten sonra menü boş görünür. Düzeltme:
`UPDATE oc_category SET top=1 WHERE category_id IN (<top-level ids>);`

## Ana sayfa modülleri (yerel)
- Modüller `oc_module` içinde (`setting` bir JSON dizesidir); atama `oc_layout_module` içinde (`code` = `<modulecode>.<id>`, `position`, `sort_order`).
- `featured` için `"product":["id1","id2",...]` gerekir; `latest`/`special`/`bestseller` yalnızca `limit`/`width`/`height`/`status` ister.
- Eski temadan kalan sahipsiz kayıtlar: `DELETE FROM oc_layout_module WHERE code LIKE 'journal2\_%' OR code LIKE 'journal3\_%' OR code='0';`
- Ürün açıklamaları `oc_product_description` içinde dil bazlıdır; OpenCart demo verisi language_id=1'de, gerçek veri mağaza dilinin id'sinde bulunur (örn. 2 = bg).

## Temiz bir yerel tema oluşturma
- Stok varsayılan temayı (`upload/catalog/view/theme/default`) `VERSION` (index.php) ile eşleşen GitHub tarball'ından kopyalayıp yeni tema dizinine koyun. Uyumluluğu garantili temel.
- `stylesheet/stylesheet.css` + `common/header.tpl`, `footer.tpl`, `home.tpl` dosyalarını özelleştirin. Stok tema Bootstrap 3'tür — CSS'te yoğun şekilde üzerine yazın.

## Tuzaklar (gerçekten karşılaşılanlar)
- `$home`, `home.tpl` içinde tanımlı DEĞİLDİR (yalnızca header.tpl'de). Göreli URL'ler kullanın (`<base href>` ayarlıdır) ya da `index.php?route=...` bağlantıları.
- `image/cache/*` dizinini root olarak silip yeniden oluşturmak → dizinlerin sahibi root olur; OpenCart (site kullanıcısı) ardından `imagepng(): Permission denied` alır. Düzeltme: `chown -R <siteuser>:<siteuser> image/cache/`.
- CDN/Varnish CSS'i agresif şekilde önbelleğe alır. Stylesheet'i değiştirdikten sonra `<link>` için önbellek kırın: `stylesheet.css?v=2` ve screenshot/curl URL'lerine `?v=$(date +%s)` ekleyin.
- CSS özgüllüğü: `.product-thumb .caption p` (0,2,1) `.product-thumb .price` (0,2,0) kuralını yener — fiyat kurallarını `.product-thumb .caption .price` olarak kapsamlandırın.

## Nulled Journal2/Journal3 temasını kaldırma
Zor kısmı: HEM OCMOD HEM de çekirdek dosyalara doğrudan düzenlemelerle bütünleşirler. Kesin yollar/adımlar için `references/journal3-removal.md` ve bağımsız yenileme için `scripts/ocmod_refresh.php` dosyasına bakın.

## Doğrulama
- Her rota için `curl -s -o /dev/null -w "%{http_code}"` (ana sayfa/kategori/ürün/sepet/hesap).
- Başsız ekran görüntüsü: Playwright'ın paketlediği chromium `/root/.cache/ms-playwright/chromium-*/chrome-linux64/chrome --headless --disable-gpu --no-sandbox --hide-scrollbars --window-size=W,H --virtual-time-budget=9000 --screenshot=/tmp/x.png URL`. Temayı PIL ortalama RGB ile doğrulayın (koyu ≈ <60).
- CSS'in gerçekten uygulandığını `browser_console` hesaplanmış stilleri ile doğrulayın (bayat CDN önbelleğine dikkat — sunulan baytları karşılaştırın, `?v=` ekleyin).
