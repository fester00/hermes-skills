# VIDVIS React/GSAP refactor session

Real refactor of a Next.js 14 / React 18 / TypeScript / Tailwind / GSAP / Lenis / Framer Motion site for VIDVIS after a code-reuse/quality audit.

## Scope

Implemented fixes across the red-zone (bugs/leaks) and yellow-zone (duplication) findings:

- `src/hooks/useLenis.ts`
- `src/components/MagneticCursor.tsx`
- `src/components/Navigation.tsx`
- `src/components/HomeTextile.tsx`
- `src/components/PerspectiveScene.tsx`
- `src/components/ProductGrid.tsx`
- `src/components/CategoryGrid.tsx`
- `src/components/ArtGallery.tsx`
- `src/components/About.tsx`
- `src/components/Footer.tsx`
- `src/components/ContactCTA.tsx`
- `src/components/ParallaxDivider.tsx`
- `src/components/Hero.tsx`
- `src/components/Products.tsx`
- `src/components/ProductCard.tsx` (new)
- `src/hooks/useTilt.ts` (new)
- `src/hooks/useGsapContext.ts` (new)
- `src/lib/gsap.ts` (new)
- `src/data/catalog.ts`
- `src/lib/format.ts`
- `tailwind.config.ts`

## Key implementation patterns

### 1. Centralized GSAP module

```ts
// src/lib/gsap.ts
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
if (typeof window !== "undefined") gsap.registerPlugin(ScrollTrigger);
export { gsap, ScrollTrigger };
```

All client components now import `{ gsap } from "@/lib/gsap"` instead of calling `gsap.registerPlugin(ScrollTrigger)` themselves.

### 2. useGsapContext helper

```ts
// src/hooks/useGsapContext.ts
"use client";
import { useEffect, RefObject, DependencyList } from "react";
import { gsap } from "@/lib/gsap";
import { useReducedMotion } from "@/hooks/useReducedMotion";

export function useGsapContext(
  setup: () => void,
  scope: RefObject<HTMLElement | null>,
  deps: DependencyList = []
) {
  const reduced = useReducedMotion();
  useEffect(() => {
    if (reduced) return;
    const ctx = gsap.context(setup, scope);
    return () => ctx.revert();
  }, [reduced, ...deps]); // eslint-disable-line react-hooks/exhaustive-deps
}
```

Converted `About`, `ContactCTA`, `Footer`, and `ParallaxDivider` to this helper.

### 3. useTilt hook + React 18 callback-ref gotcha

Extracted shared mouse-tilt logic and applied it in `ProductGrid`, `CategoryGrid`, and `ArtGallery`.

React 18 makes `ref.current` read-only inside callback refs. To share a tilt ref with a parent ref array, type it as a `MutableRefObject`:

```tsx
const tiltRef = useRef<HTMLAnchorElement | null>(null)
  as React.MutableRefObject<HTMLAnchorElement | null>;
useTilt(tiltRef, { magnitude: 8 });

return (
  <Link
    ref={(el) => { tiltRef.current = el; parentRef(el); }}
    ...
  />
);
```

### 4. MagneticCursor rewrite

Replaced `MutationObserver` spam with event delegation:

```ts
const onOver = (e: MouseEvent) => {
  const target = e.target as HTMLElement | null;
  if (target?.closest("a, button, [data-cursor-hover]")) {
    cursor.classList.add("hovering");
  }
};
document.body.addEventListener("mouseover", onOver);
document.body.addEventListener("mouseout", onOver);
```

Also renamed `data-magnetic` to `data-cursor-hover` because the component only enlarges the cursor, not true magnetic pull.

### 5. HomeTextile horizontal scroll fix

The driving tween now has `id: "ht-scroll"`, and the inner parallax uses the live tween reference instead of `gsap.getById`. Width is computed dynamically:

```ts
const tween = gsap.to(horizontalRef.current, {
  x: () => -(getTotalWidth() - window.innerWidth + 100),
  id: "ht-scroll",
  scrollTrigger: {
    trigger: sectionRef.current,
    start: "top top",
    end: () => `+=${getTotalWidth()}`,
    scrub: 1,
    pin: true,
  },
});

// inner parallax
gsap.fromTo(img, { xPercent: -20 }, {
  xPercent: 20,
  scrollTrigger: { trigger: panel, containerAnimation: tween, scrub: true, start: "left right", end: "right left" },
});
```

### 6. Navigation

Replaced `<button>` + `window.location.href` with Next.js `<Link>`. Same-page anchors on the homepage use `scrollIntoView({ behavior: "smooth" })`; everything else routes normally.

### 7. ProductCard extraction

Created a reusable `ProductCard` component and converted `Products.tsx` and `ProductGrid.tsx` to use it. Added `formatPriceRange(from, to?)` to support the previously-unused `priceTo` field.

### 8. Tailwind tokens and focus-ring utility

Extended `tailwind.config.ts` with surface colors and a reusable component class:

```ts
colors: {
  vidvis: {
    surface: { 100: '#111', 200: '#141414', 300: '#1a1a1a' }
  }
}
plugins: [plugin(({ addComponents }) => {
  addComponents({
    '.focus-ring': {
      '@apply focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-vidvis-gold/60 rounded-sm': {},
    },
  });
})]
```

Replaced raw hex colors across 17 files with the new tokens.

## Verification

- `npm run build` passes with 6 generated routes.
- `npx tsc --noEmit` is clean.
- Dev server runs on ports 3001/3002 as required.

## Lessons

1. `gsap.context(() => { ... }, scope)` does **not** clean up `addEventListener` listeners. Always pair `gsap.context` with a separate cleanup or move listeners into a dedicated hook.
2. `gsap.ticker.add` / `remove` must use the exact same function reference. Store the wrapper in a ref.
3. `data-magnetic` was a misleading name — rename attributes when the behavior does not match.
4. React 18 callback refs make `ref.current` read-only; use `MutableRefObject` when you must assign inside the callback.
5. Centralizing `gsap.registerPlugin` via `src/lib/gsap.ts` removes boilerplate and makes imports deterministic.
6. Use `formatPriceRange` to keep price display logic in one place and to activate dead `priceTo` data.

## Files added/changed during refactor

- Added: `src/hooks/useTilt.ts`, `src/hooks/useGsapContext.ts`, `src/lib/gsap.ts`, `src/components/ProductCard.tsx`
- Modified: all major client components plus `src/data/catalog.ts`, `src/lib/format.ts`, `tailwind.config.ts`
- Report: `CODE_REUSE_AUDIT.md` in repo root captures the original audit findings.
