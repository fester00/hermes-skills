# Array Fields in Admin Forms — Line-by-Line Textarea Pattern

When an admin panel needs a multi-value field (colors, keywords, surfaces,
features) but wants a simple UI, a `textarea` that splits on `\n` is the
lightest viable pattern for a JSON-file admin panel.

## Why not a tag input?

Tag-input components add dependencies and complexity. For a Bootstrap admin
panel backed by JSON, a plain textarea is enough and keeps the form
server-renderable / lightweight.

## React pattern

```tsx
<div className="col-md-6">
  <label className="form-label small">Цвета (по строке)</label>
  <textarea
    className="form-control"
    rows={3}
    value={(formData.colors || []).join('\n')}
    onChange={(e) => setFormData({
      ...formData,
      colors: e.target.value
        .split('\n')
        .map((s) => s.trim())
        .filter(Boolean),
    })}
    placeholder="Белый&#10;Красный&#10;Синий"
  />
  <div className="form-text">Каждый цвет — с новой строки.</div>
</div>
```

## Rules

1. **Always default to `[]`** in initial `formData` so `.join('\n')` does not
   throw.
2. **Trim and filter empty lines** to avoid storing `['', ' ', '']` in the DB.
3. **Use the same field name** in `DbProduct` (admin type) and `Product`
   (public catalog type), e.g. `colors?: string[]`.
4. **Render defensively** on the public page:
   ```tsx
   {product.colors && product.colors.length > 0 && (
     <>
       <h3 className="h6">Цвета:</h3>
       <ul className="list-group list-group-flush">
         {product.colors.map((color, i) => (
           <li key={i} className="list-group-item px-0">
             {color}
           </li>
         ))}
       </ul>
     </>
   )}
   ```
5. **Remember the JSON DB / static data split.** If the site still reads from a
   static TypeScript catalog (`src/data/products.tsx`), adding the field to
   the admin form alone is not enough — the public `Product` interface and the
   product objects must also be updated.

## Real-world example

PentaJunior project (`penta-junior-v2`) uses this pattern for the "Цвет"
field on silicon-products. See `references/penta-junior-v2-notes.md` for the
full project context.
