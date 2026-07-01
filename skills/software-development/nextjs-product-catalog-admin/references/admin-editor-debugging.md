# Admin Editor Debugging: "Data in DB but Fields Are Empty"

**Session:** PentaJunior v2 template editor debug  
**Context:** Next.js 16 + better-sqlite3 + SSG + admin panel with dynamic `TemplateDataEditor`

## Problem Statement

Product `si-m-aero` has valid `template_data` in SQLite:
```json
{"temp_range": "от -50 до +250 °C", "intro": "Si-M® — универсальная силиконовая смазка"}
```

Public page renders correctly after `npm run build`.  
But when opening the product in admin panel (`/admin/products`), the `temp_range` and other fields appear empty.

## Root Cause Categories

When data is correct in DB but not in the editor, the bug is **never** in the DB or the API GET route (those were verified). The bug is always in one of these three layers:

### Layer 1: Product form loses `template_data` before passing to editor

The parent `ProductForm` component opens a modal with `editing` state. If the modal initialization code does something like:

```tsx
// ❌ WRONG — overwrites template_data with empty object
setEditing({ ...product, template_data: {} });

// ❌ WRONG — creates a new object losing existing keys
setEditing({
  ...product,
  template_data: { temp_range: '', intro: '' } // empties!
});
```

The `template_data` prop passed to `TemplateDataEditor` is already empty.

**Fix:** Preserve existing `template_data` exactly:
```tsx
setEditing({ ...product }); // template_data comes from the product object
// or explicitly:
setEditing({
  ...product,
  template_data: product.template_data || {},
});
```

### Layer 2: Editor initializes local state ignoring prop

If `TemplateDataEditor` has internal state:

```tsx
// ❌ WRONG — local state initialized empty, never syncs with prop
const [data, setData] = useState({});

useEffect(() => {
  // fetches fields, but never loads existing values into data
  fetchFields(categoryId).then(setFields);
}, [categoryId]);
```

The `data` state is empty `{}` forever, even though `templateData` prop has values.

**Fix:** Do not maintain a separate `data` state. Derive values directly from the prop:
```tsx
const getValue = (key: string) => {
  const val = templateData[key];
  if (Array.isArray(val)) return val.join('\n');
  return String(val ?? '');
};
```

### Layer 3: Editor calls `onChange({})` on mount/category change

The most dangerous pattern — a `useEffect` that "resets" data when fields load:

```tsx
// ❌ WRONG — wipes data every time fields load
useEffect(() => {
  fetchFields(categoryId).then((fields) => {
    setFields(fields);
    onChange({}); // DESTROYS existing template_data!
  });
}, [categoryId, onChange]);
```

This not only makes fields appear empty in the UI, but also causes the next `handleSave` to PUT `{}` to the API, **overwriting the real data in SQLite**.

**Fix:** Separate field-loading from value-management:
```tsx
useEffect(() => {
  fetchFields(categoryId).then(setFields); // only set metadata
}, [categoryId]);

// onChange is ONLY called when user types
const setValue = (key: string, raw: string, type: string) => {
  let value: any = raw;
  if (type === 'lines') {
    value = raw.split('\n').filter((s) => s.trim() !== '');
  }
  const next = { ...templateData, [key]: value };
  if (value === '' || (Array.isArray(value) && value.length === 0)) {
    delete next[key];
  }
  onChange(next); // only here, only on user input
};
```

## Five-Step Diagnostic (run in order)

### Step 1: Verify DB directly
```bash
cd ~/pentajunior-v2 && node -e "
const db = require('better-sqlite3')('pentajunior.db');
const row = db.prepare('SELECT template_data FROM products WHERE id = ?').get('si-m-aero');
console.log('DB template_data:', JSON.parse(row.template_data));
"
```
**Expected:** `{"temp_range":"от -50 до +250 °C", ...}`

### Step 2: Verify API GET (parent form)
```bash
curl -s http://localhost:3002/api/admin/products/si-m-aero \
  -H "Cookie: admin_token=YOUR_PASSWORD" | jq '.template_data'
```
**Expected:** Same object as DB.

### Step 3: Verify editor-specific API
```bash
curl -s "http://localhost:3002/api/admin/templates?categoryId=2" \
  -H "Cookie: admin_token=YOUR_PASSWORD" | jq '.data.fields | length'
```
**Expected:** Non-zero count matching the template type.

### Step 4: Verify parent form state
In `src/app/admin/products/page.tsx`, add before the `TemplateDataEditor` call:
```tsx
console.log('Passing to editor:', editing.template_data);
```
**Expected:** Same object. If `{}` → check modal open logic.

### Step 5: Verify editor receives prop
In `TemplateDataEditor.tsx`, add at top of component:
```tsx
console.log('Editor templateData prop:', templateData);
console.log('Editor fields count:', fields.length);
console.log('Editor categoryId:', categoryId);
```
**Expected:** `templateData` has keys, `fields.length > 0`, `categoryId` is a valid number. If any of these are wrong → trace back to the corresponding layer.

## Step 6: Temporary Test Route for Isolation (optional but powerful)

When the existing API is complex (auth middleware, multi-route handlers), create a minimal test route to isolate the editor component from API uncertainty:

```ts
// src/app/api/test-templates/route.ts
import { NextResponse } from 'next/server';
import { getAllTemplates, getTemplateByName, getTemplateByCategoryId } from '@/lib/db';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const name = searchParams.get('name');
  const categoryId = searchParams.get('categoryId');

  if (name) {
    const tpl = getTemplateByName(name);
    return NextResponse.json({ data: tpl });
  }
  if (categoryId) {
    const tpl = getTemplateByCategoryId(Number(categoryId));
    return NextResponse.json({ data: tpl });
  }

  const tpls = getAllTemplates();
  return NextResponse.json({ data: tpls });
}
```

Then point the editor to `/api/test-templates?categoryId=...` temporarily. If it works, the bug is in the main API (auth, middleware, or route handler). If it still fails, the bug is in the editor component itself.

## Prevention Rules

1. **Modal open → always pass full product object** including `template_data` and `category_id`
2. **Editor → no local `data` state** — read from prop, write via `onChange`
3. **Field loading → never call `onChange`** — only `setFields` (metadata)
4. **Category change → preserve existing `template_data` keys** — add/remove only when user explicitly edits
5. **After fix → always run `npm run build`** and verify generated HTML contains the data
6. **Always guard `useEffect` with `if (categoryId)`** — prevents fetch with `undefined` which silently fails
7. **Include `categoryId` prop** in the editor call — the dual-lookup strategy needs it as primary key

## Related

- `template-data-editor-pattern.md` — full DB-driven editor architecture
- `sqlite-json-column-serialization.md` — JSON round-trip safety
