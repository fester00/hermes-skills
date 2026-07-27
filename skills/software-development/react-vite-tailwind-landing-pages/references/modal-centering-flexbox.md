# Modal Centering with Flexbox

## Anti-pattern: absolute centering only

```tsx
className="fixed inset-4 md:inset-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 ..."
```

Problems:
- On mobile, `inset-4` plus `top-1/2 -translate-y-1/2` can push the modal off-screen.
- Absolute centering does not handle dynamic content height gracefully.
- Backdrop click detection becomes fragile if the modal doesn't fill the viewport.

## Better pattern: flex wrapper

```tsx
<>
  {/* backdrop */}
  <motion.div
    onClick={onClose}
    className="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm"
  />

  {/* flex centering wrapper */}
  <div className="fixed inset-0 z-[101] flex items-start md:items-center justify-center p-4 md:p-6 overflow-y-auto">
    <motion.div
      className="relative w-full md:max-w-2xl max-h-[90vh] overflow-y-auto ... my-auto md:my-0"
      onClick={(e) => e.stopPropagation()}
    >
      {/* content */}
    </motion.div>
  </div>
</>
```

## Why it works

- `fixed inset-0` covers the viewport.
- `flex ... justify-center` centers horizontally.
- `items-start md:items-center` centers vertically on desktop, top-aligns on mobile.
- `overflow-y-auto` on both wrapper and modal lets tall content scroll.
- `my-auto` helps center shorter modals when `items-center` is active.

## Variations

- For tall modals that should always start at the top: `items-start` at all
  breakpoints and remove `my-auto`.
- For centered non-scrollable dialogs: drop `overflow-y-auto` and use a fixed
  height dialog with `items-center`.
- For reliable click-outside behavior, set `pointer-events-none` on the flex
  wrapper and `pointer-events-auto` on the modal content.
