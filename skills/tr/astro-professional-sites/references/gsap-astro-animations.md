# Astro'da GSAP animasyonları — canlıda öğrenilenler

daveholloway.uk tarzı "giriş animasyonları" için Astro üzerinde çalışan stack.

## Stack

```bash
npm install gsap lenis
```

| Kütüphane | Rol |
|---|---|
| **GSAP** | timeline, ScrollTrigger, stagger |
| **Lenis** | smooth scroll (ScrollTrigger ile bütünleşir) |
| **CSS** | `prefers-reduced-motion` yedeği |

## daveholloway.uk'den kesin değerler

```
duration: .35 / .5 / .6 / .7 / .8 / 1
ease:     power3.inOut  (IO)  /  power3.out (CORE)
stagger:  .1
```

## Lenis + ScrollTrigger entegrasyonu

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

Lenis için CSS (zorunlu, yoksa çift kaydırma):
```css
html.lenis, html.lenis body { height: auto; }
.lenis.lenis-smooth { scroll-behavior: auto !important; }
.lenis.lenis-stopped { overflow: hidden; }
```

## Yükleme sırası

Timeline sırası:
```
01 çubuklar: scaleY 0→1, 0.6s, power3.out, stagger .1
02 sayaç:    0→100, 1.2s, "<0.15" konumunda
03 kelime:   y 110%→0, 0.7s, "<0.1" konumunda
04 duraklama: 0.25s
05 kelime:   y 0→-110%, 0.5s, power3.inOut
06 perde:    scaleY 0→1, 0.6s, power3.inOut
07 clip:     inset(0 0 100% 0), 0.8s
08 header:   y -100%→0, 0.7s, "-=0.45" konumunda
```

Bunu **yalnızca ilk girişte** göster (`sessionStorage`), yoksa sinir bozar.

## KRİTİK: reveal öğeleri gizli kalmamalı

**Sorun:** CSS'te `.reveal { opacity: 0 }` + tetiklenmemiş GSAP = boş sayfa.

**Çözüm — iki aşamalı:**

1. CSS **yalnızca** JS'in hazır olduğu kanıtlandığında gizler:
```css
.reveal { opacity: 1; transform: none; }
html.js-ready .reveal { opacity: 0; transform: translateY(30px); }
```

2. JS `js-ready` ekler ve viewport'un 1.3× üzerindeki her şeyi hemen gösterir:
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

## Header: varsayılan olarak görünür

Temel CSS'e `transform: translateY(-100%)` **koymayın** — GSAP başarısız olursa header sonsuza dek kaybolur.

```css
.site-head { transform: translateY(0); }
body.is-loading .site-head { transform: translateY(-100%); }
```

JS'te, loader bittikten sonra: `head.style.transform = "none"`.

## ScrollTrigger start değerleri

| Değer | Davranış |
|---|---|
| `top 88%` | standart, ama görünür bir boşluk bırakır |
| `top 94%` | daha erken, daha az boş alan |
| `once: true` | animasyon geri kaydırırken tekrarlanmaz |

Hero ve ilk bölümler için → ScrollTrigger **kullanmayın**, doğrudan gösterin.

## Tuzaklar

1. **Headless'ta `window.innerHeight` küçüktür** (1440×900'de 633px) — "boş alanları" değerlendirmek için screenshot'a güvenmeyin. Gerçek kaydırma ile kontrol edin.
2. **Playwright `full_page=True` kaydırmaz** — lazy/reveal öğeleri gizli kalır. Screenshot'tan önce elle adım adım kaydırın.
3. **`-webkit-text-stroke`** büyük başlıklar için iyi çalışır, ince fontlarda çalışmaz.
4. **256px'te Alumni Sans** — line-height ~0.8 olmalı, yoksa başlık devasa olur.
5. **36 dil için `hreflang`** = 36 `<link>` etiketi; tek satırda değil gerçek dosyada `grep -c` ile kontrol edin.

## Kontrol

```bash
# build sonrası — ne kadar JS üretildi
ls -la dist/_astro/*.js

# GSAP'ın bundle içinde olduğunu doğrulama
grep -c "power3" dist/_astro/*.js
```
