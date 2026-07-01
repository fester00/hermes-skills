# Price Normalization: Legacy Text Prices → Clean Numbers with `price_unit` Column

## Context
In v1, prices were stored as human-readable strings like `'145 ₽/шт'`, `'700 ₽/л'`, `'от 520 руб./кг'`.
In v2, prices are split into two columns:
- `price` — numeric string only (e.g. `'145'`, `'700'`)
- `price_unit` — unit suffix (e.g. `'шт'`, `'л'`, `'кг'`)

The display helper `formatPriceFull(price, currency, unit)` renders as: `145 ₽/шт`.

## Migration Rule

```python
import re

def normalize_price(price_str: str) -> tuple[str, str]:
    """Split legacy price string into (clean_price, unit)."""
    # Remove currency symbols and prefixes
    clean = re.sub(r'[^\d\s]', '', price_str).strip()
    clean = clean.replace(' ', '')
    
    # Extract unit from original string
    unit_match = re.search(r'/(\w+)', price_str)
    unit = unit_match.group(1) if unit_match else None
    
    return clean, unit
```

## Database UPDATE Pattern

```sql
-- After migration, normalize all prices
UPDATE products SET price = '145', price_unit = 'шт' WHERE id = 'si-m-aero';
UPDATE products SET price = '700', price_unit = 'л' WHERE id = 'penta-107';
```

## Runtime Display Helper

```ts
// lib/db.ts or lib/format.ts
export function formatPriceFull(
  price: string | number | null,
  currency: string,
  unit: string | null,
  prefix?: string
): string {
  if (!price || price === 'по запросу') return 'По запросу';
  const sym = currency === 'USD' ? '$' : '₽';
  const unitStr = unit ? `/${unit}` : '';
  return `${prefix || ''}${price} ${sym}${unitStr}`;
}
```

## Anti-patterns

| ❌ Don't | ✅ Do |
|---|---|
| Store `'145 ₽/шт'` in `price` column | Store `'145'` in `price`, `'шт'` in `price_unit` |
| Parse `price` column at render time to extract unit | Use separate `price_unit` column |
| Leave text like `'от 460 руб./кг'` in `stock_info.newPrice` | Extract `'460'` as clean number |
| Show `'145 ₽/шт ₽/шт'` because helper adds currency twice | Ensure `price` contains only digits |

## Audit Query

```sql
-- Find any prices that still contain non-digit characters
SELECT id, price FROM products WHERE price GLOB '*[^0-9]*' AND price != '' AND price != 'по запросу';
```

## `stock_info` Fix

The `stock_info` JSON column stores promo data: `{"newPrice":"...", "condition":"..."}`.
The `newPrice` value must also be a clean number string, not human text.

```python
# Fix after migration
import sqlite3, json, re

db = sqlite3.connect('pentajunior.db')
rows = db.execute("SELECT id, stock_info FROM products WHERE stock_info IS NOT NULL").fetchall()
for pid, si_raw in rows:
    si = json.loads(si_raw)
    if si.get('newPrice'):
        clean = re.sub(r'[^\d]', '', si['newPrice'])
        if clean != si['newPrice']:
            si['newPrice'] = clean
            db.execute("UPDATE products SET stock_info = ? WHERE id = ?",
                       (json.dumps(si, ensure_ascii=False), pid))
db.commit()
```
