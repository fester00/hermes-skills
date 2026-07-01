# Template Data Editor Pattern: Dynamic Field Editor per Template Type

## Context

In a Next.js + SQLite SSG project, the admin panel needs to edit `template_data` JSON per product. Different product categories (template types) require **completely different fields** — a release agent needs `composition` and `temp_range`, while a silicone compound needs `application` only.

A single static form is either too sparse (missing fields) or too bloated (irrelevant fields). The solution is a **dynamic field editor** that changes its inputs based on the selected `template_type`.

## Architecture (v2: DB-Driven)

```
SQLite                            Admin API                 TemplateDataEditor
├─ category_templates
│  ├─ name (TEXT, PK)            GET /api/admin/templates   useEffect(categoryId)
│  ├─ category_id (FK)            ?categoryId=1              → fetch fields
│  └─ fields_json (TEXT)          ?name=silikon              → render inputs
│     ├─ [{key,label,type,...}]
│     └─ ...
│
└─ categories
   ├─ template_type (TEXT)       GET /api/admin/categories  → product form
   └─ id (PK)
```

**Key upgrade from v1:** Field definitions are stored in the database, not hardcoded. When an admin changes a product's category, the editor automatically loads the correct field set via API.

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS category_templates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
  fields_json TEXT NOT NULL DEFAULT '[]',
  created_at TEXT DEFAULT (datetime('now'))
);

-- Link categories to templates
ALTER TABLE categories ADD COLUMN template_type TEXT DEFAULT 'default';

-- Populate templates
INSERT INTO category_templates (name, category_id, fields_json) VALUES
('silikon', 1, '[{"key":"intro","label":"Вводное описание","type":"textarea","rows":3},{"key":"body","label":"Дополнительное описание","type":"textarea","rows":3},{"key":"bullets","label":"Основные свойства","type":"lines","rows":5},{"key":"application","label":"Применение","type":"textarea","rows":4}]'),
('release', 2, '[{"key":"intro","label":"Вводное описание","type":"textarea","rows":3},{"key":"composition","label":"Состав","type":"textarea","rows":2},{"key":"body","label":"Дополнительное описание","type":"textarea","rows":3},{"key":"bullets","label":"Основные свойства","type":"lines","rows":5},{"key":"properties","label":"Особенности","type":"lines","rows":4},{"key":"temp_range","label":"Температурный диапазон","type":"text"},{"key":"method","label":"Способ нанесения","type":"text"},{"key":"surfaces","label":"Поверхности","type":"text"},{"key":"usage","label":"Использование","type":"text"},{"key":"shelf_life","label":"Срок годности","type":"text"},{"key":"tu","label":"ТУ","type":"text"},{"key":"application_industrial","label":"Промышленное применение","type":"lines","rows":4},{"key":"application_domestic","label":"Бытовое применение","type":"textarea","rows":2}]');

-- Link categories to templates
UPDATE categories SET template_type = 'silikon' WHERE slug = 'silikonovye-i-poliuretanovye-kompaundy';
UPDATE categories SET template_type = 'release' WHERE slug = 'production-release';
```

## API: Templates

```ts
// src/app/api/admin/templates/route.ts
import { getTemplateByName, getTemplateByCategoryId } from '@/lib/db';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const name = searchParams.get('name');
  const categoryId = searchParams.get('categoryId');

  if (categoryId) {
    const template = getTemplateByCategoryId(Number(categoryId));
    return NextResponse.json({ data: template });
  }
  if (name) {
    const template = getTemplateByName(name);
    return NextResponse.json({ data: template });
  }
  // ... list all
}
```

## Component: DB-Driven TemplateDataEditor (v2)

```tsx
// src/components/admin/TemplateDataEditor.tsx
'use client';
import { useState, useEffect } from 'react';

interface TemplateField {
  key: string;
  label: string;
  type: 'text' | 'textarea' | 'lines' | 'select';
  rows?: number;
  placeholder?: string;
  options?: string[];
}

interface Props {
  templateType: string;
  categoryId: number;
  templateData: Record<string, any>;
  onChange: (data: Record<string, any>) => void;
}

export default function TemplateDataEditor({ templateType, categoryId, templateData, onChange }: Props) {
  const [fields, setFields] = useState<TemplateField[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTemplate() {
      setLoading(true);
      try {
        // Primary: fetch by categoryId (most accurate — links category → template)
        let res = await fetch(`/api/admin/templates?categoryId=${categoryId}`);
        let data = await res.json();

        // Fallback: by template name (for orphaned/global templates)
        if (!data.data && templateType) {
          res = await fetch(`/api/admin/templates?name=${encodeURIComponent(templateType)}`);
          data = await res.json();
        }

        if (data.data?.fields) {
          setFields(data.data.fields);
        } else {
          // Fallback: hardcoded field definitions if API not yet migrated
          // (keep the fallback map from v1 for graceful degradation)
          setFields(fallbackFields[templateType] || fallbackFields['default']);
        }
      } finally {
        setLoading(false);
      }
    }
    if (categoryId) {
      loadTemplate();
    }
  }, [templateType, categoryId]);

  const getValue = (key: string): string => {
    const val = templateData[key];
    if (Array.isArray(val)) return val.join('\n');
    return String(val ?? '');
  };

  const setValue = (key: string, raw: string, fieldType: string) => {
    let value: any = raw;
    if (fieldType === 'lines') {
      value = raw.split('\n').filter((s) => s.trim() !== '');
    }
    const next = { ...templateData, [key]: value };
    if (value === '' || (Array.isArray(value) && value.length === 0)) {
      delete next[key];
    }
    onChange(next);
  };

  if (loading) return <div className="text-center"><div className="spinner-border spinner-border-sm" /></div>;

  return (
    <div className="template-data-editor">
      <h6 className="text-muted mb-3">
        Данные шаблона <span className="badge bg-secondary">{templateType}</span>
      </h6>
      {fields.map((field) => (
        <div className="mb-3" key={field.key}>
          <label className="form-label small fw-semibold">{field.label}</label>
          {field.type === 'text' && (
            <input
              className="form-control form-control-sm"
              value={getValue(field.key)}
              onChange={(e) => setValue(field.key, e.target.value, field.type)}
              placeholder={field.placeholder || ''}
            />
          )}
          {field.type === 'select' && field.options && (
            <select
              className="form-select form-select-sm"
              value={getValue(field.key)}
              onChange={(e) => setValue(field.key, e.target.value, field.type)}
            >
              <option value="">— выберите —</option>
              {field.options.map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          )}
          {(field.type === 'textarea' || field.type === 'lines') && (
            <textarea
              className={`form-control form-control-sm ${field.type === 'lines' ? 'lines-textarea font-monospace' : ''}`}
              rows={field.rows || 2}
              value={getValue(field.key)}
              onChange={(e) => setValue(field.key, e.target.value, field.type)}
              onKeyDown={(e) => {
                // Allow Enter key in textarea to insert newlines
                if (e.key === 'Enter') {
                  e.stopPropagation();
                }
              }}
              placeholder={field.placeholder || ''}
              style={{ whiteSpace: field.type === 'lines' ? 'pre-wrap' : undefined }}
            />
          )}
          {field.type === 'lines' && <small className="form-text text-muted">Каждая строка — отдельный пункт</small>}
        </div>
      ))}
    </div>
  );
}

const fallbackFields: Record<string, TemplateField[]> = {
  release: [
    { key: 'intro', label: 'Вводное описание', type: 'textarea', rows: 3 },
    { key: 'composition', label: 'Состав', type: 'textarea', rows: 2 },
    { key: 'body', label: 'Дополнительное описание', type: 'textarea', rows: 3 },
    { key: 'bullets', label: 'Основные свойства (по строке)', type: 'lines', rows: 5 },
    { key: 'properties', label: 'Особенности (по строке)', type: 'lines', rows: 3 },
    { key: 'temp_range', label: 'Температурный диапазон', type: 'text' },
    { key: 'method', label: 'Способ применения', type: 'textarea', rows: 2 },
    { key: 'surfaces', label: 'Применимые поверхности (по строке)', type: 'lines', rows: 3 },
    { key: 'usage', label: 'Расход / нормы', type: 'text' },
    { key: 'shelf_life', label: 'Срок годности', type: 'text' },
    { key: 'tu', label: 'ТУ', type: 'text' },
    { key: 'application_industrial', label: 'Промышленное применение (по строке)', type: 'lines', rows: 5 },
    { key: 'application_domestic', label: 'Бытовое применение', type: 'textarea', rows: 2 },
  ],
  silikon: [
    { key: 'intro', label: 'Вводное описание', type: 'textarea', rows: 3 },
    { key: 'body', label: 'Дополнительное описание', type: 'textarea', rows: 3 },
    { key: 'bullets', label: 'Основные свойства (по строке)', type: 'lines', rows: 5 },
    { key: 'application', label: 'Применение', type: 'textarea', rows: 2 },
    { key: 'temp_range', label: 'Температурный диапазон', type: 'text' },
    { key: 'shelf_life', label: 'Срок годности', type: 'text' },
    { key: 'tu', label: 'ТУ', type: 'text' },
  ],
  oil: [
    { key: 'intro', label: 'Вводное описание', type: 'textarea', rows: 3 },
    { key: 'body', label: 'Дополнительное описание', type: 'textarea', rows: 3 },
    { key: 'viscosity_note', label: 'Примечание о вязкости', type: 'text' },
    { key: 'bullets', label: 'Основные свойства (по строке)', type: 'lines', rows: 5 },
    { key: 'applications', label: 'Области применения (по строке)', type: 'lines', rows: 5 },
    { key: 'temp_range', label: 'Температурный диапазон', type: 'text' },
    { key: 'shelf_life', label: 'Срок годности', type: 'text' },
    { key: 'tu', label: 'ТУ', type: 'text' },
  ],
  sealant: [
    { key: 'intro', label: 'Вводное описание', type: 'textarea', rows: 3 },
    { key: 'body', label: 'Дополнительное описание', type: 'textarea', rows: 3 },
    { key: 'usage', label: 'Применение / способ нанесения', type: 'textarea', rows: 2 },
    { key: 'bullets', label: 'Основные свойства (по строке)', type: 'lines', rows: 5 },
    { key: 'surfaces', label: 'Применимые поверхности (по строке)', type: 'lines', rows: 5 },
    { key: 'temp_range', label: 'Температурный диапазон', type: 'text' },
    { key: 'shelf_life', label: 'Срок годности', type: 'text' },
    { key: 'tu', label: 'ТУ', type: 'text' },
  ],
  grease: [
    { key: 'intro', label: 'Вводное описание', type: 'textarea', rows: 3 },
    { key: 'body', label: 'Дополнительное описание', type: 'textarea', rows: 3 },
    { key: 'bullets', label: 'Основные свойства (по строке)', type: 'lines', rows: 5 },
    { key: 'temp_range', label: 'Температурный диапазон', type: 'text' },
    { key: 'application_industrial', label: 'Области применения (по строке)', type: 'lines', rows: 5 },
    { key: 'shelf_life', label: 'Срок годности', type: 'text' },
    { key: 'tu', label: 'ТУ', type: 'text' },
  ],
  default: [
    { key: 'intro', label: 'Вводное описание', type: 'textarea', rows: 3 },
    { key: 'composition', label: 'Состав', type: 'textarea', rows: 2 },
    { key: 'body', label: 'Дополнительное описание', type: 'textarea', rows: 3 },
    { key: 'bullets', label: 'Основные свойства (по строке)', type: 'lines', rows: 5 },
    { key: 'application', label: 'Применение', type: 'textarea', rows: 2 },
    { key: 'temp_range', label: 'Температурный диапазон', type: 'text' },
    { key: 'shelf_life', label: 'Срок годности', type: 'text' },
    { key: 'tu', label: 'ТУ', type: 'text' },
  ],
};
```

## Integration with Product Form

```tsx
// src/app/admin/products/page.tsx
const suggestedTemplate = getSuggestedTemplate(categories, product.category_id);

const handleCategoryChange = (product: Product, categoryId: number) => {
  const suggested = getSuggestedTemplate(categories, categoryId);
  setEditing({ ...product, category_id: categoryId, template_type: suggested });
};

// In the form:
<TemplateDataEditor
  templateType={product.template_type}
  categoryId={product.category_id}
  templateData={product.template_data || {}}
  onChange={(data) => update('template_data', data)}
/>
```

## Template Type Suggestion Map

```ts
const CATEGORY_TEMPLATE_MAP: Record<string, string> = {
  'silikonovye-i-poliuretanovye-kompaundy': 'silikon',
  'production-release': 'release',
  'pms': 'oil',
  'production-grease': 'grease',
  'production-sealant': 'sealant',
};

function getSuggestedTemplate(categories: Category[], categoryId: number): string {
  const cat = categories.find((c) => c.id === categoryId);
  if (!cat) return 'default';
  return CATEGORY_TEMPLATE_MAP[cat.slug] || cat.template_type || 'default';
}
```

## Key Design Decisions

1. **Fields stored in DB** — no code changes needed to add/remove fields per template. Admins (or scripts) update `fields_json` directly.
2. **Category-linked templates** — `category_id` FK ensures each category gets the right editor automatically.
3. **Dual lookup strategy** — API tries `categoryId` first (most reliable), falls back to `name` (for orphaned or global templates).
4. **Empty fields stripped** — `undefined` and `""` deleted from JSON. Keeps database clean.
5. **`lines` type converts newline → array** — easier for admins than typing JSON arrays manually.
6. **No `dangerouslySetInnerHTML`** — all values are plain text; HTML structure lives in template components.

## Pitfall: State Re-initialization Wipes Existing Data

**Symptom:** Data exists in the database (`template_data` JSON is populated), the public page renders it correctly, but when you open the product in the admin editor, all fields are empty.

**Root cause:** The `TemplateDataEditor` component may call `onChange({})` or rebuild `templateData` from scratch inside a `useEffect` that fires on mount or when `categoryId` changes. Because the parent form receives this empty object via `onChange`, the next `handleSave` PUTs `{}` back to the API, overwriting the real data in SQLite.

**Prevention rules:**

1. **Never call `onChange` inside a `useEffect` that fetches field definitions.** Field loading only affects which inputs to render, not the values:
   ```tsx
   // ❌ WRONG — overwrites user's data on mount
   useEffect(() => {
     fetchFields(categoryId).then((fields) => {
       setFields(fields);
       onChange({}); // WIPES EXISTING DATA
     });
   }, [categoryId, onChange]);

   // ✅ RIGHT — only set field metadata, never touch values
   useEffect(() => {
     fetchFields(categoryId).then((fields) => setFields(fields));
   }, [categoryId]);
   ```

2. **Source of truth for values must be the `templateData` prop, never a local `data` state.** If the editor keeps its own `data` state initialized from an empty `{}`, it will submit empties:
   ```tsx
   // ❌ WRONG — local state diverges from prop
   const [data, setData] = useState({});

   // ✅ RIGHT — read directly from prop, write via onChange
   const getValue = (key: string) => templateData[key] ?? '';
   const setValue = (key: string, value: any) => {
     onChange({ ...templateData, [key]: value });
   };
   ```

3. **Parent form must pass existing `template_data` into the editor, not omit it.**
   ```tsx
   // ❌ WRONG — missing templateData prop means editor sees empty object
   <TemplateDataEditor templateType={product.template_type} />

   // ✅ RIGHT — always pass the full data object
   <TemplateDataEditor
     templateType={product.template_type}
     categoryId={product.category_id}
     templateData={product.template_data || {}}
     onChange={(data) => update('template_data', data)}
   />
   ```

## Debugging Checklist: "Data in DB but Not in Editor"

Follow this order — each step isolates one layer:

1. **Database layer:** Query `template_data` directly via `better-sqlite3`:
   ```js
   const db = require('better-sqlite3')('pentajunior.db');
   const row = db.prepare('SELECT template_data FROM products WHERE id = ?').get('si-m-aero');
   console.log(JSON.parse(row.template_data));
   // Expected: {"temp_range":"от -50 до +250 °C", ...}
   // If empty {} or "[object Object]" → data corruption, fix DB first
   ```

2. **API GET layer:** Check what `/api/admin/products/[id]` returns:
   ```bash
   curl -s http://localhost:3002/api/admin/products/si-m-aero \
     -H "Cookie: admin_token=YOUR_ADMIN_PASSWORD" | jq '.template_data'
   ```
   If this returns `{}` or `null` while DB has data → `JSON.parse` bug in API or double-serialization.

3. **Parent form layer:** Log what `product` object contains before rendering `<TemplateDataEditor>`:
   ```tsx
   console.log('Editing product:', product.template_data);
   ```
   If `{}` here → the `getProductById` function in `db.ts` is returning wrong data (check `JSON.parse(r.template_data || '{}')`).

4. **Editor props layer:** Log inside `TemplateDataEditor`:
   ```tsx
   console.log('Editor received:', templateData);
   ```
   If `{}` here but parent passed correct data → `ProductForm` is resetting state in a `useEffect` after opening the modal.

5. **Editor internal layer:** Verify `getValue(field.key)` returns the expected string:
   ```tsx
   console.log('Field temp_range value:', getValue('temp_range'));
   ```
   If empty here but `templateData` has the key → `getValue` has a coercion bug (e.g. `String(null)` or `Array.isArray` guard).

## Anti-patterns

| ❌ Don't | ✅ Do instead |
|---|---|
| Hardcode `FIELD_DEFINITIONS` in component | Store in `category_templates.fields_json` |
| Show all fields for all template types | Filter by `categoryId` → fetch correct fields |
| Store empty strings in DB | Strip empty/undefined before `onChange` |
| Ask admins to type JSON arrays manually | `lines` textarea with newline splitting |
| Put HTML tags in `template_data` values | HTML lives in template components |
| Allow `template_type` mismatch with `template_data` keys | `categoryId` lookup guarantees correct field set |

## Migration from v1 (Hardcoded) to v2 (DB-Driven)

```sql
-- 1. Create table
CREATE TABLE category_templates (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, category_id INTEGER, fields_json TEXT);

-- 2. Insert old FIELD_DEFINITIONS as JSON
INSERT INTO category_templates (name, category_id, fields_json) VALUES
('silikon', 1, '[...]'),
('release', 2, '[...]'),
('oil', 3, '[...]'),
('sealant', 5, '[...]'),
('grease', 4, '[...]'),
('default', NULL, '[...]');

-- 3. Add template_type to categories
ALTER TABLE categories ADD COLUMN template_type TEXT DEFAULT 'default';
UPDATE categories SET template_type = 'silikon' WHERE id = 1;
-- ... etc for each category

-- 4. Replace TEMPLATE_FIELDS constant in component with API fetch
```

## Real-World Usage

Applied in PentaJunior v2:
- Admin product form shows 13 fields for `release` type, 4 fields for `silikon`
- All products edited with correct field set per category
- `TemplateDataEditor` fetches fields from API → no code changes needed for new templates
- `template_data` JSON stored in SQLite → rendered by `ReleaseTemplate.tsx`, `SilikonTemplate.tsx`, etc.
