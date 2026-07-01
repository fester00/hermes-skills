# JSON-LD data audit for pentajunior-v2

Run before claiming JSON-LD is correct. Detects empty `meta_title`/`meta_description`, empty product `features`, non-numeric prices, missing images, and missing `/logo.png`.

```python
import sqlite3, json, os

DB = "/home/natan/pentajunior-v2/pentajunior.db"
PUBLIC = "/home/natan/pentajunior-v2/public"

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

issues = []

for c in cur.execute("SELECT * FROM categories").fetchall():
    if not c['meta_title']: issues.append(f"Category {c['slug']}: empty meta_title")
    if not c['meta_description']: issues.append(f"Category {c['slug']}: empty meta_description")

for s in cur.execute("SELECT subcategories.*, c.title cat FROM subcategories JOIN categories c ON subcategories.category_id = c.id").fetchall():
    if not s['meta_title']: issues.append(f"Subcategory {s['slug']}: empty meta_title")
    if not s['meta_description']: issues.append(f"Subcategory {s['slug']}: empty meta_description")

for p in cur.execute("SELECT * FROM products").fetchall():
    if not p['meta_title']: issues.append(f"Product {p['id']}: empty meta_title")
    if not p['meta_description']: issues.append(f"Product {p['id']}: empty meta_description")
    features = json.loads(p['features'] or '[]')
    if not features and not p['meta_description']:
        issues.append(f"Product {p['id']}: empty features and meta_description")
    if p['price']:
        normalized = p['price'].replace(' ', '').replace(',', '.').replace('.', '', 1)
        if not normalized.isdigit():
            issues.append(f"Product {p['id']}: non-numeric price '{p['price']}'")
    if p['image'] and not os.path.exists(PUBLIC + p['image']):
        issues.append(f"Product {p['id']}: missing image {p['image']}")

if not os.path.exists(PUBLIC + "/logo.png"):
    issues.append("Missing /logo.png (used in Organization JSON-LD)")

if issues:
    print(f"Issues found: {len(issues)}")
    for i in issues:
        print(i)
else:
    print("All JSON-LD data checks passed.")
```

After fixing issues, always re-run:
```bash
npx tsc --noEmit && rm -rf .next && npm run build
```
