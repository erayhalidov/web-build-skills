# Nulled Journal2/Journal3 temasını kaldırma (OpenCart 2.3)

Journal2 ve Journal3 yalnızca tema DEĞİLDİR — çekirdek dosyaları İKİ şekilde değiştirirler ve her ikisi de geri alınmalıdır:

1. **OCMOD** — `system/journal3.ocmod.xml`, `system/da_journal2.ocmod.xml` (J3 için 84 dosya işlemi). `system/storage/modification/` içine önbelleğe alınır.
2. **Doğrudan dosya düzenlemeleri** — Journal2'nin kurucusu çekirdek dosyaları doğrudan yeniden yazar (OCMOD üzerinden DEĞİL). Eşleşen stok tarball ile diff alarak doğrulayın.

## Güvenli kaldırma sırası (önce geç, doğrula, sonra sil)

### 1. Temayı değiştir (geri alınabilir)
```
UPDATE oc_setting SET value='theme_default' WHERE `key`='config_theme';
UPDATE oc_setting SET value='<newtheme>' WHERE `key`='theme_default_directory';
```
Herhangi bir şeyi kaldırmadan ÖNCE vitrinin çalıştığını (curl 200) doğrulayın. Journal dosyaları diskte kalır ama tema değiştirildiğinde etkisizdir.

### 2. Doğrudan değiştirilmiş çekirdek dosyaları bul (stok ile diff)
Eşleşen `VERSION` tarball'ını indirin: `https://github.com/opencart/opencart/archive/<VERSION>.tar.gz`.
```
for f in system/engine/front.php system/engine/loader.php system/engine/router.php \
         system/engine/action.php system/engine/event.php system/framework.php \
         system/library/template.php system/library/template/php.php system/startup.php; do
  diff -q /tmp/oc<v>/upload/$f $f >/dev/null 2>&1 || echo "DIFFERS: $f";
done
```
Bu oturumdaki suçüstü kanıt: `system/engine/front.php` içine `require_once(DIR_SYSTEM . 'journal2/startup.php')` gömülmüştü (~48. satır), journal dizini kaldırıldıktan sonra HTTP 500 ile fatal veriyor. Bu tür dosyaları stok tarball'dan geri yükleyin. `system/framework.php` ve `system/engine/router.php` farkları etkisiz uyumluluk katmanlarıydı (`version_compare(VERSION,'2.3','<')` ile korunuyor) — geri almadan önce doğrulayın.

### 3. OCMOD XML'lerini kaldır + önbelleği yeniden oluştur
- `mv system/journal3.ocmod.xml system/da_journal2.ocmod.xml <backup>/` (doğrulanana kadar SİLMEYİN; varsa `universal_import_pro.ocmod.xml` dosyasını koruyun).
- `scripts/ocmod_refresh.php` çalıştırın. `grep -c journal2 system/storage/modification/system/engine/front.php` → 0 (ya da dosya önbellekte artık yok) olduğunu doğrulayın.

### 4. Tema/kod dizinlerini webroot dışına taşı (yedek olarak sakla)
Dizinler + dağınık dosyalar (doğrulanana kadar taşıyın, düz silmeyin):
- `catalog/view/theme/journal3`, `catalog/view/theme/journal2`
- `system/library/journal3`, `system/library/journal3.php`, `system/journal2`
- `catalog/model/journal3`, `catalog/model/journal2`
- `catalog/controller/journal3`, `catalog/controller/journal2`
- `catalog/controller/module/journal2_*.php` (çok sayıda)
- `admin/view/template/journal3`, `admin/view/template/journal2`, `admin/view/javascript/journal3`, `admin/view/journal2`
- `admin/model/journal3`, `admin/model/journal2`, `admin/controller/journal3`, `admin/controller/journal2`
- `admin/language/en-gb/journal3`, `admin/language/en-gb/journal2`
- `admin/controller/extension/theme/theme_journal3.php`, `admin/controller/module/journal2.php`
- `admin/language/*/module/journal2.php`, `admin/language/*/extension/theme/theme_journal3.php`
- `admin/view/image/journal3`, `admin/view/stylesheet/journal3`

Uyarı: Düz bir yedek dizinine `mv` yapmak aynı adlı alt dizinlerde çakışır (`journal3`/`journal2` tekrar eder). Yol başına hedef adlar kullanın (`$(echo "$p" | tr '/' '_')`).

### 5. DB'yi temizle
```
DELETE FROM oc_layout_module WHERE code LIKE 'journal2\_%' OR code LIKE 'journal3\_%' OR code='0';
DELETE FROM oc_setting WHERE `key` LIKE 'journal2\_%' OR `key` LIKE 'theme_journal3%' OR `key` LIKE '%journal3%';
DELETE FROM oc_extension WHERE type='theme' AND code='theme_journal3';
```
`oc_event` genellikle journal kaydı içermez — doğrulayın.

### 6. Son doğrulama
Tüm rotalarda curl (ana sayfa/kategori/ürün/sepet/hesap) → 200; `system/storage/cache/*` temizle; yeni hatalar için `system/storage/logs/error.log` dosyasının sonuna bakın.
