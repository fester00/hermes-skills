# Penta Junior v2 — Project Notes

Condensed context for working on the `penta-junior-v2` / `pentajunior` Next.js
site.

## Project Layout

| Path | Purpose |
|---|---|
| `/home/natan/workspace/pentajunior` | Local project root |
| `src/data/products.tsx` | Static product catalog (typed `Product[]`) used by public pages |
| `src/data/categories.tsx` | Static category catalog used by public pages |
| `src/data/db.json` | JSON DB written by the admin panel |
| `src/lib/db.ts` | CRUD helpers for `db.json` (async fs, `DbProduct` / `DbCategory`) |
| `src/app/admin/products/page.tsx` | Client CRUD for products |
| `src/app/admin/categories/page.tsx` | Client CRUD for categories |
| `src/app/api/admin/products/route.ts` | API for product CRUD |
| `src/app/api/admin/categories/route.ts` | API for category CRUD |
| `src/app/api/admin/auth/route.ts` | Cookie-based login/logout |
| `src/components/UI/Cards/ProductCard.tsx` | Public product detail card |
| `src/components/Sections/UnisilSection9xxx.tsx` | Template-ish section for Unisil application instructions |

## Critical Architecture Note

Public pages import products from `src/data/products.tsx`, not from
`src/lib/db.ts`. The admin panel edits `src/data/db.json`. This means:

- Adding a field to the admin form requires the same field in `DbProduct`
  **and** in `Product`, plus rendering it in the public component.
- Existing static product objects should receive the new field (or it must be
  optional) to keep TypeScript happy.
- Switching the site to read from `db.json` is a separate migration task.

## Build Environment

- System Node is `v18.19.1` — too old for Next.js 16 (requires `>=20.9.0`).
- Use nvm Node 24:
  ```bash
  export PATH="/home/natan/.nvm/versions/node/v24.13.1/bin:$PATH"
  ```
- `npx` may not be available in PATH; prefer direct binary paths:
  ```bash
  ./node_modules/.bin/tsc --noEmit
  ./node_modules/.bin/next build
  ./node_modules/.bin/next dev --turbo
  ```

## Common Tasks

### Add a new admin field that renders on the public page

1. Add field to `src/lib/db.ts` (`DbProduct`).
2. Add field to `src/data/products.tsx` (`Product`).
3. Add form input to `src/app/admin/products/page.tsx`.
4. Render field in `src/components/UI/Cards/ProductCard.tsx` (or relevant
   template component).
5. Update at least one static product object in `src/data/products.tsx` so
   TypeScript can infer / verify the shape.
6. Run `./node_modules/.bin/tsc --noEmit` and `./node_modules/.bin/next build`
   with Node 24.

### Verify the field on a real product

Example product with colors already configured:
- URL: `/production/izdelija-iz-silikonovyh-rezin/silicon-sheet`
- Data object: `silicon-sheet` in `src/data/products.tsx`
- Field: `colors: ['Белый (стандарт)', 'Прозрачный', 'Красно-коричневый']`

## Related Skills

- `nextjs-flatfile-admin-panel` — JSON DB + admin CRUD patterns used by this
  project.
- `nextjs-bootstrap-frontend` — Bootstrap override / layout-shift fixes.
