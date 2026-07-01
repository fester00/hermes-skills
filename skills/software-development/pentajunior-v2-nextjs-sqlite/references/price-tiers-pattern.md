## Price tiers (ценовые ярусы) in pentajunior-v2

How to store and manage multiple price/volume tiers per product, similar to the legacy `https://pentajunior.ru/price` table.

### Data model
`products.price_tiers` is a JSON array stored as TEXT in SQLite. It was added via:
```sql
ALTER TABLE products ADD COLUMN price_tiers TEXT DEFAULT '[]';
```
Each item:
```ts
interface PriceTier {
  minQty: string;       // e.g. "1", "504"
  maxQty: string;       // e.g. "503", "" for open-ended
  unit: string;         // e.g. "шт", "кг", "л"
  price: string;        // e.g. "143"
  currency: 'RUB' | 'USD';
}
```

### End-to-end wiring checklist
When adding `price_tiers` (or any JSON array field) to an existing entity, update all of these in order; missing one breaks either admin save, build, or public display:

1. **Database**: `ALTER TABLE products ADD COLUMN price_tiers TEXT DEFAULT '[]';`
2. **Product type** (`src/lib/db.ts`): add `price_tiers` to `Product` interface and to every `SELECT` query that returns a product; parse `JSON.parse(r.price_tiers || '[]')` in every mapper.
3. **API routes**:
   - `GET /api/admin/products` — include column and parse it.
   - `POST /api/admin/products` — add column to INSERT and `?` parameter list.
   - `PUT /api/admin/products/[id]` — add `price_tiers = ?` to UPDATE and parameter list.
4. **Admin form** (`src/app/admin/products/page.tsx`):
   - Add field to `Product` interface.
   - Add `price_tiers: []` to `emptyProduct`.
   - Include `price_tiers` in `handleSave` body (it spreads through `...product`).
   - Render `<PriceTiersEditor tiers={draft.price_tiers} onChange={...} />`.
5. **Public display** (`src/app/price/page.tsx`): group rows by product and use `rowSpan` for the product name column; fall back to `product.price` when tiers are absent.
6. **Verify**: `tsc --noEmit && rm -rf .next && npm run build`.

### Admin editing
Use the reusable `PriceTiersEditor` component in `src/components/admin/PriceTiersEditor.tsx`.
- Inserted into the product form (`src/app/admin/products/page.tsx`) before the image URL block.
- Per-row fields: «От», «До», единица измерения, цена, валюта.
- Buttons: "×" removes a row, "+ Добавить строку" adds a row.
- Empty or unset tiers render as `[]` and are ignored on the public site.
- **Editor state safety** — follow `references/react-local-state-editor-pattern.md`. Do not call `onChange` inside `setDrafts`; do not call `onChange` on every render without comparing serialized value. Both mistakes produce console errors (`Cannot update a component while rendering` and `Maximum update depth exceeded`).

### Display rules
- **Product card / detail**: if `price_tiers` is non-empty, render a tier table. Otherwise fall back to `product.price` + `price_unit`.
- **Price page (`/price`)**: group rows by product name; show the product name in the first column with `rowspan`, then one row per tier.
- **JSON-LD**: use the first tier's price, or the base `price`, for schema.org `Offers`. Ensure `priceCurrency` is `RUB`/`USD`.

### Adding tiers in bulk via script
```python
import sqlite3, json
DB = '/home/natan/pentajunior-v2/pentajunior.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()
tiers = [
    {'minQty':'1','maxQty':'503','unit':'шт','price':'143','currency':'RUB'},
    {'minQty':'504','maxQty':'1007','unit':'шт','price':'140','currency':'RUB'},
]
cur.execute("UPDATE products SET price_tiers = ? WHERE id = ?",
            (json.dumps(tiers, ensure_ascii=False), 'sim-aero'))
conn.commit()
conn.close()
```

### Pitfalls
- Do not display rows with empty `price` or `minQty`.
- Keep `maxQty` empty (not `"0"`) for open-ended tiers.
- Always pass `JSON.stringify` to the API; the DB column stores TEXT.
- If you add tiers, update `template_data` or spec tables so the public product card remains consistent.
- **JSON array field pattern** (e.g. features, keywords, price_tiers): the same 6-step checklist above applies to any new JSON field. The most common bug is updating the API `UPDATE` but forgetting the `?` parameter, or updating the API but not the `Product` type in `src/lib/db.ts`.

### Fallback behavior (verified 2026-06-23)
When a user clears every tier in the admin form, the component should save an empty array `[]` (filter empty rows in `handleSave`) and the public display must fall back to the product's base `price`/`price_unit`. A common bug is to branch on `product.price_tiers.length > 0` instead of on the count of **valid** tiers (`price?.trim()`). If you branch on the raw array length, a product with only empty-tier stubs disappears from the price page because no valid row is emitted and the `else if (product.price)` branch is never reached.

Correct `/price` branching:
```ts
const validTiers = product.price_tiers?.filter((tier) => tier.price?.trim()) || [];

if (validTiers.length > 0) {
  // render one row per tier
} else if (product.price) {
  // render single row with product.price + product.price_unit
}
```

Correct admin save cleanup:
```ts
const cleanedTiers = (product.price_tiers || []).filter(
  (tier) => tier.price?.trim() || tier.minQty?.trim() || tier.maxQty?.trim()
);
// send cleanedTiers to API
```