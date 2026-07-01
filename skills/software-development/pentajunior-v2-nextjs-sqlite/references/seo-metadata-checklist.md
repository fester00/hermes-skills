# Pentajunior-v2 SEO metadata checklist

## Quick entity map

```sql
-- Category metadata
SELECT id, slug, title, meta_title, meta_description, page_description
FROM categories
WHERE slug = 'silikon-dlya-zalivki-form';

-- Subcategory metadata for a category
SELECT id, slug, title, meta_title, meta_description, page_description
FROM subcategories
WHERE category_id = ?
ORDER BY sort_order, id;

-- Product metadata for a subcategory
SELECT id, name, title, meta_title, meta_description, keywords, features
FROM products
WHERE subcategory_id = ?
ORDER BY id;
```

## Length limits used by frontend
- `meta_description`: target **140–160** chars; frontend truncates at **160** (adds `...`).
- `title` (rendered): keep under **60–70** chars so search engines do not truncate.
- `keywords` (product): JSON array of 5–8 phrases; subcategory page uses first 5 product keywords.

## Stored title format
For categories and subcategories, store the complete rendered title including the brand suffix, e.g.:
```
Силиконовые трубки, шланги и пластины — купить от производителя | Пента Юниор
```
For products, the current frontend uses `product.meta_title` verbatim, so the DB value must also include the brand:
```
Силиконовая трубка — купить пищевую и медицинскую на отрез | Пента Юниор
```
The code only appends `— Пента Юниор` when `meta_title` is empty.

## Update statements (template)

```sql
-- Category
UPDATE categories
SET meta_title = ?, meta_description = ?, page_description = ?
WHERE slug = 'silikon-dlya-zalivki-form';

-- Subcategory
UPDATE subcategories
SET meta_title = ?, meta_description = ?, page_description = ?
WHERE slug = ?;

-- Product
UPDATE products
SET meta_title = ?, meta_description = ?, keywords = ?
WHERE id = ?;
```

## Verification
1. Run `tsc --noEmit && rm -rf .next && npm run build`.
2. Start v2 on port 3001.
3. Inspect page source for canonical URL, `<title>`, and `<meta name="description">`.
4. Check JSON-LD breadcrumb / product / collection structure.
5. **Check `/production` category cards:** verify each `category.image` points to an existing file in `public/images/` and renders without a placeholder.

## JSON-LD audit script

Run the audit before claiming JSON-LD is correct:

```python
import sqlite3, json, os
DB = "/home/natan/pentajunior-v2/pentajunior.db"
PUBLIC = "/home/natan/pentajunior-v2/public"
conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row; cur = conn.cursor()
issues = []

def is_num(v): return not v or str(v).replace(" ","").replace(",",".").replace(".","",1).isdigit()

for c in cur.execute("SELECT slug, title, meta_title, meta_description FROM categories").fetchall():
    if not c['meta_title']: issues.append(f"Category {c['slug']}: empty meta_title")
    if not c['meta_description']: issues.append(f"Category {c['slug']}: empty meta_description")

for s in cur.execute("SELECT slug, title, meta_title, meta_description FROM subcategories").fetchall():
    if not s['meta_title']: issues.append(f"Subcategory {s['slug']}: empty meta_title")
    if not s['meta_description']: issues.append(f"Subcategory {s['slug']}: empty meta_description")

for p in cur.execute("SELECT id, name, meta_title, meta_description, price, features, image, stock_info FROM products").fetchall():
    if not p['meta_title']: issues.append(f"Product {p['id']}: empty meta_title")
    if not p['meta_description']: issues.append(f"Product {p['id']}: empty meta_description")
    if not json.loads(p['features'] or '[]') and not p['meta_description']:
        issues.append(f"Product {p['id']}: empty features and meta_description")
    if p['price'] and not is_num(p['price']): issues.append(f"Product {p['id']}: bad price {p['price']}")
    si = json.loads(p['stock_info'] or '{}')
    if si.get('newPrice') and not is_num(si['newPrice']): issues.append(f"Product {p['id']}: bad newPrice {si['newPrice']}")
    if p['image'] and not os.path.exists(PUBLIC + p['image']): issues.append(f"Product {p['id']}: missing image {p['image']}")

if not os.path.exists(PUBLIC + "/logo.png"): issues.append("/logo.png missing")

print("Issues:", len(issues))
for i in issues: print(i)
```

Key fixes to apply when the audit finds problems:
- Fill empty `meta_title`/`meta_description` for any category/subcategory/product.
- Restore missing `features` or ensure `meta_description` exists as fallback.
- Create `/logo.png` if missing (symlink to `/images/fav.svg` or another existing logo file).
- Clean `price`/`newPrice` to numeric strings (remove spaces, replace comma with dot).

## Brand suffix pitfall

Each production route's `generateMetadata` must treat `meta_title` as the final, rendered title:

- If `meta_title` is set → use it verbatim.
- If `meta_title` is empty → fall back to `<entity.title> — Пента Юниор`.

Do **not** write code like `title: `${meta_title} — Пента Юниор`` when `meta_title` already contains the brand. This produced `Силикон для заливки форм — купить двухкомпонентный жидкий силикон | Пента Юниор — Пента Юниор` for category pages and would have done the same for products.

Current code after the fix:
- `/production/[category]/page.tsx`: `title = category.meta_title || `${category.title} — Пента Юниор`; return { title }`
- `/production/[category]/[subcategory]/page.tsx`: `title = subcategory.meta_title || `${subcategory.title} — Пента Юниор`; return { title }`
- `/production/[category]/[subcategory]/[product]/page.tsx`: `title = product.meta_title || `${product.title} — Пента Юниор`; return { title }`

When editing these pages, preserve this pattern.

## Gotchas
- `product.meta_description` fallback uses `product.title`, which may duplicate the `<h1>`; always prefer a custom description.
- `keywords` column is JSON text; wrap updates in `json.dumps([...])` from Python or a valid JSON array from SQL tools.
- Verify the rendered `<title>` in the browser after build; do not rely only on the DB value.
## Composing product meta from a category SEO brief when Wordstat is unavailable

When the user provides a Wordstat/Wordcraft brief for the category but the research tool is not accessible, derive product metadata from the brief's keyword clusters plus the product's own attributes.

### Input data to collect per product
1. Subcategory cluster (e.g., "платиновый силикон", "оловянный силикон", "полиуретан для заливки").
2. Hardness / grade if present in the title or features (e.g., `2 Шор А`, `70 Шор D`).
3. Color or certification if distinctive (e.g., "прозрачный", "телесный", "FDA/BfR").
4. Primary applications from title or features (e.g., "кукол", "бетона", "шоколада", "ювелирных форм").

### Template formulas
- **Title**: `<Name> — <cluster>, <hardness><, color/cert> | Пента Юниор`
  - Keep ≤ 70 chars; truncate if necessary.
  - For polyurethane: `<Name> — полиуретан для заливки<, hardness> | Пента Юниор`
  - For non-silicone fillers: `<Name> — <what it is> для силикона и смолы | Пента Юниор`
- **Description**: `<Name> — <cluster short> для <applications>. Двухкомпонентный компаунд от производителя. Купить от 1 кг, доставка по России.`
  - Keep ≤ 160 chars; truncate with `...`.
- **Keywords**: 5–6 phrases. Always include the subcategory cluster + "для форм" / "для заливки" variants + a specific application keyword from the brief.

### Known high-value clusters for pentajunior-v2
These clusters came from the `silikon-dlya-zalivki-form` brief and are safe defaults for similar products:
- General: `"силикон для форм"`, `"силикон для заливки форм"`, `"двухкомпонентный силикон"`, `"силиконовый компаунд"`
- Platinum-specific: `"платиновый силикон"`
- Tin-specific: `"оловянный силикон"`, `"силикон на оловянной основе"`
- Polyurethane: `"полиуретан для заливки"`, `"жидкий пластик"`, `"полиуретановый компаунд"`
- Applications: `"силикон для кукол"`, `"силикон для бетона"`, `"силикон для гипса"`, `"силикон для мыла"`, `"силикон для шоколада"`, `"силикон для ювелирных форм"`

### Automation recipe
Use Python with `sqlite3` to bulk-draft and bulk-apply:
1. Backup DB: `cp pentajunior.db pentajunior.db.seo-<group>-backup-<timestamp>`.
2. Read all products in the target category via `subcategory_id` joins.
3. Build title/description/keywords with the formulas above.
4. Print a preview table with title/description lengths; ask the user for approval.
5. Apply with explicit `UPDATE ... WHERE id = ?` and check `rowcount == 1`.
6. Run the build gate and restart the v2 server before visual verification.
7. `git add pentajunior.db && git commit -m "SEO: meta tags for <group>" && git push`.

## Yandex Wordstat access
- URL: `https://wordstat.yandex.ru/`
- Requires a logged-in Yandex ID session (`Session_id` / `sessionid2` cookies). If the browser redirects to `passport.yandex.ru`, stop and ask the user for credentials or a valid `Session_id` cookie.
- Do not fabricate search-volume numbers. If the tool is unavailable, proceed from the provided brief and the product attribute formulas above.

## Where to place content from the SEO brief

SEO briefs often contain several text blocks. Map them to the correct DB fields:

| Brief element | DB field | Notes |
| :-- | :-- | :-- |
| Recommended `<title>` | `meta_title` | Must include brand suffix verbatim. |
| Recommended `<meta description>` | `meta_description` | Keep ≤160 chars. |
| Subtitle under H1 | `page_description` | Plain text, 1–2 sentences. |
| Full SEO block with H2/H3 | `seo_text` | Append to existing HTML inside the `<section>`. |
| Product H1/title recommendation | `meta_title` and `title` | `title` appears in catalog cards; `meta_title` in `<title>` tag. |
| Product description recommendation | `meta_description` and `template_data` | `meta_description` ≤160; expand in `template_data` if the detail page renders it. |
| Package sizes / фасовка | `pack` | Free-text field shown on product card. |
| Application bullet list | `template_data` or `features` JSON | `features` renders as attribute chips; `template_data` renders as structured body text. |

When a brief recommends an H1 like `Крем для рук защитный силиконовый` but the DB `title` of the subcategory is `Крема для рук` (legacy slug `hand-crem`), update `meta_title` and `page_description` to the grammatically correct form; do not rename the slug unless the user explicitly asks for it.

## Grammar / title quality

`meta_title` and `page_description` are user-visible and search-visible. Fix obvious grammar errors even when the underlying `title` or slug is legacy:
- `Крема для рук` → `Крем для рук`
- `Гидрофобизатоы` → `Гидрофобизаторы` (typo in DB title)

The slug and admin panel can keep the old value to avoid breaking URLs; the displayed SEO metadata should be correct.

### Adding missing products from the legacy site
If a subcategory is empty but the legacy catalog lists matching items:
1. Open `https://penta-junior.ru/production/<category-slug>/` and follow product links.
2. Extract the product table via browser console: `[...document.querySelectorAll('table tr')].map(tr => [...tr.querySelectorAll('td')].map(td => td.innerText.trim().replace(/\s+/g, ' ')))`.
3. Insert new products with explicit `category_id`, `subcategory_id`, valid JSON arrays in `features`/`keywords`, `template_type: 'default'`, and a `pack` value when known.
4. Generate SEO metadata for the new product before or immediately after insertion.
5. Update the subcategory `meta_title`/`meta_description`/`page_description` to mention the new product variant so the subcategory page is accurate.
