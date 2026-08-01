# Design Adaptation Checklist

Use when the user wants to apply an external design instruction/spec to an
existing project while keeping the original content, SEO, semantics, and
functionality.

## When this applies

- A reference design system or landing-page instruction is provided.
- The target project already has data, components, routes, SEO, and business logic.
- The goal is "style like X" but with our content, not a full re-implementation.

## Pre-implementation checklist

1. **Audit the source design**
   - Extract: fonts, palette, radii, spacing, motion, layout patterns, component
     primitives, iconography.
   - Note video/image assets and their paths. If the user says "use video from
     project Y", verify the path exists before writing code.

2. **Audit the target project**
   - Read `src/lib/data.ts` (or equivalent) — never change business data unless
     asked.
   - Read `src/app/layout.tsx` — preserve metadata, JSON-LD, fonts.
   - List sections/components and decide which map to the new design.

3. **Decide mapping, not cloning**
   - Hero → hero (adapt copy, keep one h1).
   - About/intro → new warm section or existing intro.
   - Features/cards → existing catalog or services.
   - CTA/contact → existing form + contact info.
   - Footer → existing footer with new tokens.

4. **Asset verification**
   - Video: `find /path -type f \( -name "*.mp4" -o -name "*.webm" \)`
   - Images: list expected images and confirm they exist or have fallbacks.
   - Fonts: prefer `next/font/google` over `@import` in production Next.js.

5. **SSR/SSG safety**
   - Any entrance animation must use `initial={{ opacity: 1, ... }}` with
     `whileInView` to keep static previews visible.
   - See `references/framer-motion-ssr-initial-opacity.md`.

## Implementation pattern

1. Write a plan in `.hermes/plans/YYYY-MM-DD_<slug>-design-adaptation.md`.
2. Run parallel subagents by layer:
   - Layer A: tokens, fonts, layout, global styles.
   - Layer B: Hero, About, main content sections.
   - Layer C: Footer, modal, form, interactions.
3. Verify after each layer: `npx tsc --noEmit`, `npm run build`.
4. Do not let parallel agents edit the same file; split by file ownership.

## Common pitfalls

- Copying proprietary brand assets (exact videos, illustrations, copy) without
  confirming rights.
- Replacing SEO metadata while changing fonts/palette.
- Dropping semantic heading hierarchy when redesigning.
- Using `opacity: 0` initial state for Framer Motion sections.
- Letting OpenCode handle multi-file design adaptation headlessly — it
  truncates on large briefs. Use `delegate_task` subagents instead.

## Session provenance

2026-08-01 — adapted a warm cream/dark "Drift" style instruction to the
tech-dark B2B landing `silicone-lending-v3`. Kept product catalog,
mailto form, SEO, and semantic HTML. Copied video asset from
`/mnt/data/natan-storage/silicone-landing/public/video/video.mp4` to
`/mnt/data/natan-storage/silicone-lending-v3/public/video/hero.mp4` after
verifying its existence. Used three parallel Hermes subagents (Groups A/B/C)
to implement tokens, sections, and interactions.
