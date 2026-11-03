import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";
import mcp from "astro-mcp";

// Професионален Astro config: i18n BG/EN/RU, sitemap, MCP за разработка
export default defineConfig({
  site: "https://example.com",

  // trailingSlash: "always" дава консистентни canonical URL-и (/ceni/ вместо /ceni)
  trailingSlash: "always",
  compressHTML: true,

  i18n: {
    defaultLocale: "bg",
    locales: ["bg", "en", "ru"],
    routing: {
      // BG без префикс: /, /ceni/  |  EN: /en/, /en/prices/  |  RU: /ru/...
      prefixDefaultLocale: false,
      redirectToDefaultLocale: false,
    },
  },

  integrations: [
    sitemap({
      i18n: {
        defaultLocale: "bg",
        locales: { bg: "bg-BG", en: "en-US", ru: "ru-RU" },
      },
    }),
    // Само за dev — дава MCP на 127.0.0.1:4321/__mcp/sse
    mcp(),
  ],

  // За API routes (prerender=false) на Cloudflare Pages:
  // изисква @astrojs/cloudflare adapter + output: "hybrid"
  // output: "hybrid",
  // adapter: cloudflare(),
});
