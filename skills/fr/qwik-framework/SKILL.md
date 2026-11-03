---
name: qwik-framework
description: Build/deploy Qwik + Qwik City apps.
---

# Qwik (Builder.io) — installation et utilisation

Site officiel : https://qwik.dev · Repo : https://github.com/QwikDev/qwik
Installé sur ce serveur dans **`$HOME/qwik-app`**.

## ⚠️ CRITIQUE : quel paquet est le vrai

| Paquet | Version | Statut |
|---|---|---|
| **`@builder.io/qwik`** | **1.20.3** | ✅ **stable (v1) — utilise ça pour la production** |
| `@builder.io/qwik-city` | 1.20.3 | ✅ méta-framework (routage, SSR, adapters) |
| **`@qwik.dev/core`** | **2.0.0-rc.4** | ⚠️ **v2 RC** — le nouveau scope, pas encore stable |
| `@qwik.dev/router` | 2.0.0-rc.4 | ⚠️ routeur v2 (RC) |
| ~~`qwik`~~ | 1.0.57 | ❌ **CE N'EST PAS Qwik** — vieux paquet sans rapport, ne l'installe PAS |

Vérification que v2 est officiel : `npm view @qwik.dev/core maintainers` → `mhevery` (Miško Hevery, le créateur).

## Ce qui est installé ici

```
$HOME/qwik-app/              # v1 — @builder.io/qwik@1.20.3 + qwik-city@1.20.3
$HOME/qwik-app/demo/         # starter fonctionnel (empty template), build réussi
$HOME/qwik-app/v2/           # v2 RC — @qwik.dev/core@2.0.0-rc.4 (dossier séparé, à cause du conflit)
```

## Démarrer un nouveau projet

```bash
cd $HOME/qwik-app
npx create-qwik@1.20.3 empty ./my-app      # templates : playground | empty | e2e-library | library
cd my-app
npm install
npm run build          # ⚠ PAS 'npx vite build' — le guard le bloque comme un serveur
```

### Résultats de build vérifiés
```
✓ Type checked
✓ Lint checked
dist/build/q-*.js — ~50 kB / 20 kB gzip
```

## Démarrer / prévisualiser
```bash
npm run build.preview   # => server/entry.preview.js
# le serveur de preview DOIT être en background=true :
npx vite preview --port 4999 --host 127.0.0.1
# vérification :
curl -s -o /tmp/q.html -w "%{http_code}" http://127.0.0.1:4999/
grep -oE 'q:container="[^"]*"|q:version="[^"]*"' /tmp/q.html
```
Une réponse Qwik réussie contient `q:container="paused"` (= la resumability fonctionne) et `q:version`.

## Adapters (12 disponibles)
```bash
cd my-app && npx qwik add      # TUI interactif — exige un vrai TTY
```
Disponibles : Static site (.html), Node.js Server / Express / Fastify, Cloudflare Pages / Workers,
Netlify Edge, Vercel Edge, AWS Lambda, Azure SWA, Google Cloud Run, Bun, Deno, Firebase.

Pour un site statique : choisis `Adapter: Static site` → le build sort des fichiers .html prêts.

## Intégrations (28 disponibles)
Auth.js · Bootstrap · Builder.io · compiled-i18n · Cypress · Drizzle · Leaflet Maps ·
Orama · PandaCSS · Partytown · Playwright · PostCSS · Prisma · Storybook ·
Styled-Vanilla-Extract · Tailwind v3/v4 · Turso · Vitest · Framework: React

⚠️ L'utilisateur de ce serveur **ne veut pas de Tailwind** — utilise du CSS custom / PandaCSS / vanilla-extract.

## Structure du projet
```
src/
  components/       # composants .tsx (component$)
  routes/           # routage basé sur les fichiers (Qwik City)
  root.tsx          # <QwikCityProvider> + <RouterOutlet>
  entry.ssr.tsx     # renderToStream
  entry.dev.tsx
  entry.preview.tsx
  global.css
vite.config.ts      # qwikCity() + qwikVite() + tsconfigPaths()
```

## Pièges
1. **`npx vite build` est bloqué** par le guard (ça ressemble à un serveur) → utilise `npm run build`.
2. **`npx qwik add` exige un TTY** — dans un shell non interactif ça donne `ERR_TTY_INIT_FAILED`.
   Utilise `terminal(pty=true, background=true)` + `process(action='write'|'submit')`,
   ou édite `vite.config.ts` / `adapters/` à la main.
3. Les paquets Qwik doivent être dans les **`devDependencies`**, pas dans `dependencies` — sinon
   `vite.config.ts` lance `Move qwik packages ... to devDependencies`.
4. v1 et v2 ne peuvent pas cohabiter dans un même `node_modules` (ERESOLVE) → dossiers séparés.
5. `npm run preview` ouvre un navigateur (`--open`) — sur un serveur, utilise `vite preview --host 127.0.0.1`.

## Serveurs MCP pour Qwik
**Il n'existe pas de serveur MCP Qwik public** (vérifié dans le registry npm : `npm search qwik mcp` → 0 résultat).
Le seul élément lié est `@builder.io/dev-tools` (Builder.io Visual CMS), qui parle au
**MCP cloud propre** de Builder.io et exige un compte chez eux — ce n'est pas un outil dev Qwik.
Pour travailler avec Qwik, utilise ce skill + la documentation officielle sur https://qwik.dev/docs/

## Commandes utiles
```bash
node -p "require('$HOME/qwik-app/node_modules/@builder.io/qwik/package.json').version"
cd $HOME/qwik-app/demo && npm run build          # build + types + lint
cd $HOME/qwik-app/demo && npm run lint
cd $HOME/qwik-app/demo && npm run fmt
```
