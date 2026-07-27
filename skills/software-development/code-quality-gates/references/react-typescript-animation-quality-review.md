---
name: react-typescript-animation-quality-review
description: |
  Review checklist for React/TypeScript codebases that use GSAP, Framer Motion,
  Lenis, or custom DOM-driven animations. Covers lifecycle leaks, stringly-typed
  code, copy-paste logic, accessibility gaps, and common AI-generated frontend
  slop patterns.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [react, typescript, frontend, quality, code-review, gsap, animation]
---

# React/TypeScript Animation Quality Review Checklist

Use when the user asks for a code-quality review of a React/TypeScript frontend,
especially one with scroll/parallax/motion libraries (GSAP, Framer Motion, Lenis).

## 1. Animation lifecycle

### 1.1 GSAP ScrollTrigger
- **Always wrap in `gsap.context(..., ref)` and `ctx.revert()` on cleanup.**
  Raw `gsap.to(..., { scrollTrigger: ... })` tweens survive component unmount
  and create duplicated triggers on HMR / re-render.
- **Register plugin once per module** (`gsap.registerPlugin(ScrollTrigger)`),
  but do not rely on it for cleanup.

### 1.2 Lenis + GSAP ticker
- The Lenis example from docs registers `lenis.raf` inside an anonymous wrapper:
  ```ts
  gsap.ticker.add((time) => lenis.raf(time * 1000));
  ```
  `gsap.ticker.remove(lenis.raf)` does **not** remove that wrapper. Store the
  wrapper in a ref and remove the exact function reference.
- **For Vite/React SPAs without Next.js PageShell**, centralize Lenis in a
  single `useLenis` hook called once at app root. Add anchor-link handling so
  `<a href="#section">` scrolls smoothly via Lenis instead of a browser jump.
  See `frontend-efficiency-audit/references/vidvis-smooth-scroll-session.md` for the consolidated smooth-scroll + animation polish recipe.

### 1.3 Animation scope in single-page landings
- Sections with continuous scroll effects (e.g. `Explorations` gallery with two
  columns moving in opposite directions) must use a single `ScrollTrigger`
  instance scoped to the section ref and clean it up with `ctx.revert()`.
- Use `scrub` values around `1`–`1.5` for smooth parallax; lower values feel
  mechanical, very high values feel disconnected.
- If a component adds raw `addEventListener` on `window`, `document`, or a ref,
  verify the cleanup removes the **same** function reference. A common bug is
  passing a new arrow function to `removeEventListener`.

### 1.4 MutationObserver in custom cursors
- A `MutationObserver` that attaches `mouseenter`/`mouseleave` listeners on every
  DOM mutation must also **remove old listeners** or disconnect the observer on
  cleanup. Otherwise listeners accumulate and cause memory leaks / stale state.

## 2. Stringly-typed / magic-string code

### 2.1 GSAP `getById`
- `gsap.getById("some-id")` returns `undefined` unless the target tween/timeline
  was created with `id: "some-id"`. Common failure: using `getById` for
  `containerAnimation` in ScrollTrigger but never setting the tween id. Verify
  the id exists; otherwise the nested animation silently does nothing.

### 2.2 DOM queries inside React
- `querySelector`, `getElementById`, and `document.querySelectorAll` inside
  components/hooks bypass React's render model. Prefer refs. If you must query,
  scope the query to the component's own ref and clean up.

### 2.3 Window dimension snapshots
- One-time `window.innerWidth` checks at mount miss resize and orientation
  changes. For cursor/animation enablement, prefer CSS media/pointer queries or
  add a resize listener with cleanup.

## 3. Copy-paste-with-variation

### 3.1 3D tilt cards
- If the same `mousemove`/`mouseleave` tilt logic appears in multiple grid
  components with only multiplier differences, extract it:
  - hook: `useCardTilt(ref, intensity)`
  - or wrapper: `<TiltCard intensity={10}>{children}</TiltCard>`

### 3.2 Page shells / client wrappers
- Nearly identical `*Client.tsx` files for `/art`, `/textile`, `/product` are a
  smell. Collapse to a single parameterized layout component if the only
  differences are props.

## 4. Redundant state

- State that is set but never read (e.g. `loaded` from `onLoadingComplete` when
  no UI depends on it) should be removed.
- Prefer deriving state with `useMemo` instead of mirroring props in state.

## 5. Accessibility / UX

- Respect `prefers-reduced-motion`. Skip or simplify scroll/parallax animations
  when the user has requested reduced motion (`useReducedMotion` or
  `matchMedia("(prefers-reduced-motion: reduce)"`).
- Image galleries should have keyboard support (`ArrowLeft`/`ArrowRight`,
  focus rings) and meaningful `alt` text.
- Navigation items that navigate should use `<Link>` (or `<a>` for external)
  rather than `<button onClick={() => window.location.href = ...}>`. Buttons
  break middle-click, keyboard shortcuts, prefetch, and accessible semantics.

## 6. AI slop patterns

- **Obvious comments** that restate the code (`// Entrance animation`,
  `// Scroll parallax for image`): remove or replace with *why*.
- **Unnecessary defensive null checks** after early returns or after TypeScript
  narrowing: keep only checks at real trust boundaries.
- **`cursor-pointer` on links**: redundant; browsers already show the pointer.
- **Inline style objects** mixed with Tailwind for simple transforms: prefer
  utility classes; use inline styles only for dynamic numeric values.

## 7. Verification commands

```bash
# Type safety
npx tsc --noEmit

# Lint (if configured)
npx next lint

# Search for common smells
grep -R "window.location.href" src/
grep -R "as gsap.core.Animation" src/
grep -R "gsap.getById" src/
grep -R "addEventListener" src/components --include="*.tsx"
grep -R "MutationObserver" src/
```
