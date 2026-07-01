# Product Card Grid Styling: Compact Cards with SEO-Safe Tags

## Context

E-commerce category pages built with Next.js + Bootstrap often suffer from
visually oversized product titles in grid cards. The `<h2>` tag is required for
SEO hierarchy, but Bootstrap's default `h2` size (1.5rem / 24px) is too large
for dense product grids, causing titles to wrap aggressively and push card
footers downward unevenly. Prices may also lack currency/unit display
(e.g. showing "890" instead of "890 ₽/кг").

## Pattern

### 1. SEO-safe title sizing

Keep the semantic `<h2>` for SEO, but override its visual size via CSS:

```tsx
<h2 className="catalog-product-title">
  <Link href={`/production/${slug}/${product.id}`}>
    {product.name}
  </Link>
</h2>
```

```css
.catalog-product-title a {
  color: var(--color-text);
  text-decoration: none;
  font-weight: 600;
  font-size: 1.0625rem;    /* 17px — compact but readable */
  line-height: 1.35;
  transition: color var(--transition-fast);
}
.catalog-product-title {
  margin-bottom: 0.5rem;
}
```

**Why this works:** Search engines see the `<h2>`. Users see a 17px title
that fits 2–3 lines without breaking the card layout.

### 2. Currency + unit price formatting

Prices stored in the DB as separate fields (`price`, `price_currency`,
`price_unit`) should be formatted client-side for display:

```ts
// src/lib/db.ts
export const CURRENCY_SYMBOLS: Record<string, string> = {
  RUB: '₽',
  USD: '$',
};

export function formatPriceFull(
  price: string | null,
  currency: string = 'RUB',
  unit: string | null = null,
  prefix: string = ''
): string {
  if (!price || price === '') return '—';
  const sym = CURRENCY_SYMBOLS[currency] || currency;
  const unitStr = unit ? `/${unit}` : '';
  return `${prefix}${price} ${sym}${unitStr}`;
}
// → "890 ₽/кг", "350 ₽/шт", "1 200 ₽/кг"
```

Usage in JSX (regular and promotional prices):

```tsx
{/* Regular price */}
<span className="catalog-product-price">
  {formatPriceFull(product.price, product.price_currency, product.price_unit)}
</span>

{/* Promotional: strikethrough old + new red price */}
<div className="d-flex flex-column">
  <span className="text-decoration-line-through text-muted small">
    {formatPriceFull(product.price, product.price_currency, product.price_unit)}
  </span>
  <span className="catalog-product-price text-danger">
    {formatPriceFull(stockInfo.newPrice, product.price_currency, product.price_unit)}
  </span>
</div>
```

### 3. Compact card body layout

Use flex column with small gap to tighten vertical rhythm:

```css
.catalog-product-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;   /* tight but not touching */
}

.catalog-product-features {
  font-size: 0.8125rem;      /* 13px — secondary info */
  color: var(--color-text-muted);
  line-height: 1.5;
  margin-bottom: 0.5rem;
}
.catalog-product-features li {
  display: flex;
  align-items: flex-start;
  gap: 0.25rem;
}
```

### 4. Price display rules

```css
.catalog-product-price {
  color: var(--olive-dark);
  font-weight: 700;
  font-size: 1.125rem;
  white-space: nowrap;       /* prevent "₽/кг" from wrapping */
}
.catalog-product-price.text-danger {
  color: #dc2626;            /* promotional red */
}
```

## Real-World Usage

Applied in PentaJunior v2 (`/production/[slug]/page.tsx`):
- Category grid with `col-md-6 col-xl-4` (2→3 columns)
- `formatPriceFull` imported from `db.ts` and applied to all price renders
- `catalog-product-title` reduced to 1.0625rem for better density
- Card body uses flex column gap for consistent spacing across variable-length
  titles and feature lists
- `white-space: nowrap` on prices prevents broken currency/unit strings

## Related

- `references/blog-filter-layout-shift.md` — similar custom-CSS-over-Bootstrap
  approach for interactive elements.
- `references/admin-modal-ui-pattern.md` — custom component sizing pattern
  (same philosophy: override Bootstrap defaults with fixed metrics).
