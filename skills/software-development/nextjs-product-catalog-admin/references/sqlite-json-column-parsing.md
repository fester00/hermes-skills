# SQLite JSON Column Parsing: better-sqlite3 String Return

## Context

`better-sqlite3` returns JSON column data as a **plain string**, not a parsed
object. When you store structured data (e.g. promotional pricing info) in a
SQLite TEXT column as JSON, the library does NOT auto-parse it — you get a
JSON-encoded string back from every `SELECT`.

This was discovered in PentaJunior v2 (2025-06-12) where `stock_info` stored
promotional data as JSON (`{ "newPrice": "750", "badge": "Акция" }`), but
`getAllProducts()` returned `stock_info: "{\"newPrice\":\"750\"...}"` (a
string). The `StockActionsCard` component then attempted `stockInfo?.newPrice`
and got `undefined`, causing `$undefined` to render in the price block and the
promo badge to never appear.

## The Problem

```typescript
// BROKEN — stock_info is a string, not an object
function getAllProducts(): Product[] {
  const rows = db.prepare('SELECT * FROM products').all();
  return rows as Product[];  // ← TypeScript trusts you, but runtime lies
}

// In component:
const stockInfo = product.stock_info;  // typeof stockInfo === 'string'
<span>{stockInfo?.newPrice}</span>     // → undefined (no crash, just wrong)
```

## The Fix

Manually `JSON.parse()` the column in **every** getter that returns a product
(or any entity with JSON columns):

```typescript
export function getAllProducts(): Product[] {
  const rows = db.prepare('SELECT * FROM products').all() as any[];
  return rows.map((r) => ({
    ...r,
    stock_info: r.stock_info ? JSON.parse(r.stock_info) : null,
  })) as Product[];
}

export function getProductById(id: string): Product | null {
  const r = db.prepare('SELECT * FROM products WHERE id = ?').get(id) as any;
  if (!r) return null;
  return {
    ...r,
    stock_info: r.stock_info ? JSON.parse(r.stock_info) : null,
  } as Product;
}

export function getProductsByCategoryId(categoryId: number): Product[] {
  const rows = db.prepare('SELECT * FROM products WHERE category_id = ?').all(categoryId) as any[];
  return rows.map((r) => ({
    ...r,
    stock_info: r.stock_info ? JSON.parse(r.stock_info) : null,
  })) as Product[];
}

export function searchProducts(query: string): Product[] {
  const rows = db.prepare('SELECT * FROM products WHERE name LIKE ?').all(`%${query}%`) as any[];
  return rows.map((r) => ({
    ...r,
    stock_info: r.stock_info ? JSON.parse(r.stock_info) : null,
  })) as Product[];
}
```

## Generic Helper (DRY)

If multiple tables have JSON columns, create a helper:

```typescript
function parseJsonFields<T>(
  row: Record<string, any>,
  jsonFields: string[]
): T {
  const parsed = { ...row };
  for (const field of jsonFields) {
    if (parsed[field] && typeof parsed[field] === 'string') {
      try {
        parsed[field] = JSON.parse(parsed[field]);
      } catch {
        parsed[field] = null;
      }
    }
  }
  return parsed as T;
}

// Usage:
return rows.map((r) => parseJsonFields<Product>(r, ['stock_info', 'meta']));
```

## When to Apply

Apply this pattern whenever:
- SQLite table has a TEXT column storing JSON.
- The TypeScript interface declares that field as an object/array (not string).
- `better-sqlite3` is the driver (confirmed behavior: returns raw TEXT as string).

## Backward Compatibility

- If `stock_info` is `NULL` in DB → `JSON.parse(null)` would throw; the
  `r.stock_info ? JSON.parse(...) : null` guard handles this.
- If `stock_info` contains invalid JSON → wrap in `try/catch` (see generic
  helper above) to prevent app crash on startup.

## Related

- `references/sqlite-currency-migration.md` — adding `price_currency` to the
  same SQLite table (same project, same DB layer).
- `references/sqlite-unit-migration.md` — adding `price_unit` column.
