# VIDVIS Project — Session Reference (Updated v3.1)

## Project: VIDVIS — Art Gallery & Home Textile (Luxury Immersive)

Luxury immersive landing page evolved across multiple sessions. Current v3.1: PerspectiveScene (CSS 3D entry) → ArtGallery → ParallaxDivider → HomeTextile → **Technologies** → Products → Footer.

## Tech Stack

```
next@14.2.35, react@18.3.1, typescript@5.5.0
GSAP@3.12.5 (ScrollTrigger)
Lenis@1.1.13 (smooth scroll)
Tailwind CSS@3.4.19
framer-motion@11.3.0 (Motion.dev declarative animations)
@react-three/fiber@8.16.8, three@0.164.1
```

## File Structure

```
vidvis/
├── package.json              # deps: GSAP, Lenis, framer-motion, Three.js
├── next.config.js            # images.remotePatterns: unsplash, wallpaperscraft
├── tsconfig.json
├── tailwind.config.ts        # custom fonts + vidvis tokens
├── postcss.config.mjs        # MUST be .mjs with export default
├── public/images/            # Local FullHD nature images from wallpaperscraft.ru
└── src/
    ├── app/
    │   ├── layout.tsx        # 4 Google Fonts: Inter, Playfair, Cormorant, Oranienbaum
    │   ├── page.tsx          # PerspectiveScene → ArtGallery → ParallaxDivider → HomeTextile → Technologies → Products → Footer
    │   └── globals.css       # grain, cursor (magnetic-cursor), scrollbar, lenis
    ├── components/
    │   ├── PerspectiveScene.tsx   # CSS 3D entry: perspective 2000px, 5 depth layers
    │   ├── ParallaxDivider.tsx    # Reusable full-screen parallax section breather
    │   ├── ArtGallery.tsx         # Grid cards with 3D tilt + inner-image parallax
    │   ├── HomeTextile.tsx        # Horizontal scroll (pin) on desktop
    │   ├── Technologies.tsx       # 🆕 v3.1: Tech stack showcase with Motion.dev animations
    │   ├── Products.tsx           # 4-col grid + stagger entrance
    │   ├── Navigation.tsx         # Glassmorphism sticky
    │   ├── Footer.tsx             # 3-col + reveal
    │   ├── Preloader.tsx          # GSAP curtain + progress
    │   └── MagneticCursor.tsx     # Custom + mix-blend-mode difference
    └── hooks/
        └── useLenis.ts            # Lenis init + GSAP ticker sync
```

## PostCSS Config (CRITICAL)

```js
/** @type {import('postcss-load-config').Config} */
const config = {
  plugins: { tailwindcss: {}, autoprefixer: {} },
};
export default config;
```

## Run Commands

```bash
cd /home/natan/projects/vidvis
npm install
./node_modules/.bin/next build    # static export
./node_modules/.bin/next dev -p 3001
```

## Evolution: v1 → v3.1

| Version | Entry | Depth | Fonts | Key Additions |
|---------|-------|-------|-------|---------------|
| v1 | Hero (classic parallax) | None | Playfair + Inter | Initial build |
| v2 | Hero + sections | CSS 3D tilt cards | + Oranienbaum, Cormorant | ParallaxDivider, local images |
| v3 | **PerspectiveScene** | CSS 3D `perspective: 2000px`, 5 layers | All 4 fonts | Single CSS 3D entry |
| v3.1 | PerspectiveScene | Same | Same | **Technologies** section (Motion.dev), cursor lerp fix |

## Technologies Section (v3.1)

Dedicated tech showcase between HomeTextile and Products.

**Pattern:**
- `framer-motion` `variants` + `staggerChildren` for card entrance
- `whileHover` with `rotateY`, `rotateX`, `translateZ` for 3D tilt
- Tier badges: core (gold), animation (blue), design (rose)
- Bottom accent line `w-0 group-hover:w-full`

**Tech cards displayed:**
| Name | Role | Tier |
|------|------|------|
| Next.js 14 | App Router, SSR/SSG | core |
| React 18 | Concurrent features | core |
| TypeScript | Type-safe | core |
| Tailwind CSS | Utility-first | core |
| GSAP + ScrollTrigger | Scroll animations | animation |
| Lenis | Smooth scroll | animation |
| **Motion.dev** | Declarative React animations | animation |
| Three.js | WebGL 3D | animation |
| next/font/google | Cyrillic fonts | design |
| next/image | Optimized images | design |

## Custom Cursor — Lerp Optimization

**Default lerp (0.15) causes visible lag.** Luxury sites need snappy cursor.

```typescript
// MagneticCursor.tsx — animate loop
pos.current.x += (target.current.x - pos.current.x) * 0.5;  // was 0.15
pos.current.y += (target.current.y - pos.current.y) * 0.5;
```

**Recommended lerp range:**
- `0.3` — Gentle luxury (slight trailing)
- `0.5` — Snappy responsive (current)
- `0.8` — Near-instant (minimal smoothing)
- `1.0` — No smoothing at all (raw position)

Also check CSS `transition` on `.magnetic-cursor` — remove or reduce `0.15s` if present.

## CSS 3D Perspective Scene Details

- `perspective: 2000px` on container
- `transform-style: preserve-3d` on scene
- Layer depths: `z: -500px` (background blur), `-200px` (decor), `0px` (text), `100px` (floating cards), `300px` (particles)
- Mouse tilt: `rotateY: x*5`, `rotateX: -y*5`, GSAP `elastic.out` on mouseleave
- Scroll: layers parallax at different speeds, scene `rotateZ: ±2deg`

## Color Tokens

- `--vidvis-black: #0a0a0a`
- `--vidvis-cream: #f4f1ea`
- `--vidvis-gold: #c9a96e`
- `--vidvis-gray: #8a8a8a`

## Font Pairing (Luxury)

| Role | Font | Tailwind | Weight |
|------|------|----------|--------|
| Display / Brand | Oranienbaum | `font-oranienbaum` | 400 |
| Calligraphic / Descriptions | Cormorant Infant | `font-cormorant` | 300–700 |
| Elegant Serif Headers | Playfair Display | `font-playfair` | auto |
| Clean Body | Inter | `font-sans` | auto |

## Image Sourcing

```bash
# wallpaperscraft.ru — replace preview with download URL
curl -sL -o public/images/nature_1.jpg <full_url>
```

## Animation Architecture

| Task | Tool | Why |
|------|------|-----|
| Scroll parallax / pin / scrub | GSAP | Motion has no ScrollTrigger |
| Component entrance/exit | Motion | `AnimatePresence` + `variants` |
| Hover/tap micro-animations | Motion | `whileHover` in JSX |
| Complex multi-step timeline | GSAP | Timeline API |
| Continuous float loops | Motion | `repeat: Infinity` declarative |

## Known Pitfalls

1. **postcss.config.mjs** — never `.js` with `module.exports`
2. **Tailwind config .ts** — use `import type { Config }` not `.js`
3. **next/image** remotePatterns — whitelist `wallpaperscraft.ru`
4. **Oranienbaum** — only weight 400, no bold
5. **Cursor lerp ≤0.15** — causes visible lag on luxury sites; use 0.3–0.8
6. **Framer-motion inside CSS 3D** — use `style={{ transformStyle: "preserve-3d" }}` not Tailwind class
7. **npm/npx not in PATH** — use `./node_modules/.bin/next` directly

## Session History

- v1: Initial build, all sections, GSAP animations
- v2: Oranienbaum/Cormorant, ParallaxDivider, Hero removed
- v3: PerspectiveScene CSS 3D single entry, floating cards
- v3.1: Technologies section (Motion.dev), cursor lerp optimized to 0.5
