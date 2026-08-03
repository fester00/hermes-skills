# Vite + React SPA Landing Page Polish

Session reference for upgrading an existing Vite + React 19 + Tailwind 3 landing page to a premium dark B2B look.

## When this applies

- Existing project path like `/mnt/data/natan-storage/silicone-landing-v2`.
- Stack: Vite 8, React 19, TypeScript, Tailwind CSS 3.4.x, Framer Motion.
- Goal: visual polish — equal-height cards, harmonious badges, glassmorphism, hover glow, video background.

## Pre-code workflow

1. **Kill competing dev servers** — check ports 3000–3003, stop stale Next.js/Vite preview processes.
2. **Start the existing preview server** on the port the user specified (e.g. 3002).
3. **Capture baseline screenshots** with Playwright directly; do not rely on `browser_navigate` for localhost because Hermes blocks private addresses.
   - Script location: `scripts/audit-screenshots.mjs` or temporary under project root.
   - Viewports: desktop 1440×900 and mobile 390×844.
   - Modal screenshot: click a product card, wait, capture.
4. **Load design skills**:
   - `ui-ux-pro-max` for product-type recommendations.
   - `popular-web-designs` for real brand palettes and component vocab.
   - `react-premium-landing-effects` for motion/FX patterns.
5. **Check Obsidian vault fallback** — if MCP times out, use `find`/`read_file` directly under `~/obsidian-memory`.
6. **Write implementation plan** before any code changes; get explicit user approval.

## Typical issues found

- Cards have different heights because `flex-wrap` feature badges push content down unevenly.
- Feature badges look like bright "buttons" instead of subtle specs.
- Modal uses a different badge style than the card.
- Video file exists in `public/video/` but is invisible due to overly dense overlay.

## Recommended fixes

### Equal-height cards

Use `auto-rows-fr` on the grid wrapper and a fixed internal content grid inside the card:

```tsx
// Grid wrapper
<div className="grid auto-rows-fr gap-5 sm:grid-cols-2 lg:grid-cols-4">
  {items.map(item => (
    <div key={item.id} className="flex h-full min-h-[480px]">
      <ProductCard item={item} />
    </div>
  ))}
</div>

// Inside ProductCard
<div className="flex flex-1 flex-col p-5">
  <h3 className="line-clamp-1">{item.name}</h3>
  <p className="line-clamp-2 min-h-[2.75rem]">{item.title}</p>
  <div className="mb-auto min-h-[5.5rem]">
    <div className="flex flex-wrap gap-2">
      {features.map(f => <FeatureBadge key={f} feature={f} />)}
    </div>
  </div>
  <div className="mt-4 border-t border-stroke pt-4">...</div>
</div>
```

### Harmonious feature badges

Create a single shared `FeatureBadge` component:

```tsx
export function FeatureBadge({ feature, size = "md" }: { feature: string; size?: "sm" | "md" }) {
  return (
    <span className={`inline-flex items-center rounded-full border border-stroke bg-surface-2/80 font-medium text-accent backdrop-blur-sm transition-colors hover:border-accent/30 hover:bg-surface-2 ${size === "sm" ? "px-2.5 py-1 text-xs" : "px-3 py-1.5 text-sm"}`}>
      {feature}
    </span>
  );
}
```

Use it in both `ProductCard` and `ProductModal` so styles stay identical.

### Premium hover on cards

Keep it simple and reliable across browsers:

```tsx
<button className="group ... transition-all duration-300 hover:-translate-y-1.5 hover:border-accent/30 hover:shadow-xl hover:shadow-black/30 hover:ring-accent/20">
  {/* content */}
</button>
```

The `-webkit-mask` gradient-border trick is fragile in Vite/SPA builds; prefer Tailwind `ring` + `border` + `shadow` unless the user explicitly asks for gradient borders.

### Background video in Hero

```tsx
<video
  autoPlay
  muted
  loop
  playsInline
  preload="auto"
  className="pointer-events-none absolute inset-0 -z-20 hidden h-full w-full object-cover opacity-[0.12] md:block"
  src="/video/background.mp4"
/>
```

Keep existing gradient overlays above the video (`-z-10`) so text remains readable. Verify the video file exists under `public/video/background.mp4` before running `npm run build`; the Vite build will include it in `dist/` automatically.

### Contact polish

- Wrap the form card in `rounded-2xl border border-stroke bg-surface/80 p-5 backdrop-blur-md sm:p-7`.
- Wrap each contact block (Email, Phones, Address) in `rounded-xl border border-stroke bg-surface/80 p-4 backdrop-blur-md transition-colors hover:border-accent/30`.

### OrderForm polish

- Input focus: `focus:border-accent focus:ring-2 focus:ring-accent/20 focus:outline-none`.
- Submit button: keep `.accent-gradient`, add `shadow-lg shadow-accent/20`, use `hover:opacity-95`.

## Verification

After every task:

```bash
npx tsc --noEmit
npm run build
npm run lint
node scripts/audit-screenshots.mjs
```

## Environment notes

- `browser_navigate` is blocked for `localhost`/`127.0.0.1` in this Hermes environment; always use Playwright scripts for local visual verification.
- Playwright script must be run from the project directory so `import { chromium } from 'playwright'` resolves.
- For type checking in Vite React projects, prefer `npx tsc --noEmit` over `tsc -b` unless the project uses project references; the session brief explicitly requests `npx tsc --noEmit`.

## Related

- `superpowers-workflow` — plan-first methodology.
- `superpowers-writing-plans` — task-by-task plan format.
- `superpowers-subagent-driven-development` — delegate multi-file visual work.
