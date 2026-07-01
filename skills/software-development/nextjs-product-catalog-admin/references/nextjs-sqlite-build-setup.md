# Next.js + SQLite Build Setup: better-sqlite3, TypeScript, Common Pitfalls

## Installing better-sqlite3

```bash
cd project-v2/
rm -rf node_modules package-lock.json
cp ../project/package.json .  # OR: npm init -y + manually add deps
npm install next react react-dom better-sqlite3
npm install -D typescript @types/react @types/react-dom @types/better-sqlite3
```

## TypeScript tsconfig.json: bun-types Conflict Resolution

**CRITICAL PITFALL:** If `bun-types` is installed in a parent directory (e.g. root workspace), TypeScript may resolve `@types/*` from `node_modules` **above** the project directory. This causes `bun-types` to override Node.js types, producing errors like:

```
../node_modules/bun-types/globals.d.ts(232,74): error TS2694:
  Namespace '"node:util"' has no exported member 'TextEncoderEncodeIntoResult'.
../node_modules/bun-types/overrides.d.ts(316,47): error TS2552:
  Cannot find name 'ConnectionOptions'. Did you mean 'BunConnectionOptions'?
```

**FIX — Add `types` array to tsconfig.json compilerOptions:**

```json
{
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./src/*"]
    },
    "types": ["node", "react", "react-dom"]
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

The `"types": ["node", "react", "react-dom"]` array **excludes** automatic inclusion of all `@types/*` packages, preventing `bun-types` from leaking in.

## Using Sync DB Queries in generateStaticParams

Next.js `generateStaticParams` runs at build time. Use synchronous `better-sqlite3` queries — no async/await needed:

```tsx
// app/production/[slug]/page.tsx
import Database from "better-sqlite3";

const db = new Database("./pentajunior.db", { readonly: true });

export function generateStaticParams() {
  const rows = db.prepare("SELECT slug FROM categories").all();
  return rows.map((row: any) => ({ slug: row.slug }));
}
```

## lib/db.ts Pattern

**Keep DB client + types + hydration helpers in ONE file** to prevent circular imports:

```typescript
// src/lib/db.ts
import Database from "better-sqlite3";
import path from "path";

const dbPath = path.join(process.cwd(), "pentajunior.db");
const db = new Database(dbPath, { readonly: true });

// ─── DB-facing interfaces (snake_case) ──────────────────────────
export interface DbCategory {
  id: number;
  slug: string;
  title: string;
  meta_description: string;
  page_description: string;
  image: string;
  related_categories: string;  // JSON string in DB
}

export interface DbProduct {
  id: string;
  category_id: number;
  name: string;
  title: string;
  price: string;
  image: string;
  features: string;          // JSON string
  keywords: string;          // JSON string
  meta_description: string;
  page_description: string;
  pack: string;
  news: number;
  stock_info: string | null; // JSON string
  spec_table_id: string | null;
  template_type: string;
  template_data: string;     // JSON string
}

// ─── Component-facing interfaces (CamelCase, hydrated) ───────────
export interface ProductForCategoryPage {
  id: string;
  name: string;
  title: string;
  price: string;
  image: string;
  metaDescription: string;
  pageDescription: string;
  pack: string;
  templateType: string;
  slug: string;
  categorySlug: string;
}

export interface ProductForDetailPage {
  id: string;
  name: string;
  title: string;
  price: string;
  image: string;
  pack: string;
  metaDescription: string;
  pageDescription: string;
  templateType: string;
  keywords: string[];
  features: string[];
  specTableId: string | null;
  stockInfo: { newPrice?: string; condition?: string } | null;
  templateData: Record<string, any>;
  relatedProducts: string[];
  categorySlug: string;
}

// ─── Query helpers (hydrate JSON at boundary) ─────────────────────
export function getProductForCategoryPage(id: string): ProductForCategoryPage | null {
  const row = db.prepare(`
    SELECT p.id, p.name, p.title, p.price, p.image,
           p.meta_description, p.page_description, p.pack,
           p.template_type, p.template_data, c.slug AS category_slug
    FROM products p
    JOIN categories c ON p.category_id = c.id
    WHERE p.id = ?
  `).get(id);
  if (!row) return null;
  return {
    id: row.id,
    name: row.name,
    title: row.title,
    price: row.price,
    image: row.image,
    metaDescription: row.meta_description,
    pageDescription: row.page_description,
    pack: row.pack,
    templateType: row.template_type,
    slug: row.id,
    categorySlug: row.category_slug,
  };
}

export function getProductForDetailPage(id: string): ProductForDetailPage | null {
  const row = db.prepare(`
    SELECT p.*, c.slug AS category_slug
    FROM products p
    JOIN categories c ON p.category_id = c.id
    WHERE p.id = ?
  `).get(id);
  if (!row) return null;
  return {
    id: row.id,
    name: row.name,
    title: row.title,
    price: row.price,
    image: row.image,
    pack: row.pack,
    metaDescription: row.meta_description,
    pageDescription: row.page_description,
    templateType: row.template_type,
    keywords: row.keywords ? JSON.parse(row.keywords) : [],
    features: row.features ? JSON.parse(row.features) : [],
    specTableId: row.spec_table_id,
    stockInfo: row.stock_info ? JSON.parse(row.stock_info) : null,
    templateData: row.template_data ? JSON.parse(row.template_data) : {},
    relatedProducts: [],  // populate separately
    categorySlug: row.category_slug,
  };
}
```

## Build Verification

After migration, verify:

```bash
cd project-v2/
npm run build
```

Expected output:
- `Compiled successfully`
- `Generating static pages using 5 workers (X/Y)` — should match original page count
- All product detail pages listed under `● /production/[slug]/[productId]`

## Pitfall: Native Rebuild After Node Version Switch

**better-sqlite3** compiles a native `.node` binary against the **current Node.js ABI version** at install time. If you later switch Node versions via `nvm` or another version manager, the existing binary becomes incompatible.

**Error signature:**
```
Error: The module '.../better_sqlite3.node'
was compiled against a different Node.js version using
NODE_MODULE_VERSION 108. This version of Node.js requires
NODE_MODULE_VERSION 137. Please try re-compiling or re-installing.
```

**Trigger context:**
- System Node v18 → install better-sqlite3 → native binary compiled for ABI 108
- Later switch to Node v24 via `nvm use 24` → ABI jumps to 137
- `next build` fails at the `Collecting page data` phase

**Fix — Rebuild native dependencies after every Node switch:**

```bash
# After switching Node version (e.g. nvm use 24)
export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh"
nvm use 24

# Rebuild native modules that use node-gyp
pnpm rebuild better-sqlite3 sharp @parcel/watcher
# OR with npm:
npm rebuild better-sqlite3 sharp @parcel/watcher
```

**Prevention — Pin Node version in build scripts:**

```bash
# package.json scripts (or CI pipeline)
"scripts": {
  "prebuild": "node -e \"if(process.version.match(/v(\\d+)/)[1] < 20) throw new Error('Node >= 20 required')\"",
  "build": "next build"
}
```

**Or set `.nvmrc` in project root:**
```
24.13.1
```

And use `nvm use` before every build session.

## Anti-patterns to Avoid

| ❌ Don't | ✅ Do |
|---|---|
| `const db = new Database("pentajunior.db")` (relative path) | `path.join(process.cwd(), "pentajunior.db")` |
| Split types across multiple files | Single `lib/db.ts` with all interfaces |
| `JSON.parse(row.field)` without null check | `row.field ? JSON.parse(row.field) : []` |
| Async `generateStaticParams` with SQLite | Sync queries — better-sqlite3 is sync by design |
| Store ReactNode/JSX in DB | Store plain strings, keep HTML in templates |

## References

- `references/jsx-to-sqlite-migration.md` — Parsing JSX content blocks into JSON
- `references/nextjs-sqlite-types.md` — Dual-type pattern (DB-facing vs component-facing)
- `references/product-template-mapping.md` — Category → template_type mapping and template component structure
- `references/search-client-side-api.md` — Moving search from DB import to client-side fetch
