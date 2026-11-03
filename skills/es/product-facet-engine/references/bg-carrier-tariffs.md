# Tarifas de transportistas búlgaros (Speedy / DPD) — tarifas publicadas para tiendas de catálogo

Banco de conocimiento para peticiones de "añade precios de envío reales a cada país europeo". Cada cifra de aquí
proviene de la lista de precios publicada por el transportista — nunca extrapoles a un destino que no esté listado.

## Datos de descubrimiento (ahorra una hora la próxima vez)

| Dato | Detalle |
| --- | --- |
| `www.dpd.bg` | Redirige a las páginas internacionales de **Speedy** — Speedy opera la red DPD en Bulgaria, así que "Speedy - DPD" es una oferta, no dos presupuestos. |
| `https://www.dpd.bg` (443) | Conexión rechazada desde el servidor. El `http://www.dpd.bg/` simple responde 200 y emite la redirección a speedy.bg. |
| `https://www.speedy.bg/...` | Challenge JS de Cloudflare "Just a moment…" — un fetch simple recupera la página del challenge, y un Chromium headless también se atasca ahí. |
| `https://services.speedy.bg/priceList/?lang=en` | **La lista de precios real.** 200 ante un curl simple con un UA de navegador normal, sin challenge. El `<title>` lleva la fecha de la versión (`Speedy Price List 13.09.2026`) — cita esa fecha a los clientes. |

```bash
curl -sSL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36" \
  -o /tmp/sp_pl.html "https://services.speedy.bg/priceList/?lang=en"
```

Parsear la página (~200 KB de tablas inline):
```python
import re, html as H
s = open('/tmp/sp_pl.html', encoding='utf-8', errors='replace').read()
flat = H.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '|', s))).replace('\xa0', ' ')  # los precios usan &nbsp;
flat = re.sub(r'\|+', '|', flat)
```
* El `\xa0` entre el importe y el signo € rompe cualquier regex de precios — normalízalo primero.
* La fila de cabecera suele estar en su propia `<table>` mientras las filas de países quedan fuera de ella, así que cortar
  entre los límites de `<table>…</table>` pierde el cuerpo. Corta el **texto aplanado** entre el título del servicio
  y el párrafo de boilerplate siguiente.
* Los nombres de país pueden llevar paréntesis (`CROATIA (LOCAL NAME: HRVATSKA)`) — si haces match con
  `[A-Z][A-Z \.\-\(\)']{3,60}` aún los perderás; verifica el número de filas contra la lista de zonas.

## Servicios de salida desde Bulgaria

| Código | Servicio | Bandas de peso | Notas |
| --- | --- | --- | --- |
| 202 | Speedy CEE Economy | 1, 2, 3, 4, 5, 7, 10, 20, 31.5 kg | Última banda RO/GR `21.72 € + 1.09 € por cada kg extra`. |
| 306 | DPD Economy — puerta a puerta | 0.5, 5, 10, 31.5, 40 kg | Servicio terrestre de Europa Occidental / del Norte. |
| 308 | DPD Economy **Solicitud de recogida** | 0.5, 5, 10, 31.5, 40 kg | Recogidas de entrada **a** Bulgaria — nunca cotices esto para pedidos de salida. |
| 302 | Speedy Air Express | pasos de 0.5 kg, 20 bandas hasta 10 kg | Zona 1 (UE fuera de la red terrestre), Zona 2 (Europa no UE), 3/4 (resto del mundo). Por encima de 10 kg → a consultar. |

Todos los importes publicados **ya incluyen IVA y el recargo por combustible**.

## Mapeo país → servicio

* **202 CEE Economy** — RO, GR, HU, CZ, PL, SK, SI, HR, CY
* **306 DPD Economy** — AT, DE, BE, FR, IT, NL, DK, LU, ES, EE, FI, LV, LT, PT, SE
* **302 Air Zone 1** — IE, MT (la lista de zona 1 también nombra AT, BE, HR, CY, CZ, DK, EE, FI, FR, DE, GR, HU, IE, IT, LV, LT, LU, MT, NL, PL, PT, SK, SI, ES, SE)
* **302 Air Zone 2** — AL, AD, BA, FO, GI, GL, VA, IS, LI, MC, ME, NO, SM, RS, CH, TR, GB, GG, JE, Canarias
* **No listado en ningún sitio** (UA, US, …) → "precio a consultar". No interpoles.

Plazos de tránsito tal como se imprimen: DE/AT/CZ/PL 3-4 · HU/SK 2-3 · SI 3-4 · HR/BE/FR/IT/NL/DK/LU/LV/LT 4-5 · ES 5-6 ·
SE 5-6 · EE 5-6 · FI/PT 5-7 · Air Zone 1 1-2 · Air Zone 2 1-3. RO/GR/CY **no** se imprimen — omite la
columna en vez de adivinar.

## Matriz de precios (versión 13.09.2026)

202 CEE Economy, bandas 1 → 31.5 kg:
```
RO        5.27  5.71  6.13 10.96 10.96 13.63 16.76 21.72 21.72 (+1.09 €/kg over 31.5)
GR        6.44  7.36  7.36 10.96 10.96 13.63 16.76 21.72 21.72 (+1.09 €/kg over 31.5)
HU        8.84  9.70 10.57 23.17 23.17 27.68 27.68 27.68 27.68
CZ        8.84  9.70 10.57 32.21 32.21 38.22 38.22 38.22 38.22
PL/SK/SI/HR 8.84 9.70 10.57 45.76 45.76 51.04 51.04 53.14 53.14
CY       17.03 19.21 21.36 23.72 25.87   —     —     —     —   (only to 5 kg)
```

306 DPD Economy, bandas 0.5 / 5 / 10 / 31.5 / 40 kg:
```
AT, DE                     23.78 23.78 28.32 28.32  65.14
BE, FR, IT, NL             32.82 32.82 38.83 38.83  75.67
DK, LU                     44.26 46.38 51.64 53.77  90.58
ES                         42.59 42.59 50.11 50.11  86.94
EE, FI, LV, LT, PT, SE     63.28 65.38 71.71 74.89 111.72
```

302 Air Express: zona 1 desde 68.41 € (≤0.5 kg) subiendo ~10-15 € por paso de 0.5 kg; zona 2 desde 84.08 €.
Transcribe las 20 filas publicadas en vez de aproximar.

Recargos que existen (menciónalos en el FAQ, no los sumes en silencio a un presupuesto): código postal de isla/zona
remota 28.06 € (202) / 26.54 € (308) con IVA · paquete pesado >50 kg 12.77 € · manipulación manual si un lado >100 cm
1.94 € · reembolso (COD) 2.4 % (mín. 1.23 € internacional). Promoción vigente en la última comprobación: **-25 % sobre
los precios de la tarifa 306 para DE e IT, 01.09.2024 – 30.09.2026**.

## Conectarlo al sitio

`inc/shipping.php`:
* `shipping_services()` — etiqueta, transportista, lista de bandas, nota por clave de servicio
* `shipping_rates()` — servicio → grupo de destino → precio por banda (arrays en el mismo orden que las bandas)
* `shipping_map()` — ISO2 → `['service' =>, 'group' =>, 'days' =>]`
* `shipping_quote($cc, $kg)` — primera banda en la que cabe el peso; **`price = null` cuando se pasa de las bandas
  publicadas** para que la UI pueda decir "a consultar" en vez de adivinar
* `shipping_pickup()` (gratis, 0.00) y `shipping_options()`
* `shipping_updated()` — el string de versión que se muestra a los clientes

El peso viene del catálogo (`products.weight`; aliasalo `AS weight_kg` en los SELECT compartidos), sumado
sobre la cantidad. Los artículos sin peso aportan una estimación documentada de 0.5 kg y la página dice que el
peso es parcialmente estimado. Recalcula todo **en servidor en el POST** desde el slug del producto — no se confía
en la cesta del navegador para precios ni pesos.

Renderizado: una tabla de precios en la página de envíos (`Delivery prices to every European country`) construida desde
los mismos arrays, para que nunca pueda desviarse del checkout. Cambian las tarifas → reemplaza los tres arrays, sube
`shipping_updated()`, vuelve a pasar el barrido de rutas.
