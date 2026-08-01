---
name: frontend-efficiency-audit
description: |
  Systematic efficiency review of frontend/React/TypeScript codebases:
  unnecessary re-renders, repeated work, missed memoization, event/listener leaks,
  missing useEffect cleanup, unbounded growth, and silent failures in animation stacks.
category: software-development
related_skills:
  - code-quality-gates
  - superpowers-workflow
---

# frontend-efficiency-audit

Audit a frontend codebase (especially React + GSAP/Framer Motion/Lenis animation stacks) for runtime efficiency problems before they become performance bugs or memory leaks.

## When to use

- User asks to "review for efficiency", "find re-renders", "optimize React", "check for memory leaks", "audit hooks", etc.
- A diff touches client components, animations, scroll handlers, or event listeners.
- Pre-commit / pre-merge review of `"use client"` components.
- Site feels janky, scroll is slow, fans spin, or memory grows during navigation.
- Auditing a recently changed component alongside the broader codebase surface.

## Audit checklist

Map the surface before changing code:

1. Identify all client components (`"use client"`).
2. List every `useEffect`, `useLayoutEffect`, and `useInsertionEffect`.
3. List every DOM event listener attachment (`addEventListener`, `onClick`, etc.).
4. List every GSAP/ScrollTrigger/Framer Motion context and verify cleanup.
5. List every `setInterval`, `setTimeout`, and `requestAnimationFrame`.
6. List every state setter called inside scroll/resize/mousemove handlers.
7. Check navigation: `window.location.href` vs framework router (`next/link`, `react-router`, etc.).
8. Check for inline style/animate/transition objects in motion components.
9. Check for inline ref callbacks in mapped arrays.
10. Check whether the SPA has prerendered/SSR content for SEO and whether the
    build produces a populated `index.html`. A Vite SPA with a loading screen
    often ships an empty `<div id="root"></div>`, which hurts search indexing.
    Verify by inspecting `dist/index.html` after `npm run build`.

### 7. Missing prerender / empty `index.html`

- **Vite/React SPA serves an empty `index.html`**. If the project cares about
  SEO, the build step must inject rendered content into the root element.
- *Fix:* migrate to Next.js 15 App Router for SSR/SSG, or add a post-build prerender.
  Next.js App Router gives populated HTML automatically; for Vite SPA use one of:
    — Playwright-based prerender that executes the client bundle.
    — lightweight `react-dom/server` via Vite SSR; pass a `prerender` prop to
      `App` so the loading screen is skipped during the SSR pass.
- *Verification for Next.js:* `curl -s http://localhost:3000 | grep -E '<title|<h1'`
  should return values. For Vite: `wc -c dist/index.html` should be 20–80 KB
  for a content-rich landing page, and `grep` should find product names and headings.
- **Migrating from Vite SPA to Next.js 15 App Router:** see `superpowers-workflow`
  → `references/nextjs-app-router-spa-migration.md` for a complete checklist
  (client-component boundaries, metadata/JSON-LD, fonts, images, build verification).

---

## Common anti-patterns and fixes

### 1. Unnecessary re-renders

- **Inline style/animate/transition objects for motion components** (`style={{...}}`, `initial={{...}}`, `animate={{...}}`, `transition={{...}}`). Each render creates a new reference; Framer Motion must diff and may re-queue animation work.
  - *Fix:* hoist static objects to module scope, or memoize with `useMemo` when props are dynamic.
- **Inline ref callbacks in mapped arrays**: `ref={(el) => { refs.current[i] = el; }}` is a new function every render, so React calls it twice per update and may churn refs.
  - *Fix:* use a `useCallback`-ed ref factory, or maintain a `Map`/`WeakMap` with stable keys.
- **Fresh closures and template literals inside `.map()`**: `onClick={() => setX(i)}` and dynamic `className` strings create new functions/strings per item every render.
  - *Fix:* extract a memoized subcomponent (`React.memo`) and pass stable callbacks or use a callback factory.

### 2. Listener and handle leaks

- **Event listeners added inside `gsap.context` without explicit removal**. `ctx.revert()` kills tweens and ScrollTriggers, but it does **not** remove DOM event listeners you attached with `addEventListener`.
  - *Fix:* attach DOM listeners in a separate effect with an explicit cleanup function, or store the handler references and call `removeEventListener` in cleanup. Better: extract a reusable hook (e.g. `useTilt`) that owns its own listeners.
- **MutationObserver re-adding listeners on every mutation** (common in custom cursor components that track `a, button, [data-magnetic]`).
  - *Fix:* prefer event delegation on `document.body`, or diff the previous interactive set and remove stale listeners before adding new ones. If the component only enlarges the cursor on hover, rename the attribute from `data-magnetic` to `data-cursor-hover` so the intent is not misleading.
- **Scroll/resize/mousemove handlers that call `setState`** on every event.
  - *Fix:* throttle with `requestAnimationFrame`, or compare with the previous value and only set state when it changes.

### 3. Missing cleanup

- **`gsap.ticker.add(fn)` / `gsap.ticker.remove(fn)` reference mismatch**. If you add a wrapper function `(time) => lenis.raf(time * 1000)`, you must remove the exact same wrapper reference.
  - *Fix:* store the wrapper in a `useRef` and pass that same ref to `gsap.ticker.remove`.
- **`setTimeout`/`setInterval` ids not cleared** when a component unmounts. This includes timeouts scheduled inside interval callbacks.
  - *Fix:* store all timer ids in refs and clear them in the effect cleanup.
- **ScrollTrigger/Lenis instances not killed** on unmount. Prefer `gsap.context(() => { ... }, scope)` and `return () => ctx.revert()`.
- **Unconditional `requestAnimationFrame` loops** running even when the tab is hidden or the component is off-screen.
  - *Fix:* pause on `document.visibilitychange` or when the tracked element is not visible.

### 4. Silent failures / broken animations

- **`containerAnimation` in ScrollTrigger referencing an animation by id** that was never assigned (`gsap.getById("...")` returns `undefined`). The inner parallax then silently does not scrub.
  - *Fix:* assign `id: "..."` to the driving tween and import from the centralized `gsap` module, or capture the tween in a ref and pass it directly. Passing the live tween reference is safer than `getById` when the tween is recreated on mount.
- **`window.location.href` instead of framework router navigation** causes full-page reloads.
  - *Fix:* use `<Link>` / `router.push` for route changes; use `scrollIntoView` only for same-page anchors.
- **Measurements taken only at mount** (`offsetWidth`, `window.innerWidth`) and never refreshed on resize or font loading.
  - *Fix:* make ScrollTrigger `end` and tween targets functions, or refresh on resize and font events. For horizontal-scroll galleries, return a function from `end` and `x` so widths are recomputed after layout.

### 5. Hot-path bloat

- Mousemove handlers firing `gsap.to()` on every event, creating overlapping tweens.
  - *Fix:* use `gsap.quickTo` for pointer-driven transforms, or throttle via a single `requestAnimationFrame` loop reading from a ref. For reusable card tilt, extract a `useTilt` hook (see `templates/useTilt.ts`) so the parent only manages reveal tweens.
- **Large static arrays/objects recreated in render** (`[...Array(N)]`, inline card data, particle configs, inline arrays of JSX descriptors).
  - *Fix:* hoist to module scope, or memoize once with `useMemo`.
- **Components registering `gsap.registerPlugin(ScrollTrigger)` repeatedly**. GSAP tolerates it but it is noisy and unnecessary.
  - *Fix:* create `src/lib/gsap.ts` that registers once and re-exports `gsap` and `ScrollTrigger`. Every component imports from there:

    ```ts
    // src/lib/gsap.ts
    import gsap from "gsap";
    import { ScrollTrigger } from "gsap/ScrollTrigger";
    if (typeof window !== "undefined") gsap.registerPlugin(ScrollTrigger);
    export { gsap, ScrollTrigger };
    ```

    ```ts
    // in a component
    import { gsap } from "@/lib/gsap";
    ```

### 5a. Animation lifecycle helpers

Repeated `useReducedMotion` guards plus `gsap.context` boilerplate invite copy-paste bugs. Extract a small hook:

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

This removes ~10 lines per animated section, centralizes reduced-motion handling, and makes it harder to forget cleanup.

### 6. Unbounded growth

- **Arrays of refs populated inline** can retain detached DOM nodes if not cleared on cleanup.
  - *Fix:* clear the ref array in the cleanup function.
- **MutationObserver left connected** after unmount.
  - *Fix:* call `observer.disconnect()` in cleanup.
- **Timers/intervals that keep scheduling work** even after the component is gone.
  - *Fix:* centralize timer ids and clear on unmount.

## Workflow

1. Read the diff and identify the changed client components.
2. Read the broader component surface that shares patterns (event listeners, GSAP contexts, mapped refs, animation hooks).
3. Run the audit checklist above and classify findings by severity:
   - **CAREFUL** — memory leaks, broken cleanup, full-page reloads, silent animation failures, empty `index.html` for an SEO landing page.
   - **SAFE** — unnecessary re-renders, inline objects, repeated static work.
4. Propose minimal, targeted fixes. Prefer stable references and explicit cleanup over premature optimization.
5. Verify after fixes:
   - `npm run build` / `next build` passes.
   - For Vite SPAs that need SEO, `dist/index.html` contains rendered body content.
   - Mount/unmount paths exercised (route changes, dialogs).
   - DevTools Performance / Memory shows no retained listeners or detached nodes.
   - Animations still respect `prefers-reduced-motion: reduce` if applicable.
   - `ScrollTrigger.getAll()` is clean after navigation.

## References

- Project-specific case studies moved to Obsidian vault.

## Related skills

- `code-quality-gates` — when a symptom already exists and you need root cause analysis.
- `superpowers-workflow` — umbrella for full project lifecycle.
- `frontend-css-maintenance` — when the audit surfaces unused or risky CSS.
- `simplify-code` — when the audit finds bloat to remove.