---
name: pentajunior-v2-nextjs-sqlite
description: |
  Class-level skill for maintaining pentajunior-v2: a Next.js 16 + better-sqlite3
  production catalog with strict 3-level routing, admin panel, templates, and
  Bootstrap UI. Covers nvm Node switching, route refactors, sidebar mechanics,
  admin API fixes, redirect handling, and PM2 port coexistence.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nextjs, better-sqlite3, sqlite, pentajunior-v2, routing, admin, sidebar, pm2, bootstrap]
    related_skills: [hermes-software-development-workflow, hermes-agent, nextjs-product-catalog-admin]
---

# Pentajunior-v2 — Next.js + better-sqlite3 Maintenance

## Project identity
- Path: `/home/natan/pentajunior-v2`
- Runtime: Node.js **v24.13.1** via `nvm use v24.13.1`
- Framework: Next.js 16.x (Turbopack)
- Database: `better-sqlite3`, DB file `pentajunior.db`
- UI: Bootstrap 5 + custom `globals.css`
- Original pentajunior (legacy) runs on **port 3000** under PM2 from `/home/natan/pentajunior`.
- **v2 runs on port 3001** (set in `ecosystem.config.js` `args: 'start --port 3001'` and `env.PORT`).

## Boot sequence
Every build / server start must run under nvm:
```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
```

## Build / verify gate
Always run in this order before claiming anything works:
```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
cd /home/natan/pentajunior-v2
./node_modules/.bin/tsc --noEmit
rm -rf .next tsconfig.tsbuildinfo
npm run build
```

## Testing checkpoints and known-good commits
When a bug is reported against a live feature (admin modal, price page, etc.), the user may identify a specific commit as the last known-good state (e.g. "в коммите aff41c7 модалка работает — пока не правим, я тестирую").

Respect that boundary:
1. Stop proposing or applying new code changes to the component/area the user is testing.
2. Do not overwrite the user's working tree with experimental patches while they are validating behavior.
3. If a fix is needed, branch from the known-good commit or wait until the user confirms testing is complete and gives permission to modify.
4. When testing finishes, capture the findings (working vs broken commit SHA, error messages, reproduction steps) before applying a targeted fix.

This prevents the common regression where the agent "fixes" something that was already working and introduces a new issue while the user is mid-test.

## Project setup / Next.js warnings
If `npm run build` prints:
1. `Next.js inferred your workspace root, but it may not be correct` because of multiple lockfiles — you can set an explicit Turbopack root in `next.config.ts`:
   ```ts
   turbopack: { root: process.cwd() }
   ```
   **Dev-mode trade-off:** this silences the warning but can make `npm run dev` noticeably slower. The slowdown comes from Turbopack scanning the entire project root (including `pentajunior.db` and backup files). If the user notices slower dev page loads, remove `turbopack.root` again and leave the warning. For production builds the warning is harmless.
2. `The "middleware" file convention is deprecated` — rename `src/middleware.ts` to `src/proxy.ts` and export `function proxy(...)` instead of `function middleware(...)`. Keep the same body and config matcher.
   **Migration trap:** if you used `mv src/middleware.ts src/proxy.ts` and changed the export name, Git may still track `src/middleware.ts`. You must explicitly `git rm src/middleware.ts` and commit the deletion, otherwise `npm run dev` fails with:
   ```
   Both middleware file "./src\middleware.ts" and proxy file "./src\proxy.ts" are detected.
   ```
3. `Custom Cache-Control headers detected for the following routes: /_next/static/(.*)` — expected; the project intentionally caches static assets long-term. Leave it unless dev-mode cache issues appear.

## Routing architecture (post-refactor)
Strict 3-level production routing because every product has a `subcategory_id`:
```
/production/[category]/page.tsx                 # subcategory tiles
/production/[category]/[subcategory]/page.tsx     # product grid
/production/[category]/[subcategory]/[product]/page.tsx  # ProductCard detail
```
Old catch-all `[[...rest]]` route is removed.

### Redirects
`next.config.ts` redirects must be **per-product**, not category catch-all:
```ts
{
  source: `/production/${category.slug}/${product.id}`,
  destination: `/production/${category.slug}/${subcategory.slug}/${product.id}`,
  permanent: true,
}
```
Catch-all `:path` redirects break subcategory pages by redirecting them to the first subcategory.

## Admin panel
- `/admin/products`, `/admin/categories`, `/admin/subcategories`, `/admin/spec-tables`
- API routes under `/api/admin/*` protected by `src/proxy.ts` cookie `admin_token`. The project migrated from `src/middleware.ts` to `src/proxy.ts` because Next.js 16 deprecated the `middleware` convention. The exported function must be named `proxy`, not `middleware`.
- Adding products requires matching number of SQL `?` placeholders to table columns.
  If `products` table has 18 columns, `VALUES` must have 18 `?`.

### Browser-based admin verification
When the user asks to verify the admin UI visually, run a local dev server on port 3001 and test through the browser:
```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
cd /home/natan/pentajunior-v2
rm -rf .next
./node_modules/.bin/next dev -p 3001
```
Then:
1. Open `http://localhost:3001/admin/login`.
2. Use the password from `.env.local` (`ADMIN_PASSWORD`).
3. Submit the form, then navigate to `http://localhost:3001/admin/products`.
4. Open a product modal and interact with the target component.
5. Watch the browser console for React errors (`Cannot update a component ... while rendering`, `Maximum update depth exceeded`).

**Automation trap:** admin tables place "Редактировать" and "Удалить" buttons next to each other. Clicking the wrong `@ref` opens a JavaScript `confirm()` dialog that the current Hermes browser tools cannot dismiss. Prefer `browser_console` with a scoped selector (e.g. `document.querySelector('button.btn-warning')?.click()`) over `@ref` clicks for destructive-adjacent actions. See `references/browser-dialog-blocker-recovery.md`.

### Resetting repo state to a known-good commit
When the user says the remote repo is "испорчено" (broken/pushed wrong commits) and wants the repository restored to a specific local commit:
1. Confirm the local commit SHA matches the desired state.
2. Run `git checkout -- package-lock.json` (or any modified files) to clean the working tree.
3. Force push the local commit to `origin/master`:
   ```bash
   git push --force origin <sha>:master
   ```
4. On success, the remote history is rewritten to match the local commit.
5. **Never pull** after a force push unless the user explicitly asks.
6. Build and deploy only after user confirmation.

### Adding a new meta field to an existing entity (e.g. `meta_title` for products)
Use the same pattern as categories/subcategories. Steps in order:
1. **Database**: `ALTER TABLE products ADD COLUMN meta_title TEXT DEFAULT ''`.
2. **API**: update `SELECT` lists, INSERT column list and `?` count, UPDATE column list.
3. **Admin form**: add `<input>` bound to `draft.meta_title` (or empty string default).
4. **Page metadata**: use `meta_title || title` in `generateMetadata` and OpenGraph.
5. **Types**: add `meta_title: string` to `Product` interface in `src/lib/db.ts`.
6. **Verify**: `tsc --noEmit && rm -rf .next && npm run build`.

### When admin edits don't persist (category `seo_text` example)
If a form field is visible and submitted but the DB value never changes:
1. Inspect the API route (`/api/admin/categories/[id]/route.ts`) and confirm the field is in both the SQL column list and the `.run()` parameter list.
2. The category form already sends `seo_text`; the bug was that the initial API omitted it. Patch by adding `seo_text = ?` (UPDATE) and `seo_text` column (INSERT).
3. Verify via `curl` or direct DB query after saving.

## Sidebar component (`CategorySidebar`)
Design reference: `/home/natan/workspace/sidebar-design-variants.html` variant 1.
- Server wrapper `CategorySidebar.tsx` loads data and passes props.
- Client component `CategorySidebarClient.tsx` owns React state for expansion.
- Categories with subcategories are `Link` toggles: click calls `e.preventDefault()` and toggles `is-expanded`.
- Categories without subcategories are plain `Link` navigators.
- Active category gets olive background; active subcategory gets mint/rgba(109, 219, 133, 0.15).
- CSS uses `max-height` transition for smooth expand/collapse.

### `meta_title` length policy
For pentajunior-v2 `meta_title` becomes the HTML `<title>`. The user may prefer meaning over strict 70-character cuts. If the user says "пусть обрезает, главное чтобы смысл был понятен с контекстом страницы", leave long titles as-is and revisit CTR only after collecting data. Do not force shorten titles without the user agreeing to test the change.

### `/contacts` page heading overload
When auditing heading hierarchy, `/contacts` may contain many partner names as `<h3>` (26+ headings). This is not necessarily wrong, but it dilutes the outline. Prefer `<strong>` inside list items for partner names unless they are true subsections.

### H1 ↔ title mismatch on service pages
On `/info` the title is `Доставка и оплата | Пента Юниор` but H1 is `Общая информация`. Keep H1 aligned with the page's primary topic. If the page covers delivery/payment, H1 should reflect that.

## PM2 / production coexistence
- **Deployment authorization:** before running `deploy.sh` or any production restart, ask the user for explicit permission every time. A prior "deploy now" in the same session does **not** grant blanket approval for later deploys. If the user says "Сделай деплой" / "задеплой" for one commit, that approval applies to that deploy only; the next change needs a fresh confirmation. Show the commits/files that will be deployed.
- **Migration path to production:** when the user asks to switch the live site from legacy `pentajunior` to `pentajunior-v2`, use the plan in `references/pentajunior-to-v2-migration-plan.md`. It covers nginx `proxy_pass` flip, PM2 shutdown, rollback procedure, and pre-flight checks.
- PM2 responsibilities: keep Node.js alive, restart on crash, memory-limit restart, log files, autostart after reboot. It does **not** run `git pull`, `npm install`, or `npm run build`. That belongs to a deploy script or manual workflow.
- `references/pentajunior-to-v2-migration-plan.md`
- `references/deploy-script-verification-checklist.md` — verify a user-edited root `deploy.sh` before running it (branch, PM2 name, port).

## SEO metadata workflow
Category / subcategory / product metadata is stored in `pentajunior.db` and rendered by `generateMetadata` in the 3-level production routes. See `references/seo-metadata-checklist.md` for quick SQL recipes, length limits, and the brand-suffix pitfall. See `references/seo-category-optimization-playbook.md` for the full end-to-end workflow (inventory, drafting, applying, verifying, adding missing products from the legacy site).

### Image optimization for performance
Before claiming images are "fast enough", audit the `public/images/` directory. Convert PNG/JPG product and category images to WebP, resize anything larger than ~1600 px, and update the `image` paths in `pentajunior.db`. Typical result: ~90% size reduction with no visual loss.

Steps:
1. Backup `public/images/`.
2. Convert all `.png`/`.jpg`/`.jpeg` files to `.webp` (quality 85, max 1600 px).
3. Update `products.image` and any category/subcategory image references from `.png`/`.jpg` to `.webp`.
4. Run `tsc --noEmit && rm -rf .next && npm run build`.
5. Commit both the converted images and the DB path updates together.

See `references/image-optimization-to-webp-pattern.md`.

### Where metadata lives
| Entity | Table | Fields used by frontend |
| :-- | :-- | :-- |
| Category | `categories` | `title`, `meta_title`, `meta_description`, `page_description`, `seo_text` |
| Subcategory | `subcategories` | `title`, `meta_title`, `meta_description`, `page_description`, `seo_text` |
| Product | `products` | `title`, `meta_title`, `meta_description`, `keywords`, `features` |

### `generateMetadata` behavior
- `/production/[category]/page.tsx`: `title = category.meta_title || \`${category.title} — Пента Юниор\``; `description = category.meta_description` (truncated to 160 chars); keywords = subcategory titles.
- `/production/[category]/[subcategory]/page.tsx`: `title = subcategory.meta_title || \`${subcategory.title} — Пента Юниор\``; `description = subcategory.meta_description` (truncated to 160 chars); keywords = first 5 product keywords.
- `/production/[category]/[subcategory]/[product]/page.tsx`: `title = product.meta_title || \`${product.title} — Пента Юниор\``; `description = product.meta_description || product.title`; keywords = `product.keywords`.

Brand suffix rule: each `generateMetadata` uses the stored `meta_title` verbatim if it exists; only when `meta_title` is empty does it fall back to `<entity.title> — Пента Юниор`. Therefore the DB value should already contain the brand (`| Пента Юниор` or `— Пента Юниор`) when it is set. Never make the code append ` — Пента Юниор` unconditionally to a stored `meta_title` or the brand will duplicate (`…| Пента Юниор — Пента Юниор`).

### Known-good pattern (post-2026-06-22 fix)
```ts
// /production/[category]/page.tsx
const title = category.meta_title || `${category.title} — Пента Юниор`;
return { title, description, ... };

// /production/[category]/[subcategory]/page.tsx
const subTitle = subcategory.meta_title || subcategory.title;
const pageTitle = subcategory.meta_title ? subTitle : `${subTitle} — Пента Юниор`;
return { title: pageTitle, description, ... };

// /production/[category]/[subcategory]/[product]/page.tsx
const metaTitle = product.meta_title || `${product.title} — Пента Юниор`;
return { title: metaTitle, description, openGraph: { title: `${metaTitle}`, ... }, twitter: { title: `${metaTitle}`, ... }, ... };
```

### `name` vs `title` for products in UI vs metadata
The `Product` interface has two name fields:

| Field | Purpose | Example |
| :-- | :-- | :-- |
| `name` | Short display name for UI | `Пентэласт-711` |
| `title` | SEO / long title for `<title>` and OpenGraph | `Заливочный компаунд Пентэласт-711 купить \| до +250°C` |

Use **`product.name`** for any user-visible text inside the page body:
- Inline product links in blog articles (`references/blog-article-product-link-pattern.md`).
- Related-product cards in blog articles.
- Related-product cards in product detail pages (`references/product-detail-related-products-pattern.md`).
- Breadcrumb active item on product detail pages (already correct).
- Image `alt` text and placeholder initials in product detail related products.

Use **`product.title`** only for metadata: `<title>`, `meta_description` fallback, OpenGraph/Twitter, JSON-LD `name`.

### Inline sections vs components on product pages
When the user asks "is the section X a component?", check `src/app/production/[category]/[subcategory]/[product]/page.tsx` first. The "Другие товары в ..." block is inline JSX, not a separate component. If you need to change it, edit the page file directly or extract it into a new component while preserving the Bootstrap column classes and CSS classes to avoid layout shifts.

### Recommended workflow for a category group
1. `git pull` first (user may have pushed changes).
2. Read the existing DB values for the category and all its subcategories/products with a SQLite query.
3. Apply or draft metadata changes from the SEO brief (title, description, page_description, keywords). Keep `meta_description` ≤ 160 chars.
4. Update the database with explicit `UPDATE` statements; never rely on a generic "save all" without checking row counts.
5. Run the build gate: `tsc --noEmit && rm -rf .next && npm run build`.
6. **Run JSON-LD audit:** verify every category/subcategory/product has `meta_title`/`meta_description`, numeric prices, filled `features`, and `/logo.png` exists. See `references/seo-metadata-checklist.md` § JSON-LD audit script.
7. Restart the v2 server on port 3001 and visually verify rendered `<title>` / `<meta name="description">`.

### When the user asks for a site-wide SEO audit (Yandex-style)
Do not treat it as an invitation to change everything. Follow this sequence:
1. **Check technical basics** first: robots, sitemap, canonical, index-glue, 404 handling, HTTPS.
2. **Run JSON-LD audit** via `seo_jsonld_audit.py` to catch data-level issues (empty meta, bad prices, missing features, logo).
3. **Sample one page per template type** for `title`/`description`/H1–H3, images without alt, internal links, email exposure in HTML. Templates are shared, so one page of each type is enough.
4. **Use `html-validate` on compiled HTML** from `.next/server/app/`; ignore Next.js/Bootstrap noise (`void-style`, `attr-case`, `attribute-boolean-style`, `no-inline-style`, `prefer-native-element`, `valid-id`). Fix only actionable findings:
   - `unique-landmark` → add `aria-label` to each `<nav>`.
   - `no-dup-class` → remove duplicated classes.
   - heading hierarchy skips → replace footer/service headings with styled `<p>`/`<div>` or adjust levels.
5. **Summarize findings in a prioritized table** (critical / medium / low) and ask the user which items to fix. Do not start mass edits without approval.
6. Build gate before claiming any fixes are complete.

### External keyword research
Yandex Wordstat (`https://wordstat.yandex.ru/`) requires a logged-in Yandex ID session. If the browser hits the login wall, stop and ask the user for credentials/cookies or proceed with the provided SEO brief instead of fabricating search-stat numbers.

## References
- `references/pentajunior-v2-port-coexistence.md`
- `references/pentajunior-v2-admin-api-pitfalls.md`
- `references/pentajunior-v2-sidebar-variant-1.md`
- `references/pentajunior-v2-adding-meta-field-pattern.md`
- `references/pentajunior-v2-seo-metadata-checklist.md`
- `references/seo-category-optimization-playbook.md`
- `references/seo-silikon-dlya-zalivki-form-2026-06-22.md`
- `references/seo-production-release-2026-06-22.md`
- `references/seo-silicon-oils-2026-06-22.md`
- `references/seo-visokotemperaturnie-smazki-2026-06-22.md`
- `references/seo-germetics-2026-06-22.md`
- `references/seo-tsm1-2026-06-22.md`
- `references/seo-silicone-rubber-products-2026-06-22.md`
- `references/seo-surface-treatment-2026-06-22.md`
- `references/seo-hand-care-2026-06-22.md`
- `references/seo-electrosealant-2026-06-22.md`
- `references/seo-sozh-2026-06-22.md`
- `references/jsonld-audit-script.py` — automated data audit for JSON-LD correctness.
- `references/adding-spec-table-pattern.md` — how to create and link a `spec_tables` entry for a product group.
- `references/blog-article-published-flag.md` — how to hide/unpublish a blog article without deleting the source file.
- `references/importing-external-product-line-pattern.md` — bulk-adding an external supplier product line (Силагерм example).
- `references/adding-json-array-field-pattern.md` — how to add a JSON array field (e.g. `price_tiers`) to an entity and wire it through API + admin form.
- `references/price-tiers-pattern.md` — storing, editing, and displaying multi-tier product prices like the legacy `pentajunior.ru/price` table.
- `references/react-local-state-editor-pattern.md` — reusable recipe for child editors with local state and `onChange`, avoiding "update while rendering" and infinite loops.
- `references/browser-dialog-blocker-recovery.md` — what to do when a browser `confirm()` / `alert()` dialog blocks automation tools.
- `references/seo-text-human-style-guide.md` — writing natural, human-sounding SEO copy for categories/subcategories without AI-isms.
- `references/html-semantics-seo-audit.md` — how to evaluate semantic HTML, heading hierarchy, and JSON-LD coverage for Yandex/Google SEO in pentajunior-v2.
- `references/css-audit-and-refactor-pattern.md` — how to audit `globals.css` for unused classes and duplicate selectors, safely remove them, and avoid staging backup files.
- `references/image-optimization-to-webp-pattern.md` — converting product/category images to WebP and updating DB paths for faster loads.
- `references/blog-table-responsive-wrapper-pattern.md` — making raw-HTML tables in blog articles horizontally scrollable on mobile without breaking the page layout.
- `references/blog-article-product-link-pattern.md` — use `product.name` (short name) instead of `product.title` (SEO title) for inline product links and related-product cards in blog articles.
- `references/product-detail-related-products-pattern.md` — related products section on product detail pages is inline JSX, must use `product.name` for card titles/image alt, and must include the `₽`/`$` currency symbol from `price_currency`.
- `references/news-page-card-markdown-and-currency-pattern.md` — render `template_data.intro` with `MarkdownParagraph` on `/news` cards and show `₽`/`$` next to prices.

### CSS maintenance and audits
- `references/css-audit-and-refactor-pattern.md` — how to audit `globals.css` for unused classes and duplicate selectors, safely remove them, and avoid staging backup files.
- `references/blog-table-responsive-wrapper-pattern.md` — wrap blog tables at render time and move borders to the wrapper for mobile scroll.
