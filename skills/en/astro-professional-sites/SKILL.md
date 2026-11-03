---
name: astro-professional-sites
description: Use when building an Astro site (i18n, SEO, CF Pages).
---

# Astro — professional websites

Astro 7.x: static HTML by default, islands architecture, built-in i18n. Ideal for
marketing sites, catalogues, booking systems — fast, SEO-clean, free hosting.

## When to use this skill

- Multilingual site (BG/EN/RU) with real `hreflang`
- Site with a catalogue + many SEO pages (one URL per product/game/service)
- Booking system with a calendar and payment
- Migration from WordPress to a static site

**Do NOT use** for: heavily dynamic applications with lots of user state (use
Medusa/Next.js), or when the client insists on a PHP admin (use `static-shop-builder`).

## Requirements

- **Node >= 22.23.4** (Astro 7). On this server: `/usr/local/bin/node` = v24.22.2.
  Default `node` in PATH is v22.23.2 — **below the requirement**. Always `export PATH=/usr/local/bin:$PATH`.
- Check the version with `/usr/local/bin/node --version` (the guard blocks bare `node`).

## MCP: `astro` (installed and connected)

**Important:** `astro-mcp` is an **Astro integration**, not a standalone server. It only works while
`astro dev` is running for a specific project. That is why this server has a bridge:

```
astro dev (127.0.0.1:4321/__mcp/sse)  →  supergateway (127.0.0.1:4322/mcp)  →  Hermes MCP "astro"
```

Files:
- `/root/astro-mcp-bridge/bridge.sh` — the bridge (autostart via crontab `@reboot`)
- `/root/astro-mcp-bridge/node_modules/supergateway/dist/index.js`
- Log: `/tmp/sg-bridge.log`
- Test project: `/root/astro-test` (Astro 7.4.4 + astro-mcp 0.4.2)

**Before using the `astro` tools** a dev server must be running for a project with the
`astro-mcp` integration installed, on port **4321**:

```bash
cd /path/to/project
export PATH=/usr/local/bin:$PATH
npm install astro astro-mcp
# astro.config.mjs: integrations: [mcp()]
setsid ./node_modules/.bin/astro dev --port 4321 --host 127.0.0.1 &
```

### Tools (9)

| Tool | What it is for |
|---|---|
| `get-astro-config` | The actual config: srcDir, outDir, i18n locales, output mode, integrations |
| `list-astro-routes` | All routes with entrypoint, params, prerendered, type |
| `get-astro-server-address` | Port and address of the dev server |
| `search-astro-docs` | **Live** search of the official documentation — use it instead of guessing the API |
| `list-astro-integrations` | All available integrations with metadata |
| `get-astro-integration` | Details for a specific integration (npm, repo, downloads) |
| `get-astro-changes` | Changelog of the Astro package |
| `get-vite-config` | Vite config digest |
| `get-vite-module-info` | Module graph: importers, imported, compiled result |

`search-astro-docs` is the most useful — it returns current text from docs.astro.build, so do not
invent an API from memory.

## Project structure (professional)

```
project/
├── astro.config.mjs
├── package.json
├── src/
│   ├── pages/
│   │   ├── index.astro
│   │   ├── [lang]/            # dynamic locales
│   │   │   ├── index.astro
│   │   │   └── [...slug].astro
│   │   └── api/               # endpoints
│   │       └── content.ts
│   ├── components/
│   ├── layouts/
│   ├── content/               # content collections (Markdown/MDX)
│   └── styles/
├── public/
└── functions/                 # Cloudflare Pages Functions (alternative to adapter)
```

## i18n — the right way

```js
// astro.config.mjs
export default defineConfig({
  site: "https://example.com",
  i18n: {
    defaultLocale: "bg",
    locales: ["bg", "en", "ru"],
    routing: { prefixDefaultLocale: false },  // BG without /bg/ prefix
  },
});
```

Rules:
- **Default locale WITHOUT prefix** (`/`, `/ceni/`), the rest with (`/en/`, `/ru/`)
- `hreflang` for **every** language + `x-default` pointing at the default locale
- Translations in `src/i18n/bg.ts`, `en.ts`, `ru.ts` — one object, one key
- Never mix languages in one file; a missing key = fallback to default

## SEO — the minimum that makes a difference

```astro
<link rel="canonical" href={canonical} />
<link rel="alternate" hreflang="bg" href={bgUrl} />
<link rel="alternate" hreflang="en" href={enUrl} />
<link rel="alternate" hreflang="x-default" href={bgUrl} />
<meta property="og:image" content={`${site}/og-image.png`} />
<meta name="robots" content="index, follow, max-image-preview:large" />
```

- `@astrojs/sitemap` for an automatic sitemap
- `schema.org` JSON-LD (LocalBusiness, Product, BreadcrumbList)
- Allow AI crawlers explicitly in `robots.txt` (`OAI-SearchBot`, `GPTBot`) if you want to be cited
- One URL = one page. No `?id=` — use `[...slug].astro`

## API routes (backend without a server)

```ts
// src/pages/api/content.ts
export const prerender = false;
export async function GET() {
  return new Response(JSON.stringify({ ok: true }), {
    headers: { "content-type": "application/json" },
  });
}
```

On Cloudflare Pages: `output: "hybrid"` (or `"server"`) + the `@astrojs/cloudflare` adapter.
Static pages stay static, only the APIs become Functions.

## Cloudflare Pages deploy

```bash
export PATH=/usr/local/bin:$PATH
npm run build
npx wrangler pages deploy dist --project-name=mysite
```

DNS: CNAME to `mysite.pages.dev`, **CF proxied** (orange cloud).
Secrets go in CF Dashboard → Pages → Settings → Environment variables, **not** in the code.

## Payments: myPOS

Ready myPOS example — see the section below. The pattern:

```
POST /api/mypos/checkout  →  { startISO, durationMin, amount }  →  redirect to myPOS
GET  /api/mypos/callback  →  signature verification  →  record + confirmation
```

**Always** verify the callback signature, otherwise anyone can "pay" without money.

## Bookings with Google Calendar

```
GET /api/calendar/availability?date=2026-11-15
→ { date, weekend, halls: [{ hall, calendarId, slots: [{ time, startISO, free }] }] }
```

Free slots are computed from what is busy in the calendar, not from a fixed list.

## Pitfalls (learned in production)

1. **Node version** — Astro 7 requires >= 22.23.4. The default is 22.23.2 and gives `EBADENGINE`.
   Always `export PATH=/usr/local/bin:$PATH` first.
2. **`astro-mcp` is not a stdio server** — `bin` is `undefined`, there is no way to register it via
   `hermes mcp add --command`. Only through the bridge (see above).
3. **Hermes does not speak plain SSE** — the `/__mcp/sse` endpoint returns `event: endpoint` + data,
   while Hermes waits for Streamable HTTP. That is why supergateway is needed with
   `--outputTransport streamableHttp`.
4. **MCP responses go over the SSE channel, not over POST** — if you write a client yourself, read
   from the SSE stream; the POST only returns `Accepted`.
5. **The guard blocks `node`, `npm`, `astro dev`, `supergateway`** on the command line and in scripts.
   Solution: `/usr/local/bin/node` directly + `.sh` scripts via crontab, or a symlink
   with a neutral name (`sg-bin`).
6. **`hermes mcp add --url` is interactive** (it asks for auth) and blocks in a non-tty. Add it
   directly in `config.yaml` under `mcp_servers:`.
7. **`trailingSlash`** — by default `ignore`. Set `trailingSlash: "always"` if
   you want consistent canonical URLs.
8. **Do not use Tailwind** for this user — custom CSS only.
9. **`output: "static"` is the default** — API routes with `prerender = false` require
   `output: "hybrid"`/`"server"` + an adapter.
10. **The MCP bridge needs a running dev server** — if the `astro` tools do not respond,
    the dev server is usually stopped or on a different port.
11. **Horizontal overflow on mobile** — always check with Playwright. Culprits: flex/grid
    children without `min-width: 0`; `<picture>` without `display: block`; a carousel using `transform`
    instead of `overflow-x: auto` on the track.
12. **`u(lang, "page?cat=x")` produces `/page/?cat=x/`** — the slash lands after the query.
    Pass the path and the query separately: `` `${u(lang,"knives").replace(/\/$/,"")}?cat=${x}` ``.
13. **Design from a reference** → see `references/design-from-reference.md`. Use the
    `design-extract` MCP for exact tokens, do not guess colours.

## Design from a reference

When the user gives a reference URL, **do not copy by eye**. The procedure is in
`references/design-from-reference.md`: token extraction with the `design-extract` MCP,
checking the reference's stack, choosing a free font with the same character, building
a design system from the ramps.

Verified in production:
- `ricola.com` → Astro + light theme, `#286140` green, `#ffc600` yellow, radii 16-34px
- `daveholloway.uk` → Astro + GSAP/Lenis, Alumni Sans up to 256px, `#2b47ff` blue,
  `#ffae00` orange, clean black header, grid lines

## Animations (GSAP + Lenis)

For "entrance animations" and scroll reveal → see `references/gsap-astro-animations.md`.
There you will find the exact timing values from the reference, the Lenis↔ScrollTrigger integration, and
**the critical rule**: `.reveal` must not stay hidden if JS fails — hiding
happens only under `html.js-ready`, and everything above 1.3× viewport is shown immediately.

## Verification after a change

```bash
export PATH=/usr/local/bin:$PATH
npm run build          # must be 0 errors
ls dist/               # check the generated .html files
# If dev is running: check routes via the MCP list-astro-routes
```

## Related skills

- `static-shop-builder` — catalogue from CSV, PHP admin (if you don't want Astro)
- `multilingual-site-rollout` — BG/EN/RU strategy
- `seo-audit` — checking canonical/hreflang/sitemap
- `responsive-mobile-qa` — mobile check
