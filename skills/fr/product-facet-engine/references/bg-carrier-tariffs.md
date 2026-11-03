# Tarifs des transporteurs bulgares (Speedy / DPD) — tarifs publiés pour les boutiques à catalogue

Banque de connaissances pour les demandes « ajoute de vrais prix de livraison pour chaque pays européen ». Chaque chiffre ici vient
de la grille tarifaire publiée du transporteur — n'extrapole jamais vers une destination non listée.

## Faits de découverte (pour gagner une heure la prochaine fois)

| Fait | Détail |
| --- | --- |
| `www.dpd.bg` | Redirige vers les pages internationales de **Speedy** — Speedy exploite le réseau DPD en Bulgarie, donc « Speedy - DPD » est une seule offre, pas deux devis. |
| `https://www.dpd.bg` (443) | Connexion refusée depuis le serveur. Le simple `http://www.dpd.bg/` répond 200 et émet la redirection vers speedy.bg. |
| `https://www.speedy.bg/...` | Challenge JS Cloudflare « Just a moment… » — un simple fetch récupère la page de challenge, et un Chromium headless s'y bloque aussi. |
| `https://services.speedy.bg/priceList/?lang=en` | **La vraie grille tarifaire.** 200 au curl simple avec un UA navigateur normal, pas de challenge. Le `<title>` porte la date de version (`Speedy Price List 13.09.2026`) — cite cette date aux clients. |

```bash
curl -sSL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36" \
  -o /tmp/sp_pl.html "https://services.speedy.bg/priceList/?lang=en"
```

Parser la page (~200 Ko de tableaux inline) :
```python
import re, html as H
s = open('/tmp/sp_pl.html', encoding='utf-8', errors='replace').read()
flat = H.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '|', s))).replace('\xa0', ' ')  # les prix utilisent &nbsp;
flat = re.sub(r'\|+', '|', flat)
```
* Le `\xa0` entre le montant et le signe € casse toutes les regex de prix — normalise-le d'abord.
* La ligne d'en-tête vit souvent dans son propre `<table>` alors que les lignes de pays sont en dehors, donc découper
  entre les frontières `<table>…</table>` perd le corps. Découpe plutôt le **texte aplati** entre le titre du service
  et le paragraphe de boilerplate qui suit.
* Les noms de pays peuvent porter des parenthèses (`CROATIA (LOCAL NAME: HRVATSKA)`) — matche
  `[A-Z][A-Z \.\-\(\)']{3,60}` et tu les perdras quand même ; vérifie le nombre de lignes contre la liste des zones.

## Services au départ de Bulgarie

| Code | Service | Tranches de poids | Notes |
| --- | --- | --- | --- |
| 202 | Speedy CEE Economy | 1, 2, 3, 4, 5, 7, 10, 20, 31.5 kg | RO/GR dernière tranche `21.72 € + 1.09 € par kg supplémentaire`. |
| 306 | DPD Economy — porte à porte | 0.5, 5, 10, 31.5, 40 kg | Service routier Europe de l'Ouest / du Nord. |
| 308 | DPD Economy **Collection request** | 0.5, 5, 10, 31.5, 40 kg | Enlèvements entrants **vers** la Bulgarie — ne cite jamais ça pour des commandes sortantes. |
| 302 | Speedy Air Express | pas de 0.5 kg, 20 tranches jusqu'à 10 kg | Zone 1 (UE hors réseau routier), Zone 2 (Europe non-UE), 3/4 (monde). Au-dessus de 10 kg → sur demande. |

Tous les montants publiés **incluent déjà la TVA et la surcharge carburant**.

## Correspondance pays → service

* **202 CEE Economy** — RO, GR, HU, CZ, PL, SK, SI, HR, CY
* **306 DPD Economy** — AT, DE, BE, FR, IT, NL, DK, LU, ES, EE, FI, LV, LT, PT, SE
* **302 Air Zone 1** — IE, MT (la liste zone 1 mentionne aussi AT, BE, HR, CY, CZ, DK, EE, FI, FR, DE, GR, HU, IE, IT, LV, LT, LU, MT, NL, PL, PT, SK, SI, ES, SE)
* **302 Air Zone 2** — AL, AD, BA, FO, GI, GL, VA, IS, LI, MC, ME, NO, SM, RS, CH, TR, GB, GG, JE, Canaries
* **Non listé nulle part** (UA, US, …) → « prix sur demande ». N'interpole pas.

Délais de transit tels qu'imprimés : DE/AT/CZ/PL 3-4 · HU/SK 2-3 · SI 3-4 · HR/BE/FR/IT/NL/DK/LU/LV/LT 4-5 · ES 5-6 ·
SE 5-6 · EE 5-6 · FI/PT 5-7 · Air Zone 1 1-2 · Air Zone 2 1-3. RO/GR/CY ne sont **pas** imprimés — omets la
colonne plutôt que de deviner.

## Matrice de prix (version 13.09.2026)

202 CEE Economy, tranches 1 → 31.5 kg :
```
RO        5.27  5.71  6.13 10.96 10.96 13.63 16.76 21.72 21.72 (+1.09 €/kg au-delà de 31.5)
GR        6.44  7.36  7.36 10.96 10.96 13.63 16.76 21.72 21.72 (+1.09 €/kg au-delà de 31.5)
HU        8.84  9.70 10.57 23.17 23.17 27.68 27.68 27.68 27.68
CZ        8.84  9.70 10.57 32.21 32.21 38.22 38.22 38.22 38.22
PL/SK/SI/HR 8.84 9.70 10.57 45.76 45.76 51.04 51.04 53.14 53.14
CY       17.03 19.21 21.36 23.72 25.87   —     —     —     —   (seulement jusqu'à 5 kg)
```

306 DPD Economy, tranches 0.5 / 5 / 10 / 31.5 / 40 kg :
```
AT, DE                     23.78 23.78 28.32 28.32  65.14
BE, FR, IT, NL             32.82 32.82 38.83 38.83  75.67
DK, LU                     44.26 46.38 51.64 53.77  90.58
ES                         42.59 42.59 50.11 50.11  86.94
EE, FI, LV, LT, PT, SE     63.28 65.38 71.71 74.89 111.72
```

302 Air Express : zone 1 à partir de 68.41 € (≤0.5 kg) en montant de ~10-15 € par pas de 0.5 kg ; zone 2 à partir de 84.08 €.
Transcris les 20 lignes publiées plutôt que d'approximer.

Surcharges qui existent (à mentionner dans la FAQ, à ne pas ajouter silencieusement à un devis) : code postal île/éloigné
28.06 € (202) / 26.54 € (308) TTC · colis lourd >50 kg 12.77 € · manutention manuelle si un côté >100 cm
1.94 € · COD 2.4 % (min 1.23 € international). Promo en vigueur au dernier contrôle : **-25 % sur les prix du tarif
306 pour DE et IT, 01.09.2024 – 30.09.2026**.

## Le brancher dans le site

`inc/shipping.php` :
* `shipping_services()` — libellé, transporteur, liste des tranches, note par clé de service
* `shipping_rates()` — service → groupe de destination → prix par tranche (tableaux dans le même ordre que les tranches)
* `shipping_map()` — ISO2 → `['service' =>, 'group' =>, 'days' =>]`
* `shipping_quote($cc, $kg)` — première tranche dans laquelle le poids rentre ; **`price = null` au-delà des tranches
  publiées** pour que l'UI puisse dire « sur demande » au lieu de deviner
* `shipping_pickup()` (gratuit, 0.00) et `shipping_options()`
* `shipping_updated()` — la chaîne de version affichée aux clients

Le poids vient du catalogue (`products.weight` ; alias-le `AS weight_kg` dans les SELECT partagés), sommé
sur la quantité. Les articles sans poids contribuent une estimation documentée de 0.5 kg et la page dit que le
poids est partiellement estimé. Recalcule tout **côté serveur au POST** depuis le slug produit — le panier
navigateur n'est pas de confiance pour les prix ni les poids.

Rendu : un tableau de prix sur la page livraison (`Delivery prices to every European country`) construit à partir
des mêmes tableaux, pour qu'il ne puisse jamais diverger du checkout. Les tarifs changent → remplace les trois tableaux, bumpe
`shipping_updated()`, relance le balayage des routes.
