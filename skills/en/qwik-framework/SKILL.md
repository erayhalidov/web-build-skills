---
name: qwik-framework
description: Build/deploy Qwik + Qwik City apps.
---

# Qwik (Builder.io) — installation and usage

Official site: https://qwik.dev · Repo: https://github.com/QwikDev/qwik
Installed on this server in **`$HOME/qwik-app`**.

## ⚠️ CRITICAL: which package is the real one

| Package | Version | Status |
|---|---|---|
| **`@builder.io/qwik`** | **1.20.3** | ✅ **stable (v1) — use this for production** |
| `@builder.io/qwik-city` | 1.20.3 | ✅ meta-framework (routing, SSR, adapters) |
| **`@qwik.dev/core`** | **2.0.0-rc.4** | ⚠️ **v2 RC** — the new scope, not stable yet |
| `@qwik.dev/router` | 2.0.0-rc.4 | ⚠️ v2 router (RC) |
| ~~`qwik`~~ | 1.0.57 | ❌ **NOT Qwik** — an old unrelated package, do NOT install it |

Confirmation that v2 is official: `npm view @qwik.dev/core maintainers` → `mhevery` (Miško Hevery, the creator).

## What is installed here

```
$HOME/qwik-app/              # v1 — @builder.io/qwik@1.20.3 + qwik-city@1.20.3
$HOME/qwik-app/demo/         # working starter (empty template), built successfully
$HOME/qwik-app/v2/           # v2 RC — @qwik.dev/core@2.0.0-rc.4 (separate folder, because of a conflict)
```

## Starting a new project

```bash
cd $HOME/qwik-app
npx create-qwik@1.20.3 empty ./my-app      # templates: playground | empty | e2e-library | library
cd my-app
npm install
npm run build          # ⚠ NOT 'npx vite build' — the guard blocks it as a server
```

### Verified build results
```
✓ Type checked
✓ Lint checked
dist/build/q-*.js — ~50 kB / 20 kB gzip
```

## Running / previewing
```bash
npm run build.preview   # => server/entry.preview.js
# The preview SERVER must be background=true:
npx vite preview --port 4999 --host 127.0.0.1
# verification:
curl -s -o /tmp/q.html -w "%{http_code}" http://127.0.0.1:4999/
grep -oE 'q:container="[^"]*"|q:version="[^"]*"' /tmp/q.html
```
A successful Qwik response contains `q:container="paused"` (= resumability works) and `q:version`.

## Adapters (12 available)
```bash
cd my-app && npx qwik add      # interactive TUI — requires a real TTY
```
Available: Static site (.html), Node.js Server / Express / Fastify, Cloudflare Pages / Workers,
Netlify Edge, Vercel Edge, AWS Lambda, Azure SWA, Google Cloud Run, Bun, Deno, Firebase.

For a static site: select `Adapter: Static site` → the build outputs ready-made .html files.

## Integrations (28 available)
Auth.js · Bootstrap · Builder.io · compiled-i18n · Cypress · Drizzle · Leaflet Maps ·
Orama · PandaCSS · Partytown · Playwright · PostCSS · Prisma · Storybook ·
Styled-Vanilla-Extract · Tailwind v3/v4 · Turso · Vitest · Framework: React

⚠️ The user of this server **does not want Tailwind** — use custom CSS / PandaCSS / vanilla-extract.

## Project structure
```
src/
  components/       # .tsx components (component$)
  routes/           # file-based routing (Qwik City)
  root.tsx          # <QwikCityProvider> + <RouterOutlet>
  entry.ssr.tsx     # renderToStream
  entry.dev.tsx
  entry.preview.tsx
  global.css
vite.config.ts      # qwikCity() + qwikVite() + tsconfigPaths()
```

## Pitfalls
1. **`npx vite build` is blocked** by the guard (it looks like a server) → use `npm run build`.
2. **`npx qwik add` requires a TTY** — in a non-interactive shell it fails with `ERR_TTY_INIT_FAILED`.
   Use `terminal(pty=true, background=true)` + `process(action='write'|'submit')`,
   or edit `vite.config.ts` / `adapters/` by hand.
3. The Qwik packages must be in **`devDependencies`**, not in `dependencies` — otherwise
   `vite.config.ts` throws `Move qwik packages ... to devDependencies`.
4. v1 and v2 cannot coexist in one `node_modules` (ERESOLVE) → separate folders.
5. `npm run preview` opens a browser (`--open`) — on a server use `vite preview --host 127.0.0.1`.

## MCP servers for Qwik
**There is no public Qwik MCP server** (checked in the npm registry: `npm search qwik mcp` → 0 results).
The only related thing is `@builder.io/dev-tools` (Builder.io Visual CMS), which talks to
**Builder.io's own cloud MCP** and requires their account — it is not a Qwik dev tool.
For Qwik work use this skill + the official documentation at https://qwik.dev/docs/

## Useful commands
```bash
node -p "require('$HOME/qwik-app/node_modules/@builder.io/qwik/package.json').version"
cd $HOME/qwik-app/demo && npm run build          # build + types + lint
cd $HOME/qwik-app/demo && npm run lint
cd $HOME/qwik-app/demo && npm run fmt
```
