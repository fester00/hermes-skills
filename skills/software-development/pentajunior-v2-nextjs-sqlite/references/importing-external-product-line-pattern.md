# Importing an external product line into pentajunior-v2

Pattern used for the Силагерм RTV1 line (8 neutral sealants) added to the existing Герметики category.

## When to use this pattern
- A supplier/manufacturer has a structured Markdown/HTML catalog (URL, title, H1, description, images, price tiers, specs).
- The products belong to an existing category/subcategory in pentajunior-v2.
- You need to bulk-add products, attach images, create a shared spec table, and write SEO metadata.

## Steps

1. **Read the source file**. Use `read_file` to parse the Markdown catalog. Identify the canonical fields:
   - product name / H1
   - article number
   - price (take the lowest tier as the product `price`; prefer creating full `price_tiers` if volume breaks are given)
   - URL (useful for image extraction)
   - first image URL
   - key properties / specs
   - application description

2. **Choose IDs and subcategory**. Map each product to an existing `subcategories.id`. Use slugs like `<brand>-<article>` (e.g. `silagerm-1041`). Check for collisions with existing `products.id` first.

3. **Draft SQL INSERTs for `products`**. Required fields:
   - `id`, `category_id`, `subcategory_id`, `name`, `title`
   - `price`, `price_currency='RUB'`, `price_unit` (usually `кг`, `шт`, or `м²`)
   - `pack` (human-readable: "от 1 кг", "картридж 310 мл, 0,5 кг")
   - `features` as JSON array
   - `keywords` as JSON array
   - `meta_title`, `meta_description`
   - `template_data` JSON with `intro`, `bullets`, `applications`
   - `template_type='default'`, `news=0`, `stock_info=NULL`, `spec_table_id=NULL` initially
   - `price_tiers` JSON array when the source has volume/price breaks

4. **Create a shared `spec_tables` row** (optional but recommended when products form a comparable family).
   - `id`: e.g. `silagerm-rtv1`
   - `columns_json`: `["Характеристика", "1041", "1042", ..., "1142"]`
   - `rows_json`: one row per parameter with a dict of per-column values
   - Update all imported products: `UPDATE products SET spec_table_id = 'silagerm-rtv1' WHERE id IN (...)`

5. **Download product images**.
   - Save to `public/images/<category>/<line>/` (e.g. `public/images/sealants/silagerm/`).
   - Use Python `urllib.request.urlretrieve` or `curl -L`.
   - Verify image format/size with PIL.
   - Update `products.image` to the public path (`/images/sealants/silagerm/silagerm-1041.jpg`).

6. **Update category and subcategory metadata** if the new products change the semantic scope (e.g. add "Силагерм" to the neutral sealants meta title/description).

7. **Build gate**:
   ```bash
   export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
   cd /home/natan/pentajunior-v2
   ./node_modules/.bin/tsc --noEmit
   rm -rf .next
   npm run build
   ```

8. **Commit scope**:
   ```bash
   git add pentajunior.db public/images/sealants/silagerm/
   git commit -m "Add Silagerm RTV1 sealants: products, spec table, images, price tiers"
   git push
   ```

## SEO metadata rules for imports
- `meta_title`: `<Brand> <Article> — <key benefit> | Пента Юниор` (≤ 60–70 chars).
- `meta_description`: concise, includes temperature range, application, pack size. ≤ 160 chars.
- `keywords`: 4–7 phrases mixing brand+article, generic category, and use-case terms.
- For distributor products (e.g. ТЕХГРАНТ / Силагерм), never claim manufacturing. Use "официальный дистрибьютор" or just the brand name.
