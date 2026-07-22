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
5. Watch the browser console for React errors (`Cannot update a component ... while rendering`, `Maximum update depth exceeded`, hydration mismatch warnings).

**Automation trap:** admin tables place "Редактировать" and "Удалить" buttons next to each other. Clicking the wrong `@ref` opens a JavaScript `confirm()` dialog that the current Hermes browser tools cannot dismiss. Prefer `browser_console` with a scoped selector (e.g. `document.querySelector('button.btn-warning')?.click()`) over `@ref` clicks for destructive-adjacent actions. See `references/browser-dialog-blocker-recovery.md`.

### Admin layout hydration mismatch
If `/admin` prints `Hydration failed because the server rendered HTML didn't match the client`, the cause is almost always a server/client branch in `src/app/admin/layout.tsx` based on `document.cookie`, `typeof window`, `localStorage`, or other browser-only globals. Because the file has `'use client'`, its initial render still runs on the server during SSR, where those globals differ from the hydrated client.

Fix pattern:
- Render the same initial shell on both server and client.
- Move auth checks and redirects into `useEffect` (after hydration).
- Use a local `authChecked` flag to switch from the loading spinner to the full admin shell only on the client.
- Keep the spinner's background/style aligned with the final shell to avoid a color flash.

See `references/admin-layout-hydration-mismatch-pattern.md` for the full recipe and a known-good code sample.

### Admin layout hydration mismatch (2026-07-18)
**Symptom:** Next.js logs "Hydration failed because the server rendered HTML didn't match the client" for `src/app/admin/layout.tsx`, showing the server rendered a spinner/loading shell while the client rendered the full `admin-app` shell.

**Root cause:** `AdminLayout` is a Client Component (`'use client'`) but its initial render branched on `document.cookie` via `typeof document === 'undefined'`. The server always took the "no token" branch; the hydrated client took the "token present" branch, producing different HTML.

**Fix pattern:**
```tsx
const [authChecked, setAuthChecked] = useState(false);

useEffect(() => {
  setAuthChecked(true);
  if (pathname === '/admin/login') return;
  if (!hasAdminToken()) router.push('/admin/login');
}, [pathname, router]);

const isLogin = pathname === '/admin/login';
const showAppShell = isLogin || authChecked;
const showSpinner = !isLogin && authChecked && !hasAdminToken();

if (!showAppShell || showSpinner) {
  return (
    <div className="d-flex justify-content-center align-items-center vh-100" style={{ background: '#161b22' }}>
      <div className="spinner-border text-light" />
    </div>
  );
}
```
Keep the first render identical on server and client. Perform auth checks and redirects only inside `useEffect`, after hydration. Align the loading spinner's background/style with the final shell to avoid a color flash.

See `references/admin-layout-hydration-mismatch-pattern.md`.

### Deploy script / GitHub access on this host
The Hermes host cannot reach GitHub over native HTTPS (TLS handshake fails). The local xray proxy exposes SOCKS5 on `127.0.0.1:1080` (and `10808`), but **SSH over SOCKS5 to GitHub is unreliable** in practice and produces:
```
Connection closed by UNKNOWN port 65535
fatal: Could not read from remote repository.
```

The stable path is HTTPS git through the xray SOCKS5 proxy with explicit config and a retry loop:

```bash
# Switch remote back to HTTPS if it was set to SSH
git remote set-url origin https://github.com/fester00/penta-junior-v2.git
```

In `deploy.sh`:
```bash
echo "📥 Получаем изменения..."
for i in 1 2 3 4 5; do
  git -c http.proxy=socks5h://127.0.0.1:1080 -c http.version=HTTP/1.1 pull origin master && break
  echo "⚠️ git pull failed, retrying in 2s... (attempt $i/5)"
  sleep 2
done
```

Why this works while other methods fail:
- `http_proxy`/`https_proxy` env vars → TLS handshake reset by peer.
- `git config http.proxy socks5h://127.0.0.1:1080` in `.git/config` → libcurl may still fall back or ignore it depending on env/state; explicit `-c` flags are honored.
- SSH over SOCKS5 (`ProxyCommand nc -X 5 -x 127.0.0.1:1080`) → works from some shells but fails from `zsh`/`deploy.sh` due to GPG agent interference (`SSH_AUTH_SOCK` pointing to a GPG agent with no SSH keys) or reality server filtering.

**Critical pitfall — GPG agent with no SSH keys (SSH variant only):**
If using SSH, the wrapper must `unset SSH_AUTH_SOCK` or force a specific key, or you get:
```
Connection closed by UNKNOWN port 65535
fatal: Could not read from remote repository.
```
Prefer the HTTPS+SOCKS5 variant above instead.

**Pushing from this host:**
Use the same explicit flags when pushing is required:
```bash
git -c http.proxy=socks5h://127.0.0.1:1080 -c http.version=HTTP/1.1 push origin master
```

**Build retry for Google Fonts:**
`next/font/google` in `layout.tsx` fetches `Inter` during `npm run build`. The same xray tunnel can reset mid-build. Wrap `npm run build` in a retry loop:
```bash
for i in 1 2 3; do
  npm run build && break
  echo "⚠️ Build failed, retrying in 3s... (attempt $i/3)"
  sleep 3
done
```

See `references/deploy-script-github-proxy-pattern.md` for the full recipe, debugging steps, and why `http.proxy` in `.git/config` alone is not always honored by libcurl in this environment.

### Resetting repo state to a known-good commit
When the user says the remote repo is "испорчено" (broken/pushed wrong commits) and wants the repository restored to a specific local commit:
1. Confirm the local commit SHA matches the desired state.
2. Run `git checkout -- .` (or `git checkout -- package-lock.json`) to clean the working tree.
3. Point local `master` to the known-good commit:
   ```bash
   git checkout master
   git reset --hard <sha>
   ```
4. Force-push the known-good commit to `origin/master`:
   ```bash
   git push --force origin <sha>:master
   ```
5. Verify both local and remote are aligned:
   ```bash
   git rev-parse master
   git rev-parse origin/master
   ```
6. On success, the remote history is rewritten to match the local commit.
7. **Never pull** after a force push unless the user explicitly asks.
8. Build and deploy only after user confirmation.

See `references/force-push-rollback-to-known-good-commit.md` for the full
recipe, verification commands, and safety rules.

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
- `references/pentajunior-to-v2-migration-plan.md` — migration path from legacy `pentajunior` to v2.
- `references/deploy-script-verification-checklist.md` — verify a user-edited root `deploy.sh` before running it (branch, PM2 name, port).
- `references/rolling-back-to-known-good-commit.md` — emergency rollback to a known-good commit and verifying repo/production alignment afterwards.

## SEO metadata workflow
Category / subcategory / product metadata is stored in `pentajunior.db` and rendered by `generateMetadata` in the 3-level production routes. See `references/seo-metadata-checklist.md` for quick SQL recipes, length limits, and the brand-suffix pitfall. See `references/seo-category-optimization-playbook.md` for the full end-to-end workflow (inventory, drafting, applying, verifying, adding missing products from the legacy site).

### Client/server boundary and shared types
- **Client components must never import `@/lib/db.ts`**. `lib/db.ts` imports `better-sqlite3`, which pulls Node modules (`fs`, native bindings) into the browser bundle and breaks the build. Always keep shared data **types** in a separate file:
  ```
  src/lib/types.ts   # pure TypeScript interfaces
  src/lib/db.ts      # server-only queries + runtime helpers
  ```
- Any client component that needs `Category`, `Product`, `Subcategory`, etc. should import `from "@/lib/types"`, not `from "@/lib/db"`.
- Server components and API routes continue to import `from "@/lib/db"`.
- If a shared UI component is used in both public pages and the admin panel, treat it as client-safe and import types from `@/lib/types`.
- After centralizing types, `lib/db.ts` should import and re-export type aliases from `lib/types.ts` so existing server/API imports keep working. Do not duplicate interface definitions in both files.
- For raw SQLite rows, prefer typed row interfaces over `as any`. See `references/typed-db-row-refactor-pattern.md`.

### Typed raw rows for better-sqlite3
Do not cast query results to `any`. Define a `*Row` type that matches the columns SQLite actually returns, then cast to `Row[]` or `Row | undefined`. This catches shape mismatches at the mapping layer and removes the largest source of `@typescript-eslint/no-explicit-any` errors in `lib/db.ts`. See `references/typed-db-row-refactor-pattern.md`.

### Product card badge logic
The `CompactProductCard` catalog variant must show badges when **either** `news === true` **or** `stockInfo?.newPrice` exists. A common regression is wrapping the badge block in `{news && (...)}`, which hides the "Акция" badge for products that are on sale but are not marked as new. The correct guard is:
```tsx
{(news || stockInfo?.newPrice) && (
  <ProductBadges news={news} stockInfo={stockInfo} variant="catalog" />
)}
```

### SEO/performance quick checks
Before claiming a page is "SEO-ready" or "fast", verify:
1. **H1 present and hierarchy clean** — every public page should have exactly one logical `<h1>` and no lower heading should appear before it in the DOM. The `CategorySidebarClient` title must be a styled `<span>` (e.g. `<span className="category-sidebar-title h5 d-block">`), not `<h3>`. The `ProductCard` title should not be hard-coded as `<h1>`; instead render an explicit `<h1>` in `page.tsx` and remove the title element from `ProductCard` (or make it configurable via a `titleTag` prop defaulting to `h2`). On product detail pages the canonical pattern is:
   ```tsx
   // src/app/production/[category]/[subcategory]/[product]/page.tsx
   <h1 className="mb-4 fs-2 fw-bold">{product.name}</h1>
   <ProductCard categorySlug={category.slug} subcategorySlug={subcategory.slug} product={product} />
   ```
   This keeps `ProductCard` reusable in lists/admin previews without risking duplicate H1s.
2. **No empty headings** — empty `<h2>`/`<h3>` confuse outline parsers.
3. **Image alt texts** — `next/image` components should have descriptive `alt`. The Yandex Metrika noscript pixel intentionally uses `alt=""`.
4. **`next/image` `fill` warnings** — if the browser console warns about `missing "sizes"` or `parent element with invalid "position"`, the immediate parent of a `fill` image is not `position: relative/absolute/fixed`. Do not rely only on CSS classes; wrap the `Image` in an explicit positioned wrapper. See `references/nextjs-image-fill-position-pattern.md`.
5. **JS bundle size** — after build, `.next/static/chunks` totals ~959 KB. Keep an eye on chunk growth; avoid pulling server-only modules into client components.
6. **Image format** — `public/images/` still contains PNG/JPG. Converting to WebP and updating DB paths is the single biggest load-speed win.
7. **OG images per entity** — use `category.image` / `subcategory.image` / `product.image` for OpenGraph when available; fall back to `/images/hero.webp` only when the entity has no image.
8. **next/image migration** — replace plain `<img>` in search dropdowns and other client UI with `<Image unoptimized>` for consistent sizing/alt handling.
9. **Font loading** — if `globals.css` references `'Inter'`, load it via `next/font/google` with `latin` and `cyrillic` subsets, or remove the name from the stack to avoid a non-loaded font reference.
   ```tsx
   // src/app/layout.tsx
   import { Inter } from 'next/font/google';

   const inter = Inter({
     subsets: ['latin', 'cyrillic'],
     display: 'swap',
     variable: '--font-inter',
   });

   export default function RootLayout({ children }) {
     return (
       <html lang="ru" className={inter.variable}>
         <body className={inter.variable}>{children}</body>
       </html>
     );
   }
   ```
   Then update `globals.css`: `font-family: var(--font-inter), -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;`.

### Security and data-layer red flags
These issues do not block daily SEO/UI work but must be fixed before any public exposure of admin endpoints or CI automation:
| Risk | Rating | Evidence |
|------|--------|----------|
| Hardcoded fallback admin password | **Critical** | `src/app/api/admin/auth/route.ts:3`, `src/proxy.ts:4` |
| Cookie stores plaintext password | **Critical** | `src/app/api/admin/auth/route.ts:14` sets `admin_token` to the raw password |
| No per-route auth re-verification | **Medium** | API routes rely only on `src/proxy.ts`; no `middleware.ts` |

### Status update (2026-07-01)
- ✅ SQL injection risk resolved: all admin API routes use parameterized `?` placeholders.
- ✅ Multiple DB connections resolved: admin API routes now import shared `db` from `lib/db`.
- ✅ DDL/DML migrations moved out of `lib/db.ts`: run `npm run migrate` (`tsx scripts/migrate.ts`) explicitly at deploy time. `lib/db.ts` no longer mutates the database on import, so `npm run build` is safe for CI/preview.
- ✅ Typed raw-row interfaces introduced in `lib/db.ts` and admin API routes; remaining explicit `any` cleaned from `lib/db.ts` and admin pages.
- ✅ Admin page types deduplicated: `admin/categories`, `admin/products`, `admin/spec-tables` import `Category`, `Subcategory`, `Product`, `SpecTable`, `StockInfo`, `PriceTier` from `lib/types`.
- ✅ React Hooks errors fixed in admin pages: `loadData`-before-declaration pattern, `setState` inside `useEffect`, and missing hook dependencies.
- ✅ Geo-audit P1 fixes applied: `/info/faq` og:image fallback, `/contacts` and `/info` canonical trailing slash removed, `/policy` OG values aligned with page content.

Recommended remaining fixes (do not start without user approval):
1. Remove fallback password; require `ADMIN_PASSWORD` env var.
2. Store signed JWT or hashed token in cookie, not raw password.
3. Add a thin `withAdminAuth(request)` wrapper to every `/api/admin/*` route.
4. Decide whether to keep `src/proxy.ts` or migrate to `src/middleware.ts` for admin protection.

## References
- `references/ui-refactor-and-cleanup-session-2026-07-01.md` — complete 2026-07-01 UI/API/types refactor pass: FormField/TextAreaField/SelectField, api-utils, site constants, type centralization, and the stock-badge regression fix.
- `references/architecture-and-quality-audit-2026-07-01.md` — post-refactor assessment: components, SEO markup, load speed, architecture risks, and prioritized next steps.
- `references/pentajunior-v2-port-coexistence.md`
| Component | Use for |
|-----------|---------|
| `FormField` | text, number, email, url inputs |
| `TextAreaField` | multi-line text (meta descriptions, SEO text, features) |
| `SelectField` | category, subcategory, currency, unit, template-type selects |

Rules:
1. Keep them dependency-free — **never import `@/lib/db.ts`**, because these components render in the admin client bundle and `better-sqlite3` pulls Node `fs` into the browser build.
2. Accept narrow props (`value`, `onChange(value)`, `label`, `hint`, `wrapperClassName`) rather than whole entity objects.
3. Let the parent handle value coercion (`Number(v)`, `v || null`, `v as 'RUB' \| 'USD'`); the component returns the raw string.
4. Preserve Bootstrap classes: `form-label` + `form-control` / `form-select` / `form-control` for textarea.
5. Be careful replacing inline `<select>` blocks: category selects may have side effects (resetting `subcategory_id` when category changes). Preserve that behavior in the parent `onChange` handler.

See `references/ui-refactor-component-extraction-pattern.md` for the full extraction safety rules, `references/stray-console-cleanup-pattern.md` for the project console-statement policy, and `references/ui-refactor-and-cleanup-session-2026-07-01.md` for the complete 2026-07-01 pass that extracted these components.

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

### Query patterns for data discovery

See `references/new-product-discovery-query-patterns.md` for reusable SQLite recipes used when extracting products/categories for exports, landing pages, or integrations. Key points:
- `products` has **no `slug` column**; use `id` or `name`.
- Product display name is `name`; SEO/long title is `title`.
- `features` and `keywords` are JSON strings.

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

### Build / verify gate (exact command)
Always run in this order before claiming anything works:
```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
cd /home/natan/pentajunior-v2
./node_modules/.bin/tsc --noEmit
rm -rf .next tsconfig.tsbuildinfo
npm run build
```
Expected result: `✓ Generating static pages using 5 workers (156/156)` and exit code `0`. If the count changes or any route fails, stop and fix before committing.

### Visual verification and preview discipline
The user owns mobile / visual QA. Follow these rules unless the user explicitly asks for a screenshot or a preview:

1. **Do not take mobile screenshots for verification.** When the user says "я сам проверю" / "визуальную проверку можешь не делать", stop all screenshot capture immediately.
2. **"Сделай push" means push after the build gate passes.** Do not block the push with local preview or screenshot verification; the user will check on the deployed / preview environment.
3. **Never touch the production server on port 3000.** The legacy `pentajunior` site runs there under PM2. Preview / dev servers must use **3001** (v2 dev) or a one-off port like **3002** only when explicitly requested, and only after confirming nothing else is listening on that port. Never assume 3002 is free.
### Google Fonts can fail during build
If `npm run build` errors with `Failed to fetch Inter from Google Fonts`, **retry before falling back**. The outage is often transient on either `fonts.googleapis.com` (the CSS) or `fonts.gstatic.com` (the font files). On this host 2–3 retries with a short delay are usually enough for the build to succeed.

Add a retry loop in `deploy.sh`:
```bash
echo "🔨 Собираем проект..."
for i in 1 2 3; do
  npm run build && break
  echo "⚠️ Build failed, retrying in 3s... (attempt $i/3)"
  sleep 3
done
```

If the outage persists after retries, temporarily remove the `next/font/google` Inter import from `src/app/layout.tsx`, drop the `inter.variable` className on `<html>` and `<body>`, and keep a system font stack in `globals.css`. Push, then restore Inter once Google Fonts is reachable again.

Example temporary fallback in `layout.tsx`:
```tsx
// import { Inter } from "next/font/google"; // commented out
// const inter = Inter({ subsets: ["latin", "cyrillic"], display: "swap", variable: "--font-inter" });

export default function RootLayout({ children }) {
  return (
    <html lang="ru" data-scroll-behavior="smooth">
      <body>{children}</body>
    </html>
  );
}
```

**Critical production pitfall:** if `deploy.sh` runs while `fonts.gstatic.com` is down and does not retry, `npm run build` aborts and leaves `.next/` partially built. PM2 then reloads into that broken directory. The site may still serve HTML, but all `/_next/static/chunks/*.css` and `*.js` return **500 Internal Server Error**, so the page has **no styles or interactivity**. Always verify the production static chunks after a deploy; do not assume `pm2 reload` success means the build succeeded. See `references/google-fonts-gstatic-build-outage.md` and `references/deploy-script-github-proxy-pattern.md` for the full recovery and deploy hardening recipes.


### Stale / incomplete build cache breaks CSS/JS chunk serving
Symptoms:
- Browser shows unstyled HTML (no Bootstrap layout, raw text).
- Console reports 500s on `/_next/static/chunks/*.css` or `*.js`.
- `curl -I https://pentajunior.ru/_next/static/chunks/<name>.css` returns `500 Internal Server Error` or `404 Not Found`.
- PM2 error log contains `ChunkLoadError: Failed to load chunk ... Cannot find module '/home/natan/pentajunior-v2/.next/server/chunks/ssr/...'` or `ENOENT: no such file or directory, open '/home/natan/pentajunior-v2/.next/prerender-manifest.json'`.

Common causes:
1. `npm run build` failed silently during `deploy.sh` (e.g., Google Fonts outage) and PM2 reloaded into a partial `.next/` directory.
2. The running `next start` server has an outdated build manifest while new HTML pages reference new chunk hashes that do not exist on disk.

**Fix on the production host:**
```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
cd /home/natan/pentajunior-v2
rm -rf .next tsconfig.tsbuildinfo
npm run build
pm2 reload pentajunior-v2 --update-env
```

**Verify recovery:**
```bash
# HTML still serves
curl -s -o /dev/null -w "%{http_code}" https://pentajunior.ru/

# CSS chunks return 200 with text/css
curl -sI https://pentajunior.ru/_next/static/chunks/<name>.css | head -1
curl -sI https://pentajunior.ru/_next/static/chunks/<name>.js | head -1
```

**After every push that should reach production, verify deploy actually finished.** Do not treat `pm2 reload` exit code zero as proof of a healthy build. Check `pm2 logs pentajunior-v2 --lines 50` for build errors and confirm static chunks are reachable.

Do **not** reload nginx unless the site is actually behind an nginx reverse proxy for `/_next/static`; in this project `next start` serves static directly. See `references/nextjs-stale-chunk-cache-recovery.md` and `references/google-fonts-gstatic-build-outage.md`.

### ESLint / code-quality gate
After the build gate passes, run ESLint and address any new errors introduced by the change:
```bash
./node_modules/.bin/eslint . --ext .ts,.tsx --max-warnings=100
```
Known recurring issues and the project's preferred fixes:
- `react-hooks/immutability` — `loadData` accessed before it is declared in admin pages (`/admin/categories/page.tsx`, `/admin/products/page.tsx`). Preferred fix: keep the data fetch inside `useEffect` as a local async function, and expose a separate `reloadData` for save/delete handlers:
  ```tsx
  useEffect(() => {
    let mounted = true;
    const loadData = async () => {
      setLoading(true);
      const res = await fetch('/api/admin/entities');
      const data = await res.json();
      if (!mounted) return;
      setItems(data.data || []);
      setLoading(false);
    };
    loadData();
    return () => { mounted = false; };
  }, []);

  const reloadData = async () => {
    setLoading(true);
    const res = await fetch('/api/admin/entities');
    const data = await res.json();
    setItems(data.data || []);
    setLoading(false);
  };
  ```
  Then call `reloadData()` from `handleSave`, `handleDelete`, etc. Do not reference the local `loadData` outside the effect.
- `react-hooks/set-state-in-effect` — calling `setState` synchronously inside `useEffect` body (`/admin/layout.tsx`). Preferred fix: move the initial value into `useState(...)` so the first render already has the right state, and keep the effect only for side effects such as redirects.
  ```tsx
  const [loading, setLoading] = useState(pathname !== '/admin/login');
  ```
- `react-hooks/no-ref-in-render` — reading/writing `ref.current` during render (`/admin/products/page.tsx`). Use an effect or event handler instead.
- `@typescript-eslint/no-explicit-any` — replace `any` with proper types. For DB queries, define typed raw-row interfaces and cast to them instead of `any`. See `references/typed-db-row-refactor-pattern.md`.
  - Also applies to admin pages that re-declare local `Category`/`Product` interfaces: delete the local copies and import from `@/lib/types`. Add missing shared types (e.g. `StockInfo`, `PriceTier`) to `lib/types.ts` if needed.
  - Also applies to admin API routes that cast query results `as any`: define a local `*Row` type and cast to it.
Do not ignore these errors; they are signals of real React lifecycle bugs.

### Recommended workflow for a category group
1. `git pull` first (user may have pushed changes).
2. Read the existing DB values for the category and all its subcategories/products with a SQLite query.
3. Apply or draft metadata changes from the SEO brief (title, description, page_description, keywords). Keep `meta_description` ≤ 160 chars.
4. Update the database with explicit `UPDATE` statements; never rely on a generic "save all" without checking row counts.
5. Run the build gate: `tsc --noEmit && rm -rf .next tsconfig.tsbuildinfo && npm run build`.
6. **Run JSON-LD audit:** verify every category/subcategory/product has `meta_title`/`meta_description`, numeric prices, filled `features`, and `/logo.png` exists. See `references/seo-metadata-checklist.md` § JSON-LD audit script.
7. Restart the v2 server on port 3001 and visually verify rendered `<title>` / `<meta name="description">`.

### When evaluating architecture or technology changes (e.g., "switch to htmx")
Before recommending a technology shift, study the project's primary goals and constraints. For pentajunior-v2 this means:

1. **Load the Yandex SEO skill first** — the user explicitly expects SEO implications to be evaluated through `yandex-seo-optimization`.
2. **Read project goals** from Obsidian project notes (`Projects/Пента Юниор — корпоративный сайт.md`, SEO audit notes) and the current codebase state.
3. **Map the proposal against each goal.** Does it help or hurt SSG, indexing, JSON-LD, metadata, speed, maintainability?
4. **Give a verdict with concrete trade-offs**, not a generic endorsement. Use tables: goal × current stack × proposed stack × risk.
5. **Only then propose implementation** if the change survives the evaluation.

Example from htmx evaluation: htmx was rejected for the public catalog because it would replace SSG/HTML links with dynamic fragments, risking indexation and metadata; it was approved only for point uses such as admin filters and search.

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
- `references/ui-refactor-and-cleanup-session-2026-07-01.md` — complete 2026-07-01 UI/API/types refactor pass: FormField/TextAreaField/SelectField, api-utils, site constants, type centralization, and the stock-badge regression fix.
- `references/architecture-and-quality-audit-2026-07-01.md` — post-refactor assessment: components, SEO markup, load speed, architecture risks, and prioritized next steps.
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
- `references/ui-refactor-component-extraction-pattern.md` — component signatures, safety rules, and git pitfalls for extracting repeated UI blocks.
- `references/client-server-boundary-and-types-pattern.md` — keep `better-sqlite3` out of the client bundle by splitting types into `src/lib/types.ts`.
- `references/api-route-refactor-pattern.md` — shared `src/lib/api-utils.ts` helpers and migration notes for `/api/admin/*` routes.
- `references/site-constants-centralization-pattern.md` — how to centralize domain, email, phones, company name, and address in `src/app/syte-config.ts` and replace hardcoded literals across public pages.
- `references/stray-console-cleanup-pattern.md` — when and how to remove leftover `console.log/error/warn` statements from client and server code.
- `references/adding-spec-table-pattern.md` — how to create and link a `spec_tables` entry for a product group.
- `references/spec-table-single-scrollbar-pattern.md` — avoid duplicating product spec tables for horizontal scroll; single native `overflow-x: auto` wrapper pattern.
- `references/importing-external-product-line-pattern.md` — bulk-adding an external supplier product line (Силагерм example).
- `references/adding-json-array-field-pattern.md` — how to add a JSON array field (e.g. `price_tiers`) to an entity and wire it through API + admin form.
- `references/post-refactor-p3-and-admin-cleanup-2026-07.md` — P3 cleanup items, heading hierarchy fix, deduping admin types, hardening admin API routes, and extracting DB migrations to `scripts/migrate.ts` after the 2026-07 refactor.
- `references/db-migration-extraction-pattern.md` — move SQLite schema/data migrations out of runtime `lib/db.ts` into an explicit `npm run migrate` script.
- `references/price-tiers-pattern.md` — storing, editing, and displaying multi-tier product prices like the legacy `pentajunior.ru/price` table.
- `references/react-local-state-editor-pattern.md` — reusable recipe for child editors with local state and `onChange`, avoiding "update while rendering" and infinite loops.
- `references/browser-dialog-blocker-recovery.md` — what to do when a browser `confirm()` / `alert()` dialog blocks automation tools.
- `references/seo-text-human-style-guide.md` — writing natural, human-sounding SEO copy for categories/subcategories without AI-isms.
- `references/typed-db-row-refactor-pattern.md` — replacing `as any` casts in `better-sqlite3` queries with typed raw-row interfaces.
- `references/post-refactor-analysis-and-p3-items-pattern.md` — how to run a post-refactor project audit (components, SEO, speed, architecture) and safely execute P3 cleanup items (remove dead files, next/image migration, OG images, next/font Inter).
- `references/html-semantics-seo-audit.md` — how to evaluate semantic HTML, heading hierarchy, and JSON-LD coverage for Yandex/Google SEO in pentajunior-v2.
- `references/css-audit-and-refactor-pattern.md` — how to audit `globals.css` for unused classes and duplicate selectors, safely remove them, and avoid staging backup files.
- `references/image-optimization-to-webp-pattern.md` — converting product/category images to WebP and updating DB paths for faster loads.
- `references/blog-table-responsive-wrapper-pattern.md` — making raw-HTML tables in blog articles horizontally scrollable on mobile without breaking the page layout.
- `references/blog-article-product-link-pattern.md` — use `product.name` (short name) instead of `product.title` (SEO title) for inline product links and related-product cards in blog articles.
- `references/product-detail-related-products-pattern.md` — related products section on product detail pages is inline JSX, must use `product.name` for card titles/image alt, and must include the `₽`/`$` currency symbol from `price_currency`.
- `references/news-page-card-markdown-and-currency-pattern.md` — render `template_data.intro` with `MarkdownParagraph` on `/news` cards and show `₽`/`$` next to prices.
- `references/nextjs-image-fill-position-pattern.md` — fix Next.js `Image` `fill` warnings about missing `sizes` or `position: static` parent in card components.

### CSS maintenance and audits
- `references/css-audit-and-refactor-pattern.md` — how to audit `globals.css` for unused classes and duplicate selectors, safely remove them, and avoid staging backup files.
- `references/refactor-types-and-productcard-pattern-2026-07-12.md` — replacing `any` in production pages, fixing the ProductCard "component created during render" anti-pattern, and build-gate verification.
- `references/blog-table-responsive-wrapper-pattern.md` — wrap blog tables at render time and move borders to the wrapper for mobile scroll.
- `references/new-product-discovery-query-patterns.md` — reusable SQLite recipes for finding categories, subcategories, and products when exporting or building external pages from pentajunior.db.
