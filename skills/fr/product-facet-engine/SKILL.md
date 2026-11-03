---
name: product-facet-engine
description: "Filtres catalogue depuis des feeds pauvres en données."
---

# Product facet engine — de vrais filtres sur des données fournisseur éparses

À utiliser quand une boutique/un catalogue (PHP+SQLite, OpenCart, Medusa, HTML statique) a besoin de **vrais filtres**, mais :
* le client dit « fais le filtre comme sur *<gros distributeur>* » (il veut dire des facettes de specs avec compteurs,
  des chips de filtres sélectionnés, du multi-select, du show-more), ou
* le flux fournisseur contient peu ou pas de données techniques (typique des CSV type ERP/Icecat : nom, EAN,
  poids, prix et rien d'autre), ou
* les sous-catégories, valeurs d'attributs ou poids de livraison n'existent simplement pas dans le flux.

Règle absolue pour chaque valeur affichée : elle doit se rattacher à une donnée du flux ou à une **extraction dérivée du nom**.
N'invente jamais une valeur de spec, un compteur ou un prix. Inconnu → omets la facette, ou affiche « sur demande ».

## 1. Décider d'où vient chaque filtre

| Source | Exemples | Notes |
| --- | --- | --- |
| Propriétés du flux | `product_properties(name,value)` venant de flux XML | Les plus riches, à utiliser en premier. |
| Dérivées du nom | Couleur, Capacité, Type de mémoire, Interface, Taille d'écran, Wi-Fi, Ports, Puissance, Longueur | Fonctionne pour les flux sans aucune propriété — voir §3. |
| Structurelles | marque, catégorie, sous-catégorie, tranche de prix, « a une photo » | Toujours disponibles. |
| Poids | `products.weight` (kg) | Pilote le prix de livraison, pas une facette. |

Un flux a souvent des propriétés et l'autre aucune : n'extrais que pour les produits dont le flux n'en a pas,
pour ne jamais écraser de vraies valeurs fournisseur.

## 2. Sous-catégories quand le flux n'a pas de niveau inférieur

Table de règles ordonnée, la première correspondance gagne, appliquée **au moment de l'import** (`inc/taxonomy.php` →
`catalogue_subcategory_rules()` : nom de catégorie → `[[sub_name, regex], …]`). Indexe la table sur le nom de
catégorie exact après tout mapping « clean split » — une différence de casse (`Junction boxes` vs `Junction Boxes`)
donne silencieusement zéro correspondance, donc dumpe les vrais noms de catégories et diff-les contre les clés de règles.

* Les produits sans correspondance restent `subcategory_id = NULL` — ne les **fais pas** tomber dans un panier « Autre ».
* Les slugs sont générés par l'importeur ; le même chemin de code sert ensuite les pages de sous-catégorie, les facettes,
  les breadcrumbs et le sitemap gratuitement.
* Résultat réaliste : 195 sous-catégories fournies par le flux → 365 après dérivation, 76 % de 38 k produits placés.
* La visibilité en UI compte autant que la donnée : une bande de chips avec compteurs en haut de la page catégorie,
  un index « Catégories dans <rayon> » sur la page rayon. **Cet utilisateur ne veut que les catégories principales
  sur l'index du rayon (pas de sous-liens ici) et la bande complète de sous-catégories sur la page
  catégorie** — ne duplique pas la même liste dans la sidebar également.

## 3. Dériver les attributs depuis les noms de produit et les stocker comme vraies propriétés

Toute l'astuce : écrire les valeurs dérivées dans `product_properties` à l'import, pour que le moteur de facettes, le
SQL de filtre, le sitemap et la table de specs fonctionnent tous avec **un seul** mécanisme au lieu d'un chemin de code
parallèle « dérivé ».

* Utilise `sort = 1200` (ou toute valeur haute) pour les lignes dérivées, et saute un nom que le flux a déjà fourni.
* Les règles vivent dans un seul fichier (`inc/attributes.php` → `extract_attributes($name, $category)`), retournant
  `['Interface' => 'HDMI', …]` — uniquement les attributs réellement trouvés.
* Les numériques bornés et les suffixes explicites font la différence entre une facette utile et du bruit :
  * la vitesse exige `Gbit|Gbps|GbE|igabit` **et** 1–400 → sinon les routeurs LTE « 4G/5G » deviennent « 4 Gbit » ;
  * taille d'écran bornée à 10–120 inch, puissance 45–4000 W, longueur de câble 0,1–100 m ;
  * `Paper size` uniquement quand le nom mentionne aussi paper/print/photo/label (sinon `A3` d'un numéro de pièce fuit) ;
  * normalise `1024 GB → 1 TB`, `gray → Grey`, `802.11ax → Wi-Fi 6`, joins deux couleurs en `Black / White`.
* Garde les faux positifs hors de la facette en écartant les groupes qui ne sont pas discriminants (§4).
* Catalogue complet des règles et pièges du parser : `references/derived-attributes-from-names.md`.

## 4. Moteur de découverte des facettes

Un **constructeur de scope partagé** alimente à la fois la requête de listing et les requêtes de facettes — dupliquer les
jointures/WHERE est la façon dont les compteurs du listing et ceux des facettes divergent.

```php
function scope_sql(array $f, bool $withSpec = true): array   // [from, whereSql, params, joinFts]
```

Découverte, à chaque requête :
1. Noms de propriétés candidats les plus fréquents dans ce scope : `SELECT pp.name, COUNT(DISTINCT pp.product_id) cov …
   GROUP BY pp.name HAVING cov >= 3 ORDER BY cov DESC LIMIT 40`, moins une **blacklist**
   (`Vendor_url`, `Dimensions`, `Weight`, `EAN`, `Part number`, `Warranty`, `Model`, `Other`, …).
2. Pour chaque nom, récupère ses ~26 meilleures valeurs avec compteurs.
3. Ne garde un nom que s'il a 2–24 valeurs, au moins 8 produits, et si sa meilleure valeur couvre ≤ 85 % du
   groupe (une valeur qui couvre tout n'est pas discriminante).
4. Ordonne les groupes par une **liste de priorité** explicite (specs matérielles d'abord, `Colour` en dernier) plutôt que
   par couverture brute — la couverture seule affiche volontiers `Audio` et `Pen` avant `Screen size`.
5. Prends ~6 groupes × 8 valeurs.

Filtrage : un `EXISTS` par groupe de propriétés (AND entre groupes, OR dans un groupe), params ajoutés dans
l'ordre :
```sql
EXISTS (SELECT 1 FROM product_properties x WHERE x.product_id = p.id AND x.name = ? AND x.value IN (?,?))
```
Indexe-le : `CREATE INDEX idx_pp_name_value ON product_properties(name, value)`.

Cache les agrégats de facettes dans un cache fichier dont la clé est `md5(scope) + built_at` avec un TTL de 1 h — à froid ≈ 230 ms,
à chaud ≈ 30–40 ms. **La méta `built_at` doit faire partie de la clé**, sinon un ré-import laisse des compteurs
obsolètes à l'écran pendant une heure. Purge les fichiers de cache de plus de ~7 jours à l'écriture.

## 5. UI de filtre et contrat d'URL

* Multi-select, pas de radio : `?brand[]=hp&brand[]=lenovo` (et `?spec[Screen size][]=27 inch`), donc la
  requête de filtre prend un tableau par groupe ; les formulaires de tri/par-page doivent réémettre les params tableau en inputs
  cachés, sinon le tri abandonne silencieusement les filtres.
* **Chips de filtres sélectionnés** au-dessus des résultats, chacun avec un ✕ qui retire exactement cette valeur
  (`url_without_value($key,$value)`, `url_without_spec($name,$value)`) plus « Tout effacer ».
* **Exactement un bouton dans la sidebar — libellé `Filter`.** Pas de titre « Filters » à côté, pas de
  toggle Afficher/Masquer, pas de « Show N more » par groupe : le propriétaire les a tous retirés explicitement. Les longues
  listes de valeurs défilent dans leur propre boîte (`max-height` + `overflow-y:auto`, `.fopts-scroll`) ; le bouton
  reste compact (`~72×37 px`, `btn-sm`, `width:auto` — pas pleine largeur ni sur desktop *ni* sur téléphone) et porte
  le nombre de filtres actifs comme petit badge. Sur téléphone ce bouton ouvre / ferme la liste (repliée) — les filtres
  s'appliquent au fur et à mesure, donc il n'y a pas d'étape « Appliquer ».
* Par groupe : badge du nombre sélectionné et compteurs alignés à droite. Par page : 24/48/96.
* URL filtrées/paginées : `noindex, follow` + canonical vers l'URL propre (inchangé par rapport à la base du site flux).
* Quand le propriétaire impose « tout est disponible », **retire la facette de disponibilité** — un filtre dont le
  seul panier égale le total est du bruit.

### 5a. Le filtrage ne doit pas recharger la page (et les compteurs se mettent à jour sur place)

Exigence du propriétaire en clair : *« cliquer un filtre ne doit pas recharger la page, pour que je puisse ajouter plusieurs
filtres d'un coup »*. Recette PHP + JS qui fonctionne, contrat JSON et méthode de test :
`references/ajax-facet-refresh.md`.

* Un seul endpoint de fragment JSON sert toutes les routes de listing (`…?<filters>&frag=1` → `{results, counts, total,
  url, title}`) ; la vue page et l'endpoint de fragment construisent tous deux leur état via **un unique
  `listing_context()` partagé**, sinon page et fragments divergent.
* **Rafraîchis les résultats, jamais le HTML de la sidebar.** Re-rendre la sidebar sous le curseur *est* précisément
  la plainte du propriétaire *« je coche un filtre et un autre se retrouve coché »* — la liste se réordonne autour du
  clic. Remplace uniquement le bloc de résultats et patch la sidebar **sur place** (texte du compteur + masquer/afficher les items) :
  la case cochée reste le même nœud DOM, cochée, là où le doigt l'a laissée.
* **Compteurs live, valeurs nulles retirées.** Compte chaque groupe avec tous les autres filtres appliqués et
  *sa propre sélection relâchée* (`facet_live_counts()`), masque les valeurs dont le compteur est 0 sauf si elles sont cochées, et masque
  tout le groupe quand il n'y reste rien. Injecte de force les valeurs cochées dans la liste de valeurs — les facettes top-N
  les retireraient sinon et l'acheteur ne pourrait pas décocher. Calcule-le uniquement quand un filtre est
  actif : sans sélection, le scan de scope mis en cache donne les mêmes chiffres bien moins cher (mesuré ici : 17 ms
  page non filtrée, 49 ms page filtrée, 53 ms fragment).
* `history.pushState` à chaque changement plus `popstate` pour le bouton retour ; remets `page` à 1 lors d'un
  changement de filtre/tri mais **conserve-le** pour la pagination et les liens par page ; réutilise la query string du
  navigateur pour l'URL propre (en retirant `frag` et le tri par défaut, en sautant les `min=`/`max=` vides) plutôt que de
  resérialiser avec `http_build_query`, qui réécrit `spec[Socket][]=LGA1700` en
  `spec[Socket][0]=LGA1700`.
* L'amélioration progressive n'est pas optionnelle : le même formulaire fait toujours un GET normal sans JS, donc un
  test doit `curl` exactement la query que le formulaire enverrait.

## 6. Prix de livraison basés sur le poids (même dataset, même règle d'honnêteté)

Le coût de livraison est une fonctionnalité du catalogue : calcule-le à partir des vrais poids produits et des **tarifs
transporteur publiés**, jamais d'une estimation.

**Le poids peut manquer pour tout un flux.** Le flux XML n'avait aucune colonne de poids, donc 5 400 produits
auraient été expédiés sur un « estimé 0,5 kg ». Extrais la valeur des propres propriétés du flux à l'import
à la place : `Weight: "1.70 kg"`, `"Starting at 1.38 kg"`, `"450 g"` → `products.weight` (parser = premier
nombre + unité, `g` → /1000, borné 0–200 kg, écrit seulement là où la colonne est vide). 1 713 produits
ont ainsi gagné un vrai poids et la tranche de livraison a cessé d'être une estimation. Ne devine jamais un poids —
un inconnu reste inconnu et le récapitulatif le dit. Bulgarie (Speedy exploite le réseau DPD là-bas ; `www.dpd.bg` redirige vers
speedy.bg), grille tarifaire officielle, codes de service, prix par groupe de pays et recette de récupération sont dans
`references/bg-carrier-tariffs.md`. Destinations hors du tarif publié → « prix sur demande ».

## 7. Combler les trous de données sans les inventer (la même règle d'honnêteté)

Quel que soit le trou — facettes, poids, photos — la réponse est *dériver de vraies données, étiqueter l'estimation, ou
ne rien afficher*.

* **Photos :** un flux peut n'avoir aucune donnée image (colonne `Images` vide pour chaque ligne, aucune URL nulle part dans
  le fichier — vérifie avant de promettre). Alors : réutilise la photo du flux qui en a **uniquement** pour le
  même numéro de pièce normalisé (les lignes variantes comme `/EXP` ou `GIFT` sont le même objet physique — 242 sur
  38 k en pratique), remplace le reste par un placeholder *designé* (glyphe line-art inline-SVG par
  rayon + marque + numéro de pièce, ~20 glyphes couvrant 24 rayons) au lieu d'une boîte grise « pas de photo »,
  garde une ligne honnête sur la page produit (« le fabricant ne publie pas de photo — demandez-nous »), et dis au propriétaire
  ce qu'un vrai flux d'images exigerait. Ne scrape jamais un concurrent et n'emprunte jamais la photo d'une marque sans rapport.
* **Poids :** extrais-les des chaînes de propriétés du flux avant de revenir à une estimation (§6) ;
  une estimation qui entre dans le total du client doit être étiquetée comme telle.
* **Attributs/sous-catégories :** les règles dérivées du nom (§2/§3) valent mieux qu'un panneau de filtres vide — mais une valeur
  qui ne peut pas être rattachée au flux ou au nom du produit reste dehors.

## 8. Patterns de demandes propriétaire vus sur des catalogues revendeurs

* **« Tous les produits doivent être disponibles. »** Ne réécris pas les données du flux. Garde la vraie disponibilité en DB
  et ajoute un flag de config (`force_availability = 'in_stock'`) que la couche d'affichage, le JSON-LD
  (`InStock`), les compteurs de facettes et le filtre de disponibilité lisent tous — réversible en une ligne. Retire la
  facette de disponibilité devenue inutile, et adoucis toute phrase qui prétendait à un stock local
  (« Disponible sur commande — délai confirmé avec la commande »).
* **« Fais-en une page de commande, pas une demande de devis. »** Alors livre un vrai checkout : récapitulatif avec totaux,
  le prix de livraison, un bouton **Passer commande**, une référence de commande (`ERP-2026-00001` issue de la séquence de
  lignes) affichée dans la confirmation, et les totaux/poids recalculés côté serveur depuis le slug produit au
  POST. Garde le flux de demande/devis sur sa propre page — la préférence constante de cet utilisateur est qu'une nouvelle
  fonction obtienne **sa propre URL avec son propre SEO**, jamais une section boulonnée sur une page existante.
* **Champs requis conditionnels (entreprise vs particulier).** Étoile les champs toujours requis ; enveloppe
  ceux dépendant du type dans `[data-business-only]` et bascule à la fois `hidden` et `required` en JS — puis
  **revalide la même règle côté serveur**, car un input `required` caché n'est simplement pas soumis.
  Vide les données qui ne s'appliquent pas au type choisi avant de stocker.
* **Les prix doivent s'afficher avec et sans TVA, et le type choisit le mode.** Client particulier : marchandises,
  livraison et total **TTC**. Entreprise / revendeur : les mêmes trois lignes **HT** (les prix transporteur
  sont publiés TTC, donc livraison HT = brut / 1,2). Taux selon la destination : TVA locale en
  BG ; 0 % intracommunautaire dès qu'un numéro de TVA est fourni (VIES) ; le taux standard de la destination pour un acheteur
  particulier de l'UE ; 0 % export hors UE — plus une ligne indiquant que la facture est le document de référence.
  Garde le détail dans un encadré et un total compact en 3 lignes juste au-dessus du bouton de soumission.
* **Hygiène de copie — ce propriétaire élimine tout ce qui est orienté fournisseur de l'UI client.** Retirés sur demande
  au fil des sessions : la bannière du haut, la note sous les options de livraison, la paire de disclaimers en pied de page
  (« Les données produit sont mises à jour automatiquement depuis nos catalogues fournisseurs (dernier import …) » / « Les noms
  et marques de produits sont la propriété de leurs détenteurs respectifs… »), l'option « retrait / transporteur propre à nos locaux »,
  et la ligne de la page produit `Second supplier price: 111.17 € net`. Livre les prix, les libellés et les champs ;
  mets les explications sur les pages FAQ/statiques. Quand un prix/un champ quitte l'UI, supprime aussi la classe CSS
  désormais morte et la variable inutilisée, et garde la colonne DB (pour pouvoir la rétablir en une ligne). La marque
  transporteur côté client ici est **DPD** ; les commentaires de provenance vivent dans le code, jamais dans la page.
* **Les grands tableaux prix/facettes doivent survivre sur un téléphone.** Avec 10+ colonnes, passe en cartes empilées à
  `≤760px` : masque `thead`, `display: block` sur les lignes, `data-label` sur chaque cellule et
  `td::before { content: attr(data-label) }`. Vérifie avec le contrôle CDP (voir `scripts/`), pas à l'œil.
* **Jamais un prix, un poids ou un délai non sourcé.** Inconnu → « sur demande », confirmé par le
  propriétaire ; cet utilisateur rejette catégoriquement les chiffres inventés et vérifie le site en direct juste après la livraison.

## Pièges

* **Une colonne qui n'existe pas dans une constante `SELECT` partagée met le site en 500.** Cas réel :
  `p.weight_kg` alors que la colonne du schéma était `weight` — chaque page de listing renvoyait 500 jusqu'au correctif.
  Vérifie d'abord le `.schema`, alias dans la constante (`p.weight AS weight_kg`), et après avoir touché une
  constante/helper de requête partagée, repasse sur chaque type de route (`curl` par route, asserte 200 + aucun `Warning:`/`Fatal`).
* **PHP : deux littéraux de chaîne sur des lignes consécutives, c'est une erreur de parse.** Les longues chaînes FAQ/tableau ont besoin d'une
  concaténation `.` explicite ; `php -l` ne l'attrape que si tu lintes vraiment (`for f in $(find . -name
  '*.php'); do php -l $f; done`).
* **`[$a, $b] = $assocRow` donne silencieusement des `null`.** Déstructurer un tableau associatif produit des cellules de
  tableau vides / des lignes manquantes sans erreur. Utilise des clés nommées (`$row['service']`). Symptôme à retenir :
  les en-têtes du tableau s'affichent, les lignes du corps sont vides.
* Les attributs dérivés ne doivent pas écraser les propriétés fournies par le flux ; log combien de lignes tu as sautées.
* Les compteurs de facettes doivent être calculés avec le même constructeur de scope que le listing, et mis en cache sur `built_at`.
* N'ajoute pas un second point d'entrée pour les filtres « dérivés » — écris-les dans la table de propriétés existante.
* **Une édition scriptée « replace all » peut dupliquer une clé de tableau.** Insérer le même bloc dans deux fonctions
  PHP (`shipping_services()` et `shipping_rates()` commencent tous deux par `'cee202' => [`) a mis une définition de service
  là où un tableau de prix devait être ; PHP garde silencieusement la **dernière** clé, donc l'option s'affichait
  « sur demande » sans aucune erreur nulle part. Après avoir édité des tables de données avec `str.replace(..., -1)`, asserte la
  forme (`php -r 'print_r(array_keys(...))'`) et imprime en unité le devis d'un pays.
* **Vérifie les flux multi-étapes depuis un fichier script, pas depuis un long one-liner inline.** Les commandes chaînées
  complexes sont refusées par le guard du shell ; écris `verify_<area>.sh` / `<area>_flow_test.sh` à côté de l'outillage du
  site, lance-le avec `bash`, et garde les réutilisables dans les `scripts/` du skill.
* **Un cookie de session `Secure` fait paraître le test HTTP local cassé.** Derrière Cloudflare l'app voit
  `X-Forwarded-Proto: https`, donc PHP met le cookie de session en `Secure` ; un test `curl http://127.0.0.1:8080`
  ne le renvoie alors jamais, les tokens CSRF ne correspondent jamais et chaque action de compte renvoie `err=csrf`.
  Lance les tests de flux cookie/compte contre l'**origine HTTPS publique**, et garde le vhost local pour les
  balayages de pages anonymes. Détails : skill `customer-accounts-and-sessions`.
* **Un `onchange="this.form.submit()"` inline tue le comportement sans rechargement.** `form.submit()` ne déclenche aucun
  événement `submit`, donc un listener qui preventDefault le submit ne le voit jamais et la page se recharge quand même
  (symptôme : tri/par-page « fonctionnent » mais toute la page saute). Retire le handler inline, accroche l'événement `change`
  sur le select (`[data-sort]`) et ajoute un bouton submit `<noscript>` pour le cas JS désactivé.
* **Une vue de fragment JSON ne doit jamais être enveloppée dans le layout de page.** `render()` require la vue puis
  `views/layout.php` ; le fragment revenait donc comme un document HTML complet avec le JSON enfoui dedans
  (bon `Content-Type`, corps inparsable). La signature de chaque route reste la même — branche à l'intérieur du
  renderer : `if (str_starts_with($view, 'api_')) { echo $content; return; }`.
* **`PRAGMA query_only = ON` sur la connexion de lecture fait échouer toute écriture CLI.** Le `db()` de l'app est un
  handle lecture seule durci, donc un script de maintenance qui réutilise `qexec()` meurt avec
  `SQLSTATE[HY000]: General error: 8 attempt to write a readonly database` alors que le chemin web (qui ouvre
  son propre handle d'écriture) va bien. Donne au chemin d'écriture sa propre connexion (`db_open_rw()` derrière un
  helper `db_write()`) et route les updates admin/CLI par là.
* **Un helper de contexte partagé + `extract($arr, EXTR_SKIP)` laisse le `$CTX` de l'appelant périmé.** Le helper
  reçoit `$CTX` par valeur, enrichit sa propre copie (filters/result/facets) et la retourne ; `EXTR_SKIP` garde alors
  l'`$CTX` *original* déjà présent dans le scope de la vue, donc les partials tournent avec un
  `$CTX['filters']` indéfini (warnings, filtres vides, pas de produits). Assigne-le explicitement
  (`$CTX = $__L['CTX'] ?? $CTX;`) avant d'extraire, et `unset($__L['CTX'], $__L['PAGE'])` pour que le
  `$PAGE` par référence ne soit pas écrasé.
* **Ne mets jamais en cache l'élément formulaire/sidebar dans une variable JS.** `var form = document.querySelector('[data-filter-form]')`
  capturé au chargement pointe sur un **nœud détaché** dès que l'endpoint de fragment échange le markup : la
  première coche fonctionne, chaque coche suivante resoumet les *anciennes* valeurs et la page semble ignorer les clics
  (symptôme : « ajouter un second filtre ne fait rien, l'URL ne change jamais »). Cherche l'élément dans le
  handler à chaque fois — et si tu remplaces la sidebar, garde vivants les nœuds DOM des inputs cochés
  (voir §5a).
* **Un gros `str.replace()` qui mange une plage de lignes peut dupliquer un en-tête.** Réécrire une vue en découpant
  index→index a laissé l'ancien bloc de prépa de données au-dessus du nouveau ; ça parse toujours, mais la page affiche
  n'importe quoi. Après une chirurgie sur une vue, `php -l` **et** relis la région assemblée avant de continuer.

## Vérification

* `scripts/mobile-overflow-check.mjs` (aucune dépendance npm, CDP via le Chromium de Playwright) — mesure
  `scrollWidth` vs `clientWidth`, liste chaque élément dépassant le bord droit, et avec
  `--selector ".ship-table"` indique si un tableau large est passé en cartes empilées. Lance-le à
  360/390/414 px sur la catégorie, le produit, le panier/commande et toute page de tableau de prix.
* Diff les groupes de facettes par catégorie après avoir changé les règles (`grep` la sidebar rendue pour `fgroup-title`).
* Contrôle ponctuel que les 5 meilleures valeurs de facette d'une catégorie sont plausibles ; une valeur comme `1 inch` sur des
  racks 19 pouces ou `4 Gbit` sur des routeurs LTE signifie qu'une règle a besoin d'une borne ou d'un suffixe.
* Confirme l'aller-retour des chips : sélectionne deux marques + une valeur de spec, puis asserte que le nombre de résultats baisse et
  que les deux chips renvoient vers une URL qui retire exactement un filtre.
