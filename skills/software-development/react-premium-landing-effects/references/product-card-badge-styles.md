# Product Card Property Badge Styles

Session-specific context: `silicone-landing-v2` card/modal polish, 2026-08-01.

## Problem

Feature/property badges ("Универсальная", "Диэлектрическая", "Водоотталкивающая", etc.) often look like bright buttons or get lost against a dark card surface. They need to read as **technical metadata**, not CTAs.

## Final style

Use a compact, muted pill with a small dot indicator. Text should be the primary light color, the background one step above the card surface, and the border slightly stronger than the card border.

```tsx
interface FeatureBadgeProps {
  feature: string;
  size?: "sm" | "md";
}

export function FeatureBadge({ feature, size = "md" }: FeatureBadgeProps) {
  const sizeClasses =
    size === "sm"
      ? "px-2 py-0.5 text-[11px]"
      : "px-2.5 py-1 text-xs";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md border border-stroke-strong bg-surface-2 font-medium text-text-primary transition-colors hover:border-muted/40 hover:text-white ${sizeClasses}`}
    >
      <span className="h-1 w-1 rounded-full bg-muted/70" />
      {feature}
    </span>
  );
}
```

## Design rationale

- **Shape:** `rounded-md` (not pill) keeps badges feeling like tags/chips, not buttons.
- **Dot indicator:** tiny `bg-muted/70` circle visually marks each entry as a property, not an action.
- **Background:** `bg-surface-2` lifts the badge just above the card (`bg-surface` or `bg-surface/95`) so it is readable without shouting.
- **Text:** `text-text-primary` (near-white) for legibility.
- **Border:** `border-stroke-strong` gives structure; hover lightens to `muted/40`.
- **Size:** `text-xs` / `text-[11px]` keeps the hierarchy subordinate to the card title.

## Usage

Share one `FeatureBadge` component between the product card and the product modal so the style never diverges.

```tsx
// In card
<div className="mb-auto flex min-h-[5.5rem] flex-wrap gap-2">
  {visibleFeatures.map((feature) => (
    <FeatureBadge key={feature} feature={feature} size="md" />
  ))}
</div>

// In modal
<div className="mb-5 flex flex-wrap gap-2">
  {item.features.map((feature) => (
    <FeatureBadge key={feature} feature={feature} size="sm" />
  ))}
</div>
```

## What to avoid

- Bright accent-filled pills (`bg-accent/15 text-accent`) — they look like buttons.
- Fully transparent or hairline-only badges on a dark card — they become illegible.
- Different badge styles in card and modal — breaks visual consistency.

## Verification

Check desktop and mobile screenshots; badges should be readable at a glance without competing with the title, image, or CTA.
