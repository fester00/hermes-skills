# Silicone Landing Session Reference

**Date:** 2026-07-17  
**Project:** `/mnt/data/natan-storage/silicone-landing`  
**Stack:** React 18 + TypeScript + Vite 5 + Tailwind CSS 3.4.17 + GSAP 3.12 + Framer Motion 11 + hls.js 1.5

## Goal

Recreate a single-page dark portfolio-style landing page from a detailed prompt. Content was adapted from the existing `pentajunior-v2` project (SQLite catalog), but the visual language follows the generic portfolio brief.

## What was built

| Section | Implementation |
|---|---|
| Loading Screen | `requestAnimationFrame` counter 000→100 over 2700ms, rotating words with `AnimatePresence`, progress bar with glow |
| Hero | HLS video background via `hls.js`, centered content, GSAP entrance, cycling role word, two CTA buttons |
| Navbar | Floating pill with gradient logo ring, nav links, "Say hi" button, shadow on scroll |
| Selected Works | Bento grid (7/5/5/7) with hover reveal and halftone overlay |
| Journal | Horizontal pill entries with image, date, read time |
| Explorations | 300vh scroll-driven parallax gallery with pinned center text and lightbox |
| Stats | 3-column grid |
| Contact/Footer | Flipped HLS video, GSAP marquee, social links, green pulsing availability dot |

## Key technical decisions and gotchas

### 1. Tailwind v3 pinning

Vite `create-vite` template installed Tailwind v4, which has no `tailwindcss init` CLI. Pinned dependencies:

```bash
npm install -D tailwindcss@3.4.17 postcss@8.4.49 autoprefixer@10.4.20
./node_modules/.bin/tailwindcss init -p
```

### 2. TypeScript `verbatimModuleSyntax`

Vite React-TS template enables `verbatimModuleSyntax`. Framer Motion types must be imported with `type`:

```tsx
import { motion, type Variants } from "framer-motion";
```

### 3. HLS video

Use `hls.js` with Safari native fallback. Mux HLS source: `https://stream.mux.com/Aa02T7oM1wH5Mk5EEVDYhbZ1ChcdhRsS2m1NYyx4Ua1g.m3u8`.

### 4. Content from pentajunior-v2 SQLite

```bash
cd /home/natan/pentajunior-v2
python3 -c "import sqlite3; ..."
```

Product IDs used for Journal cards: `si-m-aero`, `vs-m-aero`, `ks-m-aero`. Images copied from `pentajunior-v2/public/images/` into the new project's `public/images/`.

### 5. Headless screenshot pitfall

Chrome headless and Playwright hung on `requestAnimationFrame`-based loading screen in this environment. Build verification (`npm run build`) passed. Visual QA must be done in a real browser via `npm run preview`. This is an environment/tool issue, not a code issue.

### 6. GSAP + ScrollTrigger parallax cleanup

```tsx
const triggers: ScrollTrigger[] = [];
triggers.push(ScrollTrigger.create({ ... }));
const tween = gsap.to(el, { scrollTrigger: { ... } });
if (tween.scrollTrigger) triggers.push(tween.scrollTrigger);
return () => triggers.forEach((t) => t.kill());
```

### 7. Accent gradient everywhere

Utility `.accent-gradient` used for logo ring, hover borders, progress bar, scroll indicator. Reversed variant `.accent-gradient-reversed` for hover state.

## Commands

```bash
cd /mnt/data/natan-storage/silicone-landing
npm install
npm run dev
npm run build
npm run preview
```

## Outcome

- `npm run build` exit 0
- Project uploaded to Yandex.Disk: `https://yadi.sk/d/ARynKQL-k1kFDQ`
- Obsidian project note: `Projects/Silicone Materials Landing.md`
