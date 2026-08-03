# Video Background Stacking Context Fix

Session-specific context: `silicone-landing-v2` Hero video not visible, 2026-08-01.

## Symptom

- The `<video>` element reports `readyState === 4`, `paused === false`, `currentTime` advances.
- The network request for `.mp4` returns 200.
- The video is still invisible in screenshots / browser.

## Root cause

The `<video>` used a negative `z-index` (`-z-20`) inside a `relative` section that did **not** create a new stacking context. In CSS, negative-z children can render behind the parent’s own background/box, becoming invisible even though they are technically painted.

## Reproduction recipe

```tsx
// BEFORE — video invisible
<section className="relative flex min-h-screen ...">
  <video className="absolute inset-0 -z-20 opacity-25 ..." />
  <div className="absolute inset-0 -z-10 ...">overlays</div>
  <div className="mx-auto ...">content</div>
</section>
```

## Fix

Give the parent section `isolation: isolate` (Tailwind `isolate`) so it forms a new stacking context. Then the negative-z video stays inside the section instead of falling behind it.

```tsx
// AFTER — video visible
<section className="relative isolate flex min-h-screen ...">
  <video className="absolute inset-0 -z-20 opacity-35 brightness-125 contrast-110 ..." />
  <div className="absolute inset-0 -z-10 ...">overlays</div>
  <div className="relative z-10 mx-auto ...">content</div>
</section>
```

Key changes:
1. `isolate` on the section.
2. `relative z-10` on the content container so it clearly sits above overlays.
3. Raise video opacity and add `brightness-125 contrast-110` if the source footage is dark.
4. Lighten gradient overlays so they do not drown the video.

## Verification

Use Playwright to confirm the video is actually visible, not just playing:

```js
const video = page.locator('#top video').first();
const currentTime = await video.evaluate(el => el.currentTime);
const paused = await video.evaluate(el => el.paused);
console.log({ currentTime, paused });
// Then take a screenshot and visually inspect the Hero background.
```

Also useful: temporarily hide overlays and video separately to identify which layer is the culprit.

## Mobile fallback

Keep `hidden md:block` on the video to avoid performance/bandwidth issues on narrow viewports, or replace with a static gradient fallback.

## Reference

- MDN: CSS `isolation` property — https://developer.mozilla.org/en-US/docs/Web/CSS/isolation
- Tailwind `isolate` / `isolation-auto` — https://tailwindcss.com/docs/isolation
