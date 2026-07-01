# Universal product template with conditional sections

Session: 2026-06-17 — replacing six per-category templates (`default`, `silikon`, `oil`, `sealant`, `release`, `grease`) with one `UniversalTemplate.tsx` for `pentajunior-v2`.

## Goal

A single component renders every product detail page. Sections and subsections appear only when their backing data is non-empty. Legacy components are removed once the universal template is proven.

## Data model

`template_data` JSON stored in SQLite `products` table. Fields grouped by section:

- **Description:** `intro`, `body`, `composition`, `tu`, `color`, `surfaces`, `properties`, `bullets`, `usage`, `viscosity_note`, `catalyst_type`.
- **Application areas:** `application_industrial`, `application_domestic`, `applications`.
- **Application / instructions:** `application`, `recommendations`, `surface_prep_title`, `surface_prep`, `mixing_title`, `mixing_steps`, `degassing_title`, `degassing`, `important_note`, `safety_title`, `safety`.
- **Extras:** `temp_range`, `shelf_life`, `method`.

All fields are optional. `Technical characteristics` continue to render separately via `spec_table_id` / `TableIncluder`, not inside the universal template.

## Rendering rules

```tsx
function toStringArray(value: string[] | string | undefined | null): string[] {
  if (Array.isArray(value)) return value.filter((item) => typeof item === 'string' && item.trim() !== '');
  if (typeof value === 'string') {
    return value
      .split('\n')
      .map((s) => s.trim())
      .filter(Boolean);
  }
  return [];
}

function hasText(value: string | undefined | null): boolean {
  return typeof value === 'string' && value.trim().length > 0;
}
```

A section is rendered only if at least one of its fields is non-empty. Subsections (e.g. "В промышленности" / "Бытовое") are rendered independently.

## Fully removing legacy templates

After proving the universal template works, delete the old component files and remove their imports. Do not keep `_legacy_*` aliases unless the user explicitly asks for a quick-override escape hatch.

Files to delete:

```bash
rm src/components/ProductTemplates/DefaultTemplate.tsx \
   src/components/ProductTemplates/SilikonTemplate.tsx \
   src/components/ProductTemplates/OilTemplate.tsx \
   src/components/ProductTemplates/SealantTemplate.tsx \
   src/components/ProductTemplates/ReleaseTemplate.tsx \
   src/components/ProductTemplates/GreaseTemplate.tsx
```

Resulting `src/components/ProductTemplates/index.tsx`:

```tsx
import UniversalTemplate from './UniversalTemplate';

export interface TemplateProps {
  name: string;
  templateData: Record<string, any>;
}

const templates: Record<string, React.ComponentType<TemplateProps>> = {
  silikon: UniversalTemplate as React.ComponentType<TemplateProps>,
  oil: UniversalTemplate as React.ComponentType<TemplateProps>,
  sealant: UniversalTemplate as React.ComponentType<TemplateProps>,
  release: UniversalTemplate as React.ComponentType<TemplateProps>,
  grease: UniversalTemplate as React.ComponentType<TemplateProps>,
  default: UniversalTemplate as React.ComponentType<TemplateProps>,
};

export function getTemplateComponent(type: string): React.ComponentType<TemplateProps> {
  return templates[type] || templates.default;
}

export { UniversalTemplate };
export type { TemplateProps as default };
```

## Admin editor grouping

`TemplateDataEditor.tsx` renders one shared field list grouped into four sequential sections:

1. Описание
2. Области применения
3. Применение
4. Дополнительная информация

Each section contains the fields relevant to that section. The `spec_table_id` selector remains at the bottom.

After unifying on the universal template, the admin product form no longer shows a "Тип шаблона" selector and `TemplateDataEditor` does not fetch fields per `templateType`. See `references/penta-junior-admin-template-editor.md` for the final admin form details, including styled section headers and the memoized field rows that prevent modal scroll jump.

## Markdown list support

The legacy `renderMarkdownText` helper only handled `**bold**` and line breaks. Product `application` fields often contain multi-line markdown lists:

```text
**Область применения люминофора:**

- Светящиеся элементы декора из силикона и эпоксидной смолы
- Декоративные панно, вставки и панели для интерьера
- Автотюнинг: диски, элементы кузова
```

Update the helper to detect lines starting with `- ` or `* ` and render them as `<ul class="list-unstyled">`. Empty lines inside a list are ignored. Non-list lines terminate the list and continue as paragraphs.

## Normalizing a string list field in the DB

Example from `si-m-aero`: `application_domestic` was stored as a single semicolon-separated string. Convert it to an array so the template renders it as a proper list:

```python
import sqlite3, json, re

conn = sqlite3.connect('pentajunior.db')
cur = conn.cursor()
cur.execute("SELECT id, template_data FROM products WHERE id = 'si-m-aero'")
pid, raw = cur.fetchone()
data = json.loads(raw)
val = data.get('application_domestic', '')
items = [s.strip().rstrip('.;') for s in re.split(r'[;.](?=\s|$)', val) if s.strip()]
data['application_domestic'] = items
cur.execute("UPDATE products SET template_data = ? WHERE id = ?",
            (json.dumps(data, ensure_ascii=False), pid))
conn.commit()
conn.close()
```

## Dev-server caching pitfall

When `next dev` (Turbopack) is running, changes to a shared helper such as `src/lib/markdown.tsx` may not be reflected in the browser even after process restart and `rm -rf .next`. If the static output looks stale:

1. Stop all Node processes and free the port.
2. Run `rm -rf .next node_modules/.cache`.
3. Build and start production-style: `npm run build && npx next start -p <port>`.
4. Verify the actual rendered HTML with `curl` or `requests.get(...)`, not only the accessibility snapshot.

## Verification checklist

1. `npx tsc --noEmit`
2. `npm run build` — all static pages generated.
3. `npx next start` on a free port.
4. Check products with different section combinations:
   - only Description + spec table;
   - Description + Application areas + spec table;
   - Description + Application (with markdown list) + spec table;
   - product with no template data — only the header/spec table/other global UI.
5. Log in to admin, open a product, confirm the four field groups are present, save a small change, and verify it appears in the DB.
6. After deleting legacy templates, confirm representative products from each old category still build and render.
