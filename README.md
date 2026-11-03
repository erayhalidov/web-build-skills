# Web Build Skills

Agent skills (procedural playbooks in Markdown) for building and operating
websites — static shops, Astro/Nuxt/Qwik sites, SEO audits, OpenCart stores.

Available in **5 languages**: Bulgarian, English, French, Turkish, Spanish.

## Languages

| Language | Folder | Status |
|---|---|---|
| 🇧🇬 Български | [`skills/bg`](skills/bg) | complete |
| 🇬🇧 English | [`skills/en`](skills/en) | complete |
| 🇫🇷 Français | [`skills/fr`](skills/fr) | complete |
| 🇹🇷 Türkçe | [`skills/tr`](skills/tr) | complete |
| 🇪🇸 Español | [`skills/es`](skills/es) | in progress |

Every language folder has the same skill names, so you can point an agent at
the folder for the language you want it to work in.

## The skills

| Skill | What it covers |
|---|---|
| `wp-dump-to-static-php-site` | Rebuild a dead WordPress site from its `.sql` dump — content in a generated PHP data file, clean URLs, bilingual |
| `seo-audit` | Full SEO audit: technical, on-page, structured data, Core Web Vitals |
| `opencart` | Operate OpenCart 2.x stores — themes, layout, homepage modules, debugging, disk bloat |
| `static-product-shop` | Build a static catalog/shop from a CSV or JSON product export |
| `product-facet-engine` | Derive catalogue filters from sparse feed data (facets without a schema) |
| `astro-professional-sites` | Astro sites: i18n, SEO, sitemap, deployment |
| `nuxt-framework` | Nuxt 4: routing, SSR, Nitro, modules, layers, deployment |
| `qwik-framework` | Qwik + Qwik City: resumability, routing, deploy |
| `frontend-design-skill` | Frontend layout and CSS review — spacing, rhythm, hierarchy |

## Structure

```
skills/
├── bg/                       # Bulgarian
│   └── <skill-name>/
│       ├── SKILL.md          # frontmatter + the playbook
│       └── references/       # deeper notes, loaded only when needed
├── en/                       # English, same layout
├── fr/                       # French
├── tr/                       # Turkish
└── es/                       # Spanish
```

Each `SKILL.md` starts with YAML frontmatter:

```yaml
---
name: seo-audit
description: Audit or fix a site's SEO.     # under 60 chars, trigger-first
---
```

The `name:` value is identical across languages — only the prose changes.
That means an agent can match a task against any language folder and still
resolve the right skill.

## Using a skill

With Hermes Agent:

```bash
cp -r skills/en/seo-audit ~/.hermes/skills/
```

Hermes picks it up on the next turn. With any other agent, just read
`SKILL.md` — plain Markdown, no runtime needed.

Pick the language folder that matches how you want the agent to talk to you.
The technical content (commands, paths, workflows) is the same in all of them;
only the explanatory prose is translated.

## Notes on the content

- Everything is **generic** — placeholders like `<site_user>`, `<domain>`,
  `/home/<site_user>/htdocs/<domain>`.
- No credentials, no customer data, no host-specific paths from any real
  deployment.
- Commands assume Linux with PHP 8.1+, MySQL/MariaDB and nginx.

## Contributing

Open an issue or a PR. Keep skills free of anything host- or client-specific.
If you add a translation, copy the structure of an existing language folder
and keep the `name:` fields untouched.

## License

MIT — see [LICENSE](LICENSE).
