# SQLite → xlsx → Yandex Disk → Next.js JSON roundtrip

Session: 2026-06-09 (Pentajunior v3 migration). Verified on Next.js 16.2.1, React 19.2.3, Node 24.13.1.

Pattern: extract local SQLite → format multi-sheet Excel → upload to Yandex Disk → Next.js reads xlsx via API/fallback JSON.

---

## What was built

1. **Read SQLite** — all tables from `pentajunior.db` (12 categories, 59 products, 6 templates)
2. **Build 3-sheet workbook** (openpyxl) with styled headers
3. **Upload + publish** on Yandex Disk, return public URL
4. **Next.js data layer** — sync JSON fallback + async API for live updates
5. **CLI sync script** — `npm run sync` pulls xlsx → writes JSON
6. **Verified** — dev server on port 3456, all pages 200 OK, API returns live xlsx data

---

## 1. Extract from SQLite → openpyxl workbook

```python
import sqlite3
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

def sqlite_to_xlsx(db_path: str, out_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    wb = Workbook()

    TABLES = [
        ("Categories", "SELECT id, slug, title, href, image, meta_description, page_description, related_categories FROM categories"),
        ("Products", "SELECT id, category_id, name, title, price, image, features, keywords, meta_description, pack, spec_table_id, news, stock_info, template_type, template_data FROM products"),
        ("Templates", "SELECT id, template_type, name, description, image, features, meta_description FROM templates"),
    ]

    first = True
    for sheet_name, query in TABLES:
        cursor.execute(query)
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]

        ws = wb.active if first else wb.create_sheet(title=sheet_name)
        ws.title = sheet_name
        first = False

        ws.append(cols)
        for row in rows:
            ws.append([str(v) if v is not None else "" for v in row])

        # Style header
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="1565C0", end_color="1565C0", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        # Auto-width
        for col in ws.columns:
            max_len = max(len(str(cell.value) or "") for cell in col)
            ws.column_dimensions[get_column_letter(col[0].column)].width = min(max_len + 3, 60)

    wb.save(out_path)
    conn.close()
```

---

## 2. Upload / publish / download roundtrip

```python
import subprocess, json, os

def read_token():
    with open(os.path.expanduser("~/.hermes/.env")) as f:
        for line in f:
            if line.startswith("YANDEX_DISK_TOKEN="):
                return line.strip().split("=", 1)[1]

def upload_publish(local_path: str, remote_path: str = "/products.xlsx") -> str:
    token = read_token()
    r1 = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: OAuth {token}",
         f"https://cloud-api.yandex.net/v1/disk/resources/upload?path={remote_path}&overwrite=true"],
        capture_output=True, text=True
    )
    upload_url = json.loads(r1.stdout)["href"]
    subprocess.run(["curl", "-s", "-T", local_path, upload_url], capture_output=True)
    subprocess.run(
        ["curl", "-s", "-H", f"Authorization: OAuth {token}", "-X", "PUT",
         f"https://cloud-api.yandex.net/v1/disk/resources/publish?path={remote_path}"],
        capture_output=True
    )
    r4 = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: OAuth {token}",
         f"https://cloud-api.yandex.net/v1/disk/resources?path={remote_path}"],
        capture_output=True, text=True
    )
    return json.loads(r4.stdout).get("public_url", "NOT_FOUND")

def download_xlsx(remote_path: str, local_path: str):
    token = read_token()
    r = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: OAuth {token}",
         f"https://cloud-api.yandex.net/v1/disk/resources/download?path={remote_path}"],
        capture_output=True, text=True
    )
    download_url = json.loads(r.stdout)["href"]
    subprocess.run(["curl", "-sL", "-o", local_path, download_url], check=True)
```

---

## 3. Next.js: sync JSON adapter (SSR-safe, zero code changes in pages)

`src/lib/db.ts` — preserves the old SQLite interface, but reads committed JSON:

```typescript
import data from "@/data/products.json";

export interface Category {
  id: number; slug: string; title: string; href: string;
  image: string | null; meta_description: string;
  page_description: string; related_categories: number[];
}

export interface Product {
  id: string; category_id: number; name: string; title: string;
  price: string | null; image: string | null; features: string[];
  keywords: string[]; meta_description: string; pack: string | null;
  spec_table_id: string | null; news: boolean; stock_info: string | null;
  template_type: string; template_data: Record<string, any>;
}

export interface Template {
  id: number; template_type: string; name: string; description: string;
  image: string | null; features: string[]; meta_description: string;
}

export function getAllCategories(): Category[] { return data.categories; }
export function getAllProducts(): Product[]      { return data.products; }
export function getAllTemplates(): Template[]    { return data.templates; }
export function getProductById(id: string): Product | undefined {
  return data.products.find((p: Product) => p.id === id);
}
export function getProductsByCategory(categoryId: number): Product[] {
  return data.products.filter((p: Product) => p.category_id === categoryId);
}
export function getCategoryBySlug(slug: string): Category | undefined {
  return data.categories.find((c: Category) => c.slug === slug);
}
export function getTemplateByType(type: string): Template | undefined {
  return data.templates.find((t: Template) => t.template_type === type);
}
```

`src/lib/product-utils.ts` — slug helpers for routing:

```typescript
import { getAllCategories, getAllProducts } from "./db";

export function getProductHref(productId: string, categoryId: number): string {
  const category = getAllCategories().find(c => c.id === categoryId);
  if (!category) return "#";
  return `/production/${category.slug}/${productId}`;
}
export function getProductHrefSync(productId: string, categoryId: number): string {
  return getProductHref(productId, categoryId);
}
```

---

## 4. Next.js: runtime API with 5-min cache

`src/app/api/products/route.ts` — live xlsx fetch:

```typescript
import { NextResponse } from "next/server";
import * as XLSX from "xlsx";

const CACHE_TTL = 5 * 60 * 1000;
let cache: { data: any; ts: number } | null = null;

async function fetchFromDisk() {
  const token = process.env.YANDEX_DISK_TOKEN;
  if (!token) throw new Error("YANDEX_DISK_TOKEN not set");

  const metaRes = await fetch(
    "https://cloud-api.yandex.net/v1/disk/resources?path=/products.xlsx",
    { headers: { Authorization: `OAuth ${token}` } }
  );
  const meta = await metaRes.json();
  if (!meta.file) throw new Error("File not found on Disk");

  const fileRes = await fetch(meta.file, { redirect: "follow" });
  const buf = await fileRes.arrayBuffer();
  const wb = XLSX.read(new Uint8Array(buf), { type: "array" });

  const categories = XLSX.utils.sheet_to_json(wb.Sheets["Categories"]);
  const products = XLSX.utils.sheet_to_json(wb.Sheets["Products"]);
  const templates = XLSX.utils.sheet_to_json(wb.Sheets["Templates"]);

  return { categories, products, templates, cached_at: new Date().toISOString() };
}

export async function GET() {
  if (cache && Date.now() - cache.ts < CACHE_TTL) {
    return NextResponse.json(cache.data);
  }
  try {
    const data = await fetchFromDisk();
    cache = { data, ts: Date.now() };
    return NextResponse.json(data);
  } catch (err: any) {
    return NextResponse.json(
      { error: "Failed to fetch from Disk", message: err.message },
      { status: 502 }
    );
  }
}
```

`src/app/api/sync/route.ts` — admin endpoint to refresh JSON:

```typescript
import { NextResponse } from "next/server";
import * as fs from "fs";
import * as path from "path";
import * as XLSX from "xlsx";

export async function POST(request: Request) {
  const token = request.headers.get("X-Admin-Token");
  if (token !== process.env.ADMIN_TOKEN) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }
  try {
    const diskToken = process.env.YANDEX_DISK_TOKEN;
    const metaRes = await fetch(
      "https://cloud-api.yandex.net/v1/disk/resources?path=/products.xlsx",
      { headers: { Authorization: `OAuth ${diskToken}` } }
    );
    const meta = await metaRes.json();
    const fileRes = await fetch(meta.file, { redirect: "follow" });
    const buf = await fileRes.arrayBuffer();
    const wb = XLSX.read(new Uint8Array(buf), { type: "array" });

    const out = {
      categories: XLSX.utils.sheet_to_json(wb.Sheets["Categories"]),
      products: XLSX.utils.sheet_to_json(wb.Sheets["Products"]),
      templates: XLSX.utils.sheet_to_json(wb.Sheets["Templates"]),
      synced_at: new Date().toISOString(),
    };

    const jsonPath = path.join(process.cwd(), "src", "data", "products.json");
    fs.mkdirSync(path.dirname(jsonPath), { recursive: true });
    fs.writeFileSync(jsonPath, JSON.stringify(out, null, 2));

    return NextResponse.json({ success: true, ...out });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
```

`src/app/api/search/route.ts` — search over local JSON:

```typescript
import { NextResponse } from "next/server";
import { getAllProducts } from "@/lib/db";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const q = searchParams.get("q")?.toLowerCase() || "";
  if (!q) return NextResponse.json([]);

  const products = getAllProducts();
  const results = products.filter(p =>
    p.name.toLowerCase().includes(q) ||
    p.id.toLowerCase().includes(q) ||
    p.title.toLowerCase().includes(q) ||
    p.keywords.some((k: string) => k.toLowerCase().includes(q))
  );
  return NextResponse.json(results);
}
```

---

## 5. Standalone test script

`scripts/test-api.mjs` — verify Yandex Disk → xlsx pipeline outside Next.js:

```javascript
import * as XLSX from "xlsx";
import * as fs from "fs";

const TOKEN = process.env.YANDEX_DISK_TOKEN;
if (!TOKEN) { console.error("No YANDEX_DISK_TOKEN"); process.exit(1); }

async function test() {
  // 1. Meta
  const metaRes = await fetch(
    "https://cloud-api.yandex.net/v1/disk/resources?path=/products.xlsx",
    { headers: { Authorization: `OAuth ${TOKEN}` } }
  );
  const meta = await metaRes.json();
  console.log("Meta:", meta.name, meta.size, "bytes");

  // 2. Download
  const fileRes = await fetch(meta.file, { redirect: "follow" });
  const buf = await fileRes.arrayBuffer();
  fs.writeFileSync("/tmp/test-products.xlsx", Buffer.from(buf));
  console.log("Downloaded:", buf.byteLength, "bytes");

  // 3. Parse
  const wb = XLSX.read(new Uint8Array(buf), { type: "array" });
  console.log("Sheets:", wb.SheetNames);
  const categories = XLSX.utils.sheet_to_json(wb.Sheets["Categories"]);
  const products = XLSX.utils.sheet_to_json(wb.Sheets["Products"]);
  const templates = XLSX.utils.sheet_to_json(wb.Sheets["Templates"]);
  console.log(`Categories: ${categories.length}, Products: ${products.length}, Templates: ${templates.length}`);
}
test().catch(e => { console.error(e); process.exit(1); });
```

Usage: `node scripts/test-api.mjs`

---

## 6. CLI sync script

`scripts/sync-products.js`:

```javascript
#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const XLSX = require("xlsx");

async function main() {
  const token = process.env.YANDEX_DISK_TOKEN;
  if (!token) {
    console.warn("No YANDEX_DISK_TOKEN — using cached JSON if present");
    process.exit(0);
  }
  const metaRes = await fetch(
    "https://cloud-api.yandex.net/v1/disk/resources?path=/products.xlsx",
    { headers: { Authorization: `OAuth ${token}` } }
  );
  const meta = await metaRes.json();
  const fileRes = await fetch(meta.file, { redirect: "follow" });
  const buf = await fileRes.arrayBuffer();
  const wb = XLSX.read(new Uint8Array(buf), { type: "array" });

  const out = {
    categories: XLSX.utils.sheet_to_json(wb.Sheets["Categories"]),
    products: XLSX.utils.sheet_to_json(wb.Sheets["Products"]),
    templates: XLSX.utils.sheet_to_json(wb.Sheets["Templates"]),
    synced_at: new Date().toISOString(),
  };

  const outPath = path.join(__dirname, "..", "src", "data", "products.json");
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, JSON.stringify(out, null, 2));
  console.log(`Synced: ${out.categories.length} categories, ${out.products.length} products, ${out.templates.length} templates`);
}
main().catch(e => { console.error(e); process.exit(1); });
```

Package.json scripts:
```json
{
  "sync": "node scripts/sync-products.js",
  "sync:force": "node scripts/sync-products.js --force"
}
```

---

## 7. Environment variables

`.env.local.example`:
```
# Yandex Disk OAuth token (y0_...)
YANDEX_DISK_TOKEN=your_yandex_disk_oauth_token

# Admin token for /api/sync (any random string)
ADMIN_TOKEN=your_random_admin_token
```

---

## 8. Testing commands (verified)

Start dev server with token:
```bash
export YANDEX_DISK_TOKEN=$(grep YANDEX_DISK_TOKEN ~/.hermes/.env | cut -d= -f2)
npm run dev -- --port 3456
```

Verify API:
```bash
curl -s http://localhost:3456/api/products | python3 -m json.tool | head -20
curl -s "http://localhost:3456/api/search?q=9110" | python3 -m json.tool
```

Verify pages:
```bash
for url in / /production /production/silikonovye-i-poliuretanovye-kompaundy /price; do
  curl -s -o /dev/null -w "%{http_code}" http://localhost:3456$url
done
```

Standalone test:
```bash
node scripts/test-api.mjs
```

---

## 9. Architecture decisions

**Problem:** SQLite → xlsx on Disk. Next.js pages were sync (Server Components call `getAllProducts()` synchronously). Remote fetch is async.

**Solution: Hybrid adapter**
1. `src/lib/db.ts` — sync JSON import (zero latency, SSR-safe)
2. `src/lib/data.ts` — async xlsx fetcher (live updates, 5-min cache)
3. `src/app/api/products/route.ts` — API route for client-side live data
4. `src/app/api/sync/route.ts` — admin endpoint to refresh JSON from Disk
5. `scripts/sync-products.js` — CLI to pull xlsx → JSON manually

**Why this works:**
- Server Components keep using sync `db.ts` — no async/await rewrite across 14 files
- Live data available via `/api/products` for client components
- Admin can POST `/api/sync` to refresh JSON without redeploy
- Build always succeeds because JSON is committed

---

## 10. Pitfalls discovered

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| `path=app:/file` | File invisible in Yandex Disk web UI | Use `path=/file` for root visibility |
| Web preview lag | Updated xlsx shows old data | Wait 1–2 min or reload Yandex Disk page |
| openpyxl format | Can only write `.xlsx` | Use `xlsx` npm package for Node.js read |
| Empty SQLite cells | `None` → blank Excel cells | Convert to `""` before append |
| Node.js `xlsx` import | `Cannot find module` | Check `"moduleResolution": "bundler"` in tsconfig |
| Cyrillic search via curl | `[]` results for Russian queries | Terminal URL encoding issue; browser/fetch works fine |
| Cache-Control headers | Next.js dev warning about custom headers | Harmless in dev; review for production |
| `generateStaticParams` | Needs sync data at build time | Use `db.ts` (sync JSON), not `data.ts` (async fetch) |
| JSON columns in xlsx | Arrays stored as strings | Parse with `JSON.parse` or `split(",")` after `sheet_to_json` |
| Spec tables | Complex nested JSON (13-row tables) | Don't roundtrip through xlsx; keep in separate JSON or sheet |
| Template data | Per-product JSON blobs | Store empty `{}` in xlsx, keep mapping in code |
| Build without token | `npm run sync` fails | Add `if (!token) { warn; exit(0); }` fallback |
| OAuth token scope | `403` on read | Ensure token has `cloud_api:disk.read` scope |
