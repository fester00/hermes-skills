# VIDVIS React/GSAP/Framer Motion efficiency audit

Real audit of a Next.js 14 / React 18 / TypeScript / Tailwind / GSAP / Lenis / Framer Motion site for `VIDVIS`.
Scope: recent diff (`PerspectiveScene.tsx`, `ProductDetail.tsx`) + full client component surface.

## Files reviewed

- `src/components/PerspectiveScene.tsx`
- `src/components/ProductDetail.tsx`
- `src/components/Navigation.tsx`
- `src/components/MagneticCursor.tsx`
- `src/components/PageShell.tsx`
- `src/components/Hero.tsx`
- `src/components/Products.tsx`
- `src/components/ProductGrid.tsx`
- `src/components/CategoryGrid.tsx`
- `src/components/ArtGallery.tsx`
- `src/components/HomeTextile.tsx`
- `src/hooks/useLenis.ts`
- `src/hooks/useReducedMotion.ts`
- `src/data/catalog.ts`

## Findings with file/line and fix

### `useLenis.ts` — GSAP ticker callback leak

```ts
// original
lenis.on("scroll", ScrollTrigger.update);
gsap.ticker.add((time) => {
  lenis.raf(time * 1000);
});
return () => {
  lenis.destroy();
  gsap.ticker.remove(lenis.raf); // WRONG reference
};
```

**Problem:** The added function is the wrapper `(time) => lenis.raf(time * 1000)`; the removed function is `lenis.raf`. Different references ⇒ ticker callback leaks on every mount/unmount cycle.

**Fix:** store the wrapper and remove the same wrapper.

```ts
const rafRef = useRef<(time: number) => void>();
useEffect(() => {
  if (reduced) return;
  const lenis = new Lenis({ ... });
  lenisRef.current = lenis;
  lenis.on("scroll", ScrollTrigger.update);
  const raf = (time: number) => lenis.raf(time * 1000);
  rafRef.current = raf;
  gsap.ticker.add(raf);
  gsap.ticker.lagSmoothing(0);
  return () => {
    lenis.destroy();
    if (rafRef.current) gsap.ticker.remove(rafRef.current);
  };
}, [reduced]);
```

### `MagneticCursor.tsx` — listener duplication + MutationObserver spam

```ts
const observer = new MutationObserver(() => {
  const interactives = document.querySelectorAll("a, button, [data-magnetic]");
  interactives.forEach((el) => {
    el.addEventListener("mouseenter", onHover);
    el.addEventListener("mouseleave", onLeave);
  });
});
observer.observe(document.body, { childList: true, subtree: true });
```

**Problem:** Every DOM mutation re-adds listeners without removing old ones; unmount cleanup does not remove listeners previously attached to interactive elements.

**Fixes:**
1. Use event delegation on `document.body` for `mouseenter`/`mouseleave` and check `e.target.closest("a, button, [data-magnetic]")`.
2. Or keep a `WeakSet`/`Set` of observed elements, remove listeners from removed nodes before adding to new ones.
3. Pause the RAF loop when `document.hidden` or cursor not visible.

### `ProductGrid.tsx`, `CategoryGrid.tsx`, `ArtGallery.tsx` — DOM listener leaks

These add `mousemove` / `mouseleave` listeners on mapped card elements inside `gsap.context`:

```ts
card.addEventListener("mousemove", onMove);
card.addEventListener("mouseleave", onLeave);
```

**Problem:** `ctx.revert()` kills GSAP tweens but does **not** remove `addEventListener` listeners. On re-run/unmount, listeners accumulate.

**Fix:** attach listeners in a separate effect or store the handler pair and remove explicitly:

```ts
cardsRef.current.forEach((card) => {
  if (!card) return;
  const onMove = (e: MouseEvent) => { ... };
  const onLeave = () => { ... };
  card.addEventListener("mousemove", onMove);
  card.addEventListener("mouseleave", onLeave);
  card._cursorHandlers = { onMove, onLeave };
});

return () => {
  cardsRef.current.forEach((card) => {
    if (!card || !card._cursorHandlers) return;
    card.removeEventListener("mousemove", card._cursorHandlers.onMove);
    card.removeEventListener("mouseleave", card._cursorHandlers.onLeave);
  });
};
```

Also, the inline ref callback `ref={(el) => { cardsRef.current[i] = el; }}` runs every render. Use a stable ref factory.

### `HomeTextile.tsx` — broken horizontal-scroll parallax

```ts
gsap.to(horizontalRef.current, {
  x: () => -(totalWidth - window.innerWidth + 100),
  ease: "none",
  scrollTrigger: {
    trigger: sectionRef.current,
    start: "top top",
    end: () => `+=${totalWidth}`,
    scrub: 1,
    pin: true,
    anticipatePin: 1,
  },
});

// later
gsap.fromTo(img, { xPercent: -20 }, {
  xPercent: 20,
  ease: "none",
  scrollTrigger: {
    trigger: panel,
    containerAnimation: gsap.getById("ht-scroll") as gsap.core.Animation,
    ...
  },
});
```

**Problem:** `gsap.getById("ht-scroll")` returns `undefined` because the horizontal tween was never given `id: "ht-scroll"`. The inner parallax images silently do not scrub.

**Fix:** add `id: "ht-scroll"` to the horizontal tween, or capture the tween in a ref and pass it directly:

```ts
const hTween = gsap.to(horizontalRef.current, {
  id: "ht-scroll",
  ...
});
// then
gsap.fromTo(img, ..., { scrollTrigger: { containerAnimation: hTween, ... } });
```

Also, widths are measured only at mount; refresh on resize/font-load.

### `PerspectiveScene.tsx` — hot-path bloat and missing cleanup

- Mousemove handler calls `gsap.to(scene, ...)` on every event, queuing overlapping tweens. Use `gsap.quickTo(scene, { rotateY, rotateX })` or throttle with a single RAF reading `mouseRef.current`.
- Static `cards` array, `positions` array, inline particle/lines descriptors are recreated each render. Hoist to module scope.
- ScrollTrigger/gsap tweens are not wrapped in `gsap.context`; cleanup removes only mouse listeners. Wrap in `gsap.context` and call `ctx.revert()` on unmount.

### `Navigation.tsx` — scroll thrash + full-page reloads

- `onScroll` calls `setScrolled(window.scrollY > 50)` on every scroll event. RAF-throttle or compare to previous value before setting state.
- Navigation buttons use `window.location.href` for internal routes, forcing full page reloads. Use `next/link` for route changes; use `scrollIntoView` only for same-page anchors.

### `Preloader.tsx` — timeout not cleared

`setInterval` is cleared, but a `setTimeout` scheduled inside the interval callback is not cleared on unmount. Store the timeout id and clear it.

### `Hero.tsx` — unused state

`loaded` state is set but never read; remove it to avoid a re-render.

### `Products.tsx` — repeated catalog work

`const products = getAllProducts().slice(0, 8);` runs every render. The catalog is static but `getAllProducts()` flattens on each call. Memoize at module level or wrap in `useMemo`.

## Verification notes

After fixes:

- Run `npm run build` / `next build`.
- Mount/unmount components via route navigation and check `ScrollTrigger.getAll().length` returns to baseline.
- Use DevTools Memory: listeners and detached DOM nodes should not grow after navigation.
- Test with `prefers-reduced-motion: reduce` enabled; animations should be skipped.
- Confirm Framer Motion entrance animations still trigger (hoisted variants/objects should not break motion semantics).