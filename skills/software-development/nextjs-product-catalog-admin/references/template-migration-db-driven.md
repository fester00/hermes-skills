# Template Migration: Hardcoded Fields → Database-Driven

## Context

When a Next.js + SQLite SSG project starts with hardcoded template field definitions (a big `Record<string, FieldDef[]>` constant in a component), moving them to the database enables:
- Admin-driven template customization
- No code redeploy for new fields
- Per-category field sets that auto-load

## Migration Steps

### 1. Create the `category_templates` table

```sql
CREATE TABLE IF NOT EXISTS category_templates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
  fields_json TEXT NOT NULL DEFAULT '[]',
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_templates_category ON category_templates(category_id);
```

### 2. Add `template_type` to `categories`

```sql
ALTER TABLE categories ADD COLUMN template_type TEXT DEFAULT 'default';
```

### 3. Convert hardcoded `FIELD_DEFINITIONS` to SQL INSERTs

```typescript
// Extract from component code:
const TEMPLATE_FIELDS: Record<string, { key: string; label: string; type: 'text'|'textarea'|'lines'; rows?: number; placeholder?: string }[]> = {
  release: [ /* 13 fields */ ],
  silikon: [ /* 4 fields */ ],
  oil: [ /* 5 fields */ ],
  sealant: [ /* 5 fields */ ],
  grease: [ /* 5 fields */ ],
  default: [ /* 7 fields */ ],
};

// Generate SQL via Node script:
import Database from 'better-sqlite3';
const db = new Database('pentajunior.db');

const stmt = db.prepare('INSERT OR IGNORE INTO category_templates (name, category_id, fields_json) VALUES (?, ?, ?)');
for (const [name, fields] of Object.entries(TEMPLATE_FIELDS)) {
  stmt.run(name, null, JSON.stringify(fields));
}
```

### 4. Link templates to categories

```typescript
const CATEGORY_TEMPLATE_MAP: Record<string, string> = {
  'silikonovye-i-poliuretanovye-kompaundy': 'silikon',
  'production-release': 'release',
  'pms': 'oil',
  'production-grease': 'grease',
  'production-sealant': 'sealant',
};

const cats = db.prepare('SELECT id, slug FROM categories').all();
for (const cat of cats) {
  const tpl = CATEGORY_TEMPLATE_MAP[cat.slug] || 'default';
  db.prepare('UPDATE categories SET template_type = ? WHERE id = ?').run(tpl, cat.id);
  db.prepare('UPDATE category_templates SET category_id = ? WHERE name = ?').run(cat.id, tpl);
}
```

### 5. Update `db.ts` — add Template types and getters

```typescript
export interface TemplateField {
  key: string;
  label: string;
  type: 'text' | 'textarea' | 'lines' | 'select';
  rows?: number;
  placeholder?: string;
}

export interface CategoryTemplate {
  id: number;
  name: string;
  category_id: number | null;
  fields: TemplateField[];
}

// Add to Category interface:
template_type: string;

// CRUD functions:
export function getAllTemplates(): CategoryTemplate[]
export function getTemplateByName(name: string): CategoryTemplate | undefined
export function getTemplateByCategoryId(categoryId: number): CategoryTemplate | undefined
export function getTemplateFields(templateType: string): TemplateField[]
export function createTemplate(template: Omit<CategoryTemplate, 'id'>): CategoryTemplate
export function updateTemplate(id: number, updates: Partial<CategoryTemplate>): CategoryTemplate | undefined
export function deleteTemplate(id: number): boolean
```

### 6. Add API endpoint

```typescript
// src/app/api/admin/templates/route.ts
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
  const templates = getAllTemplates();
  return NextResponse.json({ data: templates });
}
```

### 7. Rewrite component — fetch instead of hardcode

Replace the `FIELD_DEFINITIONS` constant and `useEffect` rebuild with:
```typescript
const [fields, setFields] = useState<TemplateField[]>([]);

useEffect(() => {
  fetch(`/api/admin/templates?categoryId=${categoryId}`)
    .then(r => r.json())
    .then(d => setFields(d.data?.fields || []));
}, [categoryId]);
```

### 8. Update `schema.sql`

Add new tables to the canonical schema file so future clones get the full structure.

## Rollback Strategy

Keep the old `FIELD_DEFINITIONS` constant commented in the component for 1–2 releases. If the API is down or a template is missing, fall back to the constant:
```typescript
const fields = apiFields.length > 0 ? apiFields : FIELD_DEFINITIONS[templateType] || FIELD_DEFINITIONS.default;
```

## Pitfalls

| Pitfall | Prevention |
|---------|-----------|
| `better-sqlite3` compiled for wrong Node version | `pnpm rebuild better-sqlite3` after any Node upgrade |
| Missing `template_type` on existing products | Run UPDATE query: `JOIN categories` to backfill |
| Empty `fields_json` causes blank editor | Always provide `default` template with basic fields |
| `category_id` FK prevents template deletion | Use `ON DELETE SET NULL` |
| JSON.parse fails on malformed `fields_json` | Wrap in try/catch in `db.ts` getters |

## Verification

```sql
-- All categories have template_type
SELECT id, slug, template_type FROM categories WHERE template_type IS NULL;
-- Should return 0 rows

-- All templates linked
SELECT t.name, c.title FROM category_templates t LEFT JOIN categories c ON t.category_id = c.id;
-- Every template should show either a category or NULL (for global defaults)

-- Products match their category's template
SELECT p.id, p.template_type, c.template_type AS cat_template
FROM products p JOIN categories c ON p.category_id = c.id
WHERE p.template_type != c.template_type;
-- Should return 0 rows (or fix mismatches)
```
