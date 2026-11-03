---
name: qwik-framework
description: Build/deploy Qwik + Qwik City apps.
---

# Qwik (Builder.io) — инсталация и работа

Официален сайт: https://qwik.dev · Репо: https://github.com/QwikDev/qwik
Инсталирано на този сървър в **`$HOME/qwik-app`**.

## ⚠️ КРИТИЧНО: кой пакет е истинският

| Пакет | Версия | Статус |
|---|---|---|
| **`@builder.io/qwik`** | **1.20.3** | ✅ **стабилна (v1) — ползвай това за продукция** |
| `@builder.io/qwik-city` | 1.20.3 | ✅ мета-фреймуърк (рутиране, SSR, адаптери) |
| **`@qwik.dev/core`** | **2.0.0-rc.4** | ⚠️ **v2 RC** — новият scope, още не е стабилен |
| `@qwik.dev/router` | 2.0.0-rc.4 | ⚠️ v2 рутер (RC) |
| ~~`qwik`~~ | 1.0.57 | ❌ **НЕ Е Qwik** — стар несвързан пакет, НЕ го инсталирай |

Проверка, че v2 е официален: `npm view @qwik.dev/core maintainers` → `mhevery` (Miško Hevery, създателят).

## Какво е инсталирано тук

```
$HOME/qwik-app/              # v1 — @builder.io/qwik@1.20.3 + qwik-city@1.20.3
$HOME/qwik-app/demo/         # работещ starter (empty template), билдван успешно
$HOME/qwik-app/v2/           # v2 RC — @qwik.dev/core@2.0.0-rc.4 (отделна папка, заради конфликт)
```

## Стартиране на нов проект

```bash
cd $HOME/qwik-app
npx create-qwik@1.20.3 empty ./my-app      # шаблони: playground | empty | e2e-library | library
cd my-app
npm install
npm run build          # ⚠ НЕ 'npx vite build' — guard-ът го блокира като сървър
```

### Проверени резултати от билда
```
✓ Type checked
✓ Lint checked
dist/build/q-*.js — ~50 kB / 20 kB gzip
```

## Стартиране / преглед
```bash
npm run build.preview   # => server/entry.preview.js
# preview СЪРВЪРЪТ трябва да е background=true:
npx vite preview --port 4999 --host 127.0.0.1
# проверка:
curl -s -o /tmp/q.html -w "%{http_code}" http://127.0.0.1:4999/
grep -oE 'q:container="[^"]*"|q:version="[^"]*"' /tmp/q.html
```
Успешен Qwik отговор съдържа `q:container="paused"` (= resumability работи) и `q:version`.

## Адаптери (12 налични)
```bash
cd my-app && npx qwik add      # интерактивно TUI — иска истински TTY
```
Налични: Static site (.html), Node.js Server / Express / Fastify, Cloudflare Pages / Workers,
Netlify Edge, Vercel Edge, AWS Lambda, Azure SWA, Google Cloud Run, Bun, Deno, Firebase.

За статичен сайт: избира се `Adapter: Static site` → билдът изкарва готови .html файлове.

## Интеграции (28 налични)
Auth.js · Bootstrap · Builder.io · compiled-i18n · Cypress · Drizzle · Leaflet Maps ·
Orama · PandaCSS · Partytown · Playwright · PostCSS · Prisma · Storybook ·
Styled-Vanilla-Extract · Tailwind v3/v4 · Turso · Vitest · Framework: React

⚠️ Потребителят на този сървър **не иска Tailwind** — ползвай custom CSS / PandaCSS / vanilla-extract.

## Структура на проекта
```
src/
  components/       # .tsx компоненти (component$)
  routes/           # файлово-базирано рутиране (Qwik City)
  root.tsx          # <QwikCityProvider> + <RouterOutlet>
  entry.ssr.tsx     # renderToStream
  entry.dev.tsx
  entry.preview.tsx
  global.css
vite.config.ts      # qwikCity() + qwikVite() + tsconfigPaths()
```

## Капани
1. **`npx vite build` се блокира** от guard-а (изглежда като сървър) → ползвай `npm run build`.
2. **`npx qwik add` иска TTY** — в неинтерактивен shell дава `ERR_TTY_INIT_FAILED`.
   Ползвай `terminal(pty=true, background=true)` + `process(action='write'|'submit')`,
   или редактирай `vite.config.ts` / `adapters/` ръчно.
3. Qwik пакетите трябва да са в **`devDependencies`**, не в `dependencies` — иначе
   `vite.config.ts` хвърля `Move qwik packages ... to devDependencies`.
4. v1 и v2 не могат в един `node_modules` (ERESOLVE) → отделни папки.
5. `npm run preview` отваря браузър (`--open`) — на сървър ползвай `vite preview --host 127.0.0.1`.

## MCP сървъри за Qwik
**Няма публичен Qwik MCP сървър** (проверено в npm registry: `npm search qwik mcp` → 0 резултата).
Единственото свързано е `@builder.io/dev-tools` (Builder.io Visual CMS), което говори със
**собствен облачен MCP** на Builder.io и иска техен акаунт — не е Qwik dev tool.
За работа с Qwik ползвай този скил + официалната документация на https://qwik.dev/docs/

## Полезни команди
```bash
node -p "require('$HOME/qwik-app/node_modules/@builder.io/qwik/package.json').version"
cd $HOME/qwik-app/demo && npm run build          # билд + типове + линт
cd $HOME/qwik-app/demo && npm run lint
cd $HOME/qwik-app/demo && npm run fmt
```
