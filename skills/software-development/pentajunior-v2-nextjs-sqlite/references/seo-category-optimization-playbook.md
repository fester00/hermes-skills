# Pentajunior-v2 SEO category optimization playbook

End-to-end workflow for optimizing a single production category group in pentajunior-v2 from a provided SEO brief.

## When to use
- User provides `/home/natan/workspace/<seo-brief>.md` for a category.
- Goal is to fill/update `meta_title`, `meta_description`, `page_description`, `seo_text`, `keywords` for the category, its subcategories, and its products.
- Optional: add missing products discovered on the legacy site.

## Pre-requisites
- Project path: `/home/natan/pentajunior-v2`
- Node.js v24.13.1 via nvm.
- Active branch: `master`.
- Build gate before claiming done: `./node_modules/.bin/tsc --noEmit && npm run build`.

## Step-by-step

### 1. Pull and inspect
```bash
cd /home/natan/pentajunior-v2
git pull
```

Read the SEO brief and identify:
- Recommended `title`, `meta description`, `H1`, subtitle/`page_description`, SEO-block text.
- Subcategory titles/descriptions.
- Product H1/title/description recommendations.
- Missing products (if brief says a subcategory has 0 items).

### 2. Inventory the current DB
Use Python + sqlite3 to dump the category, subcategories, and products:

```python
import sqlite3, json
DB = "/home/natan/pentajunior-v2/pentajunior.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT * FROM categories WHERE slug = ?", ("<category-slug>",))
cat = cur.fetchone()
cur.execute("SELECT * FROM subcategories WHERE category_id = ?", (cat["id"],))
subs = cur.fetchall()
for s in subs:
    cur.execute("SELECT * FROM products WHERE subcategory_id = ?", (s["id"],))
    prods = cur.fetchall()
    print(s["slug"], len(prods), "products")
```

### 3. Draft metadata
- **Category**: `meta_title` must include brand suffix (`| Пента Юниор` or `— Пента Юниор`). `meta_description` ≤160 chars. `page_description` is the subtitle under the H1.
- **Subcategories**: same rules. If brief recommends a title without brand, append the brand in the DB.
- **Products**: `meta_title` also includes brand; `meta_description` ≤160 chars; `keywords` = JSON array of 5–8 phrases from the brief + product attributes.
- **seo_text**: If the brief includes a full SEO block with H2/H3 headings (e.g., "Для каких поверхностей подходит...", "Высолы на кирпиче — как убрать?"), append it to the existing `categories.seo_text` HTML block. Do not replace a well-written existing block unless the user explicitly asks.

### Structure of `seo_text` after 2026-06-23

The category/subcategory templates render an external `<h2>` heading before injecting `seo_text`. Therefore the stored HTML must:

1. **Not contain an outer `<section>` wrapper.** The template provides the `<section>`.
2. **Not contain the first/top-level `<h2>`.** The template provides the heading.
3. **Use `<h2>` for subsection headings** (former `<h3>` elements promoted one level).
4. **Contain natural internal links** to subcategories and key products.

Template pattern:
```tsx
<section className="category-seo-text mt-5 pt-4 border-top" aria-labelledby="category-seo-heading">
  <h2 id="category-seo-heading" className="h5 mb-3">
    Подробнее о {category.title.toLowerCase()}
  </h2>
  <div dangerouslySetInnerHTML={{ __html: category.seo_text }} />
</section>
```

When updating existing `seo_text`, clean it first:
```python
import re
new_text = re.sub(r'<section[^>]*aria-label="[^"]*"[^>]*>(.*)</section>', r'\1', text, flags=re.I|re.S).strip()
new_text = re.sub(r'\s*<h2[^>]*>.*?</h2>', '', new_text, count=1, flags=re.I|re.S)
new_text = re.sub(r'</?h3', lambda m: m.group(0).replace('h3', 'h2'), new_text, flags=re.I)
```

### Internal linking inside `seo_text`

After cleaning structure, add useful internal links:
- Category `seo_text` links to its subcategories and 3–5 flagship products.
- Subcategory `seo_text` links to sibling subcategories and its own products.
- Use Bootstrap cards with icons for scannable blocks:
  ```html
  <div class="row g-4 my-1">
    <div class="col-md-6">
      <div class="h-100 p-4 rounded-3 bg-body-tertiary">
        <h2 class="h6 fw-semibold mb-2">
          <i class="bi bi-droplet-half me-2 text-primary"></i>
          <a href="/production/<cat>/<sub>" class="text-decoration-none">Подкатегория</a>
        </h2>
        <p class="mb-0 small text-body-secondary">...
          <a href="/production/<cat>/<sub>/<product>">Товар</a>
        </p>
      </div>
    </div>
  </div>
  ```
- Cross-link related categories where relevant.

### Human style for SEO text

The user prefers natural, useful prose without AI-sounding filler:
- Avoid: "stands as", "vibrant", "underscores", "testament", "delve", "crucial", "fostering", "it is important to note".
- Prefer: specific facts, concrete use cases, direct comparisons, practical warnings.
- Keep sentences varied in length; use first-person or direct address sparingly but naturally.
- End sections with a practical call to action ("Напишите менеджеру", "Смотрите ...") rather than a generic upbeat summary.

### 4. Show the draft for approval

### 4. Show the draft for approval
Print a compact table:
```python
for p in products_meta:
    print(f"{p['id']}: title={len(p['meta_title'])}, desc={len(p['meta_description'])}")
```
Ask the user to approve with `clarify` before writing to the DB.

### 5. Backup and apply
```python
import shutil, datetime
backup = f"/home/natan/pentajunior-v2/pentajunior.db.seo-<group>-backup-{datetime.datetime.now():%Y%m%d-%H%M%S}"
shutil.copy2(DB, backup)
```

Apply explicit `UPDATE` statements and check `rowcount`:
```python
cur.execute("UPDATE categories SET ... WHERE slug = ?", (...))
cur.execute("UPDATE subcategories SET ... WHERE slug = ?", (...))
cur.execute("UPDATE products SET ... WHERE id = ?", (...))
conn.commit()
```

### 6. Optional: add missing products from legacy site
If a subcategory is empty and the legacy catalog has matching items:
1. Navigate to `https://penta-junior.ru/production/<category-slug>/` and follow product links.
2. Extract product tables via browser console:
   ```js
   [...document.querySelectorAll('table tr')]
     .map(tr => [...tr.querySelectorAll('td')].map(td => td.innerText.trim().replace(/\s+/g, ' ')))
   ```
   Also collect links to identify which legacy items map to which v2 subcategories:
   ```js
   [...document.querySelectorAll('table a')].map(a => ({ text: a.innerText.trim(), href: a.href }))
   ```
3. Insert new products with explicit `category_id`, `subcategory_id`, `template_type='default'`, valid JSON arrays for `features`/`keywords`, and a `pack` value when known. If a legacy page covers several variants (e.g., monolithic + porous rolls), create one aggregated product per v2 subcategory rather than mirroring every legacy table row.
4. Generate and apply SEO metadata for each new product immediately.

### 7. Build gate
```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
./node_modules/.bin/tsc --noEmit
npm run build
```

### 8. Commit and push
```bash
git add pentajunior.db
git commit -m "SEO: meta tags for <group> category, subcategories and products"
git push
```

If new products were added, mention them in the commit message.

## Common pitfalls

### Description length
Search engines typically truncate descriptions around 155–160 characters. After drafting, always run a length check. Trim by removing low-value phrases like "Производитель Пента Юниор" or "Доставка по всей России" if the title already carries the brand.

### Title grammar
Subcategory titles appear in the UI as H1. Use grammatically correct plural/singular forms:
- `Крема для рук` → `Крем для рук` (title field can stay as is if the slug is already `hand-crem`, but the `meta_title` and `page_description` should use correct grammar).

### Brand suffix duplication
The production routes use `meta_title` verbatim when set. Store the brand in the DB value, not in the code. See `references/seo-metadata-checklist.md` § Brand suffix pitfall.

### Price as "По запросу"
If a brief notes that "По запросу" hurts CTR, set a minimum public price or remove the price field if the admin does not require it. For pentajunior-v2 the product grid may show the price column only when `price` is non-null.

### Where to put SEO-text from the brief
- Short subtitle / H1 support text → `page_description`.
- Full SEO block with H2/H3 → `seo_text` (already an HTML string in `categories.seo_text`).
- Product description recommendations → `meta_description` and/or expand `template_data` if the product detail page renders it.

## External keyword research
Yandex Wordstat requires a logged-in session. If browser auth fails, do not invent numbers. Work from the provided brief and product attributes only. Document in the session that Wordstat was skipped.
