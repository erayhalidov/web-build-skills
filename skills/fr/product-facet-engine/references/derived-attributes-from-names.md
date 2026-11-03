# Dériver des attributs filtrables depuis les noms de produit

Pour les flux sans propriétés techniques (CSV type ERP/Icecat : nom + EAN + poids + prix seulement).
Les valeurs dérivées sont écrites dans la table normale `product_properties` à l'import, donc le moteur de facettes,
le SQL de filtre et la table de specs continuent tous de fonctionner sans changement.

## Catalogue d'attributs et la règle qui a réellement marché

| Attribut | Esquisse de règle | Normalisation |
| --- | --- | --- |
| `Colour` | liste de mots : black, white, silver, grey/gray, blue, red, green, yellow, pink, purple, orange, brown, gold, transparent, beige | `gray→Grey` ; deux couleurs → `Black / White` |
| `Memory type` | `DDR[2345]L?` | + ` SODIMM` / ` RDIMM` / ` UDIMM` quand le nom le dit |
| `Capacity` | `(\d+(?:[.,]\d+)?)\s*(TB|GB)` **et** le nom mentionne SSD/HDD/tape/flash/NVMe/microSD | `1024 GB → 1 TB` ; deux valeurs → `1 TB + 512 GB` |
| `Memory size` | même capture numérique, le nom mentionne DDR/RAM/memory module/SODIMM | comme ci-dessus |
| `Storage capacity` | même capture, le nom mentionne notebook/desktop/server/tablet/phone | comme ci-dessus |
| `Interface` | première correspondance de NVMe, PCIe, SATA, M.2, Thunderbolt, USB-C, USB 3.x, USB 2.0, HDMI, DisplayPort, DVI, VGA, RJ45, SAS, Fibre Channel, Serial | la première correspondance gagne, ordonnée par spécificité |
| `Screen size` | `(\d{2}(?:[.,]\d)?)\s?("|inch|in|')`, borné **10–120** | trim des zéros finaux → `27 inch` |
| `Resolution` | `4K|UHD|QHD|WQHD|UWQHD|Full HD|FHD|WUXGA|XGA|HD`, sinon `W x H` → mappé | `UHD → 4K UHD`, `1920x1080 → Full HD` |
| `Wi-Fi` | `Wi-?Fi ?[4567E]` ou `802.11(ax|ac|be|n)` | `802.11ax → Wi-Fi 6`, `802.11ac → Wi-Fi 5` |
| `Speed` | `(\d+(?:[.,]\d+)?)\s*(Gbit|Gbps|GbE|igabit)`, borné **1–400** ; `\d{2,4}\s?Mbit` | `rtrim(rtrim($v,'0'),'.').' Gbit'` |
| `PoE` | `PoE\+` avant le simple `PoE` | `PoE+` / `PoE` |
| `Ports` | `\b(\d{1,3})[-\s]?port` ou `\b(\d{1,2})\s?x\s?(RJ-?45|LAN|Gigabit|GE)` | `8 ports` |
| `Power` / `Capacity (VA)` | `(\d{3,4})\s?W(?:att)?` borné 45–4000 ; `(\d{2,4})\s?VA` | `650 W`, `1000 VA` |
| `Length` | `(\d+(?:[.,]\d+)?)\s?(m|mm|cm)` borné 0.1–100 m | cm → m, `2 m` |
| `Form factor` | `2.5"/3.5" HDD/SSD/drive` ou `M.2 (2230/2242/2280/22110)` ou `\b[124]U\b` | en majuscules |
| `Print colour` | black/cyan/magenta/yellow **près de** toner/cartridge/ink | `Black` |
| `Paper size` | `A3|A4|A5|A6` **et** paper/print/photo/label/film/designjet dans le nom | garder tel quel |

## Pourquoi les bornes et l'exigence de suffixe comptent

Ce sont les faux positifs réellement apparus en production et comment ils ont été éliminés :

* `Speed = 4 Gbit` sur des routeurs LTE — la regex matchait la génération mobile `4G`. Correctif : exiger un
  suffixe de débit explicite (`Gbit|Gbps|GbE|igabit`) **et** une plage 1–400.
* `Screen size = 1 inch` — venait du second pattern non borné. Correctif : la même borne 10–120 dans chaque
  branche, pas seulement la première.
* `Screen size = 45 inch` sur du matériel réseau — `19 inch` pour des rails de rack est correct, 45 non ; garde quand même
  la borne supérieure.
* `Paper size = A5` sur des moniteurs — `A3`/`A5` apparaissent dans les numéros de pièce. Correctif : exiger un contexte paper/print.
* `Speed = 83 Gbit` — la regex prenait un nombre au hasard suivi de `G`. Même correctif de plage.

## Règles d'ordre et de fusion

1. N'extrais que si le flux de la ligne n'a pas déjà cette propriété (le flux XML fournit `Memory type`,
   `Screen size`, … déjà) — sinon tu dégrades de vraies données fournisseur avec une supposition regex.
2. Stocke avec une valeur `sort` haute pour que la table de specs montre les propriétés du flux en premier.
3. Relance l'importeur après un changement de règles ; le cache de facettes a `built_at` dans sa clé, donc les compteurs se rafraîchissent.

## Boucle de vérification qui les a tous trouvés

```php
// imprime les meilleures valeurs de facette par grande catégorie et regarde-les à l'œil
foreach (['networking','monitors-accessories','computer-components','notebooks-tablets'] as $cat) {
    foreach (spec_facets(['cat' => $cat], 6, 8) as $g) {
        printf("%-22s cov=%-5d %s\n", $g['name'], $g['cov'],
            implode(' | ', array_map(fn($v) => $v['value'] . ' (' . $v['n'] . ')', array_slice($g['values'], 0, 4))));
    }
}
```

Les valeurs qui se lisent comme du non-sens (`1 inch`, `4 Gbit`, `A5` sur des moniteurs) sont toujours une règle qui a besoin d'une borne,
d'un suffixe ou d'un mot-clé de contexte. Une couverture de facettes de ~70–80 % du catalogue est un résultat sain ; le
reste non apparié est réel (les flux manquent vraiment de la donnée) et ne doit pas être forcé dans un panier.
