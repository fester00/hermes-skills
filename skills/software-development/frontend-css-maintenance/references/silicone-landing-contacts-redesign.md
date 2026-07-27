# Silicone-landing contacts section redesign note

Session: 2026-07-27.

## Problem

Icon wells in the contact section (`Mail`, `Phone`, `MapPin`) looked "broken" because the non-square Lucide silhouettes clashed with small circular wrappers on a busy video background.

## Final design

- Wrapper: `3.25rem × 3.25rem`, `border-radius: 1rem` (squircle), semi-transparent elevated surface.
- Icon size: `20px`, stroke width `1.5`.
- Hover: wrapper border brightens and lifts `translateY(-2px)`.

## Files changed

- `src/sections/Contact.tsx` — replaced inline Tailwind well with `.contact-icon-wrap` class.
- `src/index.css` — added `.contact-icon-wrap` rule.

## Verification

- `npm run build` ✅
- `npx oxlint` ✅
- Playwright screenshot of `#contact` at 2× scale showed clean wells.

## Note

Video background in `#contact` is intentionally left in place; user plans to swap it for a real video asset later.
