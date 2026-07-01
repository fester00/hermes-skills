# Stock Actions Card — Testing & Debugging

## Quick setup: add test promo products to DB

When testing `/news` page stock card rendering, use this to inject test data into SQLite:

```sql
-- Add 2 products with stock_info to verify rendering
UPDATE products SET
  news = 0,
  stock_info = '{"newPrice":"750","condition":"Скидка 15%"}'
WHERE id = 'unisil-9110';

UPDATE products SET
  news = 0,
  stock_info = '{"newPrice":"800","condition":"При покупке от 10 кг"}'
WHERE id = 'unisil-9120';
```

## Expected HTML output in build (after fix)

```html
<!-- Бейдж акции -->
<span class="badge bg-danger mb-2">Акция</span>

<!-- Зачёркнутая старая цена -->
<span class="text-decoration-line-through text-muted">890 ₽/кг</span>

<!-- Новая цена красным -->
<span class="fw-bold" style="color:#E31E24;font-size:1.15rem">750 ₽/кг</span>

<!-- Условие акции -->
<span class="badge fs-6 bg-warning text-dark">Скидка 15%</span>
```

## Debugging checklist when stock card shows old price only

1. **Check DB column** — `SELECT stock_info FROM products WHERE id = '...'`
2. **Check JSON validity** — `JSON.parse()` the value; should return object with `newPrice`
3. **Check hydration** — `db.ts` getter must do `stock_info: r.stock_info ? JSON.parse(r.stock_info) : null`
4. **Check ALL getters** — `getAllProducts`, `getProductById`, `getProductsByCategoryId`, `searchProducts` must ALL parse it
5. **Check TypeScript type** — `Product.stock_info` should be `{ newPrice?: string; condition?: string } | null`, not `string | null`
6. **Check build output** — SSG pages cache at build time; `npm run build` after DB changes, not just dev server restart
7. **Check component** — `StockActionsCard` expects object: `stockInfo?.newPrice`. If string comes through, `?.newPrice` = `undefined`

## Common symptoms and causes

| Symptom | Cause |
|---|---|
| No new price shown, only old price with strikethrough | `stock_info` not parsed in getter → string has no `.newPrice` |
| No stock cards at all on `/news` | `getStockProducts()` returns empty (no rows with `stock_info` in DB) |
| Cards appear after dev server restart but gone after build | Dev server caches old SSG output; need full rebuild |
| Promo shows in one place but not another | `getAllProducts` parses, `getProductById` does not (partial hydration) |

## Cleanup after testing

```sql
UPDATE products SET stock_info = NULL WHERE id IN ('unisil-9110', 'unisil-9120');
```
