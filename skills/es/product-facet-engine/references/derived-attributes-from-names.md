# Derivar atributos filtrables a partir de nombres de producto

Para feeds sin propiedades técnicas (CSVs tipo ERP/Icecat: solo nombre + EAN + peso + precio).
Los valores derivados se escriben en la tabla normal `product_properties` en el momento de la importación, así el motor de
facetas, el SQL de filtros y la tabla de especificaciones siguen funcionando sin cambios.

## Catálogo de atributos y la regla que de verdad funcionó

| Atributo | Esbozo de la regla | Normalización |
| --- | --- | --- |
| `Colour` | lista de palabras: black, white, silver, grey/gray, blue, red, green, yellow, pink, purple, orange, brown, gold, transparent, beige | `gray→Grey`; dos colores → `Black / White` |
| `Memory type` | `DDR[2345]L?` | + ` SODIMM` / ` RDIMM` / ` UDIMM` cuando el nombre lo dice |
| `Capacity` | `(\d+(?:[.,]\d+)?)\s*(TB|GB)` **y** el nombre menciona SSD/HDD/tape/flash/NVMe/microSD | `1024 GB → 1 TB`; dos valores → `1 TB + 512 GB` |
| `Memory size` | misma captura numérica, el nombre menciona DDR/RAM/memory module/SODIMM | como arriba |
| `Storage capacity` | misma captura, el nombre menciona notebook/desktop/server/tablet/phone | como arriba |
| `Interface` | primera coincidencia de NVMe, PCIe, SATA, M.2, Thunderbolt, USB-C, USB 3.x, USB 2.0, HDMI, DisplayPort, DVI, VGA, RJ45, SAS, Fibre Channel, Serial | gana la primera coincidencia, ordenada por especificidad |
| `Screen size` | `(\d{2}(?:[.,]\d)?)\s?("|inch|in|')`, acotado **10–120** | recorta ceros finales → `27 inch` |
| `Resolution` | `4K|UHD|QHD|WQHD|UWQHD|Full HD|FHD|WUXGA|XGA|HD`, si no `W x H` → mapeado | `UHD → 4K UHD`, `1920x1080 → Full HD` |
| `Wi-Fi` | `Wi-?Fi ?[4567E]` o `802.11(ax|ac|be|n)` | `802.11ax → Wi-Fi 6`, `802.11ac → Wi-Fi 5` |
| `Speed` | `(\d+(?:[.,]\d+)?)\s*(Gbit|Gbps|GbE|igabit)`, acotado **1–400**; `\d{2,4}\s?Mbit` | `rtrim(rtrim($v,'0'),'.').' Gbit'` |
| `PoE` | `PoE\+` antes que `PoE` simple | `PoE+` / `PoE` |
| `Ports` | `\b(\d{1,3})[-\s]?port` o `\b(\d{1,2})\s?x\s?(RJ-?45|LAN|Gigabit|GE)` | `8 ports` |
| `Power` / `Capacity (VA)` | `(\d{3,4})\s?W(?:att)?` acotado 45–4000; `(\d{2,4})\s?VA` | `650 W`, `1000 VA` |
| `Length` | `(\d+(?:[.,]\d+)?)\s?(m|mm|cm)` acotado 0.1–100 m | cm → m, `2 m` |
| `Form factor` | `2.5"/3.5" HDD/SSD/drive` o `M.2 (2230/2242/2280/22110)` o `\b[124]U\b` | mayúsculas |
| `Print colour` | black/cyan/magenta/yellow **cerca de** toner/cartridge/ink | `Black` |
| `Paper size` | `A3|A4|A5|A6` **y** paper/print/photo/label/film/designjet en el nombre | tal cual |

## Por qué importan los límites y el requisito de sufijo

Estos son los falsos positivos que aparecieron de verdad en producción y cómo se eliminaron:

* `Speed = 4 Gbit` en routers LTE — la regex coincidía con la generación móvil `4G`. Arreglo: exigir un
  sufijo de tasa explícito (`Gbit|Gbps|GbE|igabit`) **y** un rango 1–400.
* `Screen size = 1 inch` — venía del segundo patrón sin límites. Arreglo: el mismo límite 10–120 en todas
  las ramas, no solo en la primera.
* `Screen size = 45 inch` en equipos de red — `19 inch` para raíles de rack es correcto, 45 no; mantén
  el límite superior de todas formas.
* `Paper size = A5` en monitores — `A3`/`A5` aparecen dentro de números de pieza. Arreglo: exigir contexto de papel/impresión.
* `Speed = 83 Gbit` — la regex cogió un número aleatorio seguido de `G`. Mismo arreglo de rango.

## Reglas de ordenación y fusión

1. Extrae solo cuando la propia fila del feed no tiene esa propiedad (el feed XML ya proporciona `Memory type`,
   `Screen size`, …) — si no, degradas datos reales del proveedor con una conjetura de regex.
2. Guarda con un valor `sort` alto para que la tabla de especificaciones muestre primero las propiedades del feed.
3. Vuelve a ejecutar el importador tras cambios de reglas; la caché de facetas se indexa por `built_at`, así que los contadores se refrescan.

## Bucle de verificación que encontró todos estos

```php
// imprime los valores de faceta principales por categoría grande y los mira a ojo
foreach (['networking','monitors-accessories','computer-components','notebooks-tablets'] as $cat) {
    foreach (spec_facets(['cat' => $cat], 6, 8) as $g) {
        printf("%-22s cov=%-5d %s\n", $g['name'], $g['cov'],
            implode(' | ', array_map(fn($v) => $v['value'] . ' (' . $v['n'] . ')', array_slice($g['values'], 0, 4))));
    }
}
```

Los valores que se leen como absurdo (`1 inch`, `4 Gbit`, `A5` en monitores) son siempre una regla que necesita un límite,
un sufijo o una palabra clave de contexto. Una cobertura de facetas del ~70–80 % del catálogo es un buen resultado; el
resto sin casar es real (a los feeds les falta el dato de verdad) y no debe forzarse a un cajón.
