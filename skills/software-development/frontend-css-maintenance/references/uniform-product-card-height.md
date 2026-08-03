# Uniform product card height patterns

## Problem

In a responsive product grid, cards with different title lengths, feature lists, or price rows end up at different heights, breaking the visual rhythm.

## Pattern

Use a flex column layout with a fixed minimum height and push the bottom row down with `mt-auto`.

```tsx
// Card wrapper
<button className="group flex h-full min-h-[460px] w-full flex-col ...">
  {/* fixed-aspect image */}
  <div className="relative aspect-[4/3] overflow-hidden">...{image}...</div>

  {/* text content fills available space */}
  <div className="flex flex-1 flex-col p-5">
    <h3>{title}</h3>
    <p className="line-clamp-2 min-h-[2.75rem]">{subtitle}</p>

    {/* feature badges — mb-auto pushes the rest down */}
    <div className="mb-auto flex flex-wrap gap-2.5">
      {features.map((f) => (
        <span
          key={f}
          className="rounded-full border border-accent/30 bg-accent/15 px-4 py-2 text-sm font-semibold text-accent"
        >
          {f}
        </span>
      ))}
    </div>

    {/* bottom row always at the bottom of the card */}
    <div className="mt-5 flex items-center justify-between border-t border-stroke pt-4">
      <span>{price}</span>
      <span>{pack}</span>
    </div>
  </div>
</button>
```

## Key classes

- `flex h-full min-h-[460px] flex-col` on the card.
- `flex flex-1 flex-col` on the content wrapper.
- `mb-auto` on the feature/badge block.
- `mt-5` (or `mt-auto`) on the bottom row.
- `line-clamp-2` + `min-h` on the subtitle to reserve space even for short descriptions.

## Grid parent

Make sure the grid cells stretch so `h-full` on the card works:

```tsx
<div className="grid h-full gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
  {items.map((item) => (
    <div key={item.id} className="flex h-full">
      <ProductCard item={item} />
    </div>
  ))}
</div>
```

## Feature badge styling

For badges to feel substantial rather than cramped:

```tsx
className="rounded-full border border-accent/30 bg-accent/15 px-4 py-2 text-sm font-semibold text-accent shadow-sm"
```

Adjust `px`/`py` and font size for the target density. On mobile, consider `text-xs sm:text-sm px-3 py-1.5` if space is tight.

## Pitfalls

- Forgetting `h-full` on the card *and* on the grid cell makes min-height and flex alignment unreliable.
- Using `absolute bottom-0` for the bottom row instead of flex can cause overlaps if the content above grows.
- Long feature lists can still overflow if the card has a hard `min-h`. Either cap visible features (`slice(0, 3)`) or switch to `min-h` + `max-h` with overflow.

## Session provenance

2026-08-01 — `silicone-landing-v2` design refinement: product cards were uneven due to variable title/feature lengths. Switched to flex column with `min-h-[460px]`, `line-clamp-2` subtitle reservation, `mb-auto` feature badges, and `mt-auto` bottom price row. Cards aligned perfectly across the grid.
