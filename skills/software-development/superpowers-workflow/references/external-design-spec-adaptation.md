# Adapting an External Design Spec to an Existing Project

Use this reference when the user provides a detailed design instruction (e.g. a Figma-like spec, a pasted design-system recipe, or a reference site breakdown) and wants it applied to an existing codebase while keeping content, SEO, semantics, and functionality intact.

## Core principle

The external spec is the *visual language*, not the *content strategy*. Preserve the existing project's data, copy, SEO metadata, semantic heading hierarchy, accessibility affordances, and business logic. Strip from the spec anything that contradicts the existing domain (e.g. generic marketing videos, fake testimonials, unrelated product imagery).

## Pre-execution checklist

1. **Read the spec and the current project state.**
   - Load the spec into the plan verbatim.
   - Inspect `src/lib/data.ts`, `src/app/layout.tsx`, `page.tsx`, and key components.
   - Note current fonts, colors, component boundaries, and client/server split.

2. **Identify conflicts early.**
   - Generic video/image URLs in the spec → replace with project assets or ask the user.
   - Spec expects 3 feature cards but the project has 4 catalog items → adapt layout, don't drop data.
   - Spec uses Latin-only fonts but content is Cyrillic → switch to a Cyrillic-compatible equivalent (e.g. PT Serif italic instead of Instrument Serif).

3. **Lock the constraints in the plan.**
   - Keep `data.ts` types and content unchanged.
   - Preserve SEO: metadata, JSON-LD, `robots.txt`, `sitemap.xml`.
   - Preserve semantic HTML: one `<h1>`, `<h2>` for sections, `<h3>` for cards.
   - Preserve accessibility: modal roles, focus traps, escape handling, mailto form logic.
   - All interactivity must remain `"use client"`.

## Execution pattern

Group subagents by subsystem, not by file type. For a landing redesign:

- **Group A — Global shell:** fonts, CSS variables, Tailwind config, navbar, hero.
- **Group B — Content sections:** about, products/features, any sticky/scrolling layouts.
- **Group C — Conversion + footer:** stats, contact, form, modal, footer.

Each group gets the full spec + the list of files it may touch. After all groups return, run integration in the controller session.

## Pitfalls specific to design adaptation

### 1. SSR-invisible reveal animations

Specs often describe scroll-triggered entrance animations (`translate-x-16 → 0`, `opacity 0 → 1`). If implemented naively with `initial={{ opacity: 0 }}` + `whileInView`, the statically rendered page is blank until the client IntersectionObserver fires. This breaks:
- first paint
- full-page screenshots
- users with JS disabled / slow JS

**Fix:** keep the element visible in the initial state and animate only transform. For example:

```tsx
initial={{ opacity: 1, x: 64 }}   // visible, just offset
whileInView={{ opacity: 1, x: 0 }} // slides in, never disappears
viewport={{ once: true, amount: 0.6 }}
```

For non-motion fallback, ensure content is readable without JS.

### 2. Sticky parent / scrolling child mismatch

A sticky left column with a scrolling right column only works if the parent section is tall enough. Verify:
- the section has enough vertical space for all cards to scroll past the sticky column;
- cards are not `opacity: 0` by default (see above);
- the active-indicator IntersectionObserver threshold does not fight the reveal observer.

### 3. Font subset mismatch

`next/font/google` subsets matter. If a decorative italic font (e.g. Instrument Serif) only ships `latin`, Cyrillic italic text will fall back to a system serif. Either:
- choose a Cyrillic-compatible font (e.g. PT Serif), or
- import the original font via CSS `@import` and accept no automatic optimization.

### 4. Generic spec assets

When the spec includes URLs for hero videos or feature videos that belong to another product:
- search the existing project directories for real assets first;
- if nothing exists, use an abstract gradient/particle fallback and tell the user the slot is ready for their video.

### 5. Color-only cards on light backgrounds

A spec may call for `bg-black/20` cards. On a warm cream page this becomes muddy gray and kills contrast. Convert to solid warm surfaces (`#FFF9F2`, `#F6E4CF`) with subtle borders and shadows instead of translucent dark overlays.

### 6. Uniform card heights in grids

When the spec produces cards of varying height because of different description/feature counts, enforce a uniform height:
- set `min-h` on the card root;
- use `flex flex-col` + `mt-auto` on the bottom row;
- clamp description text with `line-clamp-2` or `line-clamp-3`;
- fix image container size so images don't stretch cards.

For feature lists, increase feature tag size (`text-sm`/`text-base`), padding (`px-3 py-1.5` or more), and use an accent background instead of a faint border so the properties read as product attributes, not metadata.

### 7. Video backgrounds

When adding a spec video behind a section:
- copy the asset into the project's `public/video/` directory rather than hotlinking;
- add an overlay (`bg-<theme>/85` or `bg-black/20`) so text stays readable;
- test on mobile: autoplay muted loop is required; provide a poster/fallback color.

## Verification steps

After integration:
1. `npx tsc --noEmit`
2. `npm run build`
3. Start production server and run Playwright smoke tests.
4. Capture full-page desktop + mobile screenshots.
5. Inspect screenshots for:
   - invisible sections due to `opacity: 0` initial states;
   - unreadable text over busy video/backgrounds;
   - cards blending into backgrounds;
   - cards of different heights;
   - leftover artifacts from the old UI.
6. Update `e2e-smoke.js` selectors if the DOM structure changed.
7. Serve with `--host 0.0.0.0` (Vite) or `-H 0.0.0.0` (Next.js) so the user can preview from another device on the LAN.

## When to stop

The goal is a faithful *adaptation*, not a pixel-perfect clone. If a spec element cannot be made to work with the existing content, surface the trade-off to the user instead of forcing the mismatch.

## Provenance

- 2026-08-01: Drift-style spec applied to `silicone-lending-v3` (Next.js 15). Switched Instrument Serif → PT Serif for Cyrillic, copied hero video from `silicone-landing/public/video`, enforced uniform card heights and accent feature tags in the Vite-based `silicone-landing-v2` as well.
