# Export CSV de OpenCart 2.x — parseo y ajustes de tienda

Aplica a cualquier tienda OpenCart 2.3.x. La forma de las columnas del CSV es la misma en los
exports 2.x; solo cambian los valores específicos de cada tienda.

## Lee los ajustes de tienda de la BD, nunca de memoria

El nombre de la tienda, el teléfono, el email y el umbral de envío gratis viven todos en
`oc_setting`. Consúltalos antes de escribir cualquier texto de página — hardcodearlos es
cómo un número de teléfono de una tienda acaba en el sitio de otra.

```bash
# ajusta la ruta/usuario al sitio en el que estás trabajando
sudo -u <site_user> /usr/bin/php -r '
require "/home/<site_user>/htdocs/<domain>/config.php";
$c = mysqli_connect(DB_HOSTNAME, DB_USERNAME, DB_PASSWORD, DB_DATABASE);
$q = "SELECT `key`,`value` FROM oc_setting WHERE store_id=0 AND `key` IN
      (\"config_telephone\",\"config_email\",\"config_name\",\"free_total\")";
$r = mysqli_query($c, $q);
while ($x = mysqli_fetch_assoc($r)) { echo $x["key"]." = ".$x["value"]."\n"; }
'
```

- `config_telephone`, `config_email`, `config_name` — contacto y marca de la tienda.
- `free_total` — umbral de envío gratis, en la moneda de la tienda.
- Los módulos de envío viven en `oc_extension` (`type=shipping`);
  `free_status=0` significa que el módulo de envío gratis está desactivado.

## Columnas del CSV (export típico de OpenCart 2.x)

El export de producto tiene unas 100 columnas; las que importan para construir un catálogo
son:

| Columna | Uso |
|---|---|
| `model` | SKU, clave única |
| `name` | título del producto |
| `description` | cuerpo HTML — quita las etiquetas para la meta description |
| `meta_title`, `meta_description`, `meta_keyword` | SEO, a menudo vacías en tiendas antiguas |
| `price`, `special` | precio normal y de promoción (`special` vacío = sin promo) |
| `quantity` | stock; `0` normalmente significa "por encargo" |
| `image`, `additional_images` | rutas relativas bajo `image/`, separadas por comas |
| `manufacturer` | nombre de la marca (join con `oc_manufacturer`) |
| `category`, `categories` | ruta de categoría, separada por `>` |
| `weight`, `unit` | campos de envío |
| `status` | `1` = publicado, `0` = oculto |
| `product_id` | id interno, estable entre exports |

## Trampas del parseo

- El archivo suele ser **UTF-8 con BOM** y separado por `;` o `,` según
  el locale de la tienda — inspecciona la primera línea en vez de asumir.
- Las descripciones de producto contienen saltos de línea y comillas; parsea con un lector CSV
  real, nunca con `split(',')`.
- `additional_images` usa `,` dentro de un campo entrecomillado — de nuevo, un lector real.
- Los precios son números pelados en la moneda de la tienda; formatéalos para mostrar
  (coma decimal en BG/DE, punto en EN) pero nunca hagas cálculos de dinero en floats —
  convierte primero a céntimos enteros.

## Localizar el export

```bash
clpctl db:show:master-credentials    # en hosts CloudPanel
# o lee config.php para las credenciales, y luego:
mysql -h127.0.0.1 -u<user> -p<pass> <db> \
  -e "SELECT COUNT(*) FROM oc_product WHERE status=1;"
```

La mayoría de tiendas tienen un módulo de export CSV en **System → Export** del admin, pero
un dump directo con `mysqli` de `oc_product` unido con `oc_product_description` es
más fiable e incluye campos que el export del admin omite.
