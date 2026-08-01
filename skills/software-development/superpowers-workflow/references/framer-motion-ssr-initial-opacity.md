# Framer Motion SSR/SSG initial opacity pitfall

## Symptom

A Next.js 15 App Router page using Framer Motion `whileInView` animations renders blank sections in the static HTML preview and on first paint. The content only becomes visible after the client-side intersection observer fires — which may be too late for screenshots, SEO first paint, or users with slow JS.

Example that fails:

```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true }}
>
```

## Fix

Keep the element visually present in its initial state and animate only transform or scale. The content is readable on first paint, and the motion still feels premium once the client hydrates.

```tsx
// BAD — blank on first paint
initial={{ opacity: 0, x: 64 }}
whileInView={{ opacity: 1, x: 0 }}

// GOOD — content is visible, then slides in
initial={{ opacity: 1, x: 64 }}
whileInView={{ opacity: 1, x: 0 }}
viewport={{ once: true, amount: 0.6 }}
```

This is especially important for **sticky-scrolling feature sections** where cards are expected to be readable in a full-page screenshot or before the client JavaScript executes.

## When `opacity: 0` initial is still safe

For elements that are not part of the initial static paint — such as modals, toasts, or error messages that only appear after user interaction — `initial={{ opacity: 0 }}` paired with `AnimatePresence` is acceptable because there is no meaningful SSR output to obscure.

## Quick diagnostic

If a full-page screenshot or static render shows an entire section as empty but the DOM contains the content, search the component for `initial={{ opacity: 0 }}` paired with `whileInView`. That is almost always the cause.

## When this matters

- Static landing pages pre-rendered with `next build`.
- Screenshots / smoke tests that capture the page without scrolling.
- SEO and accessibility: invisible text at first paint is poor UX.

## Related references

- `references/external-design-spec-adaptation.md` — applying third-party design specs while preserving SSR-visible content.

## Session provenance

2026-08-01 — `silicone-lending-v3` Drift-style redesign: sticky-scrolling Products cards were `opacity: 0` until IntersectionObserver fired, making full-page screenshots look empty. Switching cards to `initial={{ opacity: 1, x: 64 }}` restored visibility while preserving the slide-in animation.
