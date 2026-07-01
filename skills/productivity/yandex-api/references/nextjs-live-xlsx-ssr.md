# Next.js live xlsx SSR from Yandex Disk

Session: 2026-06-09 (Pentajunior v3 /price refactor). Verified on Next.js 16.2.6, Node 24.13.1.

Pattern: Next.js Server Component reads `.xlsx` directly from Yandex Disk on every request, with graceful fallback to committed `products.json`.

---

## 1. Shared library (`src/lib/yandex-disk.ts`)

Centralize all Yandex Disk I/O in one module. Both API routes and Server Components import from here.

```typescript
import * as XLSX from "xlsx";

// ─── Types ───────────────────────────────────────────────────────
export interface YCategory {
  id: number; slug: string; title: string; href: string;
  image: string | null; meta_description: string; page_description: string;
  related_categories: number[];
}

export interface YProduct {
  id: string; category_id: number; name: string; title: string;
  price: string | null; pack: string | null; spec_table_id: string | null;
  template_type: string; image: string | null; features: string[];
  keywords: string[]; meta_description: string; stock_info: string | null;
  news: boolean; template_data: Record<string, any>;
}

// ─── Fetch workbook ──────────────────────────────────────────────
export async function fetchWorkbook(token?: string): Promise<XLSX.WorkBook> {
  const t = token ?? process.env.YANDEX_DISK_TOKEN;
  if (!t) throw new Error("YANDEX_DISK_TOKEN not set");

  const metaRes = await fetch(
    "https://cloud-api.yandex.net/v1/disk/resources?path=/products.xlsx",
    { headers: { Authorization: `OAuth ${t}` } }
  );
  if (!metaRes.ok) throw new Error(`Meta error: ${metaRes.status}`);

  const meta = await metaRes.json();
  const fileRes = await fetch(meta.file, { redirect: "follow" });
  if (!fileRes.ok) throw new Error(`Download error: ${fileRes.status}`);

  const buf = await fileRes.arrayBuffer();
  return XLSX.read(new Uint8Array(buf), { type: "array" });
}

// ─── Typed parsers (raw arrays, no header mapping) ────────────────
export function parseCategories(wb: XLSX.WorkBook): YCategory[] {
  const ws = wb.Sheets["Categories"];
  if (!ws) return [];
  const rows = XLSX.utils.sheet_to_json<any[]>(ws, { header: 1, defval: null });
  if (rows.length < 2) return [];
  return rows.slice(1).map((r) => ({
    id: Number(r[0]), slug: r[1] || "", title: r[2] || "",
    href: r[3] || "", image: r[4] || null, meta_description: r[5] || "",
    page_description: r[6] || "", related_categories: parseIntArray(r[7]),
  }));
}

export function parseProducts(wb: XLSX.WorkBook): YProduct[] {
  const ws = wb.Sheets["Products"];
  if (!ws) return [];
  const rows = XLSX.utils.sheet_to_json<any[]>(ws, { header: 1, defval: null });
  if (rows.length < 2) return [];
  return rows.slice(1).map((r) => ({
    id: String(r[0] ?? ""), category_id: Number(r[1]), name: r[2] || "",
    title: r[3] || "", price: r[4] || null, pack: r[5] || null,
    spec_table_id: r[6] || null, template_type: r[7] || "default",
    image: r[8] || null, features: parseStringList(r[9]),
    keywords: parseStringList(r[10]), meta_description: r[11] || "",
    stock_info: r[12] || null, news: false, template_data: {},
  }));
}

export function parseTemplates(wb: XLSX.WorkBook): string[] {
  const ws = wb.Sheets["Templates"];
  if (!ws) return [];
  const rows = XLSX.utils.sheet_to_json<any[]>(ws, { header: 1, defval: null });
  if (rows.length < 2) return [];
  return rows.slice(1).map((r) => r[0]).filter(Boolean) as string[];
}

// ─── Helpers ─────────────────────────────────────────────────────
function parseIntArray(val: any): number[] {
  if (!val) return [];
  const str = String(val).trim().replace(/^\[/, "").replace(/\]$/, "");
  if (!str) return [];
  return str.split(/,\s*/).map(Number).filter((n) => !isNaN(n));
}

function parseStringList(val: any): string[] {
  if (!val) return [];
  return String(val).split(",").map((s) => s.trim()).filter(Boolean);
}
```

---

## 2. API routes using shared lib

**`/api/products/route.ts`** — 5-min cache, generic `parseSheet`:
```typescript
import { NextResponse } from "next/server";
import { fetchWorkbook, parseSheet } from "@/lib/yandex-disk";

const CACHE_TTL = 5 * 60 * 1000;
let cache: { data: any; ts: number } | null = null;

export async function GET() {
  if (cache && Date.now() - cache.ts < CACHE_TTL) {
    return NextResponse.json(cache.data);
  }
  try {
    const wb = await fetchWorkbook();
    const data = {
      categories: parseSheet(wb, "Categories"),
      products: parseSheet(wb, "Products"),
      templates: parseSheet(wb, "Templates"),
      source: "yandex-disk",
      cached: false,
    };
    cache = { data, ts: Date.now() };
    return NextResponse.json(data);
  } catch (err) {
    return NextResponse.json(
      { error: (err as Error).message, source: "error" },
      { status: 500 }
    );
  }
}
```

**`/api/sync/route.ts`** — admin endpoint, typed parsers, writes JSON:
```typescript
import { NextRequest, NextResponse } from "next/server";
import { fetchWorkbook, parseCategories, parseProducts } from "@/lib/yandex-disk";
import { writeFile } from "fs/promises";
import path from "path";

const _adminToken = process.env.ADMIN_TOKEN;

export async function POST(req: NextRequest) {
  const token = req.headers.get("X-Admin-Token");
  if (_adminToken && token !== _adminToken) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }
  try {
    const wb = await fetchWorkbook();
    const categories = parseCategories(wb);
    const products = parseProducts(wb);
    const data = {
      categories, products,
      templates: [...new Set(products.map((p) => p.template_type))],
      synced_at: new Date().toISOString(),
      source: "yandex-disk/products.xlsx",
    };
    const outPath = path.join(process.cwd(), "src", "data", "products.json");
    await writeFile(outPath, JSON.stringify(data, null, 2), "utf-8");
    return NextResponse.json({ ok: true, categories: categories.length, products: products.length, path: outPath, synced_at: data.synced_at });
  } catch (err) {
    return NextResponse.json({ error: (err as Error).message }, { status: 500 });
  }
}
```

---

## 3. Async Server Component with live data + fallback

**`/app/price/page.tsx`** — groups products by category, SSR from Disk:

```typescript
import { fetchWorkbook, parseCategories, parseProducts } from "@/lib/yandex-disk";
import { getAllProducts, getAllCategories, Product, Category } from "@/lib/db";

export const dynamic = "force-dynamic"; // SSR on every request

async function getPriceData() {
  try {
    const wb = await fetchWorkbook();
    return {
      categories: parseCategories(wb),
      products: parseProducts(wb),
      source: "yandex-disk" as const,
    };
  } catch (err) {
    console.warn("[Price] Disk fetch failed, fallback to JSON:", (err as Error).message);
    return {
      categories: getAllCategories(),
      products: getAllProducts(),
      source: "local-json" as const,
    };
  }
}

function groupByCategory(products: Product[], categories: Category[]) {
  const catMap = new Map<number, Category>();
  categories.forEach((c) => catMap.set(c.id, c));
  const groups = new Map<number, Product[]>();
  products.forEach((p) => {
    const list = groups.get(p.category_id) || [];
    list.push(p);
    groups.set(p.category_id, list);
  });
  return Array.from(groups.entries())
    .map(([catId, items]) => ({
      category: catMap.get(catId) || {
        id: catId, slug: `cat-${catId}`, title: "Другое",
        href: "#", image: null, meta_description: "", page_description: "", related_categories: [],
      },
      items,
    }))
    .sort((a, b) => a.category.id - b.category.id);
}

export default async function PricePage() {
  const { categories, products, source } = await getPriceData();
  const groups = groupByCategory(products, categories);
  // ... render groups as tables per category
}
```

**Why `force-dynamic`:** Next.js 16 App Router defaults to static generation for pages without dynamic data. Without this export, the page would be built once at deploy and never re-read the xlsx. `force-dynamic` makes every request hit the server (and thus Yandex Disk).

---

## 4. Architecture: Hybrid data layer

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Яндекс.Диск     │────▶│  Next.js Server  │────▶│  React Page      │
│  products.xlsx   │     │  (force-dynamic) │     │  (async SC)      │
└──────────────────┘     └──────────────────┘     └──────────────────┘
         │                        │
         │ (on error)             │ (sync import)
         ▼                        ▼
┌──────────────────┐     ┌──────────────────┐
│  fallback JSON   │     │  src/lib/db.ts   │
│  src/data/       │     │  (sync interface)│
│  products.json   │     └──────────────────┘
└──────────────────┘
```

**Three data sources, one codebase:**
1. **Async live** — `fetchWorkbook()` in Server Components or API routes (runtime)
2. **Sync JSON** — `db.ts` imports committed `products.json` (build-time, SSR-safe)
3. **Admin sync** — `POST /api/sync` refreshes JSON from Disk on demand

**When to use which:**
| Context | Use | Why |
|---------|-----|-----|
| Server Component page | `fetchWorkbook()` + fallback | Live data, SEO-friendly |
| API route (client fetch) | `fetchWorkbook()` + cache | Avoid hammering Disk |
| `generateStaticParams` | `db.ts` (sync) | Build must not depend on network |
| Client Component | `fetch("/api/products")` | Browser can't access env token |

---

## 5. Pitfalls discovered in this session

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| **Token corrupted in `.env.local`** | API returns `401 Unauthorized` even though token works via direct curl | Shell tools (`sed`, `cut`, `echo`) mangle quotes/backticks in the token. **Always use Python `split("=", 1)` to read/write `.env` files.** See SKILL.md section 4. |
| **Port already in use** | `EADDRINUSE: address already in use :::3456` | Kill old process: `pkill -f "next dev"` or pick new port (`--port 3457`) |
| **Node version mismatch** | `You are using Node.js 18.19.1. For Next.js, Node.js version ">=20.9.0" is required.` | Use nvm: `source ~/.nvm/nvm.sh && nvm use 24 && node ./node_modules/next/dist/bin/next dev` |
| **Missing `force-dynamic`** | Page shows stale data after xlsx update on Disk | Add `export const dynamic = "force-dynamic"` to async pages that read remote data |
| **Empty HTML from curl** | `curl /price` returns 0 bytes | Server still starting or port blocked; wait 5s, check `curl /api/products` first |

---

## 6. Verification commands (tested)

```bash
# 1. Start dev server with correct Node version
source ~/.nvm/nvm.sh && nvm use 24
/home/natan/.nvm/versions/node/v24.13.1/bin/node ./node_modules/next/dist/bin/next dev --port 3456

# 2. Verify API returns live data
curl -s http://localhost:3456/api/products | jq '{products: .products | length, source: .source}'
# Expected: {"products": 59, "source": "yandex-disk"}

# 3. Verify price page renders with real data
curl -s http://localhost:3456/price | grep -oE '(Юнисил|Пентэласт|ПМС|ТСМ|table-striped)' | sort | uniq -c

# 4. Standalone test (no Next.js needed)
node scripts/test-api.mjs
```

---

## 7. Key files in this pattern

| File | Purpose |
|------|---------|
| `src/lib/yandex-disk.ts` | Shared fetch + parse logic |
| `src/lib/db.ts` | Sync JSON adapter (fallback) |
| `src/app/api/products/route.ts` | API route with cache |
| `src/app/api/sync/route.ts` | Admin sync endpoint |
| `src/app/price/page.tsx` | Async Server Component, live data |
| `src/data/products.json` | Committed fallback JSON |
| `scripts/test-api.mjs` | Standalone verification |
| `.env.local` | `YANDEX_DISK_TOKEN`, `ADMIN_TOKEN` |

---

## Links

- Parent skill: `yandex-api`
- Related reference: `references/sqlite-to-xlsx-disk-roundtrip.md` — SQLite → xlsx → Disk → JSON migration (previous phase)
