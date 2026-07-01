# Spec / comparison tables: from legacy TSX to admin-editable SQLite

Product-family comparison tables (e.g. "Юнисил 9110 / 9120 / 9131" or "Силиконовые масла ПМС") appear on detail pages under "Технические характеристики". In the old project these tables were hardcoded in `src/components/UI/Tables/SpecTables.tsx`. In the new project they live in the SQLite table `spec_tables` and can be edited through `/admin/spec-tables`.

## Schema

```sql
CREATE TABLE spec_tables (
    id TEXT PRIMARY KEY,
    columns_json TEXT,  -- ["МАРКА", "9110", "9120", "9131"]
    rows_json TEXT      -- [{"name":"Цвет","values":{"9110":"зелёный","9120":"жёлтый","9131":"красный"}}]
);
```

The first column is always the row label. Remaining columns are product identifiers or product names.

Products link to a table by `spec_table_id`:

```sql
CREATE TABLE products (
    id TEXT PRIMARY KEY,
    spec_table_id TEXT REFERENCES spec_tables(id),
    template_data TEXT
);
```

`spec_table_id` is **not** the product's own `id`. It is the family key shared by several products in the same line.

## When a product needs a spec table

- Multiple similar products in one category share a comparison table.
- A product page must highlight the current product inside that table.
- A single product may also have a one-row table (column = its own name).

## Migrating tables from old `SpecTables.tsx`

The legacy file typically exports either:

1. A single big object keyed by table ID:
   ```tsx
   export const specTables = {
     'unisil-9xxx': {
       columns: ['МАРКА', '9110', '9120', '9131'],
       rows: [
         { name: 'Цвет', values: { '9110': 'зелёный', ... } }
       ]
     }
   };
   ```
2. Multiple independent arrays/objects that map 1:1 to page slugs.

### Extraction recipe

```python
import re, json, sqlite3

# Parse the TSX file manually or with a small regex pipeline.
# Goal: produce (table_id, columns, rows) tuples.

def extract_table_id_from_marker(text: str, default: str) -> str:
    # Example: export const unisil9xxx = ...
    m = re.search(r'export\s+const\s+(\w+)\s*=', text)
    return m.group(1) if m else default

def import_spec_tables(db_path: str, tables: dict[str, dict]):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for tid, table in tables.items():
        columns = table['columns']
        rows = [
            {'name': r['name'], 'values': r.get('values', {})}
            for r in table['rows']
        ]
        cur.execute(
            '''INSERT INTO spec_tables (id, columns_json, rows_json)
               VALUES (?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
                 columns_json=excluded.columns_json,
                 rows_json=excluded.rows_json''',
            (tid, json.dumps(columns, ensure_ascii=False), json.dumps(rows, ensure_ascii=False))
        )
    conn.commit()
    conn.close()
```

### Mapping `spec_table_id` to products

After importing tables, assign `spec_table_id` to each product based on its family line:

```python
family_map = {
    'unisil-9110': 'unisil-9xxx',
    'unisil-9120': 'unisil-9xxx',
    'unisil-9131': 'unisil-9xxx',
    'unisil-9231': 'unisil-92xx',
    'unisil-9331': 'unisil-93xx',
}
```

Run an update per product. If a product does not belong to a known family, leave `spec_table_id` NULL — do not invent an ID that has no table.

## Admin editor

Create `/admin/spec-tables/page.tsx` with local state for columns and rows. Keep the UI simple:

- List all tables.
- Edit table ID (only when creating; don't rename existing tables without updating `products.spec_table_id`).
- Add/remove columns.
- Add/remove rows.
- Edit any cell.
- Save via PUT `/api/admin/spec-tables/[id]`.

API endpoints needed:

```
GET    /api/admin/spec-tables        → list {id, columns_json, rows_json}
POST   /api/admin/spec-tables        → create new table
GET    /api/admin/spec-tables/[id]   → single table
PUT    /api/admin/spec-tables/[id]   → update columns + rows
DELETE /api/admin/spec-tables/[id]   → delete table
```

### Cascading delete note

Do **not** cascade-delete a spec table when a product is deleted. One table can be shared by many products. Instead, delete only the `spec_table_id` reference from the product row, or leave it as an orphan to clean up later.

### Product form integration

On the product edit page, add a select for `spec_table_id` populated from `/api/admin/spec-tables`. Allow clearing it (`NULL`). When the user picks a table, save the ID with the product, not with the template data.

## Public page rendering

In `ProductCard.tsx` or the detail page:

```tsx
{product.spec_table_id && (
  <section aria-labelledby="specs-heading">
    <h2 id="specs-heading">Технические характеристики</h2>
    <TableIncluder id={product.spec_table_id} currentProductName={product.name} />
  </section>
)}
```

`TableIncluder` reads the table from SQLite at build time for SSG, parses JSON, and renders a standard HTML `<table>`. The current product is highlighted by matching its name against column headers.

## Verification checklist

- [ ] All products that need a table have a non-null `spec_table_id`.
- [ ] Every referenced `spec_table_id` exists in `spec_tables`.
- [ ] No orphan tables that are not referenced by any product (optional — some may be kept for future use).
- [ ] Admin `/admin/spec-tables` loads and edits tables without errors.
- [ ] Public pages render tables with correct headers and current-product highlighting.
- [ ] `tsc --noEmit` passes after adding API types.

## Common pitfalls

| Pitfall | Prevention |
|---|---|
| Using product `id` as `spec_table_id` for multi-product families | Family key should be shared (e.g. `unisil-9xxx`), not `unisil-9110`. |
| Renaming `spec_tables.id` without updating `products.spec_table_id` | Treat table IDs as stable references; rename only via a migration that updates both tables. |
| Cascading delete of spec table on product delete | Remove the reference only; keep the table if other products use it. |
| Storing table data inside `template_data` | Keep tables separate in `spec_tables`; easier to edit and reuse. |
| Forgetting to assign `spec_table_id` after importing tables | Run a mapping pass per category and verify with `SELECT id, spec_table_id FROM products WHERE category_id = ?`. |

## See also

- `references/template-text-markdown-and-sync.md` — bulk-importing `template_data` from the same old project.
- `references/product-template-mapping.md` — category → template type mapping.
