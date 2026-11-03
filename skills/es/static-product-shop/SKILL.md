---
name: static-product-shop
description: "Crea tiendas/catálogos estáticos (HTML+JS+PHP) desde CSV."
---

# Frontend de tienda / catálogo de producto estático

Construye una tienda online o catálogo autocontenido (categorías + filtros + formulario de pedido) a partir de un
archivo de datos de producto existente (export CSV/JSON), alojado como archivos estáticos planos en cualquier host.
Los puntos de entrada típicos son `catalog.html` (listado) e `index.html` (landing).

Disparador: el usuario pide "haz una tienda online / catálogo desde este CSV/archivo, con todas las categorías
y filtros de producto" para un sitio que ya tiene.

## Arquitectura (multipágina, sin framework)

1. `build_products.py` — parsea los datos de origen → `products.json` (única fuente de verdad)
2. `style.css` + `common.js` — estilos compartidos + utilidades compartidas: carrito en **localStorage**
   (`getCart/saveCart/addToCart/changeQty/removeItem/cartCount/cartTotal`), renderizador de cabecera
   (`renderHeader(active)`), `productCard(p)`, `fmt/esc/toast`, `loadData()` cacheado.
3. `index.html` — catálogo: árbol de categorías + desplegables de filtro + búsqueda + ordenación + rejilla de productos.
   Las tarjetas enlazan a `product.html?id=X`.
4. `product.html?id=X` — una página por producto (imagen, tabla de especificaciones, descripción, relacionados).
5. `order.html` — checkout: ítems del carrito desde localStorage + formulario de entrega.
6. `order.php` — acepta POST JSON, anexa a `orders.json` + escribe `orders.log`.

**El usuario prefiere PÁGINAS SEPARADAS (catálogo / producto / pedido), no una SPA con
modales.** Si primero entregas un modal + mini-carrito en una sola página, espera que te pidan dividirlo
en páginas después. Empieza multipágina.

## Pasos

1. **Inspecciona primero las columnas de origen** — `head -5` más una pasada rápida con `collections.Counter`
   de Python para enumerar categorías, filtros, fabricantes, rango de precio, reparto de stock. Nunca escribas
   el generador a ciegas.
2. **Normaliza a products.json** con un objeto plano por producto:
   `id, name, manufacturer, price, special, image, stock, description, categories[] (rutas completas), filters{} (grupo→[valores]), related[]`.
3. **Genera el árbol de categorías** a partir de las cadenas de ruta (corta por el separador de jerarquía,
   p. ej. `>`), luego asigna cada producto a todas sus rutas de categoría; casa una categoría con la
   regla de prefijo `c === path || c.startsWith(path + '>')`.
4. **Construye index.html** — árbol lateral con contadores, un `<select>` por grupo de filtro, búsqueda,
   ordenación (precio asc/desc, nombre), rejilla de tarjetas. Las tarjetas enlazan a `product.html?id=<id>`; el
   botón "añadir al carrito" llama `addToCartById(id)`. Soporta los params `?q=` y `?cat=` para que
   la búsqueda y las migas de pan del producto puedan enlazar en profundidad.
5. **Construye product.html** — lee `?id=`, renderiza imagen / tabla de especificaciones / descripción / relacionados,
   migas de pan que enlazan a `index.html?cat=<path>`. Botones: "añadir al carrito" + "comprar ahora" (añade
   y luego `location.href='order.html'`).
6. **Construye order.html** — lee el carrito de localStorage, steppers de cantidad + quitar, total, formulario de
   entrega. Enviar → order.php; al éxito `saveCart([])` y muestra el id de pedido devuelto.
7. **order.php** — valida nombre/teléfono/dirección, anexa a `orders.json` (JSON_PRETTY_PRINT |
   JSON_UNESCAPED_UNICODE) y anexa una línea legible a `orders.log`. Devuelve `{ok:true, order_id}`.
8. **`chown -R <webuser>:<webuser>` al dir de la tienda** — los archivos escritos como root rompen las escrituras de PHP
   y las lecturas de PHP-FPM. (Los sitios CloudPanel corren como el usuario del sitio, p. ej. `oem`.)
9. **Verifica en vivo** — `curl` a la URL (espera 200), `curl -X POST` de un pedido de prueba, confirma la escritura
   del archivo, luego borra el pedido de prueba para que la tienda empiece vacía.

## Pitfalls

- **Encaja con el tema existente del sitio**: extrae los colores hex principales de la hoja de estilos del sitio
  (`grep -oiE '#[0-9a-f]{6}' .../stylesheet.css | sort | uniq -c | sort -rn`) y reutilízalos como
  variables CSS. Dos combinaciones que funcionan bien: azul marino oscuro `#0D1322` + naranja `#FF7A00`, o casi negro
  `#0e0f12` + rojo `#e30613`.
- **NUNCA hardcodees teléfono / email / envío gratis de memoria.** Léelos de los ajustes de la BD de la tienda
  (ver `references/opencart-csv.md`). Un número copiado de una tienda a otra es
  un bug real y vergonzoso — consulta siempre `oc_setting`.
- **`onerror` de imagen en handlers inline**: escribe `onerror="this.style.display='none'"` exactamente.
  Las variantes con barras invertidas escapadas matan el bloque `<script>` entero en silencio.
- **Moneda/locale**: muestra el dinero con el separador decimal del locale (coma para BG/DE, punto para EN)
  (`n.toFixed(2).replace('.', ',') + ' €'`). No asumas BGN si no te lo dicen.
- **Override de precio `special`**: usa `price_special` solo cuando esté puesto Y `> 0` Y `< price`.
- **Añadir al carrito asíncrono**: `addToCart` necesita un objeto producto. En los botones de tarjeta llama
  `addToCartById(id)` (que hace `findProduct(id).then(addToCart)`) en vez de inlinear
  `JSON.stringify(product)` en el onclick — inlinear el objeto completo (incluida la descripción
  HTML) hincha la página y arriesga roturas de comillas/HTML. Ojo: `findProduct` devuelve una
  promesa, así que un `getCart()` síncrono justo después de `addToCartById()` en un test sigue
  mostrando vacío — haz `await` de la promesa primero.
- **Renombrar marca ("cambia X→Y en todas partes")**: el CSV de *origen* puede seguir conteniendo el texto viejo
  de la marca en columnas que no renderizas (p. ej. una columna `store` sin usar). Haz grep solo de los
  archivos renderizados (`grep -rliE "X" --include="*.html" --include="*.js" --include="*.css"
  --include="*.json" --include="*.php" .`), no del archivo de datos crudo, para confirmar el renombrado.
  Renombra también el email visible si el usuario dice "todo", pero avísalo para que puedan revertirlo
  si ese buzón no es real.
- **Ruta de servido**: una subcarpeta como `/shop/` la recoge el `try_files ... index.php` existente de nginx
  del sitio solo porque `index.html` existe y `.json` recibe `application/json`.
  Verifica el mime type del JSON con `curl -sI` (algunos setups no necesitan config, pero compruébalo).

## Referencias

- `references/opencart-csv.md` — columnas de export de producto OpenCart 2.x, parseo de cadenas de
  categoría/filtro, y lectura de ajustes de tienda desde la tabla `oc_setting`.
