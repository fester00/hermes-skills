---
name: luxury-immersive-web
version: 2.1.0
description: |
  Build immersive, luxury-feeling landing pages with parallax, scroll-triggered
  animations, 3D tilt, smooth scroll (Lenis), GSAP ScrollTrigger, Motion.dev 
  (Framer Motion) for declarative entrances, grain overlays, magnetic cursors, 
  and split-text reveals. Next.js or plain HTML.
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [web-design, animation, gsap, parallax, luxury, landing-page, nextjs, scroll, "3d-tilt", "perspective-scene", "framer-motion", "motion-dev", "declarative-animations"]
    related_skills: [claude-design, popular-web-designs]
---

# Luxury Immersive Web

Build immersive, high-end landing pages with scroll-driven animations, parallax,
custom cursors, and cinematic transitions. Think Moooi, Awwwards sites, luxury brand
homepages.

## Core Principle

Start with the **atmosphere**, not the layout. Grain + dark canvas + gold accent +
serif display type = luxury DNA before a single component is built.

## When To Use

- Luxury/ecommerce landing pages
- Art gallery / exhibition sites
- High-end brand storytelling
- One-page scroll experiences
- "Make it feel like Moooi" requests

## Tech Stack (Validated)

| Tool | Role |
|------|------|
| **GSAP + ScrollTrigger** | Scroll-driven animations, pin sections, timelines |
| **Lenis** | Smooth scroll (mandatory for GSAP sync) |
| **next/image** | Optimized images with `sizes` prop (always use) |
| **Tailwind CSS** | Utility layout, custom properties for tokens |
| **next/font/google** | Art fonts with Cyrillic support (Inter, Oranienbaum, Cormorant Infant, Playfair Display) |
| **Motion.dev (Framer Motion)** | Declarative React animations: `AnimatePresence`, entrances, `whileHover`, drag, spring physics |

> **Note on Three.js:** Do NOT reach for Three.js unless the user explicitly asks for WebGL particles/shaders. CSS 3D transforms (`perspective`, `preserve-3d`, `translateZ`) can achieve convincing depth on section backgrounds and tilting cards at a fraction of the bundle size and complexity. See `ParallaxDivider` and `PerspectiveScene` below.
> **Note on Motion:** Motion.dev (`motion` on npm) is the evolution of `framer-motion`. Same API, same team, new branding. Use `npm install motion` for fresh projects or upgrade `framer-motion` in existing ones. GSAP and Motion **coexist perfectly** — GSAP handles scroll timelines, Motion handles component-level declarative animations.

## Standard Patterns

### 0. Vite Scaffolding (React SPA luxury sites)

When the design brief specifies React + Vite + Tailwind (not Next.js), use this skeleton:

```bash
cd /mnt/data/natan-storage   # or user's target directory
npm create vite@latest silicone-landing -- --template react-ts
cd silicone-landing
npm install gsap framer-motion hls.js react-router-dom tailwindcss-animate
npm install -D tailwindcss@3.4.17 postcss@8.4.49 autoprefixer@10.4.20 @types/node
./node_modules/.bin/tailwindcss init -p
```

**Pitfall: Tailwind v4 breaks `tailwindcss init`.** Vite's default `create-vite` may install Tailwind v4. The v4 CLI no longer creates config files the same way; `npx tailwindcss init` can fail with "could not determine executable". Pin Tailwind to v3.4.x and PostCSS 8.4.x for the classic config workflow:

```bash
npm uninstall tailwindcss autoprefixer postcss
npm install -D tailwindcss@3.4.17 postcss@8.4.49 autoprefixer@10.4.20
```

Then configure `tailwind.config.js`, `postcss.config.js`, `src/index.css` with `@tailwind` directives, and `vite.config.ts` with `@/` alias to `src/`.

### 0b. HLS Video Background

Use `hls.js` for Mux-style `.m3u8` sources. Fall back to native HLS on Safari.
Clean up thoroughly on unmount to prevent detached video elements from continuing
to stream or throw after navigation.

**Robust component (also supports `flipped` for mirrored sections):**

```tsx
import { useEffect, useRef } from "react";
import Hls from "hls.js";

interface HlsVideoProps {
  src: string;
  className?: string;
  flipped?: boolean;
}

export default function HlsVideo({ src, className = "", flipped = false }: HlsVideoProps) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    let hls: Hls | null = null;
    const onLoadedMetadata = () => {
      video.play().catch(() => {
        // autoplay may be blocked
      });
    };

    if (Hls.isSupported()) {
      hls = new Hls({ autoStartLoad: true, debug: false });
      hls.loadSource(src);
      hls.attachMedia(video);
      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        video.play().catch(() => {
          // autoplay may be blocked
        });
      });
    } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
      video.src = src;
      video.addEventListener("loadedmetadata", onLoadedMetadata);
    }

    return () => {
      hls?.destroy();
      video.removeEventListener("loadedmetadata", onLoadedMetadata);
      video.pause();
      video.removeAttribute("src");
      video.load();
    };
  }, [src]);

  return (
    <video
      ref={videoRef}
      autoPlay
      muted
      loop
      playsInline
      className={`${className} ${flipped ? "scale-y-[-1]" : ""}`}
      style={{ willChange: "transform" }}
    />
  );
}
```

**Key points:**
- `flipped` applies `scale-y-[-1]` to mirror the video (e.g. footer background).
- Always remove `loadedmetadata` listener in cleanup.
- `video.pause(); video.removeAttribute("src"); video.load()` stops network activity on unmount.
- In headless environments the video frame may not render; rely on dark overlays/gradients so the page still looks acceptable.

**See `templates/HlsVideo.tsx` for a copy-paste starter.**

### 0b-1. Gradient Border Hover Ring

Common requirement for luxury buttons: a subtle accent-gradient ring appears on hover, often animated.

```tsx
<a className="group relative inline-flex items-center justify-center rounded-full px-7 py-3.5 ...">
  <span className="absolute inset-[-2px] rounded-full accent-gradient opacity-0 group-hover:opacity-100 transition-opacity animate-gradient-shift" />
  <span className="relative z-10 ...">Label</span>
</a>
```

CSS:

```css
.accent-gradient {
  background: linear-gradient(90deg, #89AACC 0%, #4E85BF 100%);
}
.animate-gradient-shift {
  animation: gradient-shift 6s ease infinite;
  background-size: 200% 200%;
}
@keyframes gradient-shift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
```

For solid buttons that invert on hover, move the color inversion to the inner span (`group-hover:bg-bg group-hover:text-text-primary`) so the outer gradient ring stays visible.

### 0b-2. Vite SPA Smooth Scroll with Lenis + GSAP ScrollTrigger

For React + Vite luxury landings, use a `useLenis` hook instead of Next.js `PageShell`:

```ts
import Lenis from "lenis";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export function useLenis() {
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      orientation: "vertical",
      smoothWheel: true,
    });

    lenis.on("scroll", ScrollTrigger.update);
    gsap.ticker.add((time) => lenis.raf(time * 1000));
    gsap.ticker.lagSmoothing(0);

    return () => {
      lenis.destroy();
    };
  }, []);
}
```

In `index.css` disable native smooth scrolling so Lenis owns the physics:

```css
html { scroll-behavior: auto; }
html.lenis, html.lenis body { height: auto; }
.lenis.lenis-smooth { scroll-behavior: auto !important; }
```

### 0c. TypeScript + Framer Motion variants

When `verbatimModuleSyntax` is enabled (Vite React-TS default), import Framer Motion types with `type`:

```tsx
import { motion, type Variants } from "framer-motion";

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 40 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 1, ease: "easeInOut" as const },
  },
};
```

### 0d. Content adaptation from existing project

When the user says "take products from category X and release Y", query the existing project database directly instead of guessing. Example for pentajunior-v2 SQLite:

```bash
cd /home/natan/pentajunior-v2
python3 -c "
import sqlite3
c = sqlite3.connect('pentajunior.db').cursor()
c.execute('SELECT id, name, title, price, price_unit, price_currency, image, features, meta_title, meta_description, keywords FROM products WHERE id IN (?, ?, ?)', ('si-m-aero','vs-m-aero','ks-m-aero'))
for r in c.fetchall(): print(r)
"
```

Copy referenced images into the new project's `public/` directory and adapt copy to the landing tone.

### 0e. next.config.js for External Images (Next.js only)

Next.js `<Image>` refuses external domains by default. `images.remotePatterns` is a **whitelist** of allowed hostnames. Without it, hotlinking from Unsplash or wallpaperscraft.ru throws a security error.

```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "images.unsplash.com" },
      { protocol: "https", hostname: "plus.unsplash.com" },
      { protocol: "https", hostname: "wallpaperscraft.ru" },
      { protocol: "https", hostname: "i.wallpaperscraft.ru" },
    ],
  },
};
module.exports = nextConfig;
```

For quick local testing with arbitrary URLs, `hostname: "**"` works but must be removed before production.

### 1. Motion.dev Install & Coexistence with GSAP

```bash
# Fresh project
npm install motion
# Existing project with framer-motion
npm install framer-motion@latest
```

**Motion and GSAP each solve different problems:**

| Task | Best Tool | Why |
|------|-----------|-----|
| Scroll-driven parallax / scrub / pin | GSAP | Motion has no ScrollTrigger analogue |
| Component mount/unmount entrance | Motion | `AnimatePresence` handles exit automatically |
| Hover/tap micro-interactions | Motion | `whileHover={{ scale: 1.05 }}` in JSX, no boilerplate |
| Drag gestures + throw physics | Motion | Built-in `drag` with spring snap |
| Layout reflow animations | Motion | `layout` prop auto-animates DOM changes |
| Spring/bounce physics | Motion | Natively built-in, no custom eases |
| Complex multi-step timelines | GSAP | Timeline API is more powerful for sequencing |

**Rule of thumb:** GSAP for scroll-linked global orchestration, Motion for component-level declarative life.

### 0c. Motion Pattern — Floating Card Entrance (inside CSS 3D Scene)

Replace GSAP `useEffect` event listeners with declarative Motion inside `preserve-3d` containers.

```tsx
import { motion, AnimatePresence } from "motion/react"; // or "framer-motion"

// Inside PerspectiveScene or any card grid:
<motion.div
  className="float-card"
  initial={{ opacity: 0, y: 50, rotateY: -20, scale: 0.9 }}
  animate={{ opacity: 1, y: 0, rotateY: 0, scale: 1 }}
  whileHover={{
    rotateY: 12,
    rotateX: -6,
    translateZ: 40,
    transition: { type: "spring", stiffness: 200, damping: 15 },
  }}
  transition={{ type: "spring", stiffness: 100, delay: 0.5 }}
  style={{ transformStyle: "preserve-3d" }}
>
  <Image src="/images/..." fill className="object-cover" sizes="200px" />
</motion.div>
```

Key: `motion.div` works inside `preserve-3d` parent. Use `style` prop with CSS `transform-style`, not Tailwind `className`, because Tailwind may purge unused utilities in production.

### 0d. Motion Pattern — AnimatePresence Preloader Transition

```tsx
import { AnimatePresence, motion } from "motion/react";
import { useState } from "react";

export default function Home() {
  const [loaded, setLoaded] = useState(false);

  return (
    <>
      <AnimatePresence>
        {!loaded && (
          <motion.div
            key="preloader"
            className="preloader"
            initial={{ opacity: 1 }}
            exit={{ y: "-100%", transition: { duration: 1.2, ease: [0.76, 0, 0.24, 1] } }}
            style={{ position: "fixed", inset: 0, zIndex: 10001 }}
          >
            {/* Progress bar / logo */}
          <motion.div
            animate={{ scaleX: [0, 1] }}
            transition={{ duration: 2, ease: "easeInOut" }}
            className="h-[2px] bg-vidvis-gold"
          />
        </motion.div>
        )}
      </AnimatePresence>
      <motion.main
        initial={{ opacity: 0 }}
        animate={{ opacity: loaded ? 1 : 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* page content */}
      </motion.main>
    </>
  );
}
```

No `onComplete` callback chains. `AnimatePresence` automatically handles exit animation before component unmounts. Preloader `z-index` must be above grain overlay (10001).

### 0e. Motion Pattern — Staggered Reveal for Cards / Text

```tsx
const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.1, delayChildren: 0.2 },
  },
};
const itemVariants = {
  hidden: { opacity: 0, y: 40, rotateX: 10 },
  visible: {
    opacity: 1, y: 0, rotateX: 0,
    transition: { type: "spring", stiffness: 120, damping: 20 },
  },
};

<motion.div variants={containerVariants} initial="hidden" whileInView="visible" viewport={{ once: true }}>
  {items.map((item, i) => (
    <motion.div key={i} variants={itemVariants}>
      {/* card content */}
    </motion.div>
  ))}
</motion.div>
```

`whileInView` replaces GSAP ScrollTrigger for simple entrance animations. No refs, no `useEffect`. Add `viewport={{ once: true }}` to animate only on first scroll-in.

### 1. Smooth Scroll Setup (Lenis + GSAP)

```typescript
import Lenis from "lenis";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

const lenis = new Lenis({
  duration: 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
});

lenis.on("scroll", ScrollTrigger.update);
gsap.ticker.add((time) => lenis.raf(time * 1000));
gsap.ticker.lagSmoothing(0);
```

### 2. Multi-Layer Parallax (Depth via Separation)

For maximum depth, create 3+ layers inside a section, each moving at a different speed:

```typescript
// Layer 1: Background — slowest (Ken Burns scale optional)
gsap.to(bgRef.current, {
  yPercent: 20,
  scale: 1.3,
  ease: "none",
  scrollTrigger: { trigger: sectionRef.current, start: "top top", end: "bottom top", scrub: true },
});

// Layer 2: Mid decorative particles
const midRef = useRef<HTMLDivElement>(null);
gsap.to(midRef.current, {
  yPercent: -40,
  ease: "none",
  scrollTrigger: { trigger: sectionRef.current, start: "top top", end: "bottom top", scrub: true },
});

// Layer 3: Content layer — moves in opposite direction
gsap.to(".hero-title-wrap", {
  yPercent: -30,
  ease: "none",
  scrollTrigger: { trigger: sectionRef.current, start: "top top", end: "bottom top", scrub: true },
});
```

Container must have `overflow: hidden` or `overflow-x: hidden`.

### 2b. Inner-Element Parallax (Images Inside Cards)

Images inside their own containers can parallax independently of the card itself:

```typescript
// Image inside card — moves within its container
gsap.fromTo(img,
  { yPercent: -15, scale: 1.2 },
  {
    yPercent: 15, scale: 1.0,
    scrollTrigger: { trigger: card, start: "top bottom", end: "bottom top", scrub: true },
  }
);
```

Set `overflow: hidden` on the card container.

### 2c. Parallax Image (Legacy Single-Layer)

```typescript
// Image moves slower than scroll
// Applied to image wrapper, scrub syncs to scroll position

gsap.to(element, {
  yPercent: 30,
  ease: "none",
  scrollTrigger: {
    trigger: section,
    start: "top bottom",
    end: "bottom top",
    scrub: true,
  },
});
```

### 3. Horizontal Scroll Section

```typescript
// Pin section and translate container horizontally
// Use ScrollTrigger's pin + scrub

gsap.to(container, {
  x: () => -(totalWidth - viewportWidth),
  ease: "none",
  scrollTrigger: {
    trigger: section,
    start: "top top",
    end: () => `+=${totalWidth}`,
    pin: true,
    scrub: 1,
    anticipatePin: 1,
  },
});
```

**Mobile:** horizontal scroll sections should degrade to vertical stacking on
narrow viewports (`lg:` breakpoint). Do NOT pin on mobile.

### 4. Full-Screen Parallax Divider (Reuseable Section Breather)

A reusable component that creates a breathing gap between sections with a parallaxing full-screen background image. Prevents visual clutter when multiple parallax sections stack.

Use between every two major sections. Mix different speeds and overlays for rhythm.

```typescript
// ParallaxDivider.tsx — drop-in component
export default function ParallaxDivider({
  src,          // image path (public/ or unsplash)
  alt,
  speed = 0.5,  // 0.3 slow, 0.7 medium, 1.2 fast
  overlay = "bg-black/40",
  minHeight = "100vh",
  children,     // optional overlay content
}) {
  const sectionRef = useRef<HTMLDivElement>(null);
  const imgRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sectionRef.current || !imgRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo(imgRef.current,
        { yPercent: -30 * speed },
        {
          yPercent: 30 * speed,
          ease: "none",
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top bottom",
            end: "bottom top",
            scrub: true,
          },
        }
      );
    }, sectionRef);
    return () => ctx.revert();
  }, [speed]);

  return (
    <section ref={sectionRef} className="relative w-full overflow-hidden"
             style={{ minHeight }}>
      <div ref={imgRef} className="absolute inset-0 h-[130%] -top-[15%]"
           style={{ willChange: "transform" }}>
        <Image src={src} alt={alt} fill className="object-cover" sizes="100vw" quality={90} />
      </div>
      <div className={`absolute inset-0 ${overlay}`} />
      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0a] via-transparent to-[#0a0a0a]" />
      {children && <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4">{children}</div>}
    </section>
  );
}
```

Typical page layout with dividers:
```tsx
<Hero />
<ParallaxDivider src="/bg1.jpg" speed={0.6} />
<SectionA />
<ParallaxDivider src="/bg2.jpg" speed={0.4} />
<SectionB />
<ParallaxDivider src="/bg3.jpg" speed={0.5} minHeight="60vh" />
<Footer />
```

### 5. CSS 3D Perspective Scene (Atmosphere-First)

Inspired by moooi.com — a full-viewport CSS 3D scene with floating layers at different z-depths, mouse tilt, and scroll-driven rotation. No Three.js required.

**Critical rule: keep the background OUTSIDE the rotating scene.** Moving the background inside `preserve-3d` and tilting it together creates vertigo — the entire world spins. The background must stay flat; only the floating layered elements tilt.

```typescript
// PerspectiveScene.tsx — full atmospheric entry section
const containerRef = useRef<HTMLDivElement>(null);
const sceneRef = useRef<HTMLDivElement>(null);

useEffect(() => {
  const container = containerRef.current;
  const scene = sceneRef.current;
  if (!container || !scene) return;

  // Mouse tilt: scene follows cursor (max 5deg)
  const handleMouseMove = (e: MouseEvent) => {
    const rect = container.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * 2;
    gsap.to(scene, { rotateY: x * 5, rotateX: -y * 5, duration: 0.8, ease: "power2.out" });
  };
  container.addEventListener("mousemove", handleMouseMove);
  container.addEventListener("mouseleave", () => {
    gsap.to(scene, { rotateY: 0, rotateX: 0, duration: 1.2, ease: "elastic.out(1, 0.5)" });
  });

  // Floating sin-wave animation for decorative elements
  const floatEls = scene.querySelectorAll(".float-item");
  floatEls.forEach((el, i) => {
    gsap.to(el, {
      y: "+=15", x: "+=10", rotation: i % 2 === 0 ? 5 : -5,
      duration: 3 + i * 0.5, repeat: -1, yoyo: true, ease: "sine.inOut", delay: i * 0.3,
    });
  });

  // Scroll-driven depth: layers move at different speeds + scene rotation
  const layers = scene.querySelectorAll(".depth-layer");
  layers.forEach((layer, i) => {
    gsap.to(layer, { y: -(i + 1) * 20, ease: "none", scrollTrigger: {
      trigger: container, start: "top bottom", end: "bottom top", scrub: true,
    }});
  });
  gsap.to(scene, { rotateZ: 2, ease: "none", scrollTrigger: {
    trigger: container, start: "top bottom", end: "bottom top", scrub: true,
  }});

  return () => { container.removeEventListener("mousemove", handleMouseMove); };
}, []);
```

Layer stack (z-depths):
- `z: -500px` — large blurred background shapes (circles, gold/cream tones)
- `z: -200px` — decorative elements (lines, crosses, dots)
- `z: 0px` — main content (large typography with 3D depth shadow)
- `z: 100px` — floating cards (art frame, textile swatch, vase) that tilt on mouse
- `z: 300px` — small floating particles/sparkles

Always add `pointer-events: none` on decorative layers and `vignette` overlay.

#### 5a. Keeping the Background OUTSIDE the Rotating Scene (Correct Approach)

The background sits **outside** `sceneRef` and stays flat. `sceneRef` tilts on mousemove while the background remains stationary. This prevents vertigo and keeps the atmospheric base stable.

**The problem:** when `sceneRef` rotates 8° and is sized `w-full h-full`, its projected corners shrink within the viewport, exposing the flat background at the edges — a visible "window" boundary.

**The fix: oversize the scene container so its edges stay off-screen.**

```tsx
{/* Background — flat, outside the tilted scene */}
<div ref={bgRef} className="absolute inset-0 z-0">
  <Image src="/bg.jpg" fill className="object-cover" sizes="100vw" priority />
  <div className="absolute inset-0 bg-black/40" />
</div>

{/* 3D Scene — oversized 140% so edges stay hidden during 8° tilt */}
<div
  ref={sceneRef}
  className="absolute inset-[-20%]"
  style={{ transformStyle: "preserve-3d", transformOrigin: "center center" }}
>
  {/* All depth layers inside — they tilt together */}
</div>
```

**Sizing math for `inset-[-N%]`:**

| Max tilt (rotateY or rotateX) | Required oversize | Tailwind class |
|---|---|---|
| 5° | ~10% | `inset-[-5%]` (110% total) |
| 8° | ~20% | `inset-[-20%]` (140% total) |
| 12° | ~30% | `inset-[-30%]` (160% total) |
| 15°+ | ~40% | `inset-[-40%]` (180% total) |

**Rule of thumb:** `oversize_percent ≈ max_tilt_degrees × 2.5`. Always round up and test at the extreme mouse position (corner of viewport).

**Positioning elements inside an oversized scene:** when the scene is `inset-[-20%]`, percentage-based positions (`top-[20%] left-[8%]`) shift because the container is now 140% of viewport. Use **viewport units (`vw`/`vh`)** for floating card positions so they stay anchored to the screen regardless of scene size:

```tsx
// CORRECT — vw/vh stays anchored to viewport
const positions = [
  "top-[40vh] left-[28vw] md:left-[32vw]",
  "top-[35vh] right-[28vw] md:right-[35vw]",
];

// WRONG — % drifts when scene is oversized
const positions = [
  "top-[20%] left-[8%]",
  "top-[15%] right-[8%]",
];
```

**Vignette positioning:** place the vignette overlay **outside** `sceneRef` so it stays flat and doesn't tilt with the scene. A tilted vignette intensifies the dizzying effect:

```tsx
{/* Inside section, but outside sceneRef — flat, no 3D */}
<div
  className="absolute inset-0 pointer-events-none z-20"
  style={{
    background: "radial-gradient(ellipse at center, transparent 40%, rgba(10,10,10,0.4) 100%)",
  }}
/>
```

### 5a. Floating Card with Real Image (inside PerspectiveScene)

Replace CSS gradient placeholders with `<Image />` cards:

```tsx
<div className="... float-item" style={{ transform: "translateZ(100px)" }}>
  <Image src="/images/nature_1.jpg" fill className="object-cover" sizes="200px" alt="" />
</div>
```

The `Image` component works inside `preserve-3d` containers. Use `fill` + `object-cover` + explicit `sizes` for Next.js optimization.

### 5b. Artistic Font Pairing for Luxury Sites

Use `next/font/google` with Cyrillic support for Russian luxury sites:

```typescript
import { Playfair_Display, Cormorant_Infant, Oranienbaum, Inter } from "next/font/google";

const oranienbaum = Oranienbaum({ subsets: ["latin", "cyrillic"], weight: "400", variable: "--font-oranienbaum" });
const cormorant = Cormorant_Infant({ subsets: ["latin", "cyrillic"], weight: ["300","400","600","700"], variable: "--font-cormorant" });
const playfair = Playfair_Display({ subsets: ["latin", "cyrillic"], variable: "--font-playfair" });
const inter = Inter({ subsets: ["latin", "cyrillic"], variable: "--font-inter" });
```

| Role | Font | Tailwind | Use For |
|------|------|----------|---------|
| Display / Brand | Oranienbaum | `font-oranienbaum` | Huge hero titles, brand name |
| Calligraphic / Descriptions | Cormorant Infant | `font-cormorant` | Subtitles, card descriptions, quotes |
| Elegant Serif | Playfair Display | `font-playfair` | Section headers, body serif |
| Clean Body | Inter | `font-sans` | Body text, navigation, UI |

Add to Tailwind config:
```ts
fontFamily: {
  sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
  playfair: ['var(--font-playfair)', 'Georgia', 'serif'],
  cormorant: ['var(--font-cormorant)', 'Georgia', 'serif'],
  oranienbaum: ['var(--font-oranienbaum)', 'Georgia', 'serif'],
}
```

### 6. Enhanced 3D Tilt Card with Shine Gradient

```typescript
card.addEventListener("mousemove", (e) => {
  const rect = card.getBoundingClientRect();
  const x = (e.clientX - rect.left) / rect.width - 0.5;
  const y = (e.clientY - rect.top) / rect.height - 0.5;
  gsap.to(card, {
    rotateY: x * 18,
    rotateX: -y * 12,
    translateZ: 30,
    duration: 0.4,
    ease: "power2.out",
  });
});

card.addEventListener("mouseleave", () => {
  gsap.to(card, { rotateY: 0, rotateX: 0, duration: 0.6, ease: "elastic.out(1, 0.5)" });
});
```

Set `perspective: 1000px` on parent and `transform-style: preserve-3d` on card.
Optional shine overlay: pseudo-element with `linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.2) 50%, transparent 60%)` that follows cursor.

### 7. Split Text Entrance

```typescript
// Split title into chars/words, animate each
// CSS: overflow:hidden on wrapper, translateY(110%) → 0

gsap.from(".char", {
  y: "110%",
  opacity: 0,
  duration: 1.2,
  ease: "expo.out",
  stagger: 0.03,
  delay: 0.5,
});
```

### 8. Grain Overlay

```css
.grain::after {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  opacity: 0.035;
  background-image: url("data:image/svg+xml,... feTurbulence type='fractalNoise' baseFrequency='0.85' ...");
  z-index: 9999;
}
```

Always `pointer-events: none;` — the grain must not block clicks.

### 9. Custom Magnetic Cursor

- Small circle border that grows on hover over interactive elements
- `mix-blend-mode: difference` for contrast
- `requestAnimationFrame` for smooth following
- Hide on mobile (`@media (max-width: 768px)`)

### 10. Preloader Pattern

```typescript
// Animate progress bar + slide up the curtain on complete

gsap.to(".preloader", {
  yPercent: -100,
  duration: 1.2,
  ease: "expo.inOut",
  onComplete: () => setLoaded(true),
});
```

Preloader z-index must be ABOVE grain overlay (10001 vs 9999).

### 11. Custom Magnetic Cursor — Lerp Tuning

Luxury sites need a snappy cursor. A slow lerp (`0.15` or lower) creates visible lag that breaks the premium feel.

```typescript
// MagneticCursor.tsx — RAF loop with lerp
const animate = () => {
  pos.current.x += (target.current.x - pos.current.x) * 0.5;  // was 0.15
  pos.current.y += (target.current.y - pos.current.y) * 0.5;
  cursor.style.transform = `translate(${pos.current.x - 10}px, ${pos.current.y - 10}px)`;
  raf.current = requestAnimationFrame(animate);
};
```

**Recommended lerp range:**
| Value | Feel | Use When |
|-------|------|----------|
| `0.3` | Gentle trailing | Ultra-minimal luxury |
| `0.5` | Snappy responsive | Default recommendation |
| `0.8` | Near-instant | High-energy / gaming feel |
| `1.0` | No smoothing | Raw tracking |

Also check CSS `transition` on `.magnetic-cursor` — remove or reduce `transition: transform 0.15s` if present, as it compounds the lerp lag.

**Pitfall:** Never combine low lerp (`0.15`) with CSS `transition` on the same element — double lag.

### 0f. PageShell Pattern — Centralised Layout Wrapper for Multi-Page Luxury Sites

For sites with multiple routes (gallery, categories, product pages), create a single `PageShell` component that owns the global layout: Preloader, Navigation, MagneticCursor, Footer, and Lenis. Each page then only declares whether it needs the preloader.

```tsx
// src/components/PageShell.tsx
"use client";
import { useState } from "react";
import { useLenis } from "@/hooks/useLenis";
import Preloader from "@/components/Preloader";
import Navigation from "@/components/Navigation";
import MagneticCursor from "@/components/MagneticCursor";
import Footer from "@/components/Footer";

interface PageShellProps {
  children: React.ReactNode;
  preloader?: boolean;
}

export default function PageShell({ children, preloader = true }: PageShellProps) {
  useLenis();
  const [loaded, setLoaded] = useState(false);

  return (
    <>
      {preloader && !loaded && <Preloader onDone={() => setLoaded(true)} />}
      <main className={`grain ${loaded || !preloader ? "opacity-100" : "opacity-0"} transition-opacity duration-500`}>
        <MagneticCursor />
        <Navigation />
        {children}
        <Footer />
      </main>
    </>
  );
}
```

Usage:
```tsx
// homepage
<PageShell preloader={true}>
  <Hero />
  <Sections />
</PageShell>

// inner pages
<PageShell preloader={false}>
  <PageHero />
  <Content />
</PageShell>
```

Benefits:
- Preloader runs only where cinematic entrance is wanted (homepage).
- Inner pages load instantly without animation overhead.
- Global layout is changed in one place.

### 0g. Linking Sections on the Homepage to Category Pages

Turn entire section cards/titles/images into links so the homepage acts as a navigation hub. Preserve hover animations by wrapping the card in `next/link` and moving `cursor-pointer` / `focus-visible` styles to the link.

```tsx
<Link href="/art" className="group relative ... cursor-pointer">
  <Image ... />
  <div className="..."> ... </div>
</Link>
```

For horizontal-scroll category previews, link the panel image, heading, and even individual list items to the matching category route (`/textile/bed-linen`, etc.). Keep the hover/tilt effects inside the link wrapper.

### 0h. prefers-reduced-motion Hook

Always provide a `useReducedMotion` hook and gate Lenis, GSAP ScrollTrigger, and MagneticCursor behind it.

```tsx
// src/hooks/useReducedMotion.ts
"use client";
import { useEffect, useState } from "react";

export function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(mq.matches);
    const onChange = (e: MediaQueryListEvent) => setReduced(e.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);
  return reduced;
}
```

Use it inside `useLenis`, `MagneticCursor`, and any GSAP-driven component. Do not create separate component variants for reduced motion — gate the effect at the hook level.

### 0i. Lucide-React Version Quirk

`lucide-react` major versions do not follow semver the way most packages do. Version `1.x` is an old release that lacks many modern icons (e.g. `Sparkles`). The current maintained line is `0.x` (e.g. `^0.487.0`). When installing Lucide, use:

```bash
npm install lucide-react@^0.487.0
```

If an icon import fails with "Module not found" even though the package is installed, check the installed version first.

### 0j. Quality Iteration Rule

When the user instructs "do it until the design looks beautiful, animations are smooth, lines are sharp, and everything is in its place", treat that as a quality gate rather than a single implementation pass:

1. Implement the prompt literally first — every size, spacing, color token, timing, and easing.
2. Run `tsc --noEmit -p tsconfig.app.json` and `npm run build`. Fix all errors.
3. Manually review hover states, z-index stacking, alignment, and contrast.
4. Check asset paths and filenames for typos (including accidental Cyrillic characters in otherwise Latin paths).
5. Tune parallax range, scrub values, and entrance delays until motion feels intentional, not mechanical.
6. Stop when the build is clean and no obvious visual defects remain, or when the user approves.

This rule is especially important for dark luxury landings where small misalignments and harsh transitions destroy the premium feel.

## Color Tokens (Luxury Dark)

```css
:root {
  --vidvis-black: #0a0a0a;
  --vidvis-cream: #f4f1ea;
  --vidvis-gold: #c9a96e;
  --vidvis-gray: #8a8a8a;
}
```

Single accent color (gold/champagne) against near-black. Avoid multi-color palettes.

## Typography Rules

- **Display:** High-contrast Didone/Bodoni serif (Playfair Display, Cormorant Garamond)
- **Body:** Clean geometric sans (Inter, DM Sans)
- **Scale:** `clamp()` for fluid scaling, never fixed px breakpoints
- **Tracking:** Wide letter-spacing on uppercase labels (`tracking-[0.3em]`)

## Image Sourcing

### Unsplash CDN (Hotlink-friendly)
URLs with `?w=1920&q=80` params.

### Russian Sites (Cyrillic/Local Content)
`wallpaperscraft.ru/catalog/nature` — FullHD nature photography. Thumbnail URLs `300x168`; replace with `1920x1080` for original size.
Direct download: `curl -sL -O <url>` into `public/images/`.

Batch resize for consistency:
```bash
mogrify -resize 1920x1080^ -gravity center -extent 1920x1080 *.jpg
```

### Next.js Scaffolding

```bash
cd /home/natan/projects
mkdir vidvis && cd vidvis
echo '{"dependencies":{"next":"^14.2","react":"^18","gsap":"^3.12","lenis":"^1.1","framer-motion":"^11","tailwindcss":"^3.4"}}' > package.json
mkdir -p src/app src/components src/hooks
# Configure Tailwind, PostCSS (must be .mjs), tsconfig as usual
npm install
npx next dev -p 3001
```

### Vite + React SPA Scaffolding

When the brief asks for React + Vite + Tailwind + GSAP + Framer Motion (not Next.js), see **§0. Vite Scaffolding** at the top of Standard Patterns. The same luxury patterns apply; only the bundler and image handling differ.

### 10. Archive Merge & Yandex Disk Download

**When** the user sends a source archive (src.zip) and/or a full project RAR via Yandex.Disk:

- **ALWAYS ask before overwriting custom components** (PerspectiveScene, ParallaxDivider, etc.)
- **Check for external URLs** in merged components (grep for `https://`), replace with local images
- **RAR from user's machine** may include irrelevant `node_modules` — delete and `npm install` clean
- **Yandex.Disk OAuth token** = `y0_...` (access_token from browser flow), NOT `client_id`/`client_secret`
- **Use Python scripts for complex downloads** (`requests.get(href, stream=True)`), NOT multi-line bash with `curl` — escape-hell with tokens and special characters
- **Pre-installed `unrar` may not exist** — download RARLAB linux binary to `~/bin/` and extract with `~/bin/rar/unrar x -o+ archive.rar`

See `references/yandex-disk-and-archive-patterns.md` for full workflow.

## Verification Checklist

Before declaring "done":

- [ ] Site opens without console errors
- [ ] `npm run build` passes and `tsc --noEmit` is clean
- [ ] Smooth scroll works (no native scroll jerk)
- [ ] Parallax elements move with scroll
- [ ] 3D tilt responds on hover
- [ ] Preloader slides away after load
- [ ] Grain overlay is visible but not distracting
- [ ] Mobile: horizontal sections stack vertically
- [ ] Custom cursor hidden on mobile
- [ ] Images load with `next/image` optimization (Next.js) or correct `public/` paths (Vite)
- [ ] Navigation appears on scroll (glassmorphism)
- [ ] All sections from user's schema are represented
- [ ] Headless screenshot verification skipped for RAF-heavy preloaders; user visually verifies in browser

## Pitfalls

- **PostCSS config format:** Next.js 14 + Tailwind 3.4 — use `postcss.config.mjs` (NOT `.js`) with `export default config;` syntax. Old `.js` with `module.exports` causes Sucrase parse error.
- **Tailwind config:** Use `.ts` with `import type { Config }` — avoid `.js` to prevent module resolution issues.
- **Horizontal scroll on mobile:** Always degrade to vertical. Pinning on narrow viewports breaks UX.
- **Lenis cleanup:** Destroy Lenis instance and remove GSAP ticker on unmount in `useEffect` cleanup.
- **Image CORS / remotePatterns:** Unsplash allows hotlinking. `wallpaperscraft.ru` images require `next.config.js` whitelist. Without it, `<Image>` silently fails or throws.
- **Font loading:** Use `next/font/google` for Inter/Playfair. Custom fonts require `localFont` or CDN link in `_document`.
- **next/image inside preserve-3d:** Works fine with `fill` + `object-cover`, but always provide explicit `sizes` prop.
- **Telegram file delivery via curl:** quote-escape single quotes inside token extraction via `sed -n 's/^TELEGRAM_BOT_TOKEN=*** without `grep -P`. Prefer heredoc or Python `subprocess.run`.
- **Yandex Disk access patterns:** Public share links (`https://disk.yandex.ru/d/...`) can be downloaded with `curl -L -o file.zip "<url>"`. OAuth REST API requires an **access_token** (begins with `y0_...`), NOT `client_id`/`client_secret`. Client credentials are for app registration only — they cannot authenticate API calls without the OAuth flow.
- **User archive merge workflow:** When a user sends a source archive with updates, extract and compare file sizes against the current project. Ask which files to overwrite / preserve. Do NOT auto-overwrite custom components (PerspectiveScene, ParallaxDivider) that the user may not have in their archive.
- **Motion vs GSAP — know the boundary:** Motion (`framer-motion`) excels at component-level declarative animations. GSAP dominates scroll-linked orchestration. Don't use Motion for scroll pin/scrub — it has no ScrollTrigger equivalent. Don't write verbose GSAP+event listeners for simple hover/entrance when Motion's `whileHover` + `variants` + `AnimatePresence` suffice.
- **Motion import path:** Use `"motion/react"` (new v12+ alias) or `"framer-motion"` (v11 legacy). Same API; `"motion/react"` is forward-compatible.
- **Motion inside GSAP preserve-3d scene:** When a `motion.div` lives inside a GSAP-driven CSS 3D container (`preserve-3d` + `perspective`), keep GSAP for the container/scroll/tilt and Motion for hover/entrance only. Mixing both on the *same* element causes conflicts — assign roles by element layer (parent = GSAP, child = Motion, or vice versa).
- **Preloader with AnimatePresence exit:** Use a local `isExiting` state + `onExitComplete` callback instead of GSAP `onComplete`. Motion exits run after React rerender; GSAP callbacks fire inside RAF and may race React's unmount.
- **npm / npx not in PATH on this host:** `npm` and `npx` are not available in default shell PATH. Use `./node_modules/.bin/next` directly or ensure node/npm are sourced from `.nvm` or `~/.bashrc` before build commands.
- **Headless screenshots hang on RAF preloaders:** Chrome and Playwright headless often freeze or timeout when a loading screen uses a long `requestAnimationFrame` counter (e.g. 2700ms). Do not rely on headless screenshots to verify such pages. Validate with `npm run build` and `npm run preview`, then ask the user to visually verify in a real browser.
- **Cyrillic typos in asset paths break images:** Filenames like `/images/smazки/КСМ.webp` (mixed Cyrillic/Latin) are invisible to the eye in code but fail to resolve. Review paths character-by-character when images don't load.

## Related Skills

- `claude-design` — design process, asking questions, producing variants
- `ui-ux-pro-max` — design intelligence database: colors, fonts, styles, product-type recommendations. **Load this before any luxury web build.**
- `popular-web-designs` — visual vocabulary from real brands (Stripe, Linear, etc.)
- `p5js` — generative art backgrounds instead of static images

## External Design Intelligence Reference

- `references/ui-ux-pro-max-design-database.md` — 161 product-type design systems with colors, fonts, and anti-patterns from the UI/UX Pro Max open-source database.

## Templates

- `templates/vite-react-tailwind-luxury-landing.md` — starter scaffolding for React + Vite + Tailwind + GSAP + hls.js dark luxury landing pages. Includes pinned dependency versions and TypeScript config with `verbatimModuleSyntax`.
- `templates/HlsVideo.tsx` — robust hls.js video component with native fallback, cleanup, and optional `flipped` prop.

## Session References

- `references/vidvis-project-session.md` — complete VIDVIS v3 project structure, PerspectiveScene, PostCSS config fix, Motion addition, plus archive merge workflow from 2026-06-03 session (Yandex.Disk download, RAR extraction, user src.zip selective merge, external URL replacement with local images)
- `references/vidvis-v3-cursor-lerp-technologies-session.md` — VIDVIS v3 session: magnetic cursor lerp tuning (0.15 → 0.5), Technologies section with framer-motion, build verification, npm PATH workaround
- `references/vidvis-catalog-links-preloader-session.md` — adding multi-page catalog to VIDVIS, homepage section links, preloader scoped to root only, accessibility refactor (prefers-reduced-motion, focus rings), and lucide-react version gotcha
- `references/silicone-landing-session.md` — Vite + React + Tailwind + GSAP + hls.js dark portfolio landing, content sourced from pentajunior-v2 SQLite; includes Tailwind v3 pinning and Framer Motion `type` imports
- `references/silicone-landing-session-v2.md` — same stack rebuilt from a detailed design prompt; covers Lenis + GSAP ScrollTrigger integration, `verbatimModuleSyntax` type imports, headless screenshot hang with RAF preloaders, and verified build checklist
- `references/motion-dev-patterns.md` — when to choose Motion vs GSAP, quick code snippets, integration pitfalls, import paths
- `references/depth-card-patterns.md` — bottom overlay reveal, vignette overlay, index numbers for depth, radial gradient backgrounds, technologies showcase grid with 3D tilt + parallax float
- `references/motion-gsap-hybrid-float-patterns.md` — hybrid architecture: declarative Motion floating cards + continuous loops INSIDE a GSAP-driven CSS 3D `preserve-3d` scene, role separation rule, spring parameters, preloader replacement, bundle impact
- `references/lucide-react-versioning-gotcha.md` — why `lucide-react@^1.22.0` is stale and `^0.487.0` is the current maintained line; how to fix "Can't resolve 'lucide-react'" / missing icon errors