# Cleaning literal `\n` artifacts from category descriptions

## Problem

When product/category descriptions are copied from a legacy source, escaped newlines (`\n`) sometimes survive as literal two-character strings in the SQLite database:

```
Двухкомпонентный жидкий и литьевой силикон для изготовления форм. \n
Платиновый и оловянный катализатор. Для гипса, смол, свечей, мыла. \n
Полиуретановый компаунд и жидкий пластик.
```

On the rendered page these show as visible backslashes or awkward line breaks.

## Where to look

The artifacts are usually in:
- `categories.meta_description`
- `categories.page_description`
- less commonly in `products.meta_description` or `template_data` string fields

## Detection

Use a direct SQL search because Python `\\` escaping can be confusing:

```python
import sqlite3, json

conn = sqlite3.connect('pentajunior.db')
cur = conn.cursor()

# simple columns
cur.execute("SELECT id, slug, meta_description, page_description FROM categories")
for cat_id, slug, meta, page in cur.fetchall():
    if meta and '\\' in meta:
        print(cat_id, slug, 'meta', repr(meta[:200]))
    if page and '\\' in page:
        print(cat_id, slug, 'page', repr(page[:200]))

# products
cur.execute("SELECT id, name, meta_description FROM products")
for pid, name, meta in cur.fetchall():
    if meta and '\\' in meta:
        print(pid, name, repr(meta[:200]))

conn.close()
```

## Fix

Replace literal `\n` with a single space in `meta_description` (SEO metadata should be compact), and with a real newline in `page_description` (it is rendered on the page and line breaks are acceptable):

```python
new_meta = meta.replace('\\n', ' ').replace('\\', ' ')
new_page = page.replace('\\n', '\n').replace('\\', '')
# collapse multiple spaces
new_meta = ' '.join(new_meta.split())
```

Update the database and commit the `.db` file.

## Verification

After `npm run build`, grep the generated HTML:

```bash
grep -o -P '.{0,60}Платиновый.{0,60}' \
  .next/server/app/production/silikonovye-i-poliuretanovye-kompaundy.html | head
```

No backslashes should appear.

## Related

- `nextjs-dev-server-cache-invalidation.md` — if the page still shows backslashes after the DB fix, the dev server is serving the old `.next` output.
