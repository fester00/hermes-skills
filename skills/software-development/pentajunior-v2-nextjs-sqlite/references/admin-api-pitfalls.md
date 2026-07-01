## Pentajunior-v2 admin API pitfalls

### POST /api/admin/products
`products` table has 18 columns. The INSERT statement must include **all 18 column names** and **18 `?` placeholders**. A common bug is adding `subcategory_id` to the column list but keeping only 17 placeholders, causing a runtime mismatch.

```ts
db.prepare(`INSERT INTO products (
  id, category_id, subcategory_id, name, title, price, price_currency, price_unit,
  image, features, keywords, meta_description, pack, spec_table_id, news,
  stock_info, template_type, template_data
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`)
```

### PUT /api/admin/products/[id]
Same pattern for UPDATE — every column to persist must appear once, with `WHERE id = ?` at the end.

### Middleware
`src/middleware.ts` protects `/admin/*` and `/api/admin/*` by checking cookie `admin_token === ADMIN_PASSWORD`. A raw `POST` from a script returns 405/redirect unless the cookie is present; this is expected behavior. Test via the admin UI.

### DB helpers
`getSubcategoryBySlug(slug)` is preferred because subcategory slugs are unique across the database.
