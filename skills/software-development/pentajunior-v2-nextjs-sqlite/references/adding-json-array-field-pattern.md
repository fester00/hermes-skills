## Adding a JSON array field to an existing entity in pentajunior-v2

Pattern used for adding `price_tiers` to `products`. Repeat for any new list/array field on categories, subcategories, or products (e.g. multiple prices, tiers, related items).

### 1. Database migration
Add a TEXT column that stores JSON:
```sql
ALTER TABLE products ADD COLUMN price_tiers TEXT DEFAULT '[]';
```

### 2. Update `src/lib/db.ts`
- Add the field to the TypeScript interface (`Product`, `Category`, or `Subcategory`).
- Add the column to every `SELECT` query that returns the entity.
- Parse it in every mapper:
  ```ts
  price_tiers: JSON.parse(r.price_tiers || '[]'),
  ```

### 3. Update API routes
- `src/app/api/admin/products/route.ts`:
  - add `price_tiers` to `SELECT` list;
  - parse it in the response mapper: `price_tiers: JSON.parse(r.price_tiers || '[]')`;
  - add `price_tiers` to INSERT column list and one more `?` to `VALUES`;
  - pass `JSON.stringify(body.price_tiers || [])` in `.run()`.
- `src/app/api/admin/products/[id]/route.ts`:
  - add `price_tiers = ?` to UPDATE column list;
  - pass `JSON.stringify(body.price_tiers || [])` in `.run()`.

### 3. Update admin form interfaces
In `src/app/admin/products/page.tsx`:
- define the inner item interface (e.g. `PriceTier`);
- add `price_tiers: PriceTier[]` to the `Product` interface;
- set `price_tiers: []` in `emptyProduct`;
- pass `price_tiers` through the save body (it is already spread).

### 4. Create a reusable editor component
Place it under `src/components/admin/`, e.g. `PriceTiersEditor.tsx`.
- Keep local state with temporary `id` keys for stable React rendering.
- Strip the temporary `id` before calling `onChange` so the stored JSON stays clean.
- Provide per-row fields and add/remove buttons.
- **Critical:** do not call `onChange` synchronously inside `setDrafts` updater. Use the safe local-state + `useEffect` pattern from `references/react-local-state-editor-pattern.md` to avoid React's "Cannot update a component while rendering" warning and infinite loops.
- Import and use it in the form:
  ```tsx
  import PriceTiersEditor from '@/components/admin/PriceTiersEditor';
  ```
  ```tsx
  <PriceTiersEditor
    tiers={draft.price_tiers || []}
    onChange={(tiers) => update('price_tiers', tiers)}
  />
  ```

### 5. Public display
Use the new field on public pages; fall back to the base scalar value when the array is empty.

### 6. Verify
```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
./node_modules/.bin/tsc --noEmit
rm -rf .next tsconfig.tsbuildinfo
npm run build
```

## Pitfalls
- Forgetting to parse the JSON field in the GET mapper leaves the admin form with a string instead of an array.
- Forgetting to update the TypeScript interface in `src/lib/db.ts` breaks downstream pages and the admin form.
- Storing React-internal `id` keys in the database pollutes the JSON; strip them in `onChange`.
- Mismatch between INSERT/UPDATE column count and the number of `?` placeholders causes a runtime parameter error.
- Empty arrays are safe defaults; treat `null`/`undefined` as `[]` everywhere.
