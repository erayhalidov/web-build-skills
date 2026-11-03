---
name: qwik-framework
description: Crea y despliega apps Qwik + Qwik City.
---

# Qwik (Builder.io) — instalación y trabajo

Sitio oficial: https://qwik.dev · Repo: https://github.com/QwikDev/qwik
Instalado en este servidor en **`$HOME/qwik-app`**.

## ⚠️ CRÍTICO: qué paquete es el de verdad

| Paquete | Versión | Estado |
|---|---|---|
| **`@builder.io/qwik`** | **1.20.3** | ✅ **estable (v1) — usa esto para producción** |
| `@builder.io/qwik-city` | 1.20.3 | ✅ meta-framework (rutas, SSR, adaptadores) |
| **`@qwik.dev/core`** | **2.0.0-rc.4** | ⚠️ **v2 RC** — el nuevo scope, aún no es estable |
| `@qwik.dev/router` | 2.0.0-rc.4 | ⚠️ router v2 (RC) |
| ~~`qwik`~~ | 1.0.57 | ❌ **NO ES Qwik** — paquete antiguo sin relación, NO lo instales |

Comprobación de que v2 es oficial: `npm view @qwik.dev/core maintainers` → `mhevery` (Miško Hevery, el creador).

## Qué hay instalado aquí

```
$HOME/qwik-app/              # v1 — @builder.io/qwik@1.20.3 + qwik-city@1.20.3
$HOME/qwik-app/demo/         # starter funcionando (plantilla empty), compilado con éxito
$HOME/qwik-app/v2/           # v2 RC — @qwik.dev/core@2.0.0-rc.4 (carpeta aparte, por conflicto)
```

## Arrancar un proyecto nuevo

```bash
cd $HOME/qwik-app
npx create-qwik@1.20.3 empty ./my-app      # plantillas: playground | empty | e2e-library | library
cd my-app
npm install
npm run build          # ⚠ NO 'npx vite build' — el guard lo bloquea como si fuera un servidor
```

### Resultados de build verificados
```
✓ Type checked
✓ Lint checked
dist/build/q-*.js — ~50 kB / 20 kB gzip
```

## Arrancar / previsualizar
```bash
npm run build.preview   # => server/entry.preview.js
# el servidor de preview DEBE ir con background=true:
npx vite preview --port 4999 --host 127.0.0.1
# comprobación:
curl -s -o /tmp/q.html -w "%{http_code}" http://127.0.0.1:4999/
grep -oE 'q:container="[^"]*"|q:version="[^"]*"' /tmp/q.html
```
Una respuesta Qwik correcta contiene `q:container="paused"` (= la resumability funciona) y `q:version`.

## Adaptadores (12 disponibles)
```bash
cd my-app && npx qwik add      # TUI interactiva — exige un TTY real
```
Disponibles: Static site (.html), Node.js Server / Express / Fastify, Cloudflare Pages / Workers,
Netlify Edge, Vercel Edge, AWS Lambda, Azure SWA, Google Cloud Run, Bun, Deno, Firebase.

Para sitio estático: se elige `Adapter: Static site` → el build produce archivos .html listos.

## Integraciones (28 disponibles)
Auth.js · Bootstrap · Builder.io · compiled-i18n · Cypress · Drizzle · Leaflet Maps ·
Orama · PandaCSS · Partytown · Playwright · PostCSS · Prisma · Storybook ·
Styled-Vanilla-Extract · Tailwind v3/v4 · Turso · Vitest · Framework: React

⚠️ El usuario de este servidor **no quiere Tailwind** — usa CSS custom / PandaCSS / vanilla-extract.

## Estructura del proyecto
```
src/
  components/       # componentes .tsx (component$)
  routes/           # enrutado basado en archivos (Qwik City)
  root.tsx          # <QwikCityProvider> + <RouterOutlet>
  entry.ssr.tsx     # renderToStream
  entry.dev.tsx
  entry.preview.tsx
  global.css
vite.config.ts      # qwikCity() + qwikVite() + tsconfigPaths()
```

## Trampas
1. **`npx vite build` lo bloquea** el guard (parece un servidor) → usa `npm run build`.
2. **`npx qwik add` exige TTY** — en un shell no interactivo da `ERR_TTY_INIT_FAILED`.
   Usa `terminal(pty=true, background=true)` + `process(action='write'|'submit')`,
   o edita `vite.config.ts` / `adapters/` a mano.
3. Los paquetes Qwik deben estar en **`devDependencies`**, no en `dependencies` — si no
   `vite.config.ts` lanza `Move qwik packages ... to devDependencies`.
4. v1 y v2 no pueden convivir en un mismo `node_modules` (ERESOLVE) → carpetas separadas.
5. `npm run preview` abre el navegador (`--open`) — en servidor usa `vite preview --host 127.0.0.1`.

## Servidores MCP para Qwik
**No hay servidor MCP público de Qwik** (comprobado en el registry de npm: `npm search qwik mcp` → 0 resultados).
Lo único relacionado es `@builder.io/dev-tools` (Builder.io Visual CMS), que habla con
el **MCP propio en la nube** de Builder.io y necesita su cuenta — no es una herramienta de desarrollo Qwik.
Para trabajar con Qwik usa esta skill + la documentación oficial en https://qwik.dev/docs/

## Comandos útiles
```bash
node -p "require('$HOME/qwik-app/node_modules/@builder.io/qwik/package.json').version"
cd $HOME/qwik-app/demo && npm run build          # build + tipos + lint
cd $HOME/qwik-app/demo && npm run lint
cd $HOME/qwik-app/demo && npm run fmt
```
