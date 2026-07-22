# Silicone Landing — Session Notes (2026-07-17)

Vite + React + Tailwind + GSAP + Framer Motion + hls.js dark portfolio landing, rebuilt from a detailed prompt.

## Verified Stack

- `npm create vite@latest silicone-landing -- --template react-ts`
- `npm install gsap framer-motion hls.js react-router-dom tailwindcss-animate lenis`
- `npm install -D tailwindcss@3.4.17 postcss@8.4.49 autoprefixer@10.4.20 @types/node`
- `./node_modules/.bin/tailwindcss init -p`

## Pitfall: Tailwind v4 `init` fails

Vite's default install may pull Tailwind v4. `npx tailwindcss init` then fails with "could not determine executable". Pin v3.4.x and re-init.

## Pitfall: `verbatimModuleSyntax` + Framer Motion

Import types with `type` keyword:
```tsx
import { motion, type Variants } from "framer-motion";
```

## Technique: TypeScript path alias with Vite

`vite.config.ts`:
```ts
resolve: { alias: { "@": path.resolve(__dirname, "./src") } }
```

`tsconfig.app.json`:
```json
"paths": { "@/*": ["./src/*"] }
```

Do not set `baseUrl`; it is deprecated in TS 6 and triggers error TS5101/TS5090.

## Technique: Lenis + GSAP ScrollTrigger

```ts
const lenis = new Lenis({ duration: 1.2, easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)) });
lenis.on("scroll", ScrollTrigger.update);
gsap.ticker.add((time) => lenis.raf(time * 1000));
gsap.ticker.lagSmoothing(0);
```

In `index.css` disable native `scroll-behavior`:
```css
html { scroll-behavior: auto; }
html.lenis, html.lenis body { height: auto; }
.lenis.lenis-smooth { scroll-behavior: auto !important; }
```

## Pitfall: Headless screenshots hang on requestAnimationFrame loading screen

Chrome and Playwright headless can hang or produce premature screenshots when the loading screen uses a 2700ms `requestAnimationFrame` counter. In this environment, verification was done by:
1. Running `npm run build` — must exit 0.
2. Running `npm run preview` and checking HTTP response.
3. Skipping visual screenshots and warning the user to verify in a real browser.

Do not rely on headless screenshots for pages with long RAF-based preloaders.

## Pitfall: HLS video in headless

`hls.js` attaches to a `<video>`; in headless screenshots the video may not render even when script loads. Fallback is the dark overlay and gradient, which still looks acceptable.

## Technique: Robust HLS video component (hls.js + native fallback + cleanup)

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
      video.play().catch(() => {});
    };

    if (Hls.isSupported()) {
      hls = new Hls({ autoStartLoad: true, debug: false });
      hls.loadSource(src);
      hls.attachMedia(video);
      hls.on(Hls.Events.MANIFEST_PARSED, () => video.play().catch(() => {}));
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
      autoPlay muted loop playsInline
      className={`${className} ${flipped ? "scale-y-[-1]" : ""}`}
      style={{ willChange: "transform" }}
    />
  );
}
```

Use `flipped` for mirrored background sections (e.g. footer video flipped vertically).

## Technique: Animated gradient border hover ring

For buttons and pills where the prompt asks "accent gradient border ring on hover":

```tsx
<a className="group relative inline-flex items-center justify-center rounded-full px-7 py-3.5 ...">
  <span className="absolute inset-[-2px] rounded-full accent-gradient opacity-0 group-hover:opacity-100 transition-opacity animate-gradient-shift" />
  <span className="relative z-10 ...">Label</span>
</a>
```

CSS:
```css
.accent-gradient { background: linear-gradient(90deg, #89AACC 0%, #4E85BF 100%); }
.animate-gradient-shift {
  animation: gradient-shift 6s ease infinite;
  background-size: 200% 200%;
}
@keyframes gradient-shift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
```

For solid CTA buttons that invert on hover, add `group-hover:bg-bg group-hover:text-text-primary` on the inner span so the gradient ring stays visible.

## Quality Iteration Rule

When the user says "do it until the design looks beautiful, animations are smooth, lines are sharp, everything is in its place", treat it as a quality gate, not a single pass:

1. First implement the prompt literally (sizes, spacing, colors, timings).
2. Run `tsc --noEmit` and `npm run build`.
3. Review alignment, contrast, hover states, and z-index stacking.
4. Look for broken asset paths, typos in filenames, and mix-blend mode visibility.
5. Iterate on parallax range, easing, and entrance delays until motion feels intentional.
6. Stop only when build is clean and the user approves or no obvious visual defects remain.

## Animation Quality Checklist

Before declaring a landing page done:
- [ ] `npm run build` passes with zero TypeScript errors
- [ ] Lenis smooth scroll active (no native scroll jerk)
- [ ] GSAP ScrollTrigger sections pin/scrub correctly
- [ ] Framer Motion `whileInView` entrances fire once
- [ ] Loading screen counter exits after ~3.1s
- [ ] CTA hover states show accent-gradient border ring
- [ ] Grain overlay is subtle (`opacity: 0.035`) and `pointer-events: none`
- [ ] Mobile: horizontal pills stack vertically
- [ ] `::selection` uses accent color with low opacity
- [ ] All images referenced by correct paths (watch for Cyrillic typos in filenames)
- [ ] HLS video flipped prop used where required, not duplicated via className
