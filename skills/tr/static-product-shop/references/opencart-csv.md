# OpenCart 2.x CSV dışa aktarımı — ayrıştırma ve mağaza ayarları

Herhangi bir OpenCart 2.3.x mağazası için geçerlidir. CSV sütun yapısı 2.x dışa aktarımlarında
aynıdır; yalnızca mağazaya özgü değerler farklıdır.

## Mağaza ayarlarını DB'den okuyun, asla hafızadan değil

Mağaza adı, telefon, e-posta ve ücretsiz kargo eşiği `oc_setting` içinde yaşar.
Herhangi bir sayfa metni yazmadan önce bunları sorgulayın — sabit kodlamak,
bir mağazanın telefon numarasının başka bir mağazanın sitesine düşmesinin yoludur.

```bash
# adjust the path/user to the site you are working on
sudo -u <site_user> /usr/bin/php -r '
require "/home/<site_user>/htdocs/<domain>/config.php";
$c = mysqli_connect(DB_HOSTNAME, DB_USERNAME, DB_PASSWORD, DB_DATABASE);
$q = "SELECT `key`,`value` FROM oc_setting WHERE store_id=0 AND `key` IN
      (\"config_telephone\",\"config_email\",\"config_name\",\"free_total\")";
$r = mysqli_query($c, $q);
while ($x = mysqli_fetch_assoc($r)) { echo $x["key"]." = ".$x["value"]."\n"; }
'
```

- `config_telephone`, `config_email`, `config_name` — mağaza iletişimi ve marka.
- `free_total` — ücretsiz kargo eşiği, mağazanın para biriminde.
- Kargo modülleri `oc_extension` içinde (`type=shipping`);
  `free_status=0` ücretsiz kargo modülünün kapalı olduğu anlamına gelir.

## CSV sütunları (tipik OpenCart 2.x dışa aktarımı)

Ürün dışa aktarımında yaklaşık 100 sütun vardır; katalog oluşturmada
önemli olanlar:

| Sütun | Kullanım |
|---|---|
| `model` | SKU, benzersiz anahtar |
| `name` | ürün başlığı |
| `description` | HTML gövde — meta açıklama için etiketleri temizleyin |
| `meta_title`, `meta_description`, `meta_keyword` | SEO, eski mağazalarda genellikle boş |
| `price`, `special` | normal ve promosyon fiyatı (`special` boş = promosyon yok) |
| `quantity` | stok; `0` genellikle "sipariş üzerine" demektir |
| `image`, `additional_images` | `image/` altında göreli yollar, virgülle ayrılmış |
| `manufacturer` | marka adı (`oc_manufacturer` ile birleştirin) |
| `category`, `categories` | kategori yolu, `>` ile ayrılmış |
| `weight`, `unit` | kargo alanları |
| `status` | `1` = yayında, `0` = gizli |
| `product_id` | iç id, dışa aktarımlar arasında kararlı |

## Ayrıştırma tuzakları

- Dosya genellikle **BOM'lu UTF-8** ve mağazanın yerel ayarına göre `;` ya da `,` ile ayrılmıştır —
  varsaymak yerine ilk satırı koklayın.
- Ürün açıklamaları satır sonları ve tırnaklar içerir; gerçek bir CSV
  okuyucuyla ayrıştırın, asla `split(',')` ile değil.
- `additional_images` tırnak içindeki alanda `,` kullanır — yine, gerçek bir okuyucu.
- Fiyatlar mağaza para biriminde çıplak sayılardır; görüntülemek için biçimlendirin
  (BG/DE'de ondalık virgül, EN'de nokta) ama para hesabını asla float ile yapmayın —
  önce tam sayı kuruşa dönüştürün.

## Dışa aktarımı bulma

```bash
clpctl db:show:master-credentials    # on CloudPanel hosts
# or read config.php for the credentials, then:
mysql -h127.0.0.1 -u<user> -p<pass> <db> \
  -e "SELECT COUNT(*) FROM oc_product WHERE status=1;"
```

Çoğu mağazada yönetim panelinde **System → Export** altında bir CSV dışa aktarma modülü vardır, ama
`oc_product` tablosunun `oc_product_description` ile birleştirilmiş doğrudan `mysqli` dökümü
daha güvenilirdir ve yönetim paneli dışa aktarımının atladığı alanları da içerir.
