# Product spec table — single scrollbar layout

> Session: 2026-07-12. `TableIncluder` was using `SyncScrollTable`, which cloned the same `spec_tables` markup twice (one for the top scrollbar track, one for the visible table). The live page therefore rendered two identical tables. The desired UX is a single table with a top horizontal scrollbar.

## Anti-pattern: dual cloned tables

`SyncScrollTable` rendered:

```tsx
<div className="sync-scroll-table">
  <div className="table-responsive sync-scroll-top">
    <div className="sync-scroll-clone">{children}</div>
  </div>
  <div className="table-responsive sync-scroll-bottom">{children}</div>
</div>
```

Problems:
- Two copies of the same `<table>` in the DOM.
- Accessibility: screen readers see duplicate rows/columns.
- Layout weight and maintenance cost.
- Confusing CSS when only one table should be styled.

## Preferred pattern: one table in an overflow wrapper

`TableIncluder.tsx`:

```tsx
return (
  <>
    {/* optional current-product highlight alert */}
    <div className="table-responsive spec-table-top-scroll">
      <table className="table table-sm align-middle rti-range-table">
        <thead>...</thead>
        <tbody>...</tbody>
      </table>
    </div>
  </>
);
```

`globals.css`:

```css
.spec-table-top-scroll {
  overflow-x: auto;
  margin-bottom: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.spec-table-top-scroll::-webkit-scrollbar {
  height: 10px;
}

.spec-table-top-scroll::-webkit-scrollbar-track {
  background: var(--ash-lighter);
  border-radius: 6px;
}

.spec-table-top-scroll::-webkit-scrollbar-thumb {
  background: var(--olive-green);
  border-radius: 6px;
}

.spec-table-top-scroll::-webkit-scrollbar-thumb:hover {
  background: var(--olive-dark);
}

.spec-table-top-scroll table {
  margin-bottom: 0;
  min-width: 720px;
}

.rti-highlight-th {
  background-color: var(--dark-bordo) !important;
  color: #fff !important;
}

.rti-highlight {
  background-color: var(--mint-pale);
  font-weight: 600;
}
```

## Why this works

- `overflow-x: auto` on the wrapper puts the scrollbar above the table content, not below.
- `min-width` on the table forces the wrapper to scroll horizontally on narrow screens.
- No JavaScript synchronization required.
- Single DOM table.
- The highlighted column (`rti-highlight-th`, `rti-highlight`) remains a single visual cue tied to the current product.

## When to use

Use this pattern for any product page that displays a wide comparison/spec table that should remain readable on mobile without duplicating markup.

## When the rotateX trick is not needed

Older iterations used `transform: rotateX(180deg)` to move the scrollbar to the top. This flips both the container and the table back, requires two transforms, and complicates sticky headers/rounded borders. The `overflow-x: auto` wrapper is simpler and avoids those issues.
