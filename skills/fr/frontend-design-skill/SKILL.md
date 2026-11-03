---
name: frontend-design-skill
description: "Concevoir ou revoir le layout frontend et le CSS."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [frontend, design, css, layout, typography, color, motion, accessibility]
    related_skills: [design-extraction-and-fidelity, ui-ux-pro-max, tailwind-v4, responsive-mobile-qa]
---

# Frontend design skill

À utiliser pour toute tâche dont le livrable est un **écran qu'un humain regarde** : landing pages, dashboards,
formulaires, cartes, navigation. Cet utilisateur ne veut que du **CSS custom — Tailwind est refusé 2×** ; n'y
recours jamais. Le design se mesure, ne se devine pas : voir `design-extraction-and-fidelity` pour l'extraction des tokens.

## Non négociables pour cet utilisateur

- **CSS custom avec variables.** Pas de Tailwind, pas de Bootstrap, pas de défauts de bibliothèque de composants.
- **2 à 3 variantes de démo avant toute mise en ligne.** Les démos vivent dans des fichiers `.html` séparés, jamais sur le
  domaine en production.
- **Préserver la logique PHP et l'i18n existantes** pendant toute modification d'UI. Un redesign qui casse un form post
  ou une clé de traduction est une régression, pas un redesign.
- **Pas de `display:none` / `overflow:hidden` pour masquer un bug de layout.** Corrige le layout.
- **« seulement mobile » signifie ne pas toucher au desktop.**
- **Sites publics : EN par défaut + sélecteur BG.**
- Les sections sont des **cartes séparées**, pas une longue colonne indifférenciée.
- Les boutons ont besoin d'un **fort contraste** — jamais un ghost peu contrasté sur une surface sombre.

## Layout

1. **Décide la grille avant les pixels.** La colonne de contenu, les gouttières et le rythme des sections
   (`padding` par section) viennent d'abord. La plupart des « ça rend mal » sont un mauvais rythme, pas une mauvaise couleur.
2. **Le rythme vertical est une échelle, pas des valeurs ad-hoc par section.** Choisis une base (4 ou 8 px) et
   réutilise-la. Mesure la référence avec `sectune.py` (voir le skill de fidélité) plutôt qu'à l'œil.
3. **Chaque cellule de grille a besoin d'un min-height explicite** si elle contient une cellule placeholder/lead, sinon la
   première ligne s'affiche plus haute que les autres.
4. **Les chips/badges inline utilisent `width: fit-content`.** Un chip `display:block` dans une cellule de grille s'étire
   sur toute la largeur et transforme les tableaux en murs de couleur.
5. **Les sections full-bleed dans un wrapper max-width** ont besoin de
   `width:100vw; margin-left:calc(50% - 50vw)` — et vérifie ensuite `html{overflow-x:hidden}`, sinon tu
   introduis un scroll horizontal.

## Typographie

- Corps 16 px / line-height 24 px comme plancher par défaut.
- **Échelle nommée** (h1/h2/body/body-sm avec taille + graisse + line-height), pas de tailles de police ad-hoc.
- Le tracking se resserre quand la taille augmente : `letter-spacing:-0.5px` à 64 px, `+0.5px` sur les petites capitales.
- Les titres display ont leur propre famille si la marque en a une ; le corps reste sur la sans.

## Couleur

- **Tokens sémantiques uniquement** : `--bg`, `--bg-raised`, `--fg`, `--muted`, `--primary`, `--accent`.
  Les composants ne référencent jamais de hex brut.
- Vérifie le contraste avec de vrais chiffres — `#fafafa` sur `#0f0914` fait 18,81:1 (AAA) ; un accent pastel sur une
  surface sombre est souvent le couple qui échoue.
- Les surfaces sombres ont besoin de **variantes surélevées** (`--bg-raised`), sinon les cartes disparaissent dans la page.

## Motion

- Durées issues d'une échelle : 120/180/250/350 ms. Jamais `transition: all 0.3s ease`.
- Animer uniquement `transform` et `opacity`.
- **Respecte `prefers-reduced-motion`** — et note que toute comparaison de screenshots doit désactiver
  les animations, sinon deux passes de la même page diffèrent.

## Accessibilité

- Chaque élément interactif est un vrai `<a>` ou `<button>` ; les icônes reçoivent `aria-label`.
- Accordéons basés sur `summary` plutôt que sur des handlers JS sur des divs.
- Jamais `outline:none` sans anneau de focus visible en remplacement.

## Vérification avant de montrer à l'utilisateur

1. Screenshot à 390 / 834 / 1440 px.
2. Vérifie `document.documentElement.scrollWidth > clientWidth` à chaque largeur — le scroll horizontal est le
   bug qui ruine silencieusement le mobile.
3. Lance `pixdiff.py` contre la référence s'il y en a une, et cite le nombre.
4. Ne dis jamais « c’est fait » sans un résultat mesuré.
