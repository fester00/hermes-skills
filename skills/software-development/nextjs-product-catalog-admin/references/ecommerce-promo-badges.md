# Promo / Discount Badge System for SSG Catalogs

## Overview

Automatic percentage discount calculation from old/new prices, with visual badges across product cards, catalog grids, admin panel, and promo pages. No rebuild needed when promo data changes — but for SSG, a rebuild is required to update static HTML.

## Data Model

SQLite `products` table gains a `stock_info` JSON column:

```sql
stock_info TEXT  -- JSON: {"newPrice": "470 ₽", "condition": "до 31.12"}
```

Additional flag columns:
- `news INTEGER DEFAULT 0` — boolean, shows on /new-products page
- `stock_info TEXT` — non-empty means "in promo"

## Discount Calculation Utility

```ts
// src/lib/discount.ts
export function calcDiscountPercent(
  oldPrice: string | null,
  newPrice: string | null
): number | null {
  if (!oldPrice || !newPrice) return null;

  const clean = (s: string): number => {
    const num = parseFloat(
      s
        .replace(/\s/g, '')
        .replace(/,/g, '.')
        .replace(/[^\d.]/g, '')
    );
    return Number.isNaN(num) ? 0 : num;
  };

  const oldNum = clean(oldPrice);
  const newNum = clean(newPrice);

  if (!oldNum || !newNum || oldNum <= 0 || newNum <= 0 || oldNum <= newNum)
    return null;

  return Math.round((1 - newNum / oldNum) * 100);
}
```

**Parsing robustness:**
- Handles spaces: `"1 200 ₽"` → `1200`
- Handles commas: `"1.200,50"` → `1200.50` (European)
- Handles any currency suffix: `520 ₽`, `15.50 USD`
- Returns `null` on parse failure or invalid math (new ≥ old)

## Badge Display Rules

| Context | Badge Text | Color |
|---------|-----------|-------|
| Catalog grid card | `−10%` (auto-calculated) or "Акция" | Red gradient, top-right |
| Product detail page | `−10%` | Red badge, below product name |
| Admin product table | `−10%` | Red Bootstrap badge |
| Promo page card | `−10%` | Red Bootstrap badge |

## Product Detail Page Price Block

```tsx
{stockInfo?.newPrice ? (
  <>
    <p className="small text-muted mb-0">Цена по акции:</p>
    <div className="d-flex align-items-baseline gap-2">
      <span className="text-decoration-line-through text-muted fs-5">
        {product.price}
      </span>
      <span className="fs-2 fw-bold text-danger">
        {stockInfo.newPrice}
      </span>
    </div>
    {stockInfo.condition && (
      <span className="badge bg-warning text-dark mt-1">
        {stockInfo.condition}
      </span>
    )}
  </>
) : (
  <>
    <p className="small text-muted mb-0">Цена:</p>
    <p className="fs-2 fw-bold text-primary">
      {product.price || "По запросу"}
    </p>
  </>
)}
```

## Admin Panel Integration

### Form fields
- Checkbox **«Акция»** toggles `stock_info` column
- **Акционная цена** — new price input
- **Условие акции** — optional free text (e.g. "-20% до 31.12")
- **Live preview**: as manager types new price, show calculated discount percentage

```tsx
// In admin form
const pct = calcDiscountPercent(product.price, stockNewPrice || null);
{pct !== null && (
  <div className="form-text text-danger fw-semibold">
    Скидка: −{pct}% 
    <small className="text-muted">(старая {product.price} → новая {stockNewPrice})</small>
  </div>
)}
```

### Auto-populate on enable
When manager checks "Акция" for the first time, pre-fill newPrice with current price (they'll edit it down):

```tsx
const setStock = (enabled: boolean) => {
  if (!enabled) {
    update('stock_info', null);
  } else {
    update('stock_info', { newPrice: product.price || '', condition: '' });
  }
};
```

## Catalog Grid Integration

Badge uses IIFE for inline calculation at render time:

```tsx
{product.stock_info && (
  <span className="catalog-badge-stock">
    {(() => {
      const s = JSON.parse(product.stock_info);
      const pct = calcDiscountPercent(product.price, s?.newPrice ?? null);
      return pct !== null ? `−${pct}%` : 'Акция';
    })()}
  </span>
)}
```

CSS for badge (top-right of product image):
```css
.catalog-badge-stock {
  position: absolute;
  top: 10px;
  right: 10px;
  background: linear-gradient(135deg, #dc2626, #ef4444);
  color: #fff;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  box-shadow: 0 0 10px rgba(220, 38, 38, 0.3);
  z-index: 10;
}
```

## Anti-patterns

| ❌ Don't | ✅ Do instead |
|---|---|
| Store discount % in DB (stale when price changes) | Calculate at render from old+new price |
| Badge shows generic "Акция" text only | Show calculated `−10%` when math works |
| Admin enters discount % manually | Admin enters factual new price, system computes % |
| One boolean field for promo | Separate `news` flag + `stock_info` JSON for flexibility |

## Related
- `references/product-template-mapping.md` — category → template mapping
- `SKILL.md` Anti-patterns section — HTML in code, strings in DB
