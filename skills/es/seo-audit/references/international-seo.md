# SEO internacional: evidencias y fuentes

Evidencias detalladas que respaldan la sección de SEO internacional y localización de la skill de Auditoría SEO. Organizado por tema con URLs de origen y citas clave.

---

## Hreflang

### Métodos de colocación

Google admite tres métodos equivalentes: `<link>` HTML en `<head>`, cabeceras HTTP `Link` y elementos `<xhtml:link>` en el sitemap XML. Google confirmó que ningún método tiene prioridad sobre otro.

Google combina señales del HTML y de los sitemaps. Si el mismo par idioma-región apunta a URLs distintas entre métodos, Google descarta ese par en vez de adivinar.

- [Google Search Central: Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [SEJ: Google Combines Hreflang Signals](https://www.searchenginejournal.com/google-combines-hreflang-signals-from-html-sitemaps/389219/)

### Requisito de reciprocidad

Docs de Google: "Si la página X enlaza a la página Y, la página Y debe enlazar de vuelta a la página X. Si no, esas anotaciones pueden ignorarse o no interpretarse correctamente."

Cada página debe incluirse a sí misma (autorreferencia) en el conjunto hreflang. La falta de autorreferencia es el error #1 que encuentran las auditorías de Semrush. Un estudio de 374.756 dominios halló que el 67 % de las implementaciones de hreflang tenían problemas.

- [Google Search Central: Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Semrush: 9 Common Hreflang Errors](https://www.semrush.com/blog/hreflang-errors/)
- [SE Land: 31% of International Websites Contain Hreflang Errors](https://searchengineland.com/study-31-of-international-websites-contain-hreflang-errors-395161)

### x-default

Introducido en abril de 2013. Designa la página de fallback para usuarios cuyo idioma/región no coincide con ninguna variante declarada. Puede apuntar a la misma URL que uno de los alternativos específicos de idioma. Debe incluirse en el conjunto completo de anotaciones de cada página variante.

- [Google Blog: x-default hreflang](https://developers.google.com/search/blog/2013/04/x-default-hreflang-for-international-pages)
- [Google Blog: How x-default can help you (2023)](https://developers.google.com/search/blog/2023/05/x-default)

### Códigos de idioma y región

Idioma: ISO 639-1 (2 letras). Región: ISO 3166-1 Alpha 2 (2 letras). Formato: `idioma[-script][-región]`.

No puedes especificar solo un código de región. Errores comunes: `en-UK` (debería ser `en-GB`), `es-419` (no es ISO 3166-1). Un estudio halló que el 8.9 % de los sitios que usan hreflang contienen códigos de idioma inválidos.

- [Google Search Central: Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [SE Land: 31% Study](https://searchengineland.com/study-31-of-international-websites-contain-hreflang-errors-395161)

### Hreflang a escala (20+ locales)

Con 20 locales, el hreflang en `<head>` añade ~1.5KB por página sin ningún beneficio para el usuario. El hreflang basado en sitemap no tiene impacto en rendimiento en ejecución. Los elementos hijos `<xhtml:link>` NO cuentan para el límite de 50.000 URLs del sitemap (solo cuentan los elementos `<loc>`).

John Mueller recomienda centrar el hreflang en las páginas que reciben tráfico en el idioma equivocado, no en todas: "No lo haría para ninguna de las otras páginas del sitio porque es demasiado complejo y difícil de gestionar."

- [SERoundtable: Child Elements Don't Count](https://www.seroundtable.com/google-child-elements-dont-count-towards-sitemap-url-limit-34377.html)
- [SERoundtable: Where To Focus Hreflang](https://www.seroundtable.com/using-hreflang-34127.html)
- [Yoast: hreflang Ultimate Guide](https://yoast.com/hreflang-ultimate-guide/)

### Google vs Bing

Bing trata hreflang como una "señal débil". Bing se apoya en la meta etiqueta `content-language`, el atributo HTML `lang`, los ccTLDs y la ubicación del servidor. Yandex soporta hreflang igual que Google.

Para ambos motores: implementa hreflang (Google/Yandex) + `<html lang="...">` + `<meta http-equiv="content-language">` (Bing).

- [Digital Ready Marketing: Bing Doesn't Use Hreflang](https://digitalreadymarketing.com/bing-doesnt-use-hreflang-annotation-what-does-it-use/)
- [Yoast: hreflang Ultimate Guide](https://yoast.com/hreflang-ultimate-guide/)

---

## Canonicalización e i18n

### Canonicals autorreferentes

Cada página de locale debe canonicalizarse a sí misma. John Mueller: "No uses rel=canonical entre idiomas/países, úsalo solo por país/idioma."

Docs de Google: "Especifica una página canónica en el mismo idioma, o el mejor sustituto de idioma posible si no existe una canónica para el mismo idioma."

- [John Mueller: hreflang canonical](https://johnmu.com/hreflang-canonical/)
- [Google: Consolidate Duplicate URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)

### El canonical anula al hreflang

Mueller: "Si tu canonical apunta a otro sitio, Google seguirá eso e ignorará tu anotación hreflang." La URL canónica debe ser una de las URLs del conjunto hreflang, o se ignora todo el markup hreflang.

Google también afirma: "Google prefiere URLs que forman parte de clusters hreflang para la canonicalización" — cuando las señales se alinean, el hreflang refuerza la selección de canónica.

- [John Mueller: hreflang canonical](https://johnmu.com/hreflang-canonical/)
- [SEJ: Hreflang Tags Are Hints](https://www.searchenginejournal.com/google-reminds-that-hreflang-tags-are-hints-not-directives/546428/)
- [Google: Consolidate Duplicate URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)

### Variantes regionales casi duplicadas

Mueller (Office Hours 2023): "Si el contenido es completamente igual y no podemos notar ninguna diferencia, por simplicidad y experiencia de usuario podemos mostrar solo una versión — incluso si el hreflang está presente."

La detección de duplicados de Google corre ANTES de la evaluación de hreflang. Para mantener ambas versiones indexadas necesitas diferencias sustantivas de contenido más allá de los símbolos de moneda.

- [International Web Mastery: Same-Language Duplicate Pages](https://internationalwebmastery.com/blog/how-google-handles-canonicalization-of-same-language-duplicate-near-duplicate-pages/)
- [Google: Managing Multi-Regional Sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)

### Paginación entre locales

Google: "No uses la primera página de una secuencia paginada como página canónica. En su lugar, da a cada página su propia URL canónica." Cada página paginada de cada locale recibe canonical autorreferente. `rel="next/prev"` quedó obsoleto en marzo de 2019.

- [Google: Pagination Best Practices](https://developers.google.com/search/docs/specialty/ecommerce/pagination-and-incremental-page-loading)

---

## Sitemaps internacionales

### Estructura

Cada entrada `<url>` incluye alternativos `<xhtml:link>` para todos los locales. Requiere el namespace `xmlns:xhtml="http://www.w3.org/1999/xhtml"`.

Divide los sitemaps por tipo de contenido, no por locale. Dividir por locale crea problemas de mantenimiento porque cada sitemap de locale debe referenciar a todos los demás (requisito de reciprocidad).

- [Google Search Central: Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Lumar: How Google Handles Hreflang](https://www.lumar.io/office-hours/hreflang/)

### Límites de tamaño

50.000 URLs / 50MB sin comprimir por sitemap. Solo los elementos `<loc>` cuentan para el límite de 50K. Pero con 20 alternativos hreflang por entrada, el límite de 50MB por archivo se vuelve el cuello de botella. Planifica 2.000-5.000 URLs por sitemap cuando uses hreflang completo.

- [Google: Build and Submit a Sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [SERoundtable: Sitemap 50,000 Limit](https://www.seroundtable.com/google-sitemap-50-000-limit-based-on-location-urls-not-alternative-urls-33843.html)

### Envío

Envía el índice de sitemap en Search Console Y referéncialo en robots.txt. Los sitemaps hijos individuales pueden enviarse por separado para tener informes por sitemap.

- [Google: Build and Submit a Sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)

### Advertencia para Next.js

`alternates.languages` de Next.js NO incluye automáticamente un `<xhtml:link>` autorreferente para la URL del `<loc>`. Debes incluir explícitamente el propio idioma de la URL `<loc>` en el objeto `languages`.

- [Next.js Docs: sitemap.xml](https://nextjs.org/docs/app/api-reference/file-conventions/metadata/sitemap)

---

## Estructura de URL

### Estrategias comparadas

Google trata subdirectorios y subdominios de forma equivalente. Mueller: "Desde nuestro punto de vista... dicen que los subdominios y los subdirectorios son esencialmente equivalentes."

Los parámetros de URL (`?lang=en`) están explícitamente "No recomendados" según los docs de Google.

- [Google: Managing Multi-Regional Sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)

### Idioma por defecto

Mueller recomienda: poner `/` como x-default, con cada idioma en su propio prefijo. Sin marcar `/` como x-default, "para Google puede parecer que '/' es una página separada de las demás".

- [Google Blog: x-default](https://developers.google.com/search/blog/2023/05/x-default)
- [Google Blog: Creating the Right Homepage](https://developers.google.com/search/blog/2014/05/creating-right-homepage-for-your)

### Negociación de contenido / redirecciones por IP

Google desaconseja firmemente las páginas adaptativas por locale. Googlebot rastrea desde IPs de EE. UU. y no envía cabeceras Accept-Language. Se requieren URLs separadas + hreflang.

- [Google: Locale-Adaptive Pages](https://developers.google.com/search/docs/specialty/international/locale-adaptive-pages)

### Consistencia de barra final

Mueller: la barra final es "una parte significativa de la URL y cambiará la URL si está o no". Elige un formato para todas las rutas de locale, enlaces internos, canonicals, hreflang y sitemaps.

Mueller (2025): "La consistencia es el mayor factor de SEO técnico."

- [SERoundtable: Consistency Is The Biggest Technical SEO Factor](https://www.seroundtable.com/google-consistency-seo-40427.html)

### Geotargeting en Search Console

El informe International Targeting está obsoleto. Google ahora se apoya enteramente en hreflang, análisis del idioma del contenido y patrones de enlazado. Puedes añadir propiedades de subdirectorio para informes por locale.

- [Google Support: International Targeting Deprecated](https://support.google.com/webmasters/answer/12474899?hl=en)

### Modos de locale en frameworks

Usa `localePrefix: 'always'` (next-intl) o equivalente. Nunca ocultes el locale de las URLs — Google necesita URLs únicas por idioma. Usar el modo `'never'` desactiva por completo los enlaces alternativos.

- [next-intl: Routing Configuration](https://next-intl.dev/docs/routing/configuration)
- [Next.js Discussion #18419](https://github.com/vercel/next.js/discussions/18419)

---

## Calidad de contenido entre locales

### Contenido autotraducido (postura 2025)

Google retiró a mediados de 2025 la orientación de larga data que desaconsejaba el contenido autotraducido. Postura actual: "Nuestras políticas no definen estrictamente el contenido traducido por IA como spam." La política de abuso de contenido escalado menciona la traducción como posible vector, pero no la prohíbe.

Reddit escaló traducciones con IA a 35+ idiomas con conocimiento de Google. La distinción clave es la intención y la calidad, no el método.

- [Google Spam Policies](https://developers.google.com/search/docs/essentials/spam-policies)
- [Glenn Gabe: Auto-Translating Content](https://www.gsqi.com/marketing-blog/auto-translating-content-google-scaled-content-abuse/)
- [SE Land: Reddit AI Translations](https://searchengineland.com/google-comments-on-reddits-use-of-ai-to-translate-its-pages-456908)

### Páginas de locale pobres

Google: "Las versiones localizadas de una página solo se consideran duplicados si el contenido principal de la página sigue sin traducir." Las páginas con solo el boilerplate traducido se agrupan como duplicados.

NO uses noindex para páginas de locale no deseadas (desperdicia crawl budget). NO uses canonical entre locales (entra en conflicto con hreflang). Mejor enfoque: no crear páginas de locale que no puedas hacer genuinamente útiles.

- [Google: Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Google: Crawl Budget Management](https://developers.google.com/search/docs/crawling-indexing/large-site-managing-crawl-budget)

### Impacto del sistema de contenido útil

Fusionado con el ranking core en marzo de 2024. Señal de todo el sitio: "cualquier contenido — no solo el contenido poco útil — en sitios determinados como con cantidades relativamente altas de contenido poco útil en conjunto tiene menos probabilidad de rendir bien en Búsqueda."

Las páginas traducidas de baja calidad pueden arrastrar todo el sitio. Es el argumento más fuerte contra crear páginas de locale que no sean genuinamente útiles.

- [Google Blog: Helpful Content Update](https://developers.google.com/search/blog/2022/08/helpful-content-update)
- [Amsive: What Changed in 2024](https://www.amsive.com/insights/seo/googles-helpful-content-update-ranking-system-what-happened-and-what-changed-in-2024/)

### Traducción parcial

Google: "Traducir solo el texto del boilerplate de tus páginas mientras mantienes el grueso de tu contenido en un solo idioma... puede crear una mala experiencia de usuario." Google usa el contenido visible (no el atributo lang) para determinar el idioma de la página.

Traduce TODO el contenido de una página si creas una versión de locale. Los metadatos sin traducir (título, descripción) en el idioma equivocado reducen el CTR.

- [Google: Managing Multi-Regional Sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)

### Crawl budget

Solo es una preocupación para 1M+ páginas o 10K+ páginas que cambian a diario. Pero las URLs alternativas (destinos hreflang) sí consumen crawl budget. Los enlaces hreflang rotos desperdician budget Y invalidan señales.

- [Google: Crawl Budget Management](https://developers.google.com/search/docs/crawling-indexing/large-site-managing-crawl-budget)
- [Google Blog: Crawl Budget](https://developers.google.com/search/blog/2017/01/what-crawl-budget-means-for-googlebot)

### Señales específicas de locale

Google identifica la audiencia vía: "direcciones y números de teléfono locales en las páginas, el uso del idioma y la moneda locales, enlaces desde otros sitios locales, o señales de tu Perfil de Empresa."

- [Google: Managing Multi-Regional Sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)
