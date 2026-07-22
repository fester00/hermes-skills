# Query patterns for discovering products during cross-project work

When a user asks to build a landing page, export, or other artifact that pulls data from pentajunior-v2, the canonical source is `pentajunior.db` in `/home/natan/pentajunior-v2`.

## Common discovery queries

### Find a category by slug fragment

```sql
SELECT id, title, slug, meta_title, meta_description, page_description, image
FROM categories
WHERE slug LIKE '%<fragment>%';
```

### List subcategories of a category

```sql
SELECT id, title, slug, category_id, meta_title, meta_description
FROM subcategories
WHERE category_id = ?;
```

### List products inside a category

```sql
SELECT p.id, p.name, p.title, p.price, p.price_unit, p.price_currency,
       p.image, p.features, p.meta_title, p.meta_description, p.keywords,
       s.title AS subcategory_title, s.slug AS subcategory_slug
FROM products p
JOIN subcategories s ON p.subcategory_id = s.id
WHERE s.category_id = ?
ORDER BY s.id, p.name;
```

### Find products by ID or name fragment

```sql
SELECT p.id, p.name, p.title, p.price, p.price_unit, p.price_currency,
       p.image, p.features, p.meta_title, p.meta_description, p.keywords,
       s.title AS subcategory_title, s.slug AS subcategory_slug
FROM products p
JOIN subcategories s ON p.subcategory_id = s.id
WHERE p.id IN (?, ?, ?);
```

### Find products whose name/title/features/keywords match a term

```sql
SELECT p.id, p.name, p.title, p.features, p.keywords
FROM products p
WHERE p.name LIKE ? OR p.title LIKE ? OR p.features LIKE ? OR p.keywords LIKE ?;
```

Use with `f'%{term}%'` for each parameter.

## Pitfalls

- The `products` table has **no `slug` column**. Do not select `p.slug` — it will error.
- `features` and `keywords` are stored as JSON strings. Fetch them as-is and `json.loads()` in Python if needed.
- Product display name is `p.name`; SEO/long title is `p.title`.
- Always verify that referenced image files exist under `public/images/` before using them in an external project.
- `production-release` is a category slug, not a separate table.
