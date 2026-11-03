# GSAP анимации в Astro — научено на живо

Работещ стек за "анимации при влизане" като daveholloway.uk върху Astro.

## Стек

```bash
npm install gsap lenis
```

| Библиотека | Роля |
|---|---|
| **GSAP** | timeline, ScrollTrigger, stagger |
| **Lenis** | smooth scroll (интегрира се с ScrollTrigger) |
| **CSS** | `prefers-reduced-motion` fallback |

## Точни стойности от daveholloway.uk

```
duration: .35 / .5 / .6 / .7 / .8 / 1
ease:     power3.inOut  (IO)  /  power3.out (CORE)
stagger:  .1
```

## Lenis + ScrollTrigger интеграция

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

CSS за Lenis (задължително, иначе двоен скрол):
```css
html.lenis, html.lenis body { height: auto; }
.lenis.lenis-smooth { scroll-behavior: auto !important; }
.lenis.lenis-stopped { overflow: hidden; }
```

## Loading sequence

Timeline ред:
```
01 барове:  scaleY 0→1, 0.6s, power3.out, stagger .1
02 брояч:   0→100, 1.2s, на "<0.15"
03 дума:    y 110%→0, 0.7s, на "<0.1"
04 пауза:   0.25s
05 дума:    y 0→-110%, 0.5s, power3.inOut
06 завеса:  scaleY 0→1, 0.6s, power3.inOut
07 clip:    inset(0 0 100% 0), 0.8s
08 header:  y -100%→0, 0.7s, на "-=0.45"
```

Показвай го **само при първо влизане** (`sessionStorage`), иначе дразни.

## КРИТИЧНО: reveal елементите не бива да остават скрити

**Проблемът:** `.reveal { opacity: 0 }` в CSS + GSAP, който не се е задействал = празна страница.

**Решението — двустепенно:**

1. CSS скрива **само** когато JS е доказано готов:
```css
.reveal { opacity: 1; transform: none; }
html.js-ready .reveal { opacity: 0; transform: translateY(30px); }
```

2. JS добавя `js-ready` и веднага показва всичко над 1.3× viewport:
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

## Header: видим по подразбиране

**Не** слагай `transform: translateY(-100%)` в базовия CSS — ако GSAP се провали, header-ът изчезва завинаги.

```css
.site-head { transform: translateY(0); }
body.is-loading .site-head { transform: translateY(-100%); }
```

И в JS, след като loader-ът свърши: `head.style.transform = "none"`.

## ScrollTrigger start стойности

| Стойност | Поведение |
|---|---|
| `top 88%` | стандартно, но оставя видима празнина |
| `top 94%` | по-рано, по-малко празни зони |
| `once: true` | анимацията не се повтаря при скрол назад |

За hero и първите секции → **не** ползвай ScrollTrigger, показвай ги директно.

## Pitfalls

1. **`window.innerHeight` в headless е малък** (633px при 1440×900) — не се доверявай на screenshot, за да съдиш за "празни зони". Провери с истински скрол.
2. **Playwright `full_page=True` НЕ скролва** — lazy/reveal елементите остават скрити. Скролвай ръчно на стъпки преди screenshot.
3. **`-webkit-text-stroke`** работи добре за назовани заглавия, но не и за тънки шрифтове.
4. **Alumni Sans на 256px** — line-height трябва да е ~0.8, иначе заглавието е огромно.
5. **`hreflang` за 36 езика** = 36 `<link>` тага; провери с `grep -c` на реален файл, не на един ред.

## Проверка

```bash
# след build — колко JS е генериран
ls -la dist/_astro/*.js

# проверка, че GSAP е в bundle-а
grep -c "power3" dist/_astro/*.js
```
