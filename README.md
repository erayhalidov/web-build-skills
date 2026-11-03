# Web Build Skills

A collection of agent skills (procedural playbooks) for building and operating
websites — static shops, Astro/Nuxt/Qwik sites, SEO audits, OpenCart stores.

Each skill is a `SKILL.md` with frontmatter (`name`, `description`) plus optional
`references/` files. They are written for an AI coding agent: they load the
skill when a matching task appears, then follow the steps.

## Contents

| Skill | What it covers |
|---|---|
| `wp-dump-to-static-php-site` | Rebuild a dead WordPress site from its `.sql` dump — content in a generated PHP data file, clean URLs, bilingual |
| `seo-audit` | Full SEO audit: technical, on-page, structured data, Core Web Vitals |
| `opencart` | Operate OpenCart 2.x stores — themes, layout, homepage modules, debugging, disk bloat |
| `static-product-shop` | Build a static catalog/shop from a CSV or JSON product export |
| `product-facet-engine` | Derive catalogue filters from sparse feed data (facets without a schema) |
| `astro-professional-sites` | Astro sites: i18n, SEO, sitemap, deployment to Cloudflare Pages |
| `nuxt-framework` | Nuxt 4: routing, SSR, Nitro, modules, layers, deployment |
| `qwik-framework` | Qwik + Qwik City: resumability, routing, deploy |
| `frontend-design-skill` | Frontend layout and CSS review — spacing, rhythm, hierarchy |

## Using a skill with Hermes Agent

```bash
# copy the ones you want into your local skill directory
cp -r skills/seo-audit ~/.hermes/skills/
```

Hermes picks them up on the next turn. With another agent, just read
`SKILL.md` — they are plain Markdown, no runtime needed.

## Structure

```
skills/<name>/
├── SKILL.md              # frontmatter + the playbook
└── references/           # deeper notes, loaded only when needed
    └── *.md
```

The `references/` files are deliberately separate: the agent reads them only
when the main playbook points at them, which keeps the context small.

## Notes on the content

- Everything here is **generic** — placeholders like `<site_user>`,
  `<domain>`, `/home/<site_user>/htdocs/<domain>`.
- No credentials, no customer data, no host-specific paths from any real
  deployment.
- Commands assume a Linux host with PHP 8.1+, MySQL/MariaDB and nginx; all are
  marked so you can adapt them.

## Contributing

Open an issue or a PR. Keep skills free of anything host- or client-specific:
if a rule only makes sense for one deployment, it belongs in that deployment's
own notes, not here.

## License

MIT — see [LICENSE](LICENSE).
