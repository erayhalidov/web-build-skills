# SEO international : preuves & sources

Preuves détaillées qui étayent la section SEO international & localisation du skill SEO Audit. Organisées par sujet avec les URL sources et les citations clés.

---

## Hreflang

### Méthodes de placement

Google prend en charge trois méthodes équivalentes : `<link>` HTML dans `<head>`, en-têtes HTTP `Link`, et éléments `<xhtml:link>` dans le sitemap XML. Google a confirmé qu'aucune méthode n'est priorisée par rapport aux autres.

Google combine les signaux du HTML et des sitemaps. Si le même couple langue-région pointe vers des URL différentes selon les méthodes, Google abandonne ce couple plutôt que de deviner.

- [Google Search Central : Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [SEJ : Google Combines Hreflang Signals](https://www.searchenginejournal.com/google-combines-hreflang-signals-from-html-sitemaps/389219/)

### Exigence de réciprocité

Docs Google : « Si la page X pointe vers la page Y, la page Y doit pointer vers la page X. Sinon, ces annotations peuvent être ignorées ou mal interprétées. »

Chaque page doit s'inclure elle-même (auto-référence) dans l'ensemble hreflang. L'auto-référence manquante est l'erreur n°1 trouvée par les audits Semrush. Une étude sur 374 756 domaines a trouvé que 67 % des implémentations hreflang avaient des problèmes.

- [Google Search Central : Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Semrush : 9 Common Hreflang Errors](https://www.semrush.com/blog/hreflang-errors/)
- [SE Land : 31% of International Websites Contain Hreflang Errors](https://searchengineland.com/study-31-of-international-websites-contain-hreflang-errors-395161)

### x-default

Introduit en avril 2013. Désigne la page de fallback pour les utilisateurs dont la langue/région ne correspond à aucune variante déclarée. Peut pointer vers la même URL que l'un des alternates spécifiques à une langue. Doit être inclus dans l'ensemble complet des annotations sur chaque page variante.

- [Google Blog : x-default hreflang](https://developers.google.com/search/blog/2013/04/x-default-hreflang-for-international-pages)
- [Google Blog : How x-default can help you (2023)](https://developers.google.com/search/blog/2023/05/x-default)

### Codes de langue & région

Langue : ISO 639-1 (2 lettres). Région : ISO 3166-1 Alpha 2 (2 lettres). Format : `language[-script][-region]`.

Tu ne peux pas spécifier seulement un code de région. Erreurs courantes : `en-UK` (devrait être `en-GB`), `es-419` (pas ISO 3166-1). Une étude a trouvé que 8,9 % des sites utilisant hreflang contiennent des codes de langue invalides.

- [Google Search Central : Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [SE Land : 31% Study](https://searchengineland.com/study-31-of-international-websites-contain-hreflang-errors-395161)

### Hreflang à l'échelle (20+ locales)

Avec 20 locales, le hreflang en `<head>` HTML ajoute ~1,5 Ko par page pour aucun bénéfice utilisateur. Le hreflang en sitemap n'a aucun impact sur la performance à l'exécution. Les éléments enfants `<xhtml:link>` ne comptent **pas** dans la limite de 50 000 URL par sitemap (seuls les éléments `<loc>` comptent).

John Mueller recommande de concentrer le hreflang sur les pages qui reçoivent du trafic dans la mauvaise langue, pas sur toutes les pages : « I wouldn't do it for any of the other pages of the site because it's so complex & hard to manage. »

- [SERoundtable : Child Elements Don't Count](https://www.seroundtable.com/google-child-elements-dont-count-towards-sitemap-url-limit-34377.html)
- [SERoundtable : Where To Focus Hreflang](https://www.seroundtable.com/using-hreflang-34127.html)
- [Yoast : hreflang Ultimate Guide](https://yoast.com/hreflang-ultimate-guide/)

### Google vs Bing

Bing traite le hreflang comme un « signal faible ». Bing s'appuie sur la meta tag `content-language`, l'attribut HTML `lang`, les ccTLD et la localisation du serveur. Yandex prend en charge hreflang comme Google.

Pour les deux moteurs : implémente hreflang (Google/Yandex) + `<html lang="...">` + `<meta http-equiv="content-language">` (Bing).

- [Digital Ready Marketing : Bing Doesn't Use Hreflang](https://digitalreadymarketing.com/bing-doesnt-use-hreflang-annotation-what-does-it-use/)
- [Yoast : hreflang Ultimate Guide](https://yoast.com/hreflang-ultimate-guide/)

---

## Canonicalisation & i18n

### Canonicals auto-référents

Chaque page de locale doit canonicaliser vers elle-même. John Mueller : « Don't use a rel=canonical across languages/countries, only use it on a per-country/language basis. »

Docs Google : « Spécifie une page canonical dans la même langue, ou la meilleure langue de substitution possible si un canonical n'existe pas pour la même langue. »

- [John Mueller : hreflang canonical](https://johnmu.com/hreflang-canonical/)
- [Google : Consolidate Duplicate URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)

### Le canonical prime sur le hreflang

Mueller : « Si ton canonical pointe ailleurs, Google suivra cela et ignorera ton annotation hreflang. » L'URL canonical doit être l'une des URL de l'ensemble hreflang, sinon tout le markup hreflang est ignoré.

Google précise aussi : « Google préfère les URL qui font partie de clusters hreflang pour la canonicalisation » — quand les signaux s'alignent, le hreflang renforce la sélection du canonical.

- [John Mueller : hreflang canonical](https://johnmu.com/hreflang-canonical/)
- [SEJ : Hreflang Tags Are Hints](https://www.searchenginejournal.com/google-reminds-that-hreflang-tags-are-hints-not-directives/546428/)
- [Google : Consolidate Duplicate URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)

### Variantes régionales quasi dupliquées

Mueller (2023 Office Hours) : « Si le contenu est complètement identique et que nous ne pouvons voir aucune différence, alors pour la simplicité et l'expérience utilisateur nous pouvons n'afficher qu'une version — même si le hreflang est présent. »

La détection de doublons de Google s'exécute AVANT l'évaluation du hreflang. Pour garder les deux versions indexées, il te faut des différences de contenu substantielles au-delà des symboles monétaires.

- [International Web Mastery : Same-Language Duplicate Pages](https://internationalwebmastery.com/blog/how-google-handles-canonicalization-of-same-language-duplicate-near-duplicate-pages/)
- [Google : Managing Multi-Regional Sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)

### Pagination entre locales

Google : « N'utilise pas la première page d'une séquence paginée comme page canonical. Donne plutôt à chaque page sa propre URL canonical. » Chaque page paginée de chaque locale reçoit un canonical auto-référent. `rel="next/prev"` est déprécié depuis mars 2019.

- [Google : Pagination Best Practices](https://developers.google.com/search/docs/specialty/ecommerce/pagination-and-incremental-page-loading)

---

## Sitemaps internationaux

### Structure

Chaque entrée `<url>` inclut des alternates `<xhtml:link>` pour chaque locale. Nécessite le namespace `xmlns:xhtml="http://www.w3.org/1999/xhtml"`.

Découpe les sitemaps par type de contenu, pas par locale. Découper par locale crée des problèmes de maintenance, car chaque sitemap de locale doit référencer toutes les autres locales (exigence de réciprocité).

- [Google Search Central : Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Lumar : How Google Handles Hreflang](https://www.lumar.io/office-hours/hreflang/)

### Limites de taille

50 000 URL / 50 Mo non compressés par sitemap. Seuls les éléments `<loc>` comptent dans la limite des 50K. Mais avec 20 alternates hreflang par entrée, la limite de 50 Mo par fichier devient le goulot. Prévois 2 000 à 5 000 URL par sitemap quand tu utilises du hreflang complet.

- [Google : Build and Submit a Sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [SERoundtable : Sitemap 50,000 Limit](https://www.seroundtable.com/google-sitemap-50-000-limit-based-on-location-urls-not-alternative-urls-33843.html)

### Soumission

Soumets l'index de sitemap dans Search Console ET référence-le dans robots.txt. Les sitemaps enfants individuels peuvent être soumis séparément pour un reporting par sitemap.

- [Google : Build and Submit a Sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)

### Mise en garde Next.js

Les `alternates.languages` de Next.js n'incluent **pas** automatiquement un `<xhtml:link>` auto-référent pour l'URL `<loc>`. Tu dois inclure explicitement la langue de l'URL `<loc>` elle-même dans l'objet `languages`.

- [Next.js Docs : sitemap.xml](https://nextjs.org/docs/app/api-reference/file-conventions/metadata/sitemap)

---

## Structure d'URL

### Stratégies comparées

Google traite les sous-répertoires et les sous-domaines de façon équivalente. Mueller : « De notre point de vue… ils disent que les sous-domaines et les sous-répertoires sont essentiellement équivalents. »

Les paramètres d'URL (`?lang=en`) sont explicitement « Non recommandés » selon les docs Google.

- [Google : Managing Multi-Regional Sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)

### Langue par défaut

Mueller recommande : définir `/` comme x-default, mettre chaque langue dans son propre préfixe. Sans marquer `/` comme x-default, « pour Google cela peut ressembler à une page '/' séparée des autres ».

- [Google Blog : x-default](https://developers.google.com/search/blog/2023/05/x-default)
- [Google Blog : Creating the Right Homepage](https://developers.google.com/search/blog/2014/05/creating-right-homepage-for-your)

### Négociation de contenu / redirections par IP

Google déconseille fortement les pages adaptatives par locale. Googlebot crawle depuis des IP américaines et n'envoie pas d'en-têtes Accept-Language. Des URL séparées + hreflang sont requises.

- [Google : Locale-Adaptive Pages](https://developers.google.com/search/docs/specialty/international/locale-adaptive-pages)

### Cohérence du trailing slash

Mueller : le trailing slash est « une partie significative de l'URL et changera l'URL selon qu'il est là ou non ». Choisis un format pour tous les chemins de locale, liens internes, canonicals, hreflang et sitemaps.

Mueller (2025) : « La cohérence est le plus grand facteur de SEO technique. »

- [SERoundtable : Consistency Is The Biggest Technical SEO Factor](https://www.seroundtable.com/google-consistency-seo-40427.html)

### Géociblage dans Search Console

Le rapport International Targeting est déprécié. Google s'appuie désormais entièrement sur le hreflang, l'analyse de la langue du contenu et les patterns de liens. Tu peux ajouter des propriétés de sous-répertoire pour un reporting par locale.

- [Google Support : International Targeting Deprecated](https://support.google.com/webmasters/answer/12474899?hl=en)

### Modes de locale des frameworks

Utilise `localePrefix: 'always'` (next-intl) ou équivalent. Ne masque jamais la locale des URL — Google a besoin d'URL uniques par langue. Le mode `'never'` désactive entièrement les liens alternates.

- [next-intl : Routing Configuration](https://next-intl.dev/docs/routing/configuration)
- [Next.js Discussion #18419](https://github.com/vercel/next.js/discussions/18419)

---

## Qualité du contenu entre locales

### Contenu auto-traduit (position 2025)

Google a retiré mi-2025 une recommandation de longue date déconseillant le contenu auto-traduit. Position actuelle : « Nos politiques ne définissent pas strictement le contenu traduit par IA comme du spam. » La politique d'abus de contenu à grande échelle mentionne la traduction comme vecteur possible, mais ne l'interdit pas.

Reddit a mis à l'échelle des traductions IA dans 35+ langues avec la connaissance de Google. La distinction clé est l'intention et la qualité, pas la méthode.

- [Google Spam Policies](https://developers.google.com/search/docs/essentials/spam-policies)
- [Glenn Gabe : Auto-Translating Content](https://www.gsqi.com/marketing-blog/auto-translating-content-google-scaled-content-abuse/)
- [SE Land : Reddit AI Translations](https://searchengineland.com/google-comments-on-reddits-use-of-ai-to-translate-its-pages-456908)

### Pages de locale pauvres

Google : « Les versions localisées d'une page ne sont considérées comme doublons que si le contenu principal de la page reste non traduit. » Les pages dont seul le boilerplate est traduit sont regroupées comme doublons.

N'utilise PAS noindex pour les pages de locale non désirées (gaspille le budget de crawl). Ne canonicalise PAS en inter-locale (conflit avec hreflang). Meilleure approche : ne crée pas de pages de locale que tu ne peux pas rendre réellement utiles.

- [Google : Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Google : Crawl Budget Management](https://developers.google.com/search/docs/crawling-indexing/large-site-managing-crawl-budget)

### Impact du système de contenu utile

Fusionné dans le classement cœur en mars 2024. Signal à l'échelle du site : « tout contenu — pas seulement le contenu inutile — sur les sites jugés avoir globalement des quantités relativement élevées de contenu inutile a moins de chances de bien performer dans Search. »

Des pages traduites de faible qualité peuvent tirer tout le site vers le bas. C'est l'argument le plus fort contre la création de pages de locale qui ne sont pas réellement utiles.

- [Google Blog : Helpful Content Update](https://developers.google.com/search/blog/2022/08/helpful-content-update)
- [Amsive : What Changed in 2024](https://www.amsive.com/insights/seo/googles-helpful-content-update-ranking-system-what-happened-and-what-changed-in-2024/)

### Traduction partielle

Google : « Traduire seulement le texte de boilerplate de tes pages en gardant le gros de ton contenu dans une seule langue… peut créer une mauvaise expérience utilisateur. » Google utilise le contenu visible (pas l'attribut lang) pour déterminer la langue de la page.

Traduis TOUT le contenu d'une page si tu crées une version de locale. Des métadonnées non traduites (title, description) dans la mauvaise langue réduisent le CTR.

- [Google : Managing Multi-Regional Sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)

### Budget de crawl

Ne concerne que les sites de 1M+ pages ou 10K+ pages changeant quotidiennement. Mais les URL alternates (cibles hreflang) consomment bien du budget de crawl. Des liens hreflang cassés gaspillent le budget ET invalident les signaux.

- [Google : Crawl Budget Management](https://developers.google.com/search/docs/crawling-indexing/large-site-managing-crawl-budget)
- [Google Blog : Crawl Budget](https://developers.google.com/search/blog/2017/01/what-crawl-budget-means-for-googlebot)

### Signaux spécifiques à la locale

Google identifie l'audience via : « les adresses et numéros de téléphone locaux sur les pages, l'usage de la langue et de la devise locales, les liens depuis d'autres sites locaux, ou des signaux de votre Business Profile. »

- [Google : Managing Multi-Regional Sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)
