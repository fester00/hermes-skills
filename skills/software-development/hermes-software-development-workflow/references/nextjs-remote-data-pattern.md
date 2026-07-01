# Next.js Remote Data Pattern

Pattern for Next.js sites where product/catalog data lives remotely (Yandex Disk xlsx, Google Sheets, external API) and needs to be readable at build time (SSR/SSG) and optionally at runtime.

## Problem

Next.js Server Components are synchronous. Data sources (SQLite, local JSON) work because `import` is sync. But remote sources require `fetch()` which is async. Converting all pages to async cascades through the entire component tree.

## Solution: Hybrid Adapter

```
Remote Source          Async Layer           Sync Layer           Pages
─────────────          ───────────           ──────────           ─────
Yandex Disk xlsx  ──▶  src/lib/data.ts  ──▶  src/lib/db.ts  ──▶  page.tsx
Google Sheets CSV      (fetch + cache)       (JSON import)       (sync)
External API           /api/products         getAllProducts()
```

**Architecture:**
1. `src/lib/db.ts` — sync JSON import. Zero latency. SSR-safe. No code changes in pages.
2. `src/lib/data.ts` — async fetcher with memory cache + fallback to JSON. Used only where live data needed.
3. `src/app/api/products/route.ts` — API route for client components or external consumers.
4. `src/app/api/sync/route.ts` — admin endpoint to refresh JSON from remote source.
5. `scripts/sync.js` — CLI to pull remote data → write JSON → `npm run sync`.

## When to use each layer

| Layer | When | Latency | Build-safe |
|-------|------|---------|------------|
| `db.ts` (sync JSON) | All Server Components | 0ms | Yes |
| `data.ts` (async fetch) | API routes, client fetch | 500ms-2s | No (needs env) |
| `/api/products` | Client components, external | 500ms-2s | No |
| `npm run sync` | Pre-build refresh | N/A | Yes |

## Migration from SQLite (v2 → v3)

**DON'T:** Mass-rewrite all pages from sync to async. This creates "async cascade" where every Server Component becomes async, metadata generators become async, and the whole app churns.

**DO:** Keep the existing interface.

```typescript
// src/lib/db.ts — identical interface to old SQLite version
import data from "@/data/products.json";

export function getAllCategories() { return data.categories; }
export function getAllProducts()    { return data.products; }
export function getProductById(id: string) {
  return data.products.find(p => p.id === id);
}
// ... all old functions, same signatures
```

Pages import `db.ts` exactly as before. Zero changes in `page.tsx` files.

## Sync script (Node.js)

```javascript
#!/usr/bin/env node
// scripts/sync-products.js
const fs = require("fs");
const XLSX = require("xlsx");

async function main() {
  // 1. Fetch xlsx from remote
  const token = process.env.YANDEX_DISK_TOKEN;
  const metaRes = await fetch(
    "https://cloud-api.yandex.net/v1/disk/resources?path=/products.xlsx",
    { headers: { Authorization: `OAuth ${token}` } }
  );
  const meta = await metaRes.json();
  const fileRes = await fetch(meta.file);
  const buf = await fileRes.arrayBuffer();

  // 2. Parse
  const wb = XLSX.read(new Uint8Array(buf), { type: "array" });
  const categories = XLSX.utils.sheet_to_json(wb.Sheets["Categories"]);
  const products = XLSX.utils.sheet_to_json(wb.Sheets["Products"]);

  // 3. Write JSON
  const out = { categories, products, synced_at: new Date().toISOString() };
  fs.mkdirSync("src/data", { recursive: true });
  fs.writeFileSync("src/data/products.json", JSON.stringify(out, null, 2));

  console.log(`Synced: ${categories.length} categories, ${products.length} products`);
}
main().catch(e => { console.error(e); process.exit(1); });
```

Package.json scripts:
```json
{
  "scripts": {
    "sync": "node scripts/sync-products.js",
    "build": "npm run sync && next build",
    "dev": "next dev"
  }
}
```

## TypeScript types for JSON data

```typescript
// src/lib/db.ts
export interface Category {
  id: number;
  slug: string;
  title: string;
  href: string;
  image: string | null;
  meta_description: string;
  page_description: string;
  related_categories: number[];
}

export interface Product {
  id: string;
  category_id: number;
  name: string;
  title: string;
  price: string | null;
  image: string | null;
  features: string[];
  keywords: string[];
  meta_description: string;
  pack: string | null;
  spec_table_id: string | null;
  news: boolean;
  stock_info: string | null;
  template_type: string;
  template_data: Record<string, any>;
}
```

## Pitfalls

- **JSON columns in xlsx:** Arrays and objects stored as strings in xlsx cells need parsing. `features: "Для малых тиражей, Несложные формы"` → split by comma. `related_categories: "[1, 2, 5]"` → JSON.parse. Handle null/empty.
- **Spec tables:** Complex nested JSON (like product comparison tables with 13 rows) doesn't roundtrip cleanly through xlsx. Options: (a) separate JSON file for spec tables, (b) separate xlsx sheet with transposed format.
- **Template data:** `template_data` is per-product JSON (intro, body, bullets). Storing this in xlsx requires a JSON-as-string column or a separate mapping file. For v3, we used empty `template_data: {}` in xlsx and kept the mapping in code.
- **Build without env:** If `YANDEX_DISK_TOKEN` is missing, `npm run sync` fails. Make the build fall back to existing JSON: `if (!token) { console.warn("No token, using cached JSON"); process.exit(0); }`
- **xlsx library in Next.js:** `import * as XLSX from "xlsx"` works with `"moduleResolution": "bundler"` (Next.js default). If using `"node"`, may need `import XLSX from "xlsx"`.

## Real example: Pentajunior v3

See `yandex-api` skill `references/sqlite-to-xlsx-disk-roundtrip.md` for the full 59-product, 12-category migration with all file contents, verified on Next.js 16.2.1, React 19.2.3, Node 24.13.1. Includes complete `db.ts`, `product-utils.ts`, `/api/products`, `/api/sync`, `/api/search`, `test-api.mjs`, and `sync-products.js` code.
