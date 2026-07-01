# CSS Layout Transition Pitfall — `transition: all` in dynamic grids

## The Symptom
When filtering/sorting a list of cards in a Bootstrap (or any CSS-grid/flex) layout, cards appear to "grow" from a tiny size to full size, and sibling cards jump around. The effect looks like a `scale()` animation but is actually a **layout reflow** being animated because of `transition: all`.

## Root Cause
Setting `transition: all` on `.card` (or any grid child) means **every** CSS property animates, including `width`, `height`, `margin`, `top`, `left`, etc. When React re-renders the filtered list, the grid recalculates column widths. The browser animates that recalculation over the transition duration (e.g. 250 ms), producing the "grow from small" visual.

## The Fix
Restrict `transition` to only the properties that should animate on hover/interaction:

```css
/* BEFORE — causes layout animation on filter */
.card {
  transition: all 250ms ease;
}

/* AFTER — only shadow + lift animate */
.card {
  transition: box-shadow 250ms ease, transform 250ms ease;
}
```

**Golden rule:** Never use `transition: all` on elements inside dynamic grids or lists that re-render.

## Affected Patterns
- Bootstrap `.row > .col-*` card grids with client-side filtering
- CSS Grid or Flexbox item lists with conditional rendering
- Any component where `map()` re-renders children with changed count/order

## Quick Checklist
- [ ] Does the element use `transition: all`?
- [ ] Is it inside a grid/flex container with dynamic children?
- [ ] If yes → replace `all` with explicit property list (`box-shadow`, `transform`, `opacity`, `color`, etc.)
