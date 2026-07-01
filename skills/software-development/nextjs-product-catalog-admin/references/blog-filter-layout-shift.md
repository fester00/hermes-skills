# Layout-Shift Bug: Blog Filter Buttons (PentaJunior v3)

## Symptom

When switching blog category filters, the grid of articles "jerks" — cards
visibly jump/recalculate their positions. User described it as «дергание
элементов блога» during filter animation.

## Environment

- Next.js 16 + React 19 + Bootstrap 5.3.8
- `globals.css` heavily overrides `.btn-primary` with custom padding,
  gradients, shadows, `border: none`
- Blog filter toggles between `btn-primary` (active) and `btn-outline-secondary`
  (inactive)

## Root Cause

`globals.css` overrides `.btn-primary` with:

```css
.btn-primary {
  padding: 0.625rem 1.5rem;
  border: none;
  /* ... gradients, shadows */
  transition: all var(--transition-base);
}
```

But `.btn-outline-secondary` falls back to **Bootstrap defaults** for `btn-sm`:
- `padding: 0.25rem 0.5rem` (smaller)
- `border: 1px solid #6c757d`

When React switches the class, `transition: all` animates `padding` and
`border-width`, which changes the button's box size. Inside a
`d-flex flex-wrap` container, even a 2px size change triggers flex-wrap
recalculation. The whole grid reflows — hence the "jerking".

## Investigation Steps

1. **Read `BlogList.tsx`** — confirmed buttons toggle between `btn-primary`
   and `btn-outline-secondary` via ternary in `className`.
2. **Read `globals.css`** — found `.btn-primary` override with custom padding,
   `border: none`, `transition: all`. No override for `.btn-outline-secondary`.
3. **Checked for animation libraries** — none (no Framer Motion, no GSAP).
4. **Ruled out React issues** — no `AnimatePresence`, no `layout` props.
   Pure CSS class toggle.
5. **Identified the metric delta** — padding differs by ~0.375rem per axis,
   border differs by 1px. Combined with `transition: all` = guaranteed layout shift.

## Evolution of Fixes (Real-World Timeline)

### Stage 1: Original code (bug present)
```tsx
className={`btn btn-sm rounded-pill ${
  isActive ? "btn-primary" : "btn-outline-secondary"
}`}
```
- **Problem**: `btn-outline-secondary` uses Bootstrap default metrics;
  `btn-primary` is overridden in `globals.css` with different padding/border.
- **Result**: layout shift on every toggle.

### Stage 2: Quick fix (wrong colors, no shift)
```tsx
className={`btn btn-sm rounded-pill ${
  isActive ? "btn-secondary" : "btn-primary"
}`}
```
- **Why it worked**: both `btn-secondary` and `btn-primary` are overridden in
  `globals.css` with **identical metrics** (`padding`, `border-radius`, `font-size`).
- **Why it was rejected**: color scheme does not match design intent.
  User wants the **outline appearance** for inactive filters.

### Stage 3: Final fix (correct visuals, no shift)
Replaced Bootstrap class toggle with a **single custom class** + `active` modifier:

```tsx
<button className={`blog-filter-btn ${isActive ? "active" : ""}`}>
```

```css
.blog-filter-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 2px solid var(--color-primary);
  border-radius: var(--radius-full);
  padding: 0.5rem 1.375rem;        /* FIXED — identical for active + inactive */
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-primary);
  cursor: pointer;
  box-sizing: border-box;
  /* Layout-safe transitions only */
  transition: background-color 250ms ease,
              color 250ms ease,
              box-shadow 250ms ease;
  white-space: nowrap;
}

.blog-filter-btn.active {
  background: linear-gradient(135deg, var(--olive-green), var(--olive-light));
  border-color: transparent;
  color: #fff;
  box-shadow: var(--shadow-glow);
}
```

Key fix: `transition` explicitly lists only `background-color`, `color`,
`box-shadow`. `padding`, `border-width`, `width`, `height` are **not**
animated — no layout reflow possible.

## Verification

- `npx next build` passed successfully.
- Visual check: buttons maintain identical width/height between states.
- No flex-wrap recalculation — grid stays stable during filter switches.

## Key Takeaways

1. **When Bootstrap classes are heavily overridden in `globals.css`, toggling
   between two different Bootstrap classes as UI states is dangerous.** The
   overrides often apply to only one of the classes, creating a metric mismatch.
   Always prefer a **single custom class** with state modifiers for toggle UIs
   in heavily customized Bootstrap projects.

2. **A "working" fix that changes colors is not necessarily the right fix.**
   In this case `btn-secondary`/`btn-primary` eliminated the shift but produced
   an undesirable color scheme. The correct solution preserves both the
   intended visual style (outline for inactive) and layout stability.

3. **Apply fixes consistently across all project variants.** The blog filter
   bug existed in `pentajunior`, `pentajunior-v3`, and `penta-junior-v2`. The
   `.blog-filter-btn` custom class was added to all three repositories' `globals.css`
   to prevent regression. Always check whether a fix needs to propagate to
   other maintained variants before declaring the task complete.

4. **Verify the project name precisely.** The user said "pentajunior-v3" but
   a similarly-named project `pentajunior` (without `-v3`) also exists locally.
   Always `cd` into the exact directory the user names, or confirm with
   `git remote -v` before pushing.