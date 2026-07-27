# VIDVIS smooth-scroll / animation polish session

Project: Next.js 14 + React 18 + TypeScript + Tailwind + GSAP + Framer Motion + Lenis
Date: 2026-07-25

## Symptoms

- Animations felt janky
- Scroll was not smooth despite Lenis being present
- Page transitions between Next.js routes were abrupt
- Floating cards / particles in the hero caused visible main-thread load

## Root causes found

### 1. Lenis was recreated on every route change

`useLenis()` was called inside `PageShell`, which is mounted/unmounted by each page. Lenis was destroyed and rebuilt on navigation, resetting scroll state and causing a hitch.

**Fix:** Move Lenis into a global `SmoothScrollProvider` rendered once around the app. `PageShell` consumes it; the instance survives route changes.

### 2. Framer Motion + GSAP transform conflicts

`PerspectiveScene` ran many independent `framer-motion` `repeat: Infinity` loops (floating cards, particles) while GSAP ScrollTrigger and mouse-tilt also mutated the same container transform. Multiple libraries fighting for the same element properties produced inconsistent frame timing.

**Fix:** Drive all continuous ambient motion (floaters, particles) with a single GSAP context/ticker inside `PerspectiveScene`. Keep Framer Motion only for entrance states (hero text reveal) where it does not conflict with GSAP scroll/mouse transforms. Reduced total motion component count significantly.

### 3. Mousemove handler was unthrottled and created overlapping tweens

`gsap.to(scene, { rotateX/Y })` on every mousemove event caused tween queueing and visual lag.

**Fix:** Use `gsap.quickTo` for pointer-driven transforms (rotateX/rotateY) and throttle raw mousemove events to ~60 fps via `performance.now()`.

### 4. `gsap.ticker.lagSmoothing(0)` was disabled

Disabling lag smoothing makes GSAP follow the screen blindly; combined with Lenis it amplified stutters when the tab or system was under load.

**Fix:** Remove the line. Use `gsap.ticker.fps(-1)` to let GSAP sync to the display refresh while keeping smoothing.

### 5. Preloader used `setInterval` and blocked content

The original preloader advanced progress via `setInterval` and then abruptly revealed the page.

**Fix:** Advance progress with `requestAnimationFrame`, add a brief initial delay so first paint can happen, and exit with a smooth opacity + y transition via `AnimatePresence`.

### 6. No page transition wrapper

Next.js App Router renders the new route immediately; there was no `AnimatePresence` wrap around page content.

**Fix:** Add a `PageTransition` component keyed by `usePathname()` with `AnimatePresence mode="wait"`. Use a short opacity + y transition matching the project's luxury easing `[0.76, 0, 0.24, 1]`.

### 7. ScrollTrigger positions were stale after fonts loaded

Hero/section measurements taken before web fonts finished caused ScrollTrigger start/end points to be slightly off, producing jumps after the font swap.

**Fix:** Call `ScrollTrigger.refresh()` after `document.fonts.ready` resolves, and debounce `refresh()` on window resize.

### 8. `useReducedMotion` default was SSR-unsafe

The hook defaulted to `false` and accessed `window` unconditionally, which can throw during SSR/static generation.

**Fix:** Default to `true` (safe fallback), guard `window` access, and expose a non-hook `prefersReducedMotion()` helper for one-off checks.

## Patterns implemented

### SmoothScrollProvider

```tsx
"use client";
import { createContext, useContext, useRef, useEffect, ReactNode } from "react";
import Lenis from "lenis";
import { gsap, ScrollTrigger } from "@/lib/gsap";

const Ctx = createContext<{ lenis: Lenis | null }>({ lenis: null });
export const useSmoothScroll = () => useContext(Ctx);

export function SmoothScrollProvider({ children }: { children: ReactNode }) {
  const lenisRef = useRef<Lenis | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      touchMultiplier: 2,
      infinite: false,
      smoothWheel: true,
      syncTouch: false,
    });
    lenisRef.current = lenis;
    (window as any).__lenis = lenis;

    lenis.on("scroll", ScrollTrigger.update);
    const ticker = (time: number) => lenis.raf(time * 1000);
    gsap.ticker.add(ticker);
    gsap.ticker.fps(-1);

    let resizeTimeout: ReturnType<typeof setTimeout>;
    const onResize = () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => ScrollTrigger.refresh(), 150);
    };
    window.addEventListener("resize", onResize);
    document.fonts.ready.then(() => ScrollTrigger.refresh());

    return () => {
      clearTimeout(resizeTimeout);
      window.removeEventListener("resize", onResize);
      lenis.destroy();
      gsap.ticker.remove(ticker);
      (window as any).__lenis = undefined;
    };
  }, []);

  return <Ctx.Provider value={{ lenis: lenisRef.current }}>{children}</Ctx.Provider>;
}
```

### PageTransition

```tsx
"use client";
import { motion, AnimatePresence } from "framer-motion";
import { usePathname } from "next/navigation";

export default function PageTransition({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        key={pathname}
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -16 }}
        transition={{ duration: 0.5, ease: [0.76, 0, 0.24, 1] }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
```

### Throttled pointer tilt with gsap.quickTo

```tsx
const tiltX = gsap.quickTo(scene, "rotateX", { duration: 0.6, ease: "power2.out" });
const tiltY = gsap.quickTo(scene, "rotateY", { duration: 0.6, ease: "power2.out" });

let lastMove = 0;
const onMove = (e: MouseEvent) => {
  if (performance.now() - lastMove < 16) return;
  lastMove = performance.now();
  const rect = container.getBoundingClientRect();
  const x = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
  const y = ((e.clientY - rect.top) / rect.height - 0.5) * 2;
  tiltY(x * 8);
  tiltX(-y * 8);
};
```

## Verification

- `npm run build` passed with zero TypeScript errors.
- Dev server started on `localhost:3001` and served all routes.
- Cross-origin dev-origin warning from Next.js appeared (expected when accessing from another host); can be silenced via `next.config.js#allowedDevOrigins` if needed.

## Updated PerspectiveScene pattern

During this session the user iterated on the hero text behavior:
1. Text had to be perfectly horizontal at rest.
2. Text still had to react to mouse movement together with the 3D scene.
3. Earlier attempts either kept text permanently tilted (constant `rotateZ`) or made it not tilt at all (text rendered outside `sceneRef`).

Final working structure:
- The hero text is a `depth-layer` with `translateZ(0px)` **inside** `sceneRef`.
- The whole `sceneRef` is rotated on mousemove (`rotateX`, `rotateY`).
- No constant `rotateZ` is applied to the scene.
- Therefore text is horizontal at rest and tilts together with the scene when the mouse moves.

See `popular-web-designs/references/vidvis-perspectivescene-mouse-tilt.md` for the full JSX + GSAP recipe (or preserve the motion notes in the project-specific Obsidian note).

## Files changed

- `src/hooks/useLenis.ts` — exposed `useLenisScrollTo`, kept hook as alternative.
- `src/components/SmoothScrollProvider.tsx` — new global provider.
- `src/components/PageShell.tsx` — uses provider + smooth fade-in.
- `src/components/PageTransition.tsx` — new route transition wrapper.
- `src/components/PerspectiveScene.tsx` — GSAP-driven ambient motion, throttled mouse tilt, text inside the rotating scene.
- `src/components/Preloader.tsx` — RAF-based progress, smoother exit.
- `src/hooks/useReducedMotion.ts` — SSR-safe default.
