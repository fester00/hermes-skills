# Admin SQL INSERT placeholder mismatch trap

A common failure when extending the products table is adding a new column but forgetting to add the matching placeholder in the `INSERT` statement. The error only appears at runtime, because `better-sqlite3` accepts the prepared statement string until `.run()` is called with the wrong number of bindings.

## Symptom

Adding a new product through the admin UI fails silently or returns HTTP 500. The server log shows a SQLite error similar to:

```
Error: 17 values for 18 columns
```

or, if there are too few placeholders:

```
Error: table products has 18 columns but 17 values were supplied
```

## Root cause

The `INSERT` statement lists all columns, but `VALUES (...)` has one fewer `?` than the column list. For example, after adding `subcategory_id` to the schema and to the column list, the query becomes:

```ts
// WRONG
const stmt = db.prepare(`INSERT INTO products (id, category_id, subcategory_id, name, ..., template_data)
  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`);
//          1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17
//          ^ column count is 18
```

## Fix

Count columns and placeholders. They must match exactly. In the example above the fix is:

```ts
const stmt = db.prepare(`INSERT INTO products (id, category_id, subcategory_id, name, ..., template_data)
  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`);
```

and make sure the corresponding `.run(...)` call passes the same number of arguments.

In this session the mismatch was caused by adding `subcategory_id` to the `INSERT` column list but leaving the placeholder count at 17 instead of 18. The fix was a single additional `?`.

## Prevention checklist

Before committing an admin CRUD change:

1. Run `PRAGMA table_info(products)` and note the column count.
2. Count `?` placeholders in every `INSERT` and `UPDATE` statement in `src/app/api/admin/products/route.ts` (and `src/app/api/admin/products/[id]/route.ts` for edits).
3. Count arguments passed to `.run()`.
4. Test a full create + edit + delete cycle through the admin UI or with an authenticated POST.

## Quick test

From the project root, while the dev server is running:

```bash
curl -X POST http://localhost:3001/api/admin/products \
  -H 'Content-Type: application/json' \
  -H 'Cookie: admin_token=<ADMIN_PASSWORD>' \
  -d '{"name":"Probe","title":"Probe","category_id":1,"subcategory_id":1,"price":"100","price_currency":"RUB","price_unit":"шт","image":"/images/probe.jpg","features":[],"keywords":[],"meta_description":"","pack":"1 шт","spec_table_id":null,"news":false,"stock_info":null,"template_type":"default","template_data":{}}'
```

Expect `{"success":true,"id":"probe"}`. A 500 or parse error means the placeholder count is wrong.

## Related files

- `src/app/api/admin/products/route.ts`
- `src/app/api/admin/products/[id]/route.ts`
- `src/app/api/admin/categories/route.ts` and similar admin CRUD routes

## See also

- `references/sqlite-json-column-serialization.md` — how to serialize JSON fields before binding.
- `references/admin-auth-middleware.md` — the cookie-based middleware that protects `/api/admin/*` routes.
