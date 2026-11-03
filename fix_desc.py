import os, re

FR = {
 'astro-professional-sites': "À utiliser pour créer un site Astro (i18n, SEO, CF Pages).",
 'frontend-design-skill': "À utiliser pour concevoir ou revoir le layout frontend et le CSS.",
 'nuxt-framework': "Pour Nuxt 4 : routage, SSR, Nitro, modules, déploiement.",
 'opencart': "Gérer des boutiques OpenCart 2.x (thèmes, nettoyage, debug).",
 'product-facet-engine': "Quand les filtres catalogue viennent de feeds pauvres en données.",
 'qwik-framework': "Créer et déployer des apps Qwik + Qwik City.",
 'seo-audit': "À utiliser pour auditer ou corriger le SEO d'un site.",
 'static-product-shop': "Créer des boutiques/catalogues statiques (HTML+JS+PHP) depuis CSV.",
 'wp-dump-to-static-php-site': "Reconstruire un WordPress mort depuis son dump .sql.",
}

TR = {
 'nuxt-framework': "Nuxt 4 işleri için: yönlendirme, SSR, Nitro, modüller, dağıtım.",
}

ES = {
 'nuxt-framework': "Úsala para Nuxt 4: rutas, SSR, Nitro, módulos, despliegue.",
}

for lang, mapping in (('fr', FR), ('tr', TR), ('es', ES)):
    for skill, desc in mapping.items():
        p = f'skills/{lang}/{skill}/SKILL.md'
        if not os.path.isfile(p):
            print('MISSING', p)
            continue
        s = open(p, encoding='utf-8').read()
        new, n = re.subn(r'^description:.*$', f'description: "{desc}"', s, count=1, flags=re.M)
        if n:
            open(p, 'w', encoding='utf-8').write(new)
            print(f'updated {lang}/{skill} -> {len(desc)} chars')
        else:
            print('NO description line in', p)

print()
for lang in ['en', 'fr', 'tr', 'es']:
    print(f'=== {lang} ===')
    for s in sorted(os.listdir(f'skills/{lang}')):
        p = f'skills/{lang}/{s}/SKILL.md'
        if not os.path.isfile(p):
            continue
        m = re.search(r'^description:\s*(.+)$', open(p, encoding='utf-8', errors='replace').read(), re.M)
        if m:
            d = m.group(1).strip()
            print(f'  {len(d.strip(chr(34))):>3}  {d[:68]}')
