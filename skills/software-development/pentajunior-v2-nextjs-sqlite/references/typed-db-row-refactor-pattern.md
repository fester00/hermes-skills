# Typed raw-row refactor for better-sqlite3 queries

## Problem

`src/lib/db.ts` uses `as any` on almost every `better-sqlite3` query. This:
- hides shape mismatches between SQLite columns and the returned TypeScript objects;
- produces many `@typescript-eslint/no-explicit-any` errors;
- makes refactors risky because type changes in `src/lib/types.ts` do not flow through the DB layer.

## Solution

Define small `*Row` types that match the **raw columns** returned by SQLite, then cast query results to those types. Domain types from `src/lib/types.ts` are produced by mapping/parsing JSON fields.

## Pattern

```ts
// src/lib/db.ts
import Database from 'better-sqlite3';
import path from 'path';
import type { Category, Product } from './types';

// 1. Raw row shape: exactly the columns SQLite returns.
type CategoryRow = {
  id: number;
  slug: string;
  title: string;
  href: string;
  image: string | null;
  meta_title: string;
  meta_description: string;
  page_description: string;
  seo_text?: string | null;
  related_categories: string;        // JSON in DB
  template_type: string;
};

type ProductRow = {
  id: string;
  category_id: number;
  subcategory_id: number | null;
  name: string;
  title: string;
  price: string | null;
  price_currency: 'RUB' | 'USD';
  price_unit: string | null;
  image: string | null;
  features: string;                  // JSON in DB
  keywords: string;                  // JSON in DB
  meta_title: string;
  meta_description: string;
  pack: string | null;
  spec_table_id: string | null;
  news: number | boolean;
  stock_info: string;                // JSON in DB
  template_type: string;
  template_data: string;             // JSON in DB
  price_tiers: string;               // JSON in DB
};

const db = new Database(path.join(process.cwd(), 'pentajunior.db'));

// 2. Cast to the row type, not any.
export function getAllCategories(): Category[] {
  const rows = db.prepare('SELECT * FROM categories ORDER BY id').all() as CategoryRow[];
  return rows.map(r => ({
    ...r,
    related_categories: JSON.parse(r.related_categories || '[]'),
    template_type: r.template_type || 'default',
  }));
}

export function getCategoryBySlug(slug: string): Category | undefined {
  const row = db.prepare('SELECT * FROM categories WHERE slug = ?').get(slug) as CategoryRow | undefined;
  if (!row) return undefined;
  return {
    ...row,
    related_categories: JSON.parse(row.related_categories || '[]'),
    template_type: row.template_type || 'default',
  };
}

export function getAllProducts(): Product[] {
  const rows = db.prepare(
    'SELECT id, category_id, subcategory_id, name, title, price, price_currency, price_unit, image, features, keywords, meta_title, meta_description, pack, spec_table_id, news, stock_info, template_type, template_data, price_tiers FROM products ORDER BY category_id, subcategory_id, id'
  ).all() as ProductRow[];
  return rows.map(r => ({
    ...r,
    features: JSON.parse(r.features || '[]'),
    keywords: JSON.parse(r.keywords || '[]'),
    news: Boolean(r.news),
    stock_info: r.stock_info ? JSON.parse(r.stock_info) : null,
    template_data: JSON.parse(r.template_data || '{}'),
    price_tiers: JSON.parse(r.price_tiers || '[]'),
  }));
}
```

## Rules

1. **One row type per table/query shape.** If a query selects a subset of columns, define a dedicated row type or reuse the full one if the subset is compatible.
2. **JSON columns stay `string` in the row type.** Parse them in the mapping function; this makes the boundary between SQLite and the domain model explicit.
3. **Nullable columns must be `| null`.** Do not use `| undefined` for SQLite NULL.
4. **Boolean-ish SQLite columns** (`INTEGER 0/1`) are typed as `number | boolean` and normalized with `Boolean(...)`.
5. **Do not duplicate domain types.** `Category`, `Product` etc. continue to live in `src/lib/types.ts`. `lib/db.ts` imports them and produces them from rows.
6. **Count / pragma queries get tiny row types too:**
   ```ts
   type CountRow = { count: number };
   type PragmaColumnRow = { name: string };
   type TableInfoRow = { name: string };
   ```
7. **Avoid `require()` inside runtime code.** Import `fs` / `path` at the top of the file. Keep `require` only for optional / conditional platform modules if absolutely necessary.
8. **Replace `catch (e: any)` with `catch (e)` and a type guard:**
   ```ts
   } catch (e) {
     console.warn('[DB] ...', e instanceof Error ? e.message : e);
   }
   ```

## Verification

After the refactor:
```bash
./node_modules/.bin/eslint src/lib/db.ts --ext .ts --no-ignore
./node_modules/.bin/tsc --noEmit
rm -rf .next tsconfig.tsbuildinfo
npm run build
```
Expected: zero ESLint errors in `lib/db.ts`, TypeScript passes, build produces 156/156 static pages.

## Migration tip

If the project still has a few `as any` left outside `lib/db.ts`, tackle them in the same order:
1. Data layer (`lib/db.ts`, API routes reading DB rows). Define local `*Row` types in each route and cast to them instead of `any`.
2. Admin pages that re-declare local `Category`/`Product` interfaces — delete the local copies and import from `@/lib/types`. Add missing shared types (e.g. `StockInfo`, `PriceTier`) to `lib/types.ts` if needed.
3. Production pages that use `any` for `params` or JSON-LD helpers.

### Admin API route example
```ts
import { db } from '@/lib/db';

type CategoryRow = {
  id: number;
  slug: string;
  title: string;
  href: string;
  image: string | null;
  meta_title: string;
  meta_description: string;
  page_description: string;
  seo_text?: string | null;
  related_categories: string;
  template_type: string;
};

export async function GET(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const row = db.prepare('SELECT * FROM categories WHERE id = ?').get(id) as CategoryRow | undefined;
  if (!row) return notFoundResponse();
  return successResponse({
    data: {
      ...row,
      related_categories: JSON.parse(row.related_categories || '[]'),
      template_type: row.template_type || 'default',
    },
  });
}
```

## When not to use this pattern

- For one-off scripts or throwaway probes, `as any` is acceptable.
- For `template_data` or other truly dynamic JSON, use `Record<string, unknown>` (or a narrow union if the shape is known) rather than fighting the type system with `any`.
