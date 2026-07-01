---
name: nextjs-product-catalog-admin
description: |
  Class-level patterns for building and operating a Next.js product catalog + admin panel
  backed by SQLite or flat-file storage, Bootstrap 5 frontend, static generation,
  and reusable product-detail templates.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [software-development, nextjs, react, sqlite, ssg, admin, bootstrap, catalog, e-commerce]
triggers:
  - Next.js product catalog with SQLite
  - Next.js admin panel with JSON or SQLite storage
  - Migrate hardcoded product arrays to SQLite
  - Product detail templates in Next.js
  - Admin modal forms scroll jump / focus loss
  - Bootstrap 5 layout shift in Next.js
  - Cookie auth middleware in Next.js App Router
  - better-sqlite3 build or Node version issues
  - Product spec/comparison tables in Next.js
  - Promo prices / new-product badges in Next.js
  - Cyrillic case-insensitive search in Next.js
  - DangerouslySetInnerHTML hydration mismatch
---

# Next.js Product Catalog + Admin

A class-level runbook for building and maintaining small-to-medium product-catalog sites with Next.js, file-based or SQLite storage, Bootstrap 5 styling, and an integrated admin panel.

This skill covers five tightly related areas that were previously fragmented across narrow project-specific skills:

1. **SQLite + SSG migration** — moving hardcoded product data into a build-time database while keeping pages static.
2. **Flat-file / JSON admin panel** — lightweight CRUD, cookie auth, middleware, admin layout isolated from public chrome.
3. **Admin form patterns** — long modal forms that preserve scroll position and focus.
4. **Product-detail templates** — database-driven `template_data`, conditional blocks, universal templates, spec tables.
5. **Bootstrap frontend hardening** — layout-shift-free overrides, cookie-auth debugging, Cyrillic search, hydration traps.

## 1. Recommended architecture

```
SQLite (build-time + admin runtime)
├─ categories
├─ products
│  ├─ scalar fields (id, slug, name, price, ...)
│  ├─ features/keywords/stock_info as JSON strings
│  ├─ spec_table_id
│  ├─ template_type (legacy) or category-driven template
│  └─ template_data (JSON text fields)
├─ spec_tables (columns_json + rows_json)
└─ category_templates (field definitions for admin editor)

Next.js App Router
├─ Public pages — generateStaticParams → static HTML
├─ /api/admin/* — runtime CRUD protected by middleware
├─ /admin/* — client layout with cookie auth
└─ Template components — plain React, HTML in code, text from DB
```

**Core rule:** HTML and structure live in React components; only plain text and JSON data live in the database. Never store JSX, Markdown, or HTML strings in DB columns unless there is an explicit sanitization step.

## 2. Data layer: SQLite + SSG

### 2.1 Why SQLite + SSG

- Public visitors see pre-built static HTML — no runtime DB load.
- Admin API routes hit the same SQLite file when an admin is logged in.
- Updates are a DB write + rebuild (or ISR), not a code edit.
- Search/filter/pagination become indexed queries instead of in-memory loops.

### 2.2 Schema essentials

```sql
CREATE TABLE categories (
  id INTEGER PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  title TEXT,
  meta_description TEXT,
  page_description TEXT,
  image TEXT,
  related_categories TEXT,  -- JSON [2, 5, 10]
  seo_text TEXT
);

CREATE TABLE products (
  id TEXT PRIMARY KEY,
  category_id INTEGER REFERENCES categories(id),
  name TEXT,
  title TEXT,
  price TEXT,
  image TEXT,
  features TEXT,          -- JSON ["..."]
  keywords TEXT,          -- JSON ["..."]
  meta_description TEXT,
  pack TEXT,
  news INTEGER DEFAULT 0,
  stock_info TEXT,        -- JSON {"newPrice":"", "condition":""}
  spec_table_id TEXT,
  template_type TEXT,
  template_data TEXT      -- JSON {intro, body, bullets, application, ...}
);

CREATE TABLE spec_tables (
  id TEXT PRIMARY KEY,
  columns_json TEXT,      -- ["МАРКА", "9110"]
  rows_json TEXT          -- [{"name":"Цвет","values":{"9110":"зелёный"}}]
);
```

### 2.3 Dual-type pattern

Split TypeScript types at the DB boundary:

- **DB-facing** (`DbProduct`, `DbCategory`): snake_case, JSON-string fields, matches schema.
- **Component-facing** (`ProductForDetailPage`): CamelCase, hydrated via `JSON.parse()` in the query helper.

See `references/nextjs-sqlite-types.md` for full helpers.

### 2.4 generateStaticParams

```tsx
export function generateStaticParams() {
  const products = db
    .prepare('SELECT id, slug FROM products JOIN categories ...')
    .all();
  return products.map((p) => ({ slug: p.slug, productId: p.id }));
}
```

Use `better-sqlite3` for synchronous build-time queries.

### 2.5 Side-by-side migration

Prefer creating `project-v2/` alongside the existing project rather than in-place:
- safe parallel testing
- easy rollback
- independent deploy

See `references/jsx-to-sqlite-migration.md` for the original description/intro extraction pattern, `references/v1-application-block-mapping.md` for splitting mixed `application` JSX blocks into the correct v2 template fields, `references/pentajunior-v2-category-migration-log.md` for concrete per-category decisions from the `pentajunior` → `pentajunior-v2` migration, and `references/pentajunior-category-migration-recipe.md` for the complete step-by-step recipe including the Python split heuristic. See `scripts/migration-audit.py` and `scripts/extract_v1_application.py`.

## 3. Admin panel: flat-file + cookie auth

### 3.1 JSON DB CRUD library

For small catalogs, a `src/data/db.json` file is enough. Keep the library synchronous, always read before write, and pretty-print for git diffs:

```ts
const DB_PATH = path.join(process.cwd(), 'src', 'data', 'db.json');

function readDb(): DbSchema { return JSON.parse(fs.readFileSync(DB_PATH, 'utf-8')); }
function writeDb(db: DbSchema) { fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2)); }
```

See `references/json-db-crud-library.md` and `references/pentajunior-json-db-lib.ts`.

### 3.2 Middleware + cookie auth

Protect `/admin/*` and `/api/admin/*` in `src/middleware.ts`:

```ts
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  if (pathname === '/admin/login' || pathname.startsWith('/api/admin/auth')) {
    return NextResponse.next();
  }
  const token = request.cookies.get('admin_token')?.value;
  if (token !== ADMIN_PASSWORD) {
    return NextResponse.redirect(new URL('/admin/login', request.url));
  }
  return NextResponse.next();
}
```

If the client layout reads `document.cookie`, the login API must **not** set `httpOnly: true` or the client cannot see the cookie and will loop. For low-sensitivity panels this trade-off is acceptable; for higher security move auth checks to middleware/server components.

See `references/admin-auth-middleware.md` and `references/auth-cookie-httponly-trap.md`.

### 3.3 Isolating admin from public layout

Use a `ClientLayout` that conditionally renders public Navbar/Footer based on `pathname.startsWith('/admin')`:

```tsx
'use client';
export default function ClientLayout({ children }) {
  const pathname = usePathname();
  const isAdmin = pathname?.startsWith('/admin');
  return (
    <>
      {!isAdmin && <Navbar />}
      {children}
      {!isAdmin && <Footer />}
    </>
  );
}
```

Also raise admin modals above any sticky public header with `.admin-layout .modal { z-index: 1200 !important; }`.

See `references/admin-ssg-hybrid-pattern.md` and `references/admin-modal-ui-pattern.md`.

### 3.4 Promo / new-product badges

Store promo info in `stock_info` or `oldPrice`/`isNew` fields. Compute badges in the card component and admin editor:

```tsx
const isPromo = product.oldPrice && product.oldPrice > product.price;
{product.isNew && <span className="badge-new">Новинка</span>}
{isPromo && <span className="badge-promo">Акция</span>}
```

See `references/ecommerce-promo-badges.md` and `references/admin-panel-promo-prices.md`.

## 4. Admin form patterns

### 4.1 The scroll-jump root cause

In long modal forms, every `onChange` lifting state to the parent re-renders the entire form. Combined with sticky headers, centered dialogs, and controlled `textarea` props, the modal scrolls back to the focused/sticky element.

### 4.2 The durable fix: local draft state

Keep a local `draft` inside the form component and only commit to the parent on save:

```tsx
const [draft, setDraft] = useState<Product>(initialProduct);
const prevIdRef = useRef(initialProduct.id);
if (initialProduct.id !== prevIdRef.current) {
  prevIdRef.current = initialProduct.id;
  setDraft(initialProduct);
}

const update = useCallback(<K extends keyof Product>(field: K, value: Product[K]) => {
  setDraft((prev) => ({ ...prev, [field]: value }));
}, []);
```

See `references/pentajunior-v2-modal-local-draft-fix.md`.

### 4.3 CSS hardening

Pin the dialog to the top instead of vertically centering, and isolate scroll:

```css
.admin-modal-dialog {
  margin: 1.5rem auto 0;
  display: block;
}
.admin-modal-dialog .modal-content { max-height: calc(100vh - 3rem); }
.admin-modal-dialog .modal-body {
  overflow-y: auto;
  overscroll-behavior: contain;
  scroll-behavior: auto;
}
```

See `references/modal-form-css.css` and `references/pentajunior-v2-modal-scroll-bug.md`.

### 4.7 Editing meta_title for categories and subcategories

When the user needs a different page `<title>` from the displayed category/subcategory name, add a `meta_title` column to both `categories` and `subcategories`, expose it in the admin modal forms, and use it in `generateMetadata` with a fallback to `title`. See `references/admin-meta-title-editing.md` for the full recipe.

If each iteration of a `.map()` renders more than one top-level element (a main row plus an expanded detail row), the shorthand `<>...</>` fragment cannot carry a `key`. React warns:

```
Warning: Each child in a list should have a unique "key" prop.
```

Fix by importing `Fragment` and keying the Fragment:

```tsx
import { Fragment, useEffect, useState } from 'react';

{categories.map((c) => (
  <Fragment key={c.id}>
    <tr>{/* main row */}</tr>
    {expanded[c.id] && <tr key={`${c.id}-detail`}>{/* detail row */}</tr>}
  </Fragment>
))}
```

See `references/react-fragment-key-admin-lists.md`.

### 4.5 Admin CRUD placeholder safety

When the DB schema for an admin-managed table changes (e.g. adding `subcategory_id` to `products`), every `INSERT` and `UPDATE` in the admin API must receive the same number of `?` placeholders as there are columns. A mismatch does not fail TypeScript or build; it fails at runtime when an admin tries to save.

Quick guard:

```bash
# Column count
sqlite3 pentajunior.db "PRAGMA table_info(products);" | wc -l

# Placeholder count in INSERT
grep -n "VALUES (" src/app/api/admin/products/route.ts
```

Always test a full create/edit cycle after schema changes. For the full recipe see `references/admin-sql-insert-mismatch-trap.md`.

If each iteration of a `.map()` renders more than one top-level element (a main row plus an expanded detail row), the shorthand `<>...</>` fragment cannot carry a `key`. React warns:

```
Warning: Each child in a list should have a unique "key" prop.
```

Fix by importing `Fragment` and keying the Fragment:

```tsx
import { Fragment, useEffect, useState } from 'react';

{categories.map((c) => (
  <Fragment key={c.id}>
    <tr>{/* main row */}</tr>
    {expanded[c.id] && <tr key={`${c.id}-detail`}>{/* detail row */}</tr>}
  </Fragment>
))}
```

See `references/react-fragment-key-admin-lists.md`.

## 5. Product-detail templates

### 5.1 Conditional rendering

Never render a section heading if its data is absent. Wrap each field:

```tsx
{templateData.composition && (
  <section>
    <h2>Состав</h2>
    <p>{templateData.composition}</p>
  </section>
)}
```

This keeps migrated pages clean and prevents empty SEO sections.

### 5.2 One template per category (or one universal template)

- Start with category-specific templates if the DOM structures differ significantly.
- Evolve to a single `UniversalTemplate` once field-driven conditional rendering is enough.
- Store field definitions in `category_templates` so the admin editor is DB-driven.

See `references/product-template-mapping.md`, `references/template-data-editor-pattern.md`, and `references/template-migration-db-driven.md`.

### 5.3 Markdown in template fields

Use lightweight `**bold**` syntax for emphasis. Render with a safe markdown helper that maps to `<strong>`. Do not store raw HTML or JSX.

See `references/template-markdown-formatting.md` and `references/template-text-markdown-and-sync.md`.

### 5.4 Spec / comparison tables

Store family comparison tables as JSON:

```sql
CREATE TABLE spec_tables (
  id TEXT PRIMARY KEY,
  columns_json TEXT,
  rows_json TEXT
);
```

See `references/port-conflict-pm2-nextjs.md`.

### 6.3.1 301 vs 308 in Next.js redirects

Setting `permanent: true` in `next.config.ts` produces an **HTTP 308 Permanent Redirect**, not 301. This is correct behavior (308 preserves method/body), but verify with `curl -I` and look for `HTTP/1.1 308 Permanent Redirect`. Do not try to force 301 with `statusCode` unless there is an explicit SEO requirement; 308 is treated as permanent by search engines and is safer for POST replay.

## 5. Migrating content category-by-category

When `template_data` already has `intro`/`body` but is missing `application`/instructional content, extract the v1 `application` block per category and split it into the correct v2 template fields. Use the recipe in `references/v1-application-block-mapping.md`.

Key migration rules learned from `pentajunior` → `pentajunior-v2`:

- **Convert JSX/HTML to Markdown** before storing in `template_data`. `MarkdownParagraph` will escape raw HTML and users will see literal tags.
- **Watch for literal `\n` (backslash-n) artifacts in text imports.** When v1 descriptions were copied into `categories.meta_description` or `categories.page_description`, escaped newlines sometimes survived as two-character `\n` strings. Search with SQL: `SELECT ... WHERE meta_description LIKE '%\\%' ESCAPE '\'` and replace `\n` with a space (meta) or a real newline (page_description).
- **Split by semantic bold headings** (`Область применения`, `Способ нанесения`, `Способы применения`, `Важно`, numbered lists) into the matching v2 fields (`applications`, `method`, `important_note`, `recommendations`/`mixing_steps`).
- **Decide whether the block is "areas of use" or "how to use" first.** Instructions should go to `recommendations`/`method`/`important_note`, not `applications`.
- **Map explicit industrial/domestic subsections** directly to `application_industrial` / `application_domestic`. Do not also create a general `applications` array with the same items, or UniversalTemplate will render them three times (general, industrial, domestic).
- **Remove duplicate `application_industrial`** when it equals `applications`; otherwise `ApplicationAreasSection` renders the list twice.
- **Remove duplicate `surfaces`** when it equals `applications`; otherwise `DescriptionSection` renders the same list as "Применимые поверхности" and `ApplicationAreasSection` renders it again as "Области применения".
- **Remove mixed `bullets` after splitting into `surfaces` + `properties`.** When a v1 description contains several `<ul>` blocks under different bold headings ("Обрабатываемые поверхности", "Ключевые свойства", "Способ применения"), do not store all their items in a single `bullets` array. Split them into `surfaces`, `properties`, `recommendations`, etc., and delete `bullets`. Otherwise `DescriptionSection` renders one long mixed list and leaves empty heading fragments that create vertical whitespace.
- **Separate `features` (card header) from `properties` (description section).** The "Особенности:" block next to the price on the product card is rendered from the `products.features` JSON column in `ProductCard.tsx`, not from `template_data.properties`. Keep `features` short (3–4 items) for the header and `properties` complete for SEO in the description section.
- **Remove duplicate `application`** after splitting, so the "Применение" section does not duplicate "Области применения".
- **Split mixed "areas of use + instructions" lists** by action verbs. Any bullet containing `нанесите`, `разотрите`, `смойте`, `удалите`, `распределите`, `дайте`, `обновляйте`, `впитаться` is an instruction and belongs in `recommendations` (or `method`), not `applications`.
- **Clean `body`/`intro` of trailing application headings** (`Область применения {Name}:`, `Способ применения {Name}:`, `Способы применения {Name}:`) left over from v1. Use DOTALL regex to drop the heading and everything after it when it is duplicate content.
- **Commit after each category.** The SQLite DB is a binary blob; `git diff` cannot show which rows changed. Atomic commits per category keep history reviewable and prevent accidental bundling of unrelated category updates.
- **Restart `next start` after every build.** It serves the previous `.next` output until the process is killed and restarted. If the page still looks stale after restart, check for zombie `next-server` processes with `pgrep -a next` and kill them with `pkill -9 -f 'next-server'` before clearing `.next` and rebuilding.
- **Pull before editing a shared SQLite DB.** If the repository is shared, always run `git pull` before editing `pentajunior.db`. If a remote commit changed the binary DB, Git cannot merge it automatically; resolve the conflict with `git checkout --ours pentajunior.db` (or `--theirs`) and then reconcile the data via SQL/Python if both sides contain important changes.

Important: because the SQLite DB is committed as a binary blob, **commit after each category** to avoid bundling unrelated changes into a single opaque commit.

## 6. Bootstrap frontend hardening

### 6.1 Nested category sidebar tree (Variant 1)

When subcategories exist, render the sidebar as a single nested tree under each parent category instead of separate `Категории` and `Подкатегории` blocks. Use the reusable `CategorySidebar` / `CategorySidebarClient` split from `references/category-sidebar-variant1-implementation.md`:

- Server component fetches categories, products, subcategories and product counts.
- Client component (`"use client"`) holds the accordion state, renders the category name as a `Link` and a separate chevron button for expand/collapse, and uses smooth `max-height` transitions.
- Active category gets an olive background with a left accent bar; active subcategory gets a mint wash.
- The component must be wrapped in `col-lg-4` to sit in the left column of the page's `.row`.

Do **not** import `@/lib/db` directly into the client part — `better-sqlite3` needs Node.js built-ins and will fail the client bundle with `Module not found: Can't resolve 'fs'`. Serialize data as props instead.

Do **not** try to make a single `Link` perform both navigation and accordion toggling with `e.preventDefault()`; Next.js link interception makes this unreliable and users expect the category name to navigate while the chevron expands the tree.

### 6.2 Layout-shift-free toggles

Do not toggle between Bootstrap classes with different metrics (e.g. `btn-primary` ↔ `btn-outline-secondary`). Create a custom class with fixed padding/border and change only color/state modifiers.

```css
.blog-filter-btn {
  padding: 0.5rem 1.375rem;        /* fixed */
  border: 2px solid var(--color-primary);
  transition: background-color 250ms ease, color 250ms ease, box-shadow 250ms ease;
}
```

See `references/blog-filter-layout-shift.md` and `references/layout-shift-debugging.md`.

### 6.2 Product category card design

For the public `/production` listing, prefer **clean preview-first cards** over dense feature lists:

- Lead with a category preview image or initials placeholder.
- Use a brand-colored count badge, not Bootstrap `bg-secondary`.
- Keep the title as `h2`, description as a single paragraph, and a clear "go to section" link.
- Do not list product names inside the card for SEO; it adds visual noise without link equity.
- Make the whole card clickable to improve UX and accessibility.

See `references/category-card-seo-structure.md` for the full pattern and `references/design-variant-prototyping.md` for the variant-selection workflow.

### 6.3 Common Bootstrap + Next.js pitfalls

- **`<strong>` invisible in muted text:** explicitly set color/weight for `.news-card-desc strong`.
- **Cyrillic `LIKE` is case-sensitive:** perform case-insensitive search in JS or add a normalized `search_text` column.
- **JSX artifacts in HTML fields:** remove `{/* comments */}` and self-closing tags before rendering to avoid hydration mismatches. Store HTML, not JSX, in `seo_text` and other raw HTML columns.
- **Nested `<p>` inside `<p>`:** when using a `MarkdownParagraph` helper, apply styling class to the helper, not an outer `<p>`.
- **Stale dev server:** kill `next dev` and restart on an alternate port if a fix does not appear. `next start` in particular serves the existing `.next` output and will not reflect CSS/JS changes until restarted after a fresh `npm run build`. For the full recipe (including killing zombie processes and verifying with `curl`), see `references/nextjs-dev-server-cache-invalidation.md`.
- **Zombie `next-server` after `pkill -f 'next start'`:** `next start` leaves a child `next-server` process that can keep port 3001 alive. Use `pgrep -a next` to list survivors and `pkill -9 -f 'next-server'` to kill them.
- **Subcategory routing ambiguity:** do not create both `[categorySlug]/[subcategorySlug]` and `[categorySlug]/[productId]` pages; Next.js cannot distinguish `/cat/sub` from `/cat/prod`. Use a single optional catch-all route `[categorySlug]/[[...rest]]` and resolve `rest` into subcategory/product manually. See `references/subcategory-hierarchy-implementation.md` for the full recipe.
- **When every product has a subcategory, switch to strict three-level routes.** Once `SELECT COUNT(*) FROM products WHERE subcategory_id IS NULL` returns 0, replace the catch-all with explicit routes:
  - `/production/[category]/page.tsx` — category page with subcategory tiles;
  - `/production/[category]/[subcategory]/page.tsx` — subcategory product listing;
  - `/production/[category]/[subcategory]/[product]/page.tsx` — product detail using `ProductCard`, spec tables, and template data.
  This eliminates the `resolveSegments` complexity and makes metadata/JSON-LD per page simpler. Keep `getSubcategoryBySlug(slug)` in `lib/db.ts` for the product and subcategory pages.
- **Do not generate redirects by category wildcard in `next.config.ts`.** A redirect like `/production/:category/:path → /production/:category/:subcategory/:path` is wrong when a category has multiple subcategories: it sends every old product URL to the first subcategory in the DB. Generate one redirect per product instead:
  ```ts
  products
    .filter(p => p.subcategory_id)
    .map(p => ({
      source: `/production/${category.slug}/${p.id}`,
      destination: `/production/${category.slug}/${subcategory.slug}/${p.id}`,
      permanent: true,
    }));
  ```
  See `references/strict-three-level-subcategory-routing.md`.
- **PM2 respawns killed Next.js servers:** if a port stays occupied after `pkill -9 -f 'next-server'`, run `pm2 list` and `pm2 stop/delete <app>` to stop the PM2-managed daemon. See `references/port-conflict-pm2-nextjs.md`.
- **Do not import `src/lib/db` from `next.config.ts`:** the build-time transpiler cannot resolve project aliases. Query `better-sqlite3` directly inside `async redirects()` when generating 301 redirects from DB data. See `references/subcategory-hierarchy-implementation.md`.
- **PM2 respawns killed Next.js servers:** if a port stays occupied after `pkill -9 -f 'next-server'`, run `pm2 list` and `pm2 stop/delete <app>` to stop the PM2-managed daemon. See `references/port-conflict-pm2-nextjs.md`.
- **Binary `.db` merge conflicts:** when multiple parties edit the committed SQLite file, `git pull` produces a binary conflict. Choose a side with `git checkout --ours pentajunior.db` or `--theirs`, then reconcile row-level changes with a Python/SQLite script if needed. See `references/pentajunior-v2-waterproof-template-cleanup.md`.
- **User explicitly asks for `pull` before edits:** always `git pull origin master` first when the user says they pushed changes, especially for the binary `pentajunior.db`. If both local and remote changed the DB, resolve with `--ours`/`--theirs` and reconcile row-level changes via SQL/Python when both sides contain important data. Never attempt a textual merge of a binary `.db` file.
- **Accidental backup files in commits:** `pentajunior.db.bak.*` and `migration_*.log` files can be created by helper scripts. Add them to `.gitignore` or delete before `git add -A` to avoid pushing them.

See `references/case-insensitive-cyrillic-search.md`, `references/jsx-in-dangerouslysetinnerHTML-hydration-mismatch.md`, `references/mixed-script-column-matching.md`, `references/node-version-mismatch-better-sqlite3.md`, and `references/blog-dark-theme-styling.md`.

## Verification checklist

- [ ] `npm run build` succeeds and all expected pages are generated.
- [ ] `generateStaticParams` returns correct slug/productId pairs for categories, subcategories and products.
- [ ] Optional catch-all route resolves category / subcategory / product without 404.
- [ ] 301/308 redirects from old flat product URLs to `/category/subcategory/productId` return `Location` header (expect 308 for `permanent: true`).
- [ ] Product pages render identical HTML to the legacy version (if migrating).
- [ ] SEO metadata and JSON-LD preserved.
- [ ] No `dangerouslySetInnerHTML` unless explicitly sanitized.
- [ ] All prices verified after migration (run `scripts/migration-audit.py`).
- [ ] All categories have non-empty `seo_text`.
- [ ] Admin auth works end-to-end (login, protected routes, logout).
- [ ] Modal forms preserve `scrollTop` while typing.
- [ ] Public layout header/footer do not appear on `/admin` pages.
- [ ] Layout-shift recording in DevTools shows zero Layout events during toggles.
- [ ] No PM2-managed process respawns the dev server on the test port after kill.
- [ ] Admin product CREATE/UPDATE/DELETE round-trip works end-to-end (placeholder counts match column counts).

## Scripts

- `scripts/migration-audit.py` — post-migration audit for prices, stock_info, empty categories, dangling spec-table references, missing images.
- `scripts/reconcile-product-spec-tables.py` — remove duplicate specs from `template_data` when a `spec_table_id` exists; create personal spec tables from legacy "Характеристики" sections.
- `scripts/extract_v1_application.py` — extract and split legacy v1 `application` blocks into the correct v2 template fields.
- `scripts/verify-three-level-routing.sh` — after switching to `/production/[category]/[subcategory]/[product]`, verify category, subcategory, product pages and 308 redirects from old flat URLs. See `references/strict-three-level-subcategory-routing.md`.

## Templates

- `templates/three-level-production-pages.tsx` — copy-paste starter for `/production/[category]/page.tsx`, `/production/[category]/[subcategory]/page.tsx`, and `/production/[category]/[subcategory]/[product]/page.tsx` after migrating away from the catch-all route.
- `references/design-variant-prototyping.md` — how to build side-by-side HTML style-variant files for user selection before changing project code.
- `references/pentajunior-v2-category-sidebar-variant1.md` — concrete reusable `CategorySidebar` server/client split (smooth expand, olive/mint active states, separated counters, rotating chevrons) chosen via design-variant prototyping.
- `references/strict-three-level-subcategory-routing.md` — when every product has a subcategory, replace the optional catch-all with explicit `/production/[category]/[subcategory]/[product]` routes and avoid wildcard redirects that misroute products.

Session-specific and topic-specific notes moved from the previous narrow skills:

- `references/strict-three-level-subcategory-routing.md` — when every product has a subcategory, replace the optional catch-all with explicit `/production/[category]/[subcategory]/[product]` routes and avoid wildcard redirects that misroute products.
- `references/admin-sql-insert-mismatch-trap.md` — after adding columns to `products` (e.g. `subcategory_id`), verify that `INSERT` and `UPDATE` placeholders match the column count; this is a silent runtime failure in the admin API.
- `references/port-conflict-pm2-nextjs.md` — when `next start` respawns on a port after `pkill`, look for a PM2-managed `pentajunior` (or similarly named) app holding the port.
- `references/subcategory-hierarchy-implementation.md` — when a category mixes distinct product families and the user wants SEO-friendly subcategory landing pages (e.g. tin vs platinum silicone vs polyurethane inside a mold-making category). Covers DB schema, optional catch-all routing, generateStaticParams, 301 redirects from `next.config.ts`, admin UI, and SEO templates.
- `references/nested-category-sidebar-tree.md` — render categories and subcategories as a single nested sidebar tree instead of separate blocks.
- `references/react-fragment-key-admin-lists.md` — fix the `Each child in a list should have a unique "key" prop` warning when mapped admin rows contain expandable detail rows.
- `references/category-card-seo-structure.md` — semantic structure and content recommendations for category listing cards.
- `references/design-variant-prototyping.md` — how to build side-by-side HTML style-variant files for user selection before changing project code.
- `references/nextjs-dev-server-cache-invalidation.md` — why `next start` may serve stale pages and the full rebuild/kill recipe.
- `references/blog-article-typography-dark.md` — typography and table/list/FAQ styling for long-form article content inside `blog-page-dark`.
- `references/blog-dark-theme-styling.md` — dark-theme redesign workflow for `/blog` and `/blog/[articleId]`.
- `references/admin-dark-theme-variables.md`
- `references/admin-editor-debugging.md`
- `references/admin-modal-ui-pattern.md`
- `references/admin-panel-promo-prices.md`
- `references/admin-ssg-hybrid-pattern.md`
- `references/admin-template-lines-field.md`
- `references/array-fields-in-admin-form.md`
- `references/auth-cookie-httponly-trap.md`
- `references/subcategory-hierarchy-implementation.md` — when a category mixes distinct product families and the user wants SEO-friendly subcategory landing pages (e.g. tin vs platinum silicone vs polyurethane inside a mold-making category).
- `references/category-card-seo-structure.md` — semantic structure and content recommendations for category listing cards.
- `references/design-variant-prototyping.md` — how to build side-by-side HTML style-variant files for user selection before changing project code.
- `references/nextjs-dev-server-cache-invalidation.md` — why `next start` may serve stale pages and the full rebuild/kill recipe.
- `references/blog-article-typography-dark.md` — typography and table/list/FAQ styling for long-form article content inside `blog-page-dark`.
- `references/blog-dark-theme-styling.md` — dark-theme redesign workflow for `/blog` and `/blog/[articleId]`.
- `references/blog-filter-layout-shift.md`
- `references/case-insensitive-cyrillic-search.md`
- `references/category-seo-text-generation.md`
- `references/conditional-template-blocks.md`
- `references/ecommerce-promo-badges.md`
- `references/jsx-in-dangerouslysetinnerHTML-hydration-mismatch.md`
- `references/jsx-to-sqlite-migration.md`
- `references/json-db-crud-library.md`
- `references/layout-shift-debugging.md`
- `references/mixed-script-column-matching.md`
- `references/modal-form-css.css`
- `references/nextjs-sqlite-build-setup.md`
- `references/nextjs-sqlite-types.md`
- `references/penta-junior-admin-template-editor.md`
- `references/penta-junior-color-field-list.md`
- `references/penta-junior-spec-table-matching.md`
- `references/penta-junior-styling-match.md`
- `references/penta-junior-template-dedup.md`
- `references/pentajunior-v2-node-version-workaround.md` — when system `node` is v18 and the project requires Node v24 via nvm, set `PATH=/home/natan/.nvm/versions/node/v24.13.1/bin:$PATH` before `npm`/`npx` commands.
- `references/pentajunior-v2-category-backslash-cleanup.md` — detecting and removing literal `\n` artifacts from `meta_description` / `page_description` after legacy imports.
- `references/pentajunior-v2-waterproof-template-cleanup.md` — example of splitting mixed `bullets` into `surfaces`/`properties` and resolving binary `.db` merge conflicts; covers `penta-811`/`penta-870`.
- `references/penta-junior-template-fix.md`
- `references/penta-junior-universal-template.md`
- `references/penta-junior-v2-notes.md`
- `references/pentajunior-json-db-lib.ts`
- `references/pentajunior-product-lookup.md`
- `references/pentajunior-v2-modal-local-draft-fix.md`
- `references/pentajunior-v2-modal-scroll-bug.md`
- `references/pentajunior-v2-template-data-editor-rerender.md`
- `references/performance-ssg-sqlite.md`
- `references/price-corruption-migration-fix.md`
- `references/price-normalization-unit-column.md`
- `references/price-table-from-db.md`
- `references/product-card-grid-styling.md`
- `references/product-data-reconciliation.md`
- `references/product-template-mapping.md`
- `references/related-products-section.md`
- `references/runtime-image-path-validation.md`
- `references/search-seo-client-side.md`
- `references/spec-comparison-tables-admin.md`
- `references/sqlite-currency-migration.md`
- `references/sqlite-json-column-parsing.md`
- `references/sqlite-json-column-serialization.md`
- `references/sqlite-unit-migration.md`
- `references/stock-actions-card-debug.md`
- `references/template-data-body-normalization.md`
- `references/template-data-editor-pattern.md`
- `references/template-data-population-workflow.md`
- `references/template-markdown-formatting.md`
- `references/template-migration-db-driven.md`
- `references/template-text-markdown-and-sync.md`
- `references/textarea-enter-key-interception.md`
- `references/uncontrolled-field-row.tsx`
- `references/wrong-push-recovery.md`
