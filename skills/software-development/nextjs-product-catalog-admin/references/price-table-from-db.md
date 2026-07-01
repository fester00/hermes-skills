# Price Table: Migrating Hardcoded Arrays to SQLite

Condensed guide for migrating a hardcoded `products[]` price array (with multiple pack options per product) into a database-driven Next.js price page.

## When This Applies

- Price page uses a large hardcoded TypeScript array: `const products: IProduct[] = [...]`
- Each product has multiple pack rows: `pack: [{ weight: "1.04 кг", pricePerSet: "925 руб." }, ...]`
- Site already uses SQLite (`better-sqlite3`) for products/categories
- Want prices editable via admin panel / DB without code changes

## Current vs Target Schema

### Old (hardcoded)
```typescript
interface IPackOption {
  weight: string;
  pricePerUnit?: string;
  pricePerSet?: string;
}
interface IProduct {
  title: string;
  pack: IPackOption[];
}
// 60+ products, 2-4 pack rows each = 200+ lines of TSX
```

### Existing DB (single-row products table)
```sql
CREATE TABLE products (
  id TEXT PRIMARY KEY,
  name TEXT,
  title TEXT,
  price TEXT,      -- e.g. "от 925 ₽/кг"
  pack TEXT,       -- e.g. "1.04 кг / 5.2 кг / 20.8 кг"
  ...
);
```

The existing schema stores **one price string** and **one pack string** per product. This loses the per-pack-row granularity of the old table.

## Strategy A: Quick Adapt (single row per product)

Use when you need the price page working from DB **now**, and multi-row granularity is acceptable to lose or defer.

### Server Component Page (Strategy A — simple one-row-per-product)

When the DB schema already stores one `price` and one `pack` string per product (no `price_items` table), use `getAllProducts()` from your existing `lib/db.ts` and render a single-row table. This is the fastest zero-migration path.

```tsx
// app/price/page.tsx — Server Component
import { getAllProducts } from '@/lib/db';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Прайс-лист | Penta Junior',
  // ... SEO metadata
};

export default function PricePage() {
  const products = getAllProducts(); // sync, build-time

  return (
    <div className="container my-4">
      <h1 className="h3 mb-4">Прайс-лист</h1>
      <div className="table-responsive">
        <table className="table table-striped table-bordered">
          <thead className="table-light">
            <tr><th>Наименование</th><th>Упаковка</th><th>Цена</th></tr>
          </thead>
          <tbody>
            {products.map((p) => (
              <tr key={p.id}>
                <td style={{ fontWeight: 600 }}>{p.name}</td>
                <td>{p.pack || '—'}</td>
                <td>{p.price || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

**Key details:**
- `getAllProducts()` must be **synchronous** (return array, not Promise). `better-sqlite3` is sync by design.
- Keep the page as a **Server Component** — no `'use client'`. The data is fetched at build time for SSG.
- The old hardcoded `const products: IProduct[] = [...]` array is deleted entirely.

### Server Component Page (Strategy A — raw SQL)

If you don't have `getAllProducts()` in `lib/db.ts`, use a local `db.prepare(...).all()` inline. This is the pattern from the admin-panel recipe reference.

## Strategy B: Full Migration (multi-row price_items table)

Use when the old multi-row pack table must be preserved exactly.

### 1. Add table
```sql
CREATE TABLE price_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  weight TEXT NOT NULL,          -- "1.04 кг", "5.2 кг"
  price_per_unit TEXT,           -- "925 руб./кг" (optional)
  price_per_set TEXT,            -- "925 руб." (optional)
  sort_order INTEGER DEFAULT 0
);

CREATE INDEX idx_price_items_product ON price_items(product_id, sort_order);
```

### 2. Migration script (Node.js)
```javascript
const Database = require('better-sqlite3');
const db = new Database('pentajunior.db');

// Old hardcoded array (paste or require from old file)
const oldProducts = [
  { title: "Юнисил® – 9110, 9131, 9120", pack: [
    { weight: "1.04 кг", pricePerSet: "925 руб." },
    { weight: "5.2 кг", pricePerSet: "4420 руб." },
  ]},
  // ... 60 more products
];

const insert = db.prepare(
  `INSERT INTO price_items (product_id, weight, price_per_unit, price_per_set, sort_order)
   VALUES (?, ?, ?, ?, ?)`
);

const insertMany = db.transaction((items) => {
  for (const item of items) insert.run(...item);
});

const rows = [];
for (const p of oldProducts) {
  const productId = p.title.toLowerCase().replace(/[^a-z0-9]/g, '-');
  p.pack.forEach((pack, i) => {
    rows.push([
      productId,
      pack.weight,
      pack.pricePerUnit || null,
      pack.pricePerSet || null,
      i
    ]);
  });
}
insertMany(rows);
console.log(`Migrated ${rows.length} price rows`);
```

### 3. Server Component Page
```tsx
import { db } from '@/lib/db';

interface PriceItem {
  weight: string;
  price_per_unit: string | null;
  price_per_set: string | null;
}

interface PriceProduct {
  name: string;
  title: string;
  items: PriceItem[];
}

export default function PricePage() {
  const rows = db.prepare(`
    SELECT p.id, p.name, p.title,
      pi.weight, pi.price_per_unit, pi.price_per_set, pi.sort_order
    FROM products p
    LEFT JOIN price_items pi ON pi.product_id = p.id
    WHERE p.price IS NOT NULL OR pi.id IS NOT NULL
    ORDER BY p.category_id, p.id, pi.sort_order
  `).all();

  // Group by product
  const products: PriceProduct[] = [];
  let current: PriceProduct | null = null;
  for (const r of rows) {
    if (!current || current.name !== r.name) {
      current = { name: r.name, title: r.title, items: [] };
      products.push(current);
    }
    if (r.weight) {
      current.items.push({
        weight: r.weight,
        price_per_unit: r.price_per_unit,
        price_per_set: r.price_per_set,
      });
    }
  }

  return (
    <div className="container my-4">
      <h1 className="h3 mb-4">Прайс-лист</h1>
      <div className="table-responsive">
        <table className="table table-striped table-bordered">
          <thead className="table-light">
            <tr><th>Наименование</th><th>Объём</th><th>Цена</th></tr>
          </thead>
          <tbody>
            {products.map((product) =>
              product.items.length > 0 ? (
                product.items.map((item, idx) => (
                  <tr key={`${product.name}-${idx}`}>
                    {idx === 0 && (
                      <td rowSpan={product.items.length}
                          style={{ verticalAlign: 'middle', fontWeight: 600 }}>
                        {product.title || product.name}
                      </td>
                    )}
                    <td>{item.weight}</td>
                    <td>{item.price_per_unit || item.price_per_set || '—'}</td>
                  </tr>
                ))
              ) : (
                <tr key={product.name}>
                  <td style={{ fontWeight: 600 }}>{product.title || product.name}</td>
                  <td>{product.pack || '—'}</td>
                  <td>{product.price || '—'}</td>
                </tr>
              )
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

**Pros:** Preserves exact old table layout (rowSpan per product, multiple pack rows).
**Cons:** Schema migration + data migration + admin panel needs new CRUD for price_items.

## Hybrid: Strategy A now, Strategy B later

1. Implement Strategy A immediately — price page works from DB today
2. Add `price_items` table in a follow-up migration
3. Update admin panel product form to manage pack rows
4. Switch page to Strategy B once data is migrated

## Verification Checklist

- [ ] Price page renders all products from DB (no hardcoded array left)
- [ ] `npm run build` succeeds — no SSG issues with dynamic data
- [ ] Admin panel edits to `price` / `pack` fields reflect on price page after rebuild
- [ ] (Strategy B) `price_items` rows match old hardcoded array exactly
- [ ] (Strategy B) Admin panel can add/edit/delete pack rows per product
