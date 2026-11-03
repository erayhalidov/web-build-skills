# Animations GSAP dans Astro — appris en production

Stack qui fonctionne pour des « animations à l'entrée » comme sur daveholloway.uk, sur Astro.

## Stack

```bash
npm install gsap lenis
```

| Bibliothèque | Rôle |
|---|---|
| **GSAP** | timeline, ScrollTrigger, stagger |
| **Lenis** | smooth scroll (s'intègre à ScrollTrigger) |
| **CSS** | fallback `prefers-reduced-motion` |

## Valeurs exactes de daveholloway.uk

```
duration: .35 / .5 / .6 / .7 / .8 / 1
ease:     power3.inOut  (IO)  /  power3.out (CORE)
stagger:  .1
```

## Intégration Lenis + ScrollTrigger

```ts
import Lenis from "lenis";
import { ScrollTrigger } from "gsap/ScrollTrigger";

const lenis = new Lenis({
  duration: 1.1,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  smoothWheel: true,
});
lenis.on("scroll", ScrollTrigger.update);
gsap.ticker.add((time) => lenis.raf(time * 1000));
gsap.ticker.lagSmoothing(0);
```

CSS pour Lenis (obligatoire, sinon double scroll) :
```css
html.lenis, html.lenis body { height: auto; }
.lenis.lenis-smooth { scroll-behavior: auto !important; }
.lenis.lenis-stopped { overflow: hidden; }
```

## Loading sequence

Ordre de la timeline :
```
01 barres : scaleY 0→1, 0.6s, power3.out, stagger .1
02 compteur: 0→100, 1.2s, à "<0.15"
03 mot :    y 110%→0, 0.7s, à "<0.1"
04 pause :  0.25s
05 mot :    y 0→-110%, 0.5s, power3.inOut
06 rideau : scaleY 0→1, 0.6s, power3.inOut
07 clip :   inset(0 0 100% 0), 0.8s
08 header : y -100%→0, 0.7s, à "-=0.45"
```

Ne l'affiche que **lors de la première visite** (`sessionStorage`), sinon c'est agaçant.

## CRITIQUE : les éléments reveal ne doivent pas rester cachés

**Le problème :** `.reveal { opacity: 0 }` en CSS + un GSAP qui ne s'est pas déclenché = page blanche.

**La solution — en deux temps :**

1. Le CSS ne masque **que** quand le JS est prouvé prêt :
```css
.reveal { opacity: 1; transform: none; }
html.js-ready .reveal { opacity: 0; transform: translateY(30px); }
```

2. Le JS ajoute `js-ready` et affiche immédiatement tout ce qui dépasse 1,3× le viewport :
```ts
document.documentElement.classList.add("js-ready");

requestAnimationFrame(() => {
  const vh = window.innerHeight;
  document.querySelectorAll(".reveal, .split-line > span").forEach((el) => {
    const r = el.getBoundingClientRect();
    if (r.top < vh * 1.3 && r.bottom > -vh * 0.3) {
      el.style.opacity = "1";
      el.style.transform = "none";
    }
  });
});
```

## Header : visible par défaut

**Ne** mets **pas** `transform: translateY(-100%)` dans le CSS de base — si GSAP échoue, le header disparaît pour toujours.

```css
.site-head { transform: translateY(0); }
body.is-loading .site-head { transform: translateY(-100%); }
```

Et en JS, une fois le loader terminé : `head.style.transform = "none"`.

## Valeurs de start ScrollTrigger

| Valeur | Comportement |
|---|---|
| `top 88%` | standard, mais laisse un vide visible |
| `top 94%` | plus tôt, moins de zones vides |
| `once: true` | l'animation ne se répète pas au scroll arrière |

Pour le hero et les premières sections → **n'utilise pas** ScrollTrigger, affiche-les directement.

## Pièges

1. **`window.innerHeight` en headless est petit** (633px pour 1440×900) — ne te fie pas au screenshot pour juger des « zones vides ». Vérifie avec un vrai scroll.
2. **Playwright `full_page=True` NE scrolle PAS** — les éléments lazy/reveal restent cachés. Scrolle manuellement par étapes avant le screenshot.
3. **`-webkit-text-stroke`** fonctionne bien pour les titres épais, mais pas pour les polices fines.
4. **Alumni Sans à 256px** — le line-height doit être ~0.8, sinon le titre est énorme.
5. **`hreflang` pour 36 langues** = 36 balises `<link>` ; vérifie avec `grep -c` sur un vrai fichier, pas sur une seule ligne.

## Vérification

```bash
# après le build — combien de JS est généré
ls -la dist/_astro/*.js

# vérifie que GSAP est dans le bundle
grep -c "power3" dist/_astro/*.js
```
