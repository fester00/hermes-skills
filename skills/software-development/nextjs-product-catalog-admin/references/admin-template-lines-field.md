# Admin Editor `lines` Field Type

Pattern for multi-line list fields in a database-driven admin editor for
Next.js + SQLite SSG projects.

## When to use

A product template needs an ordered list of short items where:
- Admin enters one item per line in a `<textarea>`
- Database stores a JSON array of strings
- Frontend template renders the list as `<ul>` with icons or bullets

Examples: "Основные свойства", "Применимые поверхности", "Особенности".

## Three-way sync rule

Changing a field from `text` (single-line `<input>`) to `lines` (multi-line
`<textarea>` → `string[]`) requires updates in **three places**. Missing any
one causes silent data corruption or rendering errors.

| Layer | What to change | Failure mode if missed |
|---|---|---|
| **DB `category_templates`** | `fields_json` field `type`: `"lines"` | Admin shows single-line `<input>`; data saves as plain string |
| **Editor fallback** | `TemplateDataEditor.tsx` fallback defs | If DB unreachable, editor falls back to old `text` field |
| **React template** | Prop type `string[]` + `<ul>{...map(...)}</ul>` | Component receives string instead of array; `.map` crashes or renders `[object Object]` |

## DB schema snippet

```sql
-- category_templates.fields_json excerpt for template 'release'
[
  {"key":"properties", "type":"lines", "label":"Основные свойства", "rows":4},
  {"key":"surfaces",   "type":"lines", "label":"Применимые поверхности", "rows":5}
]
```

## Editor fallback snippet

```tsx
// TemplateDataEditor.tsx — fallback when /api/admin/templates fails
const FALLBACK_FIELDS: Record<string, FieldDef[]> = {
  release: [
    { key: 'properties', type: 'lines', label: 'Основные свойства', rows: 4 },
    { key: 'surfaces',   type: 'lines', label: 'Применимые поверхности', rows: 5 },
    // ... other fields
  ],
};
```

## React template snippet

```tsx
// ReleaseTemplate.tsx
interface ReleaseTemplateData {
  properties?: string[];  // was string before migration
  surfaces?: string[];    // was string before migration
}

export default function ReleaseTemplate({ templateData }: { templateData: ReleaseTemplateData }) {
  return (
    <>
      {templateData.properties && (
        <section>
          <h2>Основные свойства</h2>
          <ul className="list-unstyled">
            {templateData.properties.map((item, i) => (
              <li key={i}><i className="bi bi-check-circle-fill text-primary" /> {item}</li>
            ))}
          </ul>
        </section>
      )}
      {templateData.surfaces && (
        <section>
          <h2>Применимые поверхности</h2>
          <ul className="list-unstyled">
            {templateData.surfaces.map((s, i) => (
              <li key={i}><i className="bi bi-check-circle-fill text-primary" /> {s}</li>
            ))}
          </ul>
        </section>
      )}
    </>
  );
}
```

## Serialization contract

- **Save (admin → API → DB):** `textarea.value.split('\n').filter(s => s.trim() !== '')`
- **Load (DB → API → admin):** `array.join('\n')` so the textarea shows one item per line
- **DB storage:** JSON array string inside `products.template_data`

## Migration recipe: `text` → `lines`

1. **Update DB template:**
   ```sql
   UPDATE category_templates
   SET fields_json = json_set(fields_json, '$[?].type', 'lines')
   WHERE name = 'release' AND json_extract(fields_json, '$[?].key') = 'surfaces';
   ```
   (Or rebuild full `fields_json` via node script for clarity.)

2. **Update editor fallback:** change `type: 'text'` → `type: 'lines'` in `TemplateDataEditor.tsx`.

3. **Update React template:** change prop type `string` → `string[]` and renderer from `<p>{text}</p>` to `<ul>{array.map(...)}</ul>`.

4. **Backfill existing data:** products that already have the field as a plain string will show that string as a single `<li>` after the template change. Re-edit them in the admin panel so the editor splits the string into lines and saves a proper array.

## Pitfall: `text` vs `lines` mismatch

If the DB template says `type: 'text'` but the React component expects `string[]`,
the admin editor renders a single-line `<input>`. The user enters comma-separated
values or one long string. On save it goes into `template_data` as a plain string.
At build time the template tries `.map()` on a string → runtime error or `[object Object]`
in the static HTML.

**Detection:**
- Query: `SELECT id, template_data FROM products WHERE template_data LIKE '%surfaces%' AND json_type(template_data, '$.surfaces') = 'text'`
- Or: grep component for `.map(` and check if the corresponding DB field is `lines`.

**Prevention:** after any DB template change, run `npx tsc --noEmit` and `npm run build`
to catch type mismatches before they reach production.

## Related: Enter Key Interception

When `lines` fields render as `<textarea>` inside a modal or dialog, pressing
**Enter** may not insert a newline because parent elements intercept the key
via event bubbling. See `references/textarea-enter-key-interception.md` for
the fix (`e.stopPropagation()` on `onKeyDown`) and CSS `whiteSpace: 'pre-wrap'`
guidance.

