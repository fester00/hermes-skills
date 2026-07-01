# Price String Corruption During Migration

## Symptom

After running a JSX-to-SQLite migration script, product prices are corrupted:
- `'145 ₽/шт'` becomes `'145шт'`
- `'890 ₽/кг'` becomes `'890кг'`
- `'700 ₽/л'` becomes `'700л'`

## Root Cause

The regex or string-processing step that strips JSX content artifacts (like cleaning up `news-card-desc` className noise) is too aggressive. It strips ALL non-digit characters, including the space, currency symbol (`₽`), and slash separator.

Common buggy pattern in migration scripts:
```python
# WRONG — strips everything after digits
price = re.sub(r'[^\d]', '', price)  # "145 ₽/шт" → "145"
# Then concatenated with unit: f"{price}{unit}" → "145шт"
```

## Correct Pattern

Preserve the full price string exactly as in source data:
```python
# CORRECT — keep the original price string verbatim
price = product_dict.get('price', '')  # e.g., "145 ₽/шт"
# Only strip if you need the numeric part for meta tags
numeric_part = re.search(r'[\d\s]+', price).group().replace(' ', '')
```

## Post-Migration Audit Query

```sql
-- Find all corrupted prices (no space before currency symbol)
SELECT id, name, price 
FROM products 
WHERE price IS NOT NULL 
  AND price != '' 
  AND price NOT LIKE '% ₽%' 
  AND price NOT LIKE '%$%' 
  AND price != 'позапросу';
```

## Automated Fix Script

```python
import sqlite3, re

db = sqlite3.connect('pentajunior.db')
cursor = db.execute('SELECT id, price FROM products WHERE price IS NOT NULL')
updates = []
for row in cursor:
    price = row['price']
    m = re.match(r'^(\d+)(кг|шт|л|пм)$', price)
    if m:
        new_price = f"{m.group(1)} ₽/{m.group(2)}"
        updates.append((new_price, row['id']))
        print(f"  {row['id']}: {price!r} → {new_price!r}")

for new_price, pid in updates:
    db.execute('UPDATE products SET price = ? WHERE id = ?', (new_price, pid))
db.commit()
print(f'Total fixed: {len(updates)}')
db.close()
```

## Prevention

1. In the migration script, log every price transformation
2. After migration, run the audit query above before declaring success
3. Store `price_currency` and `price_unit` as separate columns in the DB — makes reconstruction trivial if the display string is lost
