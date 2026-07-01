# Adding Price Unit Support to an Existing SQLite Admin Panel

Pattern for adding a `price_unit` column to an existing SQLite `products` table,
with auto-migration at startup (parsing existing price strings), admin UI unit
selector, and display across ProductCard / StockActionsCard / Searcher.

## Context

PentaJunior project (2025-06-12). After adding `price_currency` (RUB/USD), the
next requirement was to separate the unit of measurement from the price string.
Previously prices were stored as combined strings like `"от 890 ₽/кг"` or
`"от 1 200 ₽/шт"`. The goal: store clean numeric price, currency code, and
unit code as separate columns.

## 1. DB Schema Migration (Runtime)

### 1.1 Add Auto-Migration to `lib/db.ts`

```typescript
// After the price_currency migration — runs every startup, harmless if
// column already exists:

try {
  const cols = db.prepare('PRAGMA table_info(products)').all() as any[];
  if (!cols.find((c) => c.name === 'price_unit')) {
    db.prepare("ALTER TABLE products ADD COLUMN price_unit TEXT DEFAULT NULL").run();
    console.log('[DB] Migrated: added price_unit column');
  }
} catch (e: any) {
  console.warn('[DB] Migration check failed:', e.message);
}
```

### 1.2 Data Migration: Parse Existing Price Strings

Existing `price` field contains combined strings. Extract unit and clean price:

```typescript
const units = ['кг', 'шт', 'м²', 'м', 'л', 'компл', 'пар', 'упак'];

const allProducts = db.prepare('SELECT id, price FROM products').all() as any[];
for (const row of allProducts) {
  const raw = row.price || '';
  
  // Extract unit suffix (e.g. "/кг" → "кг")
  let unit: string | null = null;
  for (const u of units) {
    if (raw.includes('/' + u)) {
      unit = u;
      break;
    }
  }
  
  // Clean price: remove "от ", currency symbol, unit suffix, spaces
  let cleanPrice = raw
    .replace(/^от\s+/, '')           // remove "от " prefix
    .replace(/[₽$€]/g, '')           // remove currency symbols
    .replace(/\s+/g, '')             // remove all spaces
    .replace(new RegExp('/' + (unit || ''), 'g'), '')  // remove /unit
    .trim();
  
  // Update the row
  db.prepare('UPDATE products SET price = ?, price_unit = ? WHERE id = ?')
    .run(cleanPrice, unit, row.id);
}
```

**Important:** Run this migration **only once**, guarded by a version check or
by checking whether any row already has `price_unit !== NULL`.

### 1.3 Update the TypeScript Interface

```typescript
export interface Product {
  id: string;
  category_id: number;
  name: string;
  title: string;
  price: string | null;          // clean number only (e.g. "890")
  price_currency: 'RUB' | 'USD';  // from previous migration
  price_unit: string | null;      // ← new: "кг", "шт", "м²", etc.
  image: string | null;
  // ... rest unchanged
}
```

### 1.4 Helper: Format Full Price String

```typescript
export const PRICE_UNITS = [
  'шт', 'кг', 'м²', 'м', 'л', 'компл', 'пар', 'упак'
];

export function formatPriceFull(
  price: string | null,
  currency: string = 'RUB',
  unit: string | null = null
): string {
  if (!price || price === '') return '—';
  const sym = CURRENCY_SYMBOLS[currency] || currency;
  return unit ? `${price} ${sym}/${unit}` : `${price} ${sym}`;
}
```

## 2. Update API Routes

### 2.1 POST (Create Product)

Add `price_unit` as the 17th parameter (or last after `price_currency`):

```typescript
db.prepare(`INSERT INTO products (
  id, category_id, name, title, price, price_currency, price_unit, image, ...
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ...)`)
  .run(
    id,
    body.category_id,
    body.name,
    body.title,
    body.price || null,
    body.price_currency || 'RUB',
    body.price_unit || null,       // ← new
    body.image || null,
    // ... rest
  );
```

### 2.2 PUT (Update Product)

```typescript
db.prepare(`UPDATE products SET
  category_id = ?, name = ?, title = ?, price = ?, price_currency = ?,
  price_unit = ?, image = ?, ... WHERE id = ?`)
  .run(
    body.category_id,
    body.name,
    body.title,
    body.price || null,
    body.price_currency || 'RUB',
    body.price_unit || null,       // ← new
    body.image || null,
    // ... rest
    id
  );
```

## 3. Admin UI: Unit Selector

In the product edit/create form (`/admin/products/page.tsx`), add a `<select>`
for unit of measurement:

```tsx
<div className="col-md-2">
  <label className="form-label">Ед. изм.</label>
  <select
    className="form-select"
    value={product.price_unit || ''}
    onChange={(e) => update('price_unit', e.target.value || null)}
  >
    <option value="">—</option>
    <option value="шт">шт</option>
    <option value="кг">кг</option>
    <option value="м²">м²</option>
    <option value="м">м</option>
    <option value="л">л</option>
    <option value="компл">компл</option>
    <option value="пар">пар</option>
    <option value="упак">упак</option>
  </select>
</div>
```

**Grid layout note:** Combine with price (4 cols) and currency (2 cols) in the
same row, leaving remaining cols for category/template selectors.

### 3.1 Admin Table Display

Show price with unit in the products list:

```tsx
<td>
  {p.price
    ? `${p.price} ${p.price_currency === 'USD' ? '$' : '₽'}`
      + (p.price_unit ? `/${p.price_unit}` : '')
    : '—'}
</td>
```

## 4. Public Site: Unit Display

### 4.1 ProductCard (Catalog Grid & Detail)

```tsx
const currencySymbol = product.price_currency === 'USD' ? '$' : '₽';
const unitSuffix = product.price_unit ? `/${product.price_unit}` : '';

// Regular price
<p className="fs-2 fw-bold text-primary">
  {product.price
    ? `${product.price} ${currencySymbol}${unitSuffix}`
    : "По запросу"}
</p>

// Promo price (crossed-out old + new)
<span className="text-decoration-line-through text-muted fs-5">
  {product.price ? `${product.price} ${currencySymbol}${unitSuffix}` : "—"}
</span>
<span className="fs-2 fw-bold text-danger">
  {stockInfo.newPrice} {currencySymbol}{unitSuffix}
</span>
```

**Remove "от " prefix from display** — the migration strips it from the DB,
so the site no longer shows it. If the business still wants "от ", add it
conditionally in the component, not in the database.

### 4.2 StockActionsCard (Promo Grid)

Same pattern — append `/${unit}` to both old and new price strings.

### 4.3 Searcher (Search Dropdown)

```tsx
<small className="text-primary ms-2">
  {product.price} {product.price_currency === 'USD' ? '$' : '₽'}
  {product.price_unit ? `/${product.price_unit}` : ''}
</small>
```

**Important:** The search endpoint must include `price_unit` in its SELECT clause.
If search uses a custom query (not direct `products` table), add the column.

## 5. Backward Compatibility

- Existing products after migration: `price` = clean number, `price_unit` =
  extracted unit (or null if no unit was found).
- Old code that ignores `price_unit`: still works — prices render without unit.
- New code that reads `price_unit`: shows `890 ₽/кг` instead of raw `"от 890 ₽/кг"`.

## 6. Adding More Units

To add a new unit (e.g. "банка", "рул"):

1. Update `PRICE_UNITS` array in `lib/db.ts`.
2. Add `<option>` in the admin form selector.
3. No DB schema change needed (TEXT column accepts any string).

## Related References

- `references/sqlite-currency-migration.md` — Adding `price_currency` column
  (RUB/USD) to the same SQLite table. The unit migration builds on top of the
currency migration.
