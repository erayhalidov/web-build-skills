---
name: frontend-design-skill
description: "Úsala al diseñar o revisar layout frontend y CSS."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [frontend, design, css, layout, typography, color, motion, accessibility]
    related_skills: [design-extraction-and-fidelity, ui-ux-pro-max, tailwind-v4, responsive-mobile-qa]
---

# Skill de diseño frontend

Úsala para cualquier tarea cuyo entregable sea **una pantalla que una persona mira**: landing pages, dashboards,
formularios, tarjetas, navegación. Este usuario quiere **solo CSS custom — Tailwind está rechazado 2×**; nunca
recurras a él. El diseño se mide, no se adivina: ver `design-extraction-and-fidelity` para la extracción de tokens.

## Innegociables para este usuario

- **CSS custom con variables.** Nada de Tailwind, nada de Bootstrap, nada de defaults de librerías de componentes.
- **2–3 variantes de demo antes de publicar nada.** Las demos viven en archivos `.html` separados, nunca en el
  dominio en producción.
- **Preserva la lógica PHP y el i18n existentes** en cualquier cambio de UI. Un rediseño que rompe un form post
  o una clave de traducción es una regresión, no un rediseño.
- **Nada de `display:none` / `overflow:hidden` para esconder un bug de layout.** Arregla el layout.
- **„solo móvil" significa no tocar el desktop.**
- **Sitios públicos: EN por defecto + selector BG.**
- Las secciones son **tarjetas separadas**, no una columna larga e indiferenciada.
- Los botones necesitan **alto contraste** — nunca un ghost de bajo contraste sobre una superficie oscura.

## Layout

1. **Decide la rejilla antes que los píxeles.** La columna de contenido, los márgenes y el ritmo de secciones
   (`padding` por sección) van primero. Casi todo "se ve mal" es ritmo incorrecto, no color incorrecto.
2. **El ritmo vertical es una escala, no valores ad-hoc por sección.** Elige una base (4 u 8 px) y reutilízala.
   Mide la referencia con `sectune.py` (ver la skill de fidelidad) en vez de hacerlo a ojo.
3. **Cada celda de la rejilla necesita un min-height explícito** si contiene un placeholder/celda inicial, o la
   primera fila se renderiza más alta que el resto.
4. **Los chips/badges inline usan `width: fit-content`.** Un chip `display:block` dentro de una celda de rejilla se
   estira a todo el ancho y convierte las tablas en muros de color.
5. **Las secciones full-bleed dentro de un wrapper con max-width** necesitan
   `width:100vw; margin-left:calc(50% - 50vw)` — y comprueba `html{overflow-x:hidden}` después, o
   introduces scroll horizontal.

## Tipografía

- Cuerpo 16 px / line-height 24 px como mínimo por defecto.
- **Escala con nombres** (h1/h2/body/body-sm con tamaño + peso + line-height), no tamaños de fuente ad-hoc.
- El tracking se aprieta a medida que crece el tamaño: `letter-spacing:-0.5px` a 64 px, `+0.5px` en versalitas.
- Los títulos display tienen familia propia si la marca la tiene; el cuerpo se queda en la sans.

## Color

- **Solo tokens semánticos**: `--bg`, `--bg-raised`, `--fg`, `--muted`, `--primary`, `--accent`.
  Los componentes nunca referencian hex crudo.
- Verifica el contraste con números reales — `#fafafa` sobre `#0f0914` es 18.81:1 (AAA); un acento pastel sobre
  una superficie oscura suele ser el par que falla.
- Las superficies oscuras necesitan **variantes elevadas** (`--bg-raised`) o las tarjetas desaparecen en la página.

## Motion

- Duraciones de una escala: 120/180/250/350 ms. Nunca `transition: all 0.3s ease`.
- Anima solo `transform` y `opacity`.
- **Respeta `prefers-reduced-motion`** — y ten en cuenta que cualquier comparación de screenshots debe desactivar
  las animaciones, o dos pasadas de la misma página difieren.

## Accesibilidad

- Cada elemento interactivo es un `<a>` o `<button>` real; los iconos llevan `aria-label`.
- Acordeones basados en `summary` en vez de handlers de click en divs con JS.
- Nunca `outline:none` sin un focus ring visible que lo reemplace.

## Verificación antes de enseñar al usuario

1. Screenshot a 390 / 834 / 1440 px.
2. Comprueba `document.documentElement.scrollWidth > clientWidth` en cada ancho — el scroll horizontal es el
   bug que arruina el móvil en silencio.
3. Ejecuta `pixdiff.py` contra la referencia si hay una, y cita el número.
4. Nunca digas "listo" sin un resultado medido.
