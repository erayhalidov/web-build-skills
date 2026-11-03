import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";
import mcp from "astro-mcp";

// Professional Astro config: i18n BG/EN/RU, sitemap, MCP for development
export default defineConfig({
  site: "https://example.com",

  // trailingSlash: "always" gives consistent canonical URLs (/ceni/ instead of /ceni)
  trailingSlash: "always",
  compressHTML: true,

  i18n: {
    defaultLocale: "bg",
    locales: ["bg", "en", "ru"],
    routing: {
      // BG without prefix: /, /ceni/  |  EN: /en/, /en/prices/  |  RU: /ru/...
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
    // Dev only — serves MCP at 127.0.0.1:4321/__mcp/sse
    mcp(),
  ],

  // For API routes (prerender=false) on Cloudflare Pages:
  // requires the @astrojs/cloudflare adapter + output: "hybrid"
  // output: "hybrid",
  // adapter: cloudflare(),
});
