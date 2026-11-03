---
name: frontend-design-skill
description: "Use when designing or reviewing frontend layout and CSS."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [frontend, design, css, layout, typography, color, motion, accessibility]
    related_skills: [design-extraction-and-fidelity, ui-ux-pro-max, tailwind-v4, responsive-mobile-qa]
---

# Frontend design skill

Use for any task where the deliverable is a **screen a human looks at**: landing pages, dashboards,
forms, cards, navigation. This user wants **custom CSS only — Tailwind is 2× rejected**; never reach
for it. Design is measured, not guessed: see `design-extraction-and-fidelity` for token extraction.

## Non-negotiables for this user

- **Custom CSS with variables.** No Tailwind, no Bootstrap, no component-library defaults.
- **2–3 demo variants before anything goes live.** Demos live in separate `.html` files, never on the
  live domain.
- **Preserve existing PHP logic and i18n** during any UI change. A redesign that breaks a form post
  or a translation key is a regression, not a redesign.
- **No `display:none` / `overflow:hidden` to hide a layout bug.** Fix the layout.
- **"mobile only" means do not touch desktop.**
- **Public sites: EN default + BG switcher.**
- Sections are **separate cards**, not one long undifferentiated column.
- Buttons need **high contrast** — never a low-contrast ghost on a dark surface.

## Layout

1. **Decide the grid before the pixels.** Content column, gutters, and the section rhythm
   (`padding` per section) come first. Most "it looks off" is wrong rhythm, not wrong colour.
2. **Vertical rhythm is a scale, not per-section ad-hoc values.** Pick a base (4 or 8 px) and reuse
   it. Measure the reference with `sectune.py` (see the fidelity skill) rather than eyeballing.
3. **Every grid cell needs an explicit min-height** if it holds a placeholder/leading cell, or the
   first row renders taller than the rest.
4. **Inline chips/badges use `width: fit-content`.** A `display:block` chip in a grid cell stretches
   to full width and turns tables into walls of colour.
5. **Full-bleed sections inside a max-width wrapper** need
   `width:100vw; margin-left:calc(50% - 50vw)` — and check `html{overflow-x:hidden}` afterwards or you
   introduce horizontal scroll.

## Typography

- Body 16 px / line-height 24 px as the default floor.
- **Named scale** (h1/h2/body/body-sm with size + weight + line-height), not ad-hoc font sizes.
- Tracking tightens as size grows: `letter-spacing:-0.5px` at 64 px, `+0.5px` on small caps.
- Display headings get their own family if the brand has one; body stays on the sans.

## Colour

- **Semantic tokens only**: `--bg`, `--bg-raised`, `--fg`, `--muted`, `--primary`, `--accent`.
  Components never reference raw hex.
- Verify contrast with real numbers — `#fafafa` on `#0f0914` is 18.81:1 (AAA); a pastel accent on a
  dark surface is often the pair that fails.
- Dark surfaces need **raised variants** (`--bg-raised`) or cards disappear into the page.

## Motion

- Durations from a scale: 120/180/250/350 ms. Never `transition: all 0.3s ease`.
- Animate `transform` and `opacity` only.
- **Respect `prefers-reduced-motion`** — and note that any screenshot comparison must disable
  animations, or two runs of the same page differ.

## Accessibility

- Every interactive element is a real `<a>` or `<button>`; icons get `aria-label`.
- `summary`-based accordions instead of JS-div click handlers.
- Never `outline:none` without a visible replacement focus ring.

## Verification before showing the user

1. Screenshot at 390 / 834 / 1440 px.
2. Check `document.documentElement.scrollWidth > clientWidth` at each width — horizontal scroll is the
   bug that silently ruins mobile.
3. Run `pixdiff.py` against the reference if there is one, and quote the number.
4. Never say "done" without a measured result.
