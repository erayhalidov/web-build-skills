# OpenCart 2.x CSV export — parsing & store settings

Applies to any OpenCart 2.3.x store. The CSV column shape is the same across
2.x exports; only the store-specific values differ.

## Read store settings from the DB, never from memory

Store name, phone, email and the free-shipping threshold all live in
`oc_setting`. Query them before you write any page copy — hardcoding them is
how a phone number from one shop ends up on another shop's site.

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

- `config_telephone`, `config_email`, `config_name` — store contact and brand.
- `free_total` — free-shipping threshold, in the store's currency.
- Shipping modules live in `oc_extension` (`type=shipping`);
  `free_status=0` means the free-shipping module is disabled.

## CSV columns (typical OpenCart 2.x export)

The product export has roughly 100 columns; the ones that matter for a catalog
build are:

| Column | Use |
|---|---|
| `model` | SKU, unique key |
| `name` | product title |
| `description` | HTML body — strip tags for meta description |
| `meta_title`, `meta_description`, `meta_keyword` | SEO, often empty in old shops |
| `price`, `special` | regular and promo price (`special` empty = no promo) |
| `quantity` | stock; `0` usually means "on order" |
| `image`, `additional_images` | relative paths under `image/`, comma-separated |
| `manufacturer` | brand name (join `oc_manufacturer`) |
| `category`, `categories` | category path, `>` separated |
| `weight`, `unit` | shipping fields |
| `status` | `1` = published, `0` = hidden |
| `product_id` | internal id, stable across exports |

## Parsing pitfalls

- The file is usually **UTF-8 with BOM** and `;` or `,` separated depending on
  the shop's locale — sniff the first line instead of assuming.
- Product descriptions contain newlines and quotes; parse with a real CSV
  reader, never `split(',')`.
- `additional_images` uses `,` inside a quoted field — again, a real reader.
- Prices are bare numbers in the store currency; format them for display
  (decimal comma in BG/DE, dot in EN) but never do money maths in floats —
  convert to integer cents first.

## Locating the export

```bash
clpctl db:show:master-credentials    # on CloudPanel hosts
# or read config.php for the credentials, then:
mysql -h127.0.0.1 -u<user> -p<pass> <db> \
  -e "SELECT COUNT(*) FROM oc_product WHERE status=1;"
```

Most shops have a CSV export module under **System → Export** in the admin, but
a direct `mysqli` dump of `oc_product` joined with `oc_product_description` is
more reliable and includes the fields the admin export omits.
