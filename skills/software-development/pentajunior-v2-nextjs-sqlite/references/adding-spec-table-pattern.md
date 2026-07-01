# Adding a spec table to a product group in pentajunior-v2

Spec tables live in `spec_tables` (columns: `id TEXT PK`, `columns_json TEXT`, `rows_json TEXT`) and are referenced from `products.spec_table_id`.

## When to create a spec table
- A product group shares comparable numeric/spec attributes.
- The table is useful on both product pages and the parent category/subcategory page.

## How to create

1. Read the existing spec table format:
   ```bash
   sqlite3 pentajunior.db "SELECT columns_json, rows_json FROM spec_tables LIMIT 1;"
   ```

2. Build `columns_json` as `["Характеристика", "MARK-1", "MARK-2", ...]`.

3. Build `rows_json` as a list of objects:
   ```json
   [{"name": "Параметр", "values": {"MARK-1": "value1", "MARK-2": "value2"}}, ...]
   ```

4. Insert and link products:
   ```sql
   INSERT INTO spec_tables (id, columns_json, rows_json) VALUES ('group-id', '[...]', '[...]');
   UPDATE products SET spec_table_id = 'group-id' WHERE id IN ('id1', 'id2', ...);
   ```

5. Run the build gate:
   ```bash
   npx tsc --noEmit && rm -rf .next && npm run build
   ```

## Example from Silagerm RTV1
Table `silagerm-rtv1` compares 8 sealants with columns `1041`, `1042`, `1043`, `1044`, `1112`, `1113`, `1121`, `1142` and rows covering артикул, тип, консистенция, цвет, температура, вязкость, прочность, удлинение, твёрдость, электрическая прочность, удельное сопротивление, особенности, фасовка, цена.

## Rendering
Product detail template uses `spec_table_id` automatically. Verify by visiting `/production/[category]/[subcategory]/[product]`.
