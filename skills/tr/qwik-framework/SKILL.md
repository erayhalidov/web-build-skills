---
name: qwik-framework
description: Qwik + Qwik City uygulamaları kurun/yayınlayın.
---

# Qwik (Builder.io) — kurulum ve çalışma

Resmî site: https://qwik.dev · Depo: https://github.com/QwikDev/qwik
Bu sunucuda **`$HOME/qwik-app`** içine kuruldu.

## ⚠️ KRİTİK: hangi paket gerçek olan

| Paket | Sürüm | Durum |
|---|---|---|
| **`@builder.io/qwik`** | **1.20.3** | ✅ **kararlı (v1) — üretim için bunu kullan** |
| `@builder.io/qwik-city` | 1.20.3 | ✅ meta-çerçeve (yönlendirme, SSR, adaptörler) |
| **`@qwik.dev/core`** | **2.0.0-rc.4** | ⚠️ **v2 RC** — yeni kapsam, henüz kararlı değil |
| `@qwik.dev/router` | 2.0.0-rc.4 | ⚠️ v2 yönlendirici (RC) |
| ~~`qwik`~~ | 1.0.57 | ❌ **Qwik DEĞİL** — eski ilgisiz paket, KURMAYIN |

v2'nin resmî olduğunu doğrulama: `npm view @qwik.dev/core maintainers` → `mhevery` (Miško Hevery, yaratıcısı).

## Burada ne kurulu

```
$HOME/qwik-app/              # v1 — @builder.io/qwik@1.20.3 + qwik-city@1.20.3
$HOME/qwik-app/demo/         # çalışan starter (empty template), başarıyla derlendi
$HOME/qwik-app/v2/           # v2 RC — @qwik.dev/core@2.0.0-rc.4 (çakışma nedeniyle ayrı klasör)
```

## Yeni proje başlatma

```bash
cd $HOME/qwik-app
npx create-qwik@1.20.3 empty ./my-app      # şablonlar: playground | empty | e2e-library | library
cd my-app
npm install
npm run build          # ⚠ 'npx vite build' DEĞİL — guard onu sunucu sanıp engeller
```

### Doğrulanmış derleme sonuçları
```
✓ Type checked
✓ Lint checked
dist/build/q-*.js — ~50 kB / 20 kB gzip
```

## Başlatma / önizleme
```bash
npm run build.preview   # => server/entry.preview.js
# preview SUNUCUSU background=true olmalı:
npx vite preview --port 4999 --host 127.0.0.1
# kontrol:
curl -s -o /tmp/q.html -w "%{http_code}" http://127.0.0.1:4999/
grep -oE 'q:container="[^"]*"|q:version="[^"]*"' /tmp/q.html
```
Başarılı bir Qwik yanıtı `q:container="paused"` (= resumability çalışıyor) ve `q:version` içerir.

## Adaptörler (12 mevcut)
```bash
cd my-app && npx qwik add      # etkileşimli TUI — gerçek TTY ister
```
Mevcut: Static site (.html), Node.js Server / Express / Fastify, Cloudflare Pages / Workers,
Netlify Edge, Vercel Edge, AWS Lambda, Azure SWA, Google Cloud Run, Bun, Deno, Firebase.

Statik site için: `Adapter: Static site` seçilir → derleme hazır .html dosyaları üretir.

## Entegrasyonlar (28 mevcut)
Auth.js · Bootstrap · Builder.io · compiled-i18n · Cypress · Drizzle · Leaflet Maps ·
Orama · PandaCSS · Partytown · Playwright · PostCSS · Prisma · Storybook ·
Styled-Vanilla-Extract · Tailwind v3/v4 · Turso · Vitest · Framework: React

⚠️ Bu sunucunun kullanıcısı **Tailwind istemiyor** — custom CSS / PandaCSS / vanilla-extract kullanın.

## Proje yapısı
```
src/
  components/       # .tsx bileşenleri (component$)
  routes/           # dosya tabanlı yönlendirme (Qwik City)
  root.tsx          # <QwikCityProvider> + <RouterOutlet>
  entry.ssr.tsx     # renderToStream
  entry.dev.tsx
  entry.preview.tsx
  global.css
vite.config.ts      # qwikCity() + qwikVite() + tsconfigPaths()
```

## Tuzaklar
1. **`npx vite build`** guard tarafından **engellenir** (sunucu gibi görünür) → `npm run build` kullanın.
2. **`npx qwik add` TTY ister** — etkileşimsiz shell'de `ERR_TTY_INIT_FAILED` verir.
   `terminal(pty=true, background=true)` + `process(action='write'|'submit')` kullanın,
   ya da `vite.config.ts` / `adapters/` dosyalarını elle düzenleyin.
3. Qwik paketleri **`devDependencies`** içinde olmalı, `dependencies` içinde değil — yoksa
   `vite.config.ts` `Move qwik packages ... to devDependencies` hatası fırlatır.
4. v1 ve v2 tek bir `node_modules` içinde olamaz (ERESOLVE) → ayrı klasörler.
5. `npm run preview` tarayıcı açar (`--open`) — sunucuda `vite preview --host 127.0.0.1` kullanın.

## Qwik için MCP sunucuları
**Genel bir Qwik MCP sunucusu YOK** (npm registry'de kontrol edildi: `npm search qwik mcp` → 0 sonuç).
İlgili tek şey `@builder.io/dev-tools` (Builder.io Visual CMS) ki bu Builder.io'nun
**kendi bulut MCP'siyle** konuşur ve onların hesabını ister — Qwik dev aracı değildir.
Qwik ile çalışmak için bu beceriyi + https://qwik.dev/docs/ resmî belgelerini kullanın

## Faydalı komutlar
```bash
node -p "require('$HOME/qwik-app/node_modules/@builder.io/qwik/package.json').version"
cd $HOME/qwik-app/demo && npm run build          # derleme + tipler + lint
cd $HOME/qwik-app/demo && npm run lint
cd $HOME/qwik-app/demo && npm run fmt
```
