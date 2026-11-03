# Export CSV OpenCart 2.x — parsing & réglages boutique

S'applique à toute boutique OpenCart 2.3.x. La forme des colonnes CSV est la même sur tous les
exports 2.x ; seules les valeurs propres à la boutique changent.

## Lis les réglages boutique dans la DB, jamais de mémoire

Nom de la boutique, téléphone, email et seuil de livraison gratuite vivent tous dans
`oc_setting`. Interroge-les avant d'écrire le moindre texte de page — coder en dur, c'est
comment un numéro de téléphone d'une boutique finit sur le site d'une autre.

```bash
# adapte le chemin/l'utilisateur au site sur lequel tu travailles
sudo -u <site_user> /usr/bin/php -r '
require "/home/<site_user>/htdocs/<domain>/config.php";
$c = mysqli_connect(DB_HOSTNAME, DB_USERNAME, DB_PASSWORD, DB_DATABASE);
$q = "SELECT `key`,`value` FROM oc_setting WHERE store_id=0 AND `key` IN
      (\"config_telephone\",\"config_email\",\"config_name\",\"free_total\")";
$r = mysqli_query($c, $q);
while ($x = mysqli_fetch_assoc($r)) { echo $x["key"]." = ".$x["value"]."\n"; }
'
```

- `config_telephone`, `config_email`, `config_name` — contact et marque de la boutique.
- `free_total` — seuil de livraison gratuite, dans la devise de la boutique.
- Les modules de livraison vivent dans `oc_extension` (`type=shipping`) ;
  `free_status=0` signifie que le module de livraison gratuite est désactivé.

## Colonnes CSV (export OpenCart 2.x typique)

L'export produit a environ 100 colonnes ; celles qui comptent pour construire un catalogue
sont :

| Colonne | Usage |
|---|---|
| `model` | SKU, clé unique |
| `name` | titre du produit |
| `description` | corps HTML — retire les balises pour la meta description |
| `meta_title`, `meta_description`, `meta_keyword` | SEO, souvent vides sur les vieilles boutiques |
| `price`, `special` | prix normal et promo (`special` vide = pas de promo) |
| `quantity` | stock ; `0` signifie généralement « sur commande » |
| `image`, `additional_images` | chemins relatifs sous `image/`, séparés par virgules |
| `manufacturer` | nom de marque (jointure `oc_manufacturer`) |
| `category`, `categories` | chemin de catégorie, séparé par `>` |
| `weight`, `unit` | champs de livraison |
| `status` | `1` = publié, `0` = masqué |
| `product_id` | id interne, stable entre exports |

## Pièges de parsing

- Le fichier est généralement en **UTF-8 avec BOM** et séparé par `;` ou `,` selon
  la locale de la boutique — renifle la première ligne au lieu de supposer.
- Les descriptions produit contiennent des retours à la ligne et des guillemets ; parse avec un vrai lecteur
  CSV, jamais `split(',')`.
- `additional_images` utilise `,` à l'intérieur d'un champ entre guillemets — encore une fois, un vrai lecteur.
- Les prix sont des nombres bruts dans la devise de la boutique ; formate-les pour l'affichage
  (virgule décimale en BG/DE, point en EN) mais ne fais jamais de calculs monétaires en flottants —
  convertis d'abord en centimes entiers.

## Localiser l'export

```bash
clpctl db:show:master-credentials    # sur les hôtes CloudPanel
# ou lis config.php pour les identifiants, puis :
mysql -h127.0.0.1 -u<user> -p<pass> <db> \
  -e "SELECT COUNT(*) FROM oc_product WHERE status=1;"
```

La plupart des boutiques ont un module d'export CSV sous **System → Export** dans l'admin, mais
un dump `mysqli` direct de `oc_product` joint à `oc_product_description` est
plus fiable et inclut les champs que l'export admin omet.
