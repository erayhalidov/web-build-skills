# Animaciones GSAP en Astro — aprendido en producción

Stack que funciona para "animaciones de entrada" como daveholloway.uk sobre Astro.

## Stack

```bash
npm install gsap lenis
```

| Librería | Rol |
|---|---|
| **GSAP** | timeline, ScrollTrigger, stagger |
| **Lenis** | smooth scroll (se integra con ScrollTrigger) |
| **CSS** | fallback `prefers-reduced-motion` |

## Valores exactos de daveholloway.uk

```
duration: .35 / .5 / .6 / .7 / .8 / 1
ease:     power3.inOut  (IO)  /  power3.out (CORE)
stagger:  .1
```

## Integración Lenis + ScrollTrigger

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

CSS para Lenis (obligatorio, si no hay doble scroll):
```css
html.lenis, html.lenis body { height: auto; }
.lenis.lenis-smooth { scroll-behavior: auto !important; }
.lenis.lenis-stopped { overflow: hidden; }
```

## Loading sequence

Orden de la línea de tiempo:
```
01 barras:    scaleY 0→1, 0.6s, power3.out, stagger .1
02 contador:  0→100, 1.2s, en "<0.15"
03 palabra:   y 110%→0, 0.7s, en "<0.1"
04 pausa:     0.25s
05 palabra:   y 0→-110%, 0.5s, power3.inOut
06 cortina:   scaleY 0→1, 0.6s, power3.inOut
07 clip:      inset(0 0 100% 0), 0.8s
08 header:    y -100%→0, 0.7s, en "-=0.45"
```

Muéstralo **solo en la primera entrada** (`sessionStorage`), si no cansa.

## CRÍTICO: los elementos reveal no deben quedarse ocultos

**El problema:** `.reveal { opacity: 0 }` en CSS + GSAP que no se ha ejecutado = página en blanco.

**La solución — en dos fases:**

1. El CSS oculta **solo** cuando el JS está demostradamente listo:
```css
.reveal { opacity: 1; transform: none; }
html.js-ready .reveal { opacity: 0; transform: translateY(30px); }
```

2. El JS añade `js-ready` y muestra de inmediato todo lo que supere 1.3× el viewport:
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

## Header: visible por defecto

**No** pongas `transform: translateY(-100%)` en el CSS base — si GSAP falla, el header desaparece para siempre.

```css
.site-head { transform: translateY(0); }
body.is-loading .site-head { transform: translateY(-100%); }
```

Y en JS, cuando el loader termina: `head.style.transform = "none"`.

## Valores de start de ScrollTrigger

| Valor | Comportamiento |
|---|---|
| `top 88%` | estándar, pero deja visible un hueco |
| `top 94%` | antes, menos zonas vacías |
| `once: true` | la animación no se repite al hacer scroll hacia atrás |

Para el hero y las primeras secciones → **no** uses ScrollTrigger, muéstralas directamente.

## Pitfalls

1. **`window.innerHeight` en headless es pequeño** (633px con 1440×900) — no te fíes del screenshot para juzgar "zonas vacías". Compruébalo con scroll real.
2. **Playwright `full_page=True` NO hace scroll** — los elementos lazy/reveal se quedan ocultos. Haz scroll manual por pasos antes del screenshot.
3. **`-webkit-text-stroke`** funciona bien para títulos grandes, pero no para fuentes finas.
4. **Alumni Sans a 256px** — el line-height debe ser ~0.8, si no el título es enorme.
5. **`hreflang` para 36 idiomas** = 36 etiquetas `<link>`; compruébalo con `grep -c` sobre un archivo real, no sobre una sola línea.

## Verificación

```bash
# tras el build — cuánto JS se ha generado
ls -la dist/_astro/*.js

# comprobar que GSAP está en el bundle
grep -c "power3" dist/_astro/*.js
```
