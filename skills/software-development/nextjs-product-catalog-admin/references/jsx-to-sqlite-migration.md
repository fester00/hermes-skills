# JSX-to-SQLite Migration: Extraction Recipes

## Pattern: Parsing JSX description blocks into template_data JSON

### Input (from products.tsx)
```tsx
description: (
  <>
    <p className="news-card-desc mb-3"><strong>Юнисил® 9110</strong> — двухкомпонентный...</p>
    <p className="news-card-desc mb-3">Отличается низкой вязкостью...</p>
    <ul>
      <li>Точно воспроизводит детали</li>
      <li>Легко смешивается 100:3</li>
    </ul>
  </>
),
```

### Output (template_data JSON in SQLite)
```json
{
  "intro": "двухкомпонентный силиконовый компаунд для изготовления гибких литьевых форм при многократном тиражировании изделий",
  "body": "Отличается низкой вязкостью (12 000 мПа·с) и отличной текучестью. Идеален для начинающих мастеров",
  "bullets": [
    "Точно воспроизводит мелкие детали рельефа",
    "Легко смешивается в пропорции 100:3",
    "Время отверждения — 8 часов при комнатной температуре",
    "Рабочая температура форм до +200°C"
  ]
}
```

## Extraction Rules

### 1. Strip HTML tags (keep only text content)
```python
import re

def strip_jsx_tags(text: str) -> str:
    # Remove <strong>, <em>, <b>, <i> tags but keep their content
    text = re.sub(r'<(strong|em|b|i)>(.*?)</\1>', r'\2', text)
    # Remove self-closing tags like <br />, <hr />
    text = re.sub(r'<(br|hr)\s*/?>', ' ', text)
    # Remove other tags entirely
    text = re.sub(r'<[^>]+>', '', text)
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text
```

### 2. Split into sections
```
First <p> after <strong>NAME</strong> → intro (text after "—" or first sentence)
Subsequent <p> without <strong> → body
<ul><li> items → bullets array
```

### 3. Handle edge cases

| Case | Action |
|---|---|
| Only one <p> | intro = full text, no body |
| No <ul> | bullets = [] or omitted |
| <p> with inline <strong> | Strip tags, keep text |
| Application block separate | Separate template_data field |
| **Name already in intro** | Do NOT prepend `<strong>{name}</strong> — ` in template — leads to empty name display if hydration fails or name field is missing. Template should render `{intro}` directly, with the name already inside the intro string. See Pitfall below. |

### 3a. Template Duplication Pitfall

**Problem:** Template component prepends the product name:
```tsx
// WRONG — causes empty "—" on live site if name is missing
<p><strong>{name}</strong> — {templateData.intro}</p>
```
If `name` is undefined or the template receives `templateData.intro` that already starts with the name, the output becomes: ` — универсальная смазка...` (name missing before dash).

**Fix:** Store the name inside `template_data.intro` during migration:
```json
{
  "intro": "Si-M® — универсальная силиконовая смазка-спрей для промышленного и бытового применения..."
}
```

And render directly:
```tsx
// CORRECT — name is part of the intro string
<p>{templateData.intro}</p>
```

This also handles cases where the product name contains a ® symbol or formatting that would be awkward as a separate JSX expression.

## Spec Table Migration

### From SpecTables.tsx
```tsx
const specTables: Record<string, SpecTable> = {
  "unisil-9xxx": {
    id: "unisil-9xxx",
    columns: ["МАРКА", "9110", "9120", "9131", "9145"],
    rows: [
      { name: "Цвет", values: { "9110": "зелёный", ... }},
      ...
    ]
  }
};
```

### To SQLite
```sql
INSERT INTO spec_tables (id, columns_json, rows_json) VALUES (
  'unisil-9xxx',
  '["МАРКА","9110","9120","9131","9145"]',
  '[{"name":"Цвет","values":{"9110":"зелёный",...}},...]'
);
```

## Category-to-Template Mapping

```typescript
const categoryTemplates: Record<number, string> = {
  1:  'silikon',      // silikonovye-i-poliuretanovye-kompaundy
  2:  'smazka',       // razdelitelnye-smazki
  3:  'sealant',      // silikonovye-germetiki
  4:  'oil',          // masla-pms
  5:  'kovrik',       // antiprigarnye-kovriki
  6:  'penogasitel',  // penogasiteli
  7:  'gidrofob',     // gidrofobizatory
  8:  'smazka',       // smazki
  9:  'krem',         // kosmeticheskie-krema
  10: 'techmol',      // tekhnologicheskie-zhidkosti
  11: 'silicon',      // silicon-products
  12: 'elastomer',    // silikonovye-elastomery
};
```

## Full Migration Script Structure

```python
# migrate.py
# 1. Parse products.tsx using regex or TypeScript AST
# 2. Parse SpecTables.tsx
# 3. Create SQLite DB
# 4. Insert categories from categories.tsx
# 5. Insert products with template_data JSON
# 6. Insert spec_tables
# 7. Verify row counts match original
```

## Category-by-category content backfill

When the initial migration already populated `intro`/`body` but left `application`/instructional fields empty, backfill one category at a time:

1. Extract `application` JSX for the target `categoryId` from v1 `products.tsx`.
2. Convert JSX to markdown and split by bold headings into the correct v2 fields (`applications`, `method`, `important_note`, `recommendations`, `mixing_steps`, `surface_prep`, `degassing`, `safety`).
3. For categories with shared instructions (e.g. RTV-2 silicones), inject the same instructional blocks into every product in the category.
4. Clear the legacy `application` field after splitting to avoid duplicate sections.
5. Commit the DB change before moving to the next category to keep commits atomic.

See `references/v1-application-block-mapping.md` for the splitting recipe and atomic-commit checklist.

## Verification

After migration:
- products count: `SELECT COUNT(*) FROM products` → should match original
- spec_tables count: `SELECT COUNT(*) FROM spec_tables` → should match unique specTableId values
- products with description: `SELECT COUNT(*) FROM products WHERE json_extract(template_data, '$.intro') IS NOT NULL`
- Check specific product: `SELECT template_data FROM products WHERE id = 'unisil-9110'`
