# Case-insensitive Cyrillic search with better-sqlite3

## Symptom

Product search on a Next.js + better-sqlite3 site returns no results when the
user types lowercase Cyrillic, e.g. `юни` or `юн`, but works when the same word
is capitalized (`Юни`, `Юн`).

## Root cause

SQLite's default `LIKE` collation is only ASCII case-insensitive. For Cyrillic
(and other non-ASCII scripts) `LOWER('Юнисил')` and `LOWER('юни')` may not
reduce to the same bytes because the default SQLite build lacks ICU support or
case-folding tables. Therefore:

```sql
SELECT * FROM products WHERE name LIKE '%юни%'
```

does **not** match `Юнисил® 9110`.

## Fix for small catalogs

For catalogs with hundreds or fewer products, move the search into JavaScript
and rely on the Unicode-aware `String.prototype.toLowerCase()`:

```ts
// src/lib/db.ts
export function searchProducts(query: string): Product[] {
  const q = query.toLowerCase().trim();
  if (!q) return [];

  return getAllProducts().filter((p) => {
    const haystack = [
      p.name,
      p.title,
      p.meta_description,
      p.pack,
      ...p.features,
      ...p.keywords,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();
    return haystack.includes(q);
  });
}
```

Trade-offs:
- **Pros:** Correct Unicode case folding; trivial to extend to `features`,
  `keywords`, `pack`; no DB migration; works on any SQLite build.
- **Cons:** Loads the full product table into memory. Acceptable for ~1k products,
  but becomes inefficient for very large catalogs.

## Fix for large catalogs

If the product list grows large, prefer a database-level solution:

1. Add a normalized search column:
   ```sql
   ALTER TABLE products ADD COLUMN search_text TEXT;
   ```
2. Populate it whenever a product is created/updated:
   ```ts
   const searchText = [name, title, meta_description, pack, ...features, ...keywords]
     .filter(Boolean)
     .join(' ')
     .toLowerCase();
   ```
3. Query with equality or `LIKE` on the normalized column:
   ```sql
   SELECT * FROM products WHERE search_text LIKE ?
   ```

Alternatively, compile SQLite with ICU and use `COLLATE NOCASE`, or use a
full-text search extension such as FTS5 with a custom tokenizer.

## Verification

1. Search lowercase: `юни` should return `Юнисил` products.
2. Search mixed case: `ЮниКаст` should return `unicast-*` products if the title
   contains the Cyrillic brand name.
3. Search brand prefix: `юн` should still match.

## Prevention

Never rely on `LIKE` alone for user-facing text search in languages with
non-ASCII characters. Always normalize the query and the indexed text in a way
that matches the runtime's Unicode support.
