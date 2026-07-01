# SQLite JSON Column Serialization in Next.js

## The Round-Trip Pattern (correct)

When using `better-sqlite3` with JSON columns, only **one** `JSON.parse` and **one** `JSON.stringify` should happen per round-trip:

```
SQLite (TEXT)  →  API GET (JSON.parse)  →  Client (object)  →  API POST/PUT (JSON.stringify)  →  SQLite (TEXT)
```

### API GET Route — parse once

```ts
// src/app/api/admin/products/route.ts
export async function GET() {
  const rows = db.prepare('SELECT * FROM products').all();
  const products = rows.map((r: any) => ({
    ...r,
    features: JSON.parse(r.features || '[]'),
    keywords: JSON.parse(r.keywords || '[]'),
    // ✅ Parse here — the ONLY parse in the round-trip
    stock_info: r.stock_info ? JSON.parse(r.stock_info) : null,
    template_data: JSON.parse(r.template_data || '{}'),
  }));
  return NextResponse.json({ success: true, data: products });
}
```

### Client receives object — work directly

```ts
// Component interface matches the PARSED shape
interface Product {
  // ... other fields
  // ✅ Object type — NOT string
  stock_info: { newPrice?: string; condition?: string } | null;
  features: string[];        // already parsed
  keywords: string[];        // already parsed
  template_data: Record<string, any>;  // already parsed
}
```

```tsx
// Use directly — NO JSON.parse()
const stockInfo = product.stock_info;
if (stockInfo?.newPrice) {
  return <span>{stockInfo.newPrice}</span>;
}
```

### Client sends data back — send object

```ts
// src/app/admin/products/page.tsx — handleSave
const body = {
  ...product,
  features: product.features.filter((f) => f.trim()),
  keywords: product.keywords.filter((k) => k.trim()),
  // ✅ Send as object — server will stringify
  stock_info: product.stock_info,
};
```

### API POST/PUT — stringify once

```ts
// src/app/api/admin/products/route.ts
export async function POST(request: Request) {
  const body = await request.json();
  db.prepare(`INSERT INTO products (...) VALUES (...)`).run(
    // ... other fields
    JSON.stringify(body.features || []),      // ✅ stringify
    JSON.stringify(body.keywords || []),      // ✅ stringify
    body.stock_info ? JSON.stringify(body.stock_info) : null,  // ✅ stringify
    JSON.stringify(body.template_data || {}), // ✅ stringify
  );
}
```

## Pitfalls

### Pitfall 1: Double-stringify (client + server)

```ts
// ❌ WRONG — client stringifies, server stringifies again
const body = {
  stock_info: product.stock_info ? JSON.stringify(product.stock_info) : null,
};
// Server does: JSON.stringify(body.stock_info) → "\"{\\\"newPrice\\\":\\\"470\\\"}\""
// DB stores a double-escaped JSON STRING, not JSON object
```

**Symptoms:**
- Data saved "successfully" but promo prices don't display
- `JSON.parse` on GET returns a **string** instead of object
- `product.stock_info?.newPrice` is `undefined`
- Console shows no errors (parsing succeeds, it parses a string)

**Fix:** Client sends object, server does the single stringify.

### Pitfall 2: Double-parse (client re-parses already-parsed data)

```ts
// ❌ WRONG — GET already parsed, this tries to parse an object
let stockInfo = null;
if (product.stock_info) {
  try { stockInfo = JSON.parse(product.stock_info); } catch {}
}
```

**Symptoms:**
- `JSON.parse([object Object])` silently fails → `stockInfo = null`
- Promo prices don't display on `/news` or catalog pages
- Badge always shows generic "Акция" instead of "−10%"
- No console error (caught by empty `catch`)

**Fix:** Type `Product.stock_info` as object, not string. Use directly.

### Pitfall 3: TypeScript type mismatch

```ts
// ❌ WRONG — interface says string, but runtime is object
export interface Product {
  stock_info: string | null;
}
// Then in component:
JSON.parse(product.stock_info);  // TypeScript allows this but fails at runtime
```

**Fix:** Make the `Product` interface reflect the hydrated shape:

```ts
export interface Product {
  stock_info: { newPrice?: string; condition?: string } | null;
  features: string[];
  keywords: string[];
  template_data: Record<string, any>;
}
```

The hydration boundary is in `db.ts` query functions (or API route). Everything downstream uses the hydrated type.

### Pitfall 4: `.trim()` on object type

```ts
// ❌ WRONG — stock_info is an object, not a string
const stockProducts = products.filter(
  (p) => p.stock_info && p.stock_info.trim() !== ""
);
```

**Fix:** Check for truthiness/null:

```ts
const stockProducts = products.filter(
  (p) => p.stock_info !== null && !!p.stock_info
);
```

### Pitfall 5: Partial hydration — some getters parse, others don't

**The most insidious bug.** You add a new JSON column (`stock_info`) and parse it in one getter (e.g. `getAllProducts`), but forget to add the same `JSON.parse` to other getters (`getProductById`, `getProductsByCategoryId`, `searchProducts`).

```ts
// ❌ WRONG — getAllProducts parses stock_info, but getProductById does NOT
export function getAllProducts() {
  return rows.map(r => ({
    ...r,
    features: JSON.parse(r.features || '[]'),
    stock_info: r.stock_info ? JSON.parse(r.stock_info) : null,  // ✅ parsed
    template_data: JSON.parse(r.template_data || '{}'),
  }));
}

export function getProductById(id: string) {
  const row = db.prepare('SELECT * FROM products WHERE id = ?').get(id);
  return {
    ...row,
    features: JSON.parse(row.features || '[]'),
    // ❌ stock_info NOT parsed — returns raw string!
    template_data: JSON.parse(row.template_data || '{}'),
  };
}
```

**Symptoms:**
- Promo price shows on `/news` (uses `getAllProducts`) but NOT on product detail page (uses `getProductById`)
- OR vice versa — some pages work, others silently broken
- `stockInfo?.newPrice` is `undefined` on broken pages
- No console error — TypeScript is happy because `Product` interface says object, but runtime delivers string
- Difficult to debug because the data "looks correct" in DB, and some pages work fine

**Root cause:** `JSON.parse` is scattered as inline code in each getter. Adding a new column requires updating N places.

**Fix — Centralize hydration in a single helper:**

```ts
// lib/db.ts — single source of truth for hydration
function hydrateProduct(row: any): Product {
  return {
    ...row,
    features: JSON.parse(row.features || '[]'),
    keywords: JSON.parse(row.keywords || '[]'),
    news: Boolean(row.news),
    stock_info: row.stock_info ? JSON.parse(row.stock_info) : null,
    template_data: JSON.parse(row.template_data || '{}'),
  };
}

export function getAllProducts(): Product[] {
  const rows = db.prepare('SELECT * FROM products').all() as any[];
  return rows.map(hydrateProduct);
}

export function getProductById(id: string): Product | undefined {
  const row = db.prepare('SELECT * FROM products WHERE id = ?').get(id) as any;
  return row ? hydrateProduct(row) : undefined;
}

export function getProductsByCategoryId(categoryId: number): Product[] {
  const rows = db.prepare('SELECT * FROM products WHERE category_id = ?').all(categoryId) as any[];
  return rows.map(hydrateProduct);
}

export function searchProducts(query: string): Product[] {
  const like = `%${query}%`;
  const rows = db.prepare(
    'SELECT * FROM products WHERE name LIKE ? OR title LIKE ?'
  ).all(like, like) as any[];
  return rows.map(hydrateProduct);
}
```

**Rule of thumb:** If you find yourself writing `JSON.parse(r.features)` more than once in the same file, extract a `hydrateProduct` helper. Every new JSON column needs exactly one line added — in the helper only.

## Database Schema

```sql
CREATE TABLE products (
    -- Scalar columns
    id TEXT PRIMARY KEY,
    name TEXT,
    price TEXT,
    price_currency TEXT DEFAULT 'RUB',
    price_unit TEXT DEFAULT NULL,

    -- JSON columns (stored as TEXT, parsed by application)
    features TEXT,       -- JSON: ["Для малых тиражей", ...]
    keywords TEXT,     -- JSON: ["силикон для форм", ...]
    stock_info TEXT,   -- JSON: {"newPrice": "470", "condition": "до 31.12"}
    template_data TEXT -- JSON: {"intro": "...", "body": "..."}
);
```

## Migration Helpers

### Clean price strings during data migration

When migrating from existing data that includes prefixes like `"от "` and currency symbols:

```ts
const unitMap: Record<string, string> = {
  'шт': 'шт', 'кг': 'кг', 'м²': 'м²', 'м2': 'м²', 'м': 'м', 'л': 'л', 'компл': 'компл',
};

for (const r of rows) {
  // Extract unit from /unit suffix
  const match = r.price?.match(/\/(шт|кг|м²|м2|м|л|компл)$/i);
  let unit = null;
  if (match) {
    unit = unitMap[match[1].toLowerCase()] || match[1];
  }

  // Clean: remove "от " prefix, all spaces, currency symbols
  let cleanPrice = r.price
    .replace(/^от\s+/i, '')
    .replace(/\s/g, '')
    .trim();
  cleanPrice = cleanPrice
    .replace(/₽\/?.*$/, '')
    .replace(/\$\/?.*$/, '')
    .trim();

  db.prepare("UPDATE products SET price = ?, price_unit = ? WHERE id = ?")
    .run(cleanPrice, unit, r.id);
}
```

**Key points:**
- Clean prices for ALL rows in scope, not just those with `/unit` suffix
- `"от 350 ₽"` → `"350"`
- `"1 200 ₽/кг"` → `"1200"` with `price_unit = "кг"`
- Store only numeric value in `price`, currency in `price_currency`, unit in `price_unit`

## Verification

- [ ] `stock_info` renders correctly on `/news` and catalog pages
- [ ] Editing a product with promo: form shows existing `newPrice`
- [ ] After save + reload: promo price still displays
- [ ] DB inspection: `stock_info` column contains valid JSON (not double-quoted string)
- [ ] TypeScript builds without errors on `JSON.parse` calls on `stock_info`
- [ ] **All getters use centralized hydration** — no inline `JSON.parse` duplication in db.ts
