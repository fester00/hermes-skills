# Next.js + SQLite: Dynamic Category Templates

Pattern for adding per-category product templates to a Next.js + better-sqlite3 admin panel.
Each category gets a configurable set of fields; the product edit form renders dynamically based on the category's assigned template.

## When This Applies

- Next.js 14+ App Router + better-sqlite3
- Products belong to categories
- Different categories need different product description fields (e.g. "силикон" needs `intro`/`body`/`bullets`/`application`; "масло" needs `viscosity_note`/`applications`; "разделитель" needs `composition`/`temp_range`/`method`/`surfaces`)
- Admin panel exists with product CRUD
- You want the product form to adapt automatically when the user switches category

## Schema

### New table: `category_templates`

```sql
CREATE TABLE IF NOT EXISTS category_templates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,            -- human-readable name (e.g. "Силиконовый компаунд")
  category_id INTEGER NOT NULL,  -- FK to categories (NULL = reusable across categories)
  fields_json TEXT NOT NULL,     -- JSON array of field definitions
  UNIQUE(category_id)
);
```

### Extend `categories` table

```sql
ALTER TABLE categories ADD COLUMN default_template_id INTEGER REFERENCES category_templates(id);
```

Or store template name directly:

```sql
ALTER TABLE categories ADD COLUMN default_template_type TEXT DEFAULT 'default';
```

Simpler: if you already have 6 known templates (`silikon`, `oil`, `sealant`, `release`, `grease`, `default`), store the template type name on `categories` and keep field definitions in code (`TemplateDataEditor.tsx`).

For full admin configurability, store field definitions in `category_templates`.

### Field Definition JSON

```json
[
  { "key": "intro",          "label": "Вводное описание",    "type": "textarea", "rows": 3, "placeholder": "Описание продукта" },
  { "key": "body",           "label": "Дополнительное описание", "type": "textarea", "rows": 3 },
  { "key": "bullets",        "label": "Основные свойства",   "type": "lines",    "rows": 5 },
  { "key": "application",    "label": "Применение",           "type": "textarea", "rows": 4 },
  { "key": "composition",    "label": "Состав",               "type": "textarea", "rows": 2 },
  { "key": "temp_range",     "label": "Температурный диапазон", "type": "text",   "placeholder": "от −50 до +200 °C" },
  { "key": "method",         "label": "Способ нанесения",      "type": "text",   "placeholder": "Распыление, кисть" },
  { "key": "viscosity_note", "label": "Примечание о вязкости", "type": "textarea", "rows": 2 }
]
```

**Field types:**
| Type | UI element | Stored as |
|---|---|---|
| `text` | `<input>` | string |
| `textarea` | `<textarea>` | string |
| `lines` | `<textarea>` (monospace, `whiteSpace: 'pre'`) | string[] (split on `\n`, filter empty) |
| `select` | `<select>` | string |

## Admin Panel: Dynamic Template Editor

### `TemplateDataEditor.tsx` (dynamic version)

Instead of hardcoded `TEMPLATE_FIELDS`, fetch fields from the DB based on the selected template type:

```typescript
'use client';

interface TemplateField {
  key: string;
  label: string;
  type: 'text' | 'textarea' | 'lines' | 'select';
  rows?: number;
  placeholder?: string;
  options?: string[];  // for select
}

interface Props {
  templateType: string;     // e.g. "silikon"
  templateData: Record<string, any>;
  onChange: (data: Record<string, any>) => void;
}

export default function TemplateDataEditor({ templateType, templateData, onChange }: Props) {
  const [fields, setFields] = useState<TemplateField[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/admin/templates/${templateType}`)
      .then(r => r.json())
      .then(data => {
        setFields(data.fields || []);
        setLoading(false);
      });
  }, [templateType]);

  if (loading) return <div>Загрузка полей шаблона...</div>;
  if (fields.length === 0) return <div>Нет полей для шаблона «{templateType}»</div>;

  const getValue = (key: string): string => {
    const val = templateData[key];
    if (Array.isArray(val)) return val.join('\n');
    return val === null || val === undefined ? '' : String(val);
  };

  const setValue = (key: string, raw: string, type: string) => {
    let value: any = raw;
    if (type === 'lines') {
      value = raw.split('\n').filter(s => s.trim() !== '');
    }
    const next = { ...templateData, [key]: value };
    if (value === '' || (Array.isArray(value) && value.length === 0)) {
      delete next[key];
    }
    onChange(next);
  };

  return (
    <div className="template-data-editor">
      <h6 className="text-muted mb-3">
        <i className="bi bi-file-earmark-text me-2" />
        Данные шаблона <span className="badge bg-secondary">{templateType}</span>
      </h6>
      {fields.map(field => (
        <div className="mb-3" key={field.key}>
          <label className="form-label small fw-semibold">{field.label}</label>
          {field.type === 'text' ? (
            <input className="form-control form-control-sm"
              value={getValue(field.key)}
              onChange={e => setValue(field.key, e.target.value, 'text')}
              placeholder={field.placeholder || ''}
            />
          ) : field.type === 'textarea' || field.type === 'lines' ? (
            <textarea className={`form-control form-control-sm ${field.type === 'lines' ? 'font-monospace' : ''}`}
              rows={field.rows || 3}
              value={getValue(field.key)}
              onChange={e => setValue(field.key, e.target.value, field.type)}
              placeholder={field.placeholder || ''}
              style={field.type === 'lines' ? { whiteSpace: 'pre' } : undefined}
            />
          ) : null}
          {field.type === 'lines' && (
            <small className="form-text text-muted">Каждая строка — отдельный пункт</small>
          )}
        </div>
      ))}
    </div>
  );
}
```

### API: `/api/admin/templates/[type]/route.ts`

```typescript
import { NextResponse } from 'next/server';
import { getTemplateFields } from '@/lib/db';

export async function GET(
  request: Request,
  { params }: { params: { type: string } }
) {
  const fields = getTemplateFields(params.type);
  return NextResponse.json({ fields });
}
```

### DB helper: `getTemplateFields`

```typescript
export function getTemplateFields(templateType: string): TemplateField[] {
  const row = db
    .prepare('SELECT fields_json FROM category_templates WHERE name = ?')
    .get(templateType) as any;
  if (!row) return getDefaultFields();
  return JSON.parse(row.fields_json);
}
```

### Admin: `/admin/categories` page (template assignment)

In the category edit form, add a template selector:

```tsx
<div className="col-md-6">
  <label className="form-label">Шаблон по умолчанию</label>
  <select
    className="form-select"
    value={category.default_template_type || 'default'}
    onChange={e => setFormData({ ...formData, default_template_type: e.target.value })}
  >
    <option value="default">default — Универсальный</option>
    <option value="silikon">silikon — Силиконовый компаунд</option>
    <option value="oil">oil — Силиконовое масло</option>
    <option value="sealant">sealant — Герметик</option>
    <option value="release">release — Разделительная смазка</option>
    <option value="grease">grease — Высокотемпературная смазка</option>
  </select>
  <div className="form-text text-muted">Товары в этой категории будут использовать этот шаблон по умолчанию</div>
</div>
```

When creating a new product, auto-suggest the template from the selected category:

```typescript
function getSuggestedTemplate(categories: Category[], categoryId: number): string {
  const cat = categories.find(c => c.id === categoryId);
  return cat?.default_template_type || 'default';
}
```

### Product admin form: auto-switch template on category change

```typescript
const handleCategoryChange = (product: Product, categoryId: number) => {
  const suggested = getSuggestedTemplate(categories, categoryId);
  // Reset template_data partially? Or keep existing fields?
  setEditing({ ...product, category_id: categoryId, template_type: suggested });
};
```

**Design decision:** When switching category, should `template_data` be reset or preserved?  
→ **Preserve** — the user may have typed content and only wants to switch the layout/template. The new template may have different fields; unused old keys remain in JSON harmlessly.

## Product Detail Page: "Other products in this category"

Section already works in `pentajunior-v2`. Recipe:

```tsx
// In [slug]/[productId]/page.tsx
const relatedProducts = products
  .filter(p => p.category_id === category.id && p.id !== product.id)
  .slice(0, 3);  // or 6

{relatedProducts.length > 0 && (
  <section className="product-related mt-5" aria-labelledby="related-heading">
    <h2 id="related-heading" className="product-related-title">
      <i className="bi bi-grid-3x2-gap me-2" />
      Другие товары в категории «{category.title}»
    </h2>
    <div className="row g-3 mt-3">
      {relatedProducts.map(rp => (
        <div className="col-12 col-md-6 col-lg-4" key={rp.id}>
          <Link href={`/production/${category.slug}/${rp.id}`}
                className="product-related-card d-block text-decoration-none">
            <div className="d-flex align-items-start gap-3">
              <span className="product-related-icon">
                {rp.title.substring(0, 2).toUpperCase()}
              </span>
              <div>
                <h3 className="product-related-name">{rp.title}</h3>
                {rp.price && <span className="product-related-price">{rp.price}</span>}
                <ul className="product-related-features list-unstyled mb-0">
                  {rp.features.slice(0, 2).map((f, i) => <li key={i}>{f}</li>)}
                </ul>
              </div>
            </div>
          </Link>
        </div>
      ))}
    </div>
  </section>
)}
```

### Styling (globals.css)

```css
.product-related-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
}
.product-related-card {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1rem;
  transition: transform 0.2s, box-shadow 0.2s;
}
.product-related-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.product-related-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
}
.product-related-name { font-size: 1rem; font-weight: 600; margin-bottom: 0.25rem; }
.product-related-price { color: #dc3545; font-weight: 600; font-size: 0.875rem; }
.product-related-features li { font-size: 0.8rem; color: #6c757d; }
```

## Data Migration from Hardcoded Templates

If you currently have hardcoded template fields in `TemplateDataEditor.tsx`, migrate to DB:

```typescript
// One-time migration script (run via Node.js or in API route)
const TEMPLATE_FIELDS: Record<string, any[]> = { /* your hardcoded fields */ };

for (const [name, fields] of Object.entries(TEMPLATE_FIELDS)) {
  db.prepare(`
    INSERT INTO category_templates (name, category_id, fields_json)
    VALUES (?, ?, ?)
    ON CONFLICT(category_id) DO UPDATE SET fields_json = excluded.fields_json
  `).run(name, null, JSON.stringify(fields));
}
```

Then update `TemplateDataEditor` to fetch from API instead of using `TEMPLATE_FIELDS`.

## Verification Steps

1. Create a category with `default_template_type = 'silikon'`
2. Create a product in that category — template editor should show `intro`, `body`, `bullets`, `application`
3. Switch category to `release` — template editor should show `composition`, `temp_range`, `method`, etc.
4. Fill fields, save, reload — data persists in `products.template_data`
5. Visit product page — "Другие товары в категории" section shows other products

## Common Pitfalls

- **Template fields not loading in editor** → Check that `category_templates` row exists for the selected `template_type`. Fallback to default fields if missing.
- **Template data lost on category switch** → Decide: preserve or reset. Default: preserve (old keys stay, new keys empty). Document this behavior.
- **Template editor renders too many fields** → If a category has 15+ fields, consider accordion groups or tabs in `TemplateDataEditor`.
- **Same template for multiple categories** → If `category_templates.category_id` is unique, you can't share a template. Use `category_id = NULL` for reusable templates and reference by `name`.
- **JSON parse errors in `fields_json`** → Validate on save. Use `zod` or simple schema check in the API before writing to DB.
- **"Other products" section empty** → Check that `products.category_id` matches and `p.id !== product.id`. If only one product in category, section hides (correct behavior).
- **Product page crashes with bad `template_data`** → Wrap template component rendering in try/catch, or validate `template_data` keys against expected fields before rendering.

## References

- `nextjs-sqlite-admin-panel.md` — Base admin panel recipe (middleware, auth, upload, layout)
- `nextjs-sqlite-static-generation.md` — SSG build performance and data sourcing patterns
