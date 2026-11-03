---
name: nuxt-framework
description: "Use for Nuxt 4 work: scaffolding, routing, SSR, Nitro, modules, deployment."
version: 1.0.0
author: Nuxt community skills + Hermes
license: MIT
metadata:
  hermes:
    tags: [nuxt, vue, ssr, nitro, fullstack, webdev, typescript]
    related_skills: [astro-professional-sites, qwik-framework, tailwind-v4]
---

# Nuxt 4

Nuxt is the full-stack Vue framework: file-based routing, auto-imports, SSR/SSG/ISR per route, Nitro server
routes, modules and layers. Use this skill whenever the task involves a `nuxt.config.ts`, `app/` directory,
`server/` routes, or writing a Nuxt module.

**Live docs MCP is wired in**: server `nuxt` → tools `mcp__nuxt__*` (12 tools, `https://nuxt.com/mcp`,
no key needed). Prefer it over guessing — `mcp__nuxt__get_documentation_page` for an exact path,
`mcp__nuxt__list_documentation_pages` to search, `mcp__nuxt__get_module` for module metadata,
`mcp__nuxt__get_changelog` for what's new. There is also a public REST surface under `/api/v1`
(module directory, health, teams) and `<url>.md` / `llms-full.txt` for raw docs.

## Before writing code

1. Read `nuxt.config.ts`: `compatibilityVersion`, `modules`, `experimental`, `srcDir`.
2. Check the layout. Nuxt 4 puts app code in `app/` (`~` and `@` point there); `server/`, `shared/`,
   `public/`, `modules/`, `layers/` stay at the root (`~~`, `@@`). A Nuxt 3 layout without `app/` still works.
3. Check server-utility imports. Since 4.6 they can come from `nuxt/server`; a project uses either that or
   auto-imports, not both (`NUXT_E8012`).
4. A Nuxt 3 project is migration work first — see `references/nuxt4-migration.md`.

## Rules that matter most (full set in best-practices/)

- Fetch in pages/components with `useFetch` / `useAsyncData` so data travels in the SSR payload.
  `$fetch` in setup fetches **twice**. `$fetch` is for event handlers and server routes.
- Parallelise independent fetches with `Promise.all` — sequential `await` is the classic Nuxt slowdown.
- Give `useAsyncData` stable unique keys; same key = shared state.
- Nuxt 4 data refs are **shallow** — replace `data.value`, or opt in with `deep: true`.
- Cross-component shared state = `useState`, **never** a module-level `ref` (leaks between SSR requests).
- Browser-only code → `onMounted`, `<ClientOnly>`, or a `.client` plugin. Anything touching `window`,
  `document`, `localStorage`, `Date.now()`, `Math.random()` at setup level breaks hydration.
- Secrets in `runtimeConfig` (server side). Only `runtimeConfig.public` reaches the browser.
- Validate input in server routes; `throw createError({ statusCode: 404 })` instead of returning errors.
- `routeRules` per path beats global config: `prerender`, `isr: 3600`, `ssr: false`, `swr`.

## Reference map

| Topic | File |
|---|---|
| Nuxt 4 structure, config, routing, data fetching, server, rendering, layers, hooks | `references/nuxt-guide.md` |
| Nuxt 3 → 4 changes | `references/nuxt4-migration.md` |
| Writing and publishing Nuxt modules | `references/modules-guide.md` |
| Nitro v3 (beta), standalone Nitro, Nuxt 5 prep | `references/nitro-guide.md` |
| Raw Nuxt docs mirror (MDC markdown) | `references/docs/` |
| Official module READMEs | `references/modules/` |
| Nitro docs | `references/nitro/` |
| Nuxt UI + Reka UI components | `reference-vue-ui/vue-ui.md` |
| Data loaders, patterns, Pinia Colada | `reference-vue-data/vue-data.md` |
| 57 performance rules by category (SSR, data, reactivity, components, state, bundle) | `best-practices/best-practices.md` + `best-practices/rules/` |

## Versions (checked 2026-10)

- **Nuxt 4.6.x** is current stable (Node `^22.22.3 || ^24.15.0 || >=26`).
- **Nuxt 3 reached end of life 2026-07-31** — treat Nuxt 3 work as migration.
- **Nuxt 5** is Q4 2026, nightly only. **Nitro v3** (`nitro` package, not `nitropack`) is public beta.

## Adding the dev-server MCP to a Nuxt project (optional)

`nuxt-mcp-dev` lets an agent see the running app's routes, components and config. It is a **Nuxt module**,
not a standalone server — it only works inside a dev server:

```bash
npm i -D nuxt-mcp-dev          # in the Nuxt project
# nuxt.config.ts → modules: ['nuxt-mcp-dev']
npm run dev                     # dev server then exposes its MCP endpoint
```

Do not register it with `hermes mcp add` — there is nothing for a global client to connect to until the
project's `npm run dev` is running.

## Pitfalls

- **`@nuxtjs/mcp-toolkit` is for exposing YOUR app's data as an MCP server**, not for understanding Nuxt.
  Use the `nuxt` MCP server (already wired) or this skill for framework knowledge.
- **Dev-only modules must not ship to prod.** `nuxt-mcp-dev` is `-D` and dev-only; enabling it in a
  production build is dead weight.
- **`useFetch` inside a non-setup context** (composable called from an event, `setTimeout`) does not
  populate SSR payload — use `$fetch` + `refresh()` there.
- **Auto-imports do not apply in `server/utils` vs `app/utils`** identically; check the directory before
  wondering why a composable is undefined.
- **Hydration warnings are a real bug, not noise** — they cause content flicker and broken interactivity
  on slow devices. Fix the mismatch; do not silence it.
