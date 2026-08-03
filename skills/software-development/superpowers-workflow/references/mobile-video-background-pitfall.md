# Mobile video background pitfall

## Symptom

A product grid or card section with a full-width looping video background looks correct on desktop but appears empty on mobile screenshots. The DOM contains the cards, but they are invisible behind a dark overlay or the video layer.

Typical layout that fails on mobile:

```tsx
<section className="relative overflow-hidden">
  <video
    autoPlay muted loop playsInline
    className="absolute inset-0 -z-20 h-full w-full object-cover opacity-20"
    src="/video/background.mp4"
  />
  <div className="absolute inset-0 -z-10 bg-gradient-to-b from-bg/80 via-bg/85 to-bg/80" />
  {/* cards here */}
</section>
```

On narrow viewports the video keeps its aspect ratio and may not cover the whole section height; the gradient overlay can dominate the frame and hide cards, especially when combined with Framer Motion `whileInView` that delays card entrance.

## Fixes

1. **Hide the video on mobile and use a solid background.** This is the safest option when the video is decorative.

```tsx
<video
  autoPlay muted loop playsInline
  className="pointer-events-none absolute inset-0 -z-20 hidden h-full w-full object-cover opacity-10 md:block"
  src="/video/background.mp4"
/>
<div className="pointer-events-none absolute inset-0 -z-10 bg-bg md:bg-bg/40" />
```

2. **Keep the video visible but dramatically reduce opacity and lighten the overlay.**

```tsx
<video className="... opacity-[0.08]" />
<div className="... bg-gradient-to-b from-bg/40 via-bg/50 to-bg/40" />
```

3. **Ensure cards are not `opacity: 0` at first paint.** See `references/framer-motion-ssr-initial-opacity.md`. Combine with the above for reliable mobile rendering.

## Verification

Always capture both desktop and mobile full-page screenshots after adding a video background. A desktop-only check will miss this issue.

## Session provenance

2026-08-01 — `silicone-landing-v2` design refinement: added video background to Products. Desktop looked fine, but the mobile full-page screenshot showed an empty section because the overlay + video covered the cards and `whileInView` opacity animation hid cards until scroll. Fixed by reducing overlay opacity and hiding the video on mobile.
