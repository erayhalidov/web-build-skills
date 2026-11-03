# GSAP animations in Astro — learned in production

A working stack for "entrance animations" like daveholloway.uk on top of Astro.

## Stack

```bash
npm install gsap lenis
```

| Library | Role |
|---|---|
| **GSAP** | timeline, ScrollTrigger, stagger |
| **Lenis** | smooth scroll (integrates with ScrollTrigger) |
| **CSS** | `prefers-reduced-motion` fallback |

## Exact values from daveholloway.uk

```
duration: .35 / .5 / .6 / .7 / .8 / 1
ease:     power3.inOut  (IO)  /  power3.out (CORE)
stagger:  .1
```

## Lenis + ScrollTrigger integration

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

CSS for Lenis (mandatory, otherwise you get double scroll):
```css
html.lenis, html.lenis body { height: auto; }
.lenis.lenis-smooth { scroll-behavior: auto !important; }
.lenis.lenis-stopped { overflow: hidden; }
```

## Loading sequence

Timeline order:
```
01 bars:     scaleY 0→1, 0.6s, power3.out, stagger .1
02 counter:  0→100, 1.2s, at "<0.15"
03 word:     y 110%→0, 0.7s, at "<0.1"
04 pause:    0.25s
05 word:     y 0→-110%, 0.5s, power3.inOut
06 curtain:  scaleY 0→1, 0.6s, power3.inOut
07 clip:     inset(0 0 100% 0), 0.8s
08 header:   y -100%→0, 0.7s, at "-=0.45"
```

Show it **only on the first visit** (`sessionStorage`), otherwise it gets annoying.

## CRITICAL: reveal elements must not stay hidden

**The problem:** `.reveal { opacity: 0 }` in CSS + GSAP that never fired = a blank page.

**The solution — two-stage:**

1. CSS hides **only** when JS is proven ready:
```css
.reveal { opacity: 1; transform: none; }
html.js-ready .reveal { opacity: 0; transform: translateY(30px); }
```

2. JS adds `js-ready` and immediately shows everything above 1.3× viewport:
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

## Header: visible by default

Do **not** put `transform: translateY(-100%)` in the base CSS — if GSAP fails, the header disappears forever.

```css
.site-head { transform: translateY(0); }
body.is-loading .site-head { transform: translateY(-100%); }
```

And in JS, once the loader finishes: `head.style.transform = "none"`.

## ScrollTrigger start values

| Value | Behaviour |
|---|---|
| `top 88%` | standard, but leaves a visible gap |
| `top 94%` | earlier, fewer empty zones |
| `once: true` | the animation does not repeat when scrolling back |

For the hero and the first sections → do **not** use ScrollTrigger, show them directly.

## Pitfalls

1. **`window.innerHeight` is small in headless** (633px at 1440×900) — do not trust a screenshot to judge "empty zones". Check with real scrolling.
2. **Playwright `full_page=True` does NOT scroll** — lazy/reveal elements stay hidden. Scroll manually in steps before screenshotting.
3. **`-webkit-text-stroke`** works well for outline headings, but not for thin fonts.
4. **Alumni Sans at 256px** — line-height must be ~0.8, otherwise the heading is enormous.
5. **`hreflang` for 36 languages** = 36 `<link>` tags; verify with `grep -c` on the real file, not on one line.

## Verification

```bash
# after build — how much JS was generated
ls -la dist/_astro/*.js

# verify that GSAP is in the bundle
grep -c "power3" dist/_astro/*.js
```
