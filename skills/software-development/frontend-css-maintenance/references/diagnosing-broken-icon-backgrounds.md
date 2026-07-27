# Diagnosing "broken" icon backgrounds / visual artifacts

Session: silicone-landing contacts section, 2026-07-27.

## Symptom

User reports "broken substrates/backgrounds under icons" next to phone/email/address in a dark landing page. The icons sit inside circular `rounded-full` containers. Screenshot shows dark vertical streaks or clipped shapes apparently coming from behind the icon circle.

## First hypothesis (wrong)

CSS conflict between inline Tailwind classes and component-level `.icon-container` rules: duplicate background/border definitions creating visual glitch.

## Actual root cause

The Lucide SVG icons themselves (`Mail`, `Phone`, `MapPin`) have stroke shapes that extend beyond a tight circular bounding box, especially `MapPin` (point extends downward) and `Phone` (handset curves). When placed inside a small `w-11 h-11 rounded-full` circle, the icon strokes either:
- visually touch or cross the circle edge, making the border look ragged; or
- when the container has no `overflow-hidden`, appear to "leak" outside the circle against the busy video background.

The circular container shape is the wrong choice for these non-square icon silhouettes.

## Diagnostic recipe

When a user reports broken icon backgrounds, verify before editing CSS:

1. **Check computed styles of the icon wrapper** with Playwright or DevTools:
   ```ts
   const s = await page.evaluate(() => window.getComputedStyle(document.querySelector('.icon-wrapper')));
   // look for unexpected box-shadow, filter, transform, pseudo-elements
   ```
   If background, border-radius, border, and `overflow` are all correct and there are no `::before`/`::after`, the problem is likely not CSS.

2. **Check `transform` and `opacity` on every ancestor up to the icon wrapper.** Scroll-reveal wrappers (`.reveal`, `.in-view`) may apply `translateY` + opacity transitions that can interact with subpixel rendering on thin borders or translucent backgrounds, especially at 1× device scale. Wait for the transition to finish before judging the final state.

3. **Hide the background layer** (video/image/gradient) in DevTools. If the artifact disappears, it was leakage from the busy background through a translucent or un-clipped icon area. If the artifact remains, it is part of the icon or container.

4. **Zoom / clip a screenshot** at 2× device scale factor focused on the icon. Look for whether the "streak" is inside or outside the wrapper's computed box.

5. **Inspect the SVG `viewBox` and paths**:
   - Lucide icons default to a 24×24 viewBox.
   - Icons like `MapPin`, `Phone`, `Headphones`, `Send`, `Megaphone` have shapes that do not fit well in a small circle.
   - A circular mask works best for compact square-ish icons: `Mail` (with reduced size), `User`, `Settings`, `Check`, `Star`.

## Fix options

| Approach | When to use | Trade-off |
|----------|-------------|-----------|
| **Use `overflow-hidden` on the wrapper** | Fast mitigation, keeps circular shape | May clip icon strokes abruptly, still looks slightly off for non-square icons |
| **Increase wrapper size** (`w-13 h-13`) and reduce icon size (`size={18}`) | Best first fix | Preserves circle, adds padding, keeps icon silhouette intact |
| **Switch wrapper shape to rounded square / squircle** (`rounded-xl` or `rounded-2xl`) | Most robust for irregular icon silhouettes | Slightly changes visual language; make sure it matches card design |
| **Replace icon with a more compact variant** | When brand language demands a circle | Requires user/design approval |

## Recommended pattern for contact cards

For the silicone-landing style (dark, glassy, blue accent):

```tsx
<div className="w-13 h-13 rounded-2xl bg-surface-elevated border border-stroke flex items-center justify-center flex-shrink-0 overflow-hidden">
  <Icon size={20} strokeWidth={1.5} className="text-accent-blue-light" />
</div>
```

- `w-13 h-13` (52px) gives the icon enough internal padding.
- `rounded-2xl` (16px) is more forgiving than `rounded-full` for irregular strokes.
- `overflow-hidden` clips only in extreme cases; usually not needed with this size.

## Lesson

"Broken background under icon" is often misdiagnosed as a CSS background/opacity bug. Verify the icon silhouette against the container shape first. Small circular icon wells look elegant but fail for icons whose artwork extends toward the corners or has a tail/pin shape.
