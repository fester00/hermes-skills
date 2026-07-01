# Adding Currency Support to an Existing SQLite Admin Panel

Pattern for adding a `price_currency` column to an existing SQLite `products`
table, with auto-migration at startup, admin UI currency selector, and symbol
display across ProductCard / StockActionsCard / Searcher.

## Context

PentaJunior project (2025-06-12). Admin panel already existed on SQLite with
products table. Requirement: allow products to be priced in either RUB (₽) or
USD ($). Existing products default to RUB. The change must be backward-compatible
(no data loss) and show the currency symbol everywhere prices appear.

## 1. DB Schema Migration (Runtime, Not Build-Time)

### 1.1 Add Auto-Migration to `lib/db.ts`

```typescript
// After `const db = new Database(...)` — runs every startup, harmless if
// column already exists:

try {
  const cols = db.prepare('PRAGMA table_info(products)').all() as any[];
  if (!cols.find((c) => c.name === 'price_currency')) {
    db.prepare("ALTER TABLE products ADD COLUMN price_currency TEXT DEFAULT 'RUB'").run();
    console.log('[DB] Migrated: added price_currency column');
  }
} catch (e: any) {
  console.warn('[DB] Migration check failed:', e.message);
}
```

**Why at runtime?** SQLite doesn't have a formal migration runner like
Alembic/Knex. Adding the check at module load is idempotent (safe to re-run).

### 1.2 Update the TypeScript Interface

```typescript
export interface Product {
  id: string;
  category_id: number;
  name: string;
  title: string;
  price: string | null;
  price_currency: 'RUB' | 'USD';   // ← new
  image: string | null;
  // ... rest unchanged
}
```

### 1.3 Helper: Currency Symbol Map

```typescript
export const CURRENCY_SYMBOLS: Record<string, string> = {
  RUB: '₽',
  USD: '$',
};

export function formatPrice(price: string | null, currency: string = 'RUB'): string {
  if (!price || price === '') return '—';
  const sym = CURRENCY_SYMBOLS[currency] || currency;
  return `${price} ${sym}`;
}
```

## 2. Update API Routes

### 2.1 POST (Create Product)

```typescript
// src/app/api/admin/products/route.ts — POST body
db.prepare(`INSERT INTO products (
  id, category_id, name, title, price, price_currency, image, ...
) VALUES (?, ?, ?, ?, ?, ?, ?, ...)`)
  .run(
    id,
    body.category_id,
    body.name,
    body.title,
    body.price || null,
    body.price_currency || 'RUB',   // ← new
    body.image || null,
    // ... rest
  );
```

### 2.2 PUT (Update Product)

```typescript
// src/app/api/admin/products/[id]/route.ts
db.prepare(`UPDATE products SET
  category_id = ?, name = ?, title = ?, price = ?, price_currency = ?,
  image = ?, ... WHERE id = ?`)
  .run(
    body.category_id,
    body.name,
    body.title,
    body.price || null,
    body.price_currency || 'RUB',   // ← new
    body.image || null,
    // ... rest
    id
  );
```

## 3. Admin UI: Currency Selector

In the product edit/create form (`/admin/products/page.tsx`):

```tsx
<div className="col-md-4">
  <label className="form-label">Цена (обычная)</label>
  <input
    className="form-control"
    value={product.price || ''}
    onChange={(e) => update('price', e.target.value || null)}
  />
</div>
<div className="col-md-2">
  <label className="form-label">Валюта</label>
  <select
    className="form-select"
    value={product.price_currency || 'RUB'}
    onChange={(e) => update('price_currency', e.target.value)}
  >
    <option value="RUB">₽ RUB</option>
    <option value="USD">$ USD</option>
  </select>
</div>
```

**Grid layout note:** Price takes 4 cols, currency takes 2 cols (same row with
category or template selector taking remaining 6). This keeps the form compact.

### 3.1 Admin Table Display

Show symbol in the products list:

```tsx
<td>
  {p.price
    ? `${p.price} ${p.price_currency === 'USD' ? '$' : '₽'}`
    : '—'}
</td>
```

## 4. Public Site: Symbol Display

### 4.1 ProductCard (Detail Page)

```tsx
const currencySymbol = product.price_currency === 'USD' ? '$' : '₽';

// Promo price block
<span className="text-decoration-line-through text-muted fs-5">
  {product.price ? `${product.price} ${currencySymbol}` : "—"}
</span>
<span className="fs-2 fw-bold text-danger">
  {stockInfo.newPrice} {currencySymbol}
</span>

// Regular price block
<p className="fs-2 fw-bold text-primary">
  {product.price ? `${product.price} ${currencySymbol}` : "По запросу"}
</p>
```

### 4.2 StockActionsCard (Promo Grid)

Same pattern — compute `currencySymbol` from `item.price_currency`, append to
both old (crossed-out) and new price.

### 4.3 Searcher (Search Dropdown)

```tsx
<small className="text-primary ms-2">
  {product.price} {product.price_currency === 'USD' ? '$' : '₽'}
</small>
```

**Note:** The `price_currency` field must be included in the search API response.
If the search endpoint uses a different query (e.g. custom `SELECT` not from
`products` table), add `price_currency` to the `SELECT` clause.

## 5. Backward Compatibility

- Existing products: `DEFAULT 'RUB'` fills all rows on migration.
- Old code that ignores `price_currency`: still works — price renders without
  symbol (or falls back to ₽ in format helper).
- New code that reads `price_currency`: gets correct symbol.

## 6. Extending to More Currencies

To add EUR, CNY, etc.:

1. Update `CURRENCY_SYMBOLS` map:
   ```typescript
   EUR: '€', CNY: '¥'
   ```
2. Update `<select>` options in admin form.
3. No DB schema change needed (TEXT column accepts any string).

## Pitfall: Node.js Binary Mismatch

If `better-sqlite3` fails with `ERR_DLOPEN_FAILED` (compiled against different
Node version), the migration check at module load will crash the app.

### Symptoms

```
Error: The module '.../better_sqlite3.node'
was compiled against a different Node.js version using
NODE_MODULE_VERSION 137. This version of Node.js requires
NODE_MODULE_VERSION 109.
```

### Root Cause

`better-sqlite3` is a native C++ addon. The binary `.node` file is compiled
against a specific Node.js ABI version. Installing dependencies with Node 24
and then running with Node 18 (or vice versa) breaks the binary.

### Full Recovery Procedure

**Step 1 — Identify the target Node version:**
Ask the user (or check `package.json` engines field, or the CI config) what
Node version the project expects. For Next.js 16.x, Node 20.x–24.x is typical.

**Step 2 — Install via nvm (Linux/macOS):**

```bash
# Install nvm if not present
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Install and switch to the target version
nvm install 24.13.0
nvm alias default 24.13.0
nvm use 24.13.0
node -v   # should print v24.13.0
```

**Step 3 — Rebuild the native module:**

```bash
cd ~/project-dir
npm install           # refresh lockfile if needed
npm rebuild better-sqlite3
```

**Step 4 — Verify the build:**

```bash
npm run build
```

If the build succeeds, the binary is compatible. If it still fails with
`ERR_DLOPEN_FAILED`, check whether multiple Node versions are in PATH
(e.g. system Node from apt + nvm Node) and ensure `which node` points to
the nvm version.

### Prevention

- Always run `npm install` and `npm run build` with the same Node version.
- Use `.nvmrc` in the project root to pin the version:
  ```
  echo "24.13.0" > .nvmrc
  ```
  Then `nvm use` in the project directory auto-switches.
- On CI/CD, specify `node-version: 24.13.0` in the workflow file.
- Consider adding an engines constraint to `package.json`:
  ```json
  "engines": { "node": ">=20.0.0" }
  ```
