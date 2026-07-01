## Adding a meta field to an existing entity in pentajunior-v2

Pattern used for adding `meta_title` to `products`. Repeat for any new scalar field on categories, subcategories, or products.

### 1. Database migration
Use a one-time SQLite ALTER:
```sql
ALTER TABLE products ADD COLUMN meta_title TEXT DEFAULT '';
```
If the DB is shared with production, include the migration in the commit or runbook.

### 2. Update API routes
- `src/app/api/admin/products/route.ts`:
  - add `meta_title` to `SELECT` list;
  - add `meta_title` to INSERT column list;
  - add one more `?` to `VALUES`;
  - pass `body.meta_title || ''` in `.run()`.
- `src/app/api/admin/products/[id]/route.ts`:
  - add `meta_title = ?` to UPDATE column list;
  - pass `body.meta_title || ''` in `.run()`.

### 3. Update admin form
In `src/app/admin/products/page.tsx`:
- add `meta_title: string` to the `Product` interface;
- set `meta_title: ''` in `emptyProduct`;
- add an input field above Meta description:
  ```tsx
  <div className="col-12">
    <hr className="my-3" />
    <label className="form-label">Meta title (заголовок страницы)</label>
    <input className="form-control" value={draft.meta_title} onChange={(e) => update('meta_title', e.target.value)} />
    <small className="text-muted">Если пусто — используется заголовок товара.</small>
  </div>
  ```

### 4. Use the field on the public page
In `src/app/production/[category]/[subcategory]/[product]/page.tsx`:
```ts
const metaTitle = product.meta_title || product.title;
return {
  title: metaTitle,
  openGraph: { title: `${metaTitle} | Пента Юниор` },
};
```

### 5. Update TypeScript types
In `src/lib/db.ts`:
- add `meta_title: string` to `Product` interface;
- replace all `SELECT * FROM products` with explicit column lists so new columns are always returned in a controlled way.

### 6. Verify
```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
./node_modules/.bin/tsc --noEmit
rm -rf .next tsconfig.tsbuildinfo
npm run build
```

## Pitfalls
- Forgetting to add a matching `?` in INSERT `VALUES` causes a runtime parameter mismatch.
- Using `SELECT *` in `src/lib/db.ts` may skip new columns if the DB schema changes; prefer explicit columns.
- Forgetting to add the new field to `emptyProduct` leaves the create form with `undefined`, which can break controlled inputs.
