# `<textarea>` Enter Key Interception in Modal Dialogs

## Symptom

In an admin product editor using a `<dialog>` or Bootstrap modal, `<textarea>`
fields of type `lines` (multi-line list input) do **not** insert a newline when
the user presses **Enter**. Instead, the cursor stays on the same line or the
modal/dialog captures the key and does something else (e.g., closes or submits).

CSS `whiteSpace: 'pre-wrap'` on the textarea only affects how existing text is
**rendered** — it does **not** enable the Enter key to insert `\n`.

## Root Cause

The `keydown` event for `Enter` bubbles up from the `<textarea>` to the parent
`<dialog>` element (or a parent `<form>` wrapper). Many modal/dialog
implementations, Bootstrap modals, and custom form handlers listen for
`keydown` on the container and intercept Enter for "submit on Enter" behavior.
This prevents the textarea from receiving the default browser action
(inserting a newline).

## Fix

Add an explicit `onKeyDown` handler directly on every `<textarea>` that needs
multi-line input:

```tsx
<textarea
  className="form-control form-control-sm lines-textarea"
  rows={field.rows || 2}
  value={getValue(field.key)}
  onChange={(e) => setValue(field.key, e.target.value, field.type)}
  onKeyDown={(e) => {
    // Allow Enter key in textarea to insert newlines
    if (e.key === 'Enter') {
      e.stopPropagation();
    }
  }}
  style={{ whiteSpace: field.type === 'lines' ? 'pre-wrap' : undefined }}
/>
```

### Why `stopPropagation` and not `preventDefault`?

- **`e.stopPropagation()`** — stops the event from bubbling up to parent elements
  (modal, form, dialog) while allowing the browser's default textarea behavior
  (insert newline). This is the correct fix.
- **`e.preventDefault()`** — would block the default behavior entirely, preventing
  the newline from being inserted. Do **not** use `preventDefault` here.

## Also Required: CSS `whiteSpace: 'pre-wrap'`

After the newline is successfully inserted, the textarea must display wrapped
lines. Without `pre-wrap`, long lines overflow horizontally instead of wrapping:

```tsx
style={{ whiteSpace: field.type === 'lines' ? 'pre-wrap' : undefined }}
```

| CSS value | Behavior |
|---|---|
| `pre` | Preserves whitespace and newlines, but does **not** wrap long lines. Horizontal scroll. |
| `pre-wrap` | Preserves whitespace and newlines, **and** wraps long lines. ✅ Correct for `lines` fields. |
| `pre-line` | Collapses consecutive whitespace, preserves newlines, wraps. Acceptable but collapses leading spaces. |
| `normal` | Collapses whitespace and newlines into a single space. ❌ Breaks multi-line display. |

## Where to Apply

Apply the `onKeyDown` + `pre-wrap` pattern to **all** `<textarea>` elements used
for `lines` type fields in a modal/form context:

- Admin product editor (`TemplateDataEditor.tsx`)
- Category template field editor (if building template editing UI)
- Any other multi-line text inputs inside dialogs

## Verification

1. Open admin product editor modal.
2. Focus a `lines` textarea (e.g., "Основные свойства").
3. Press **Enter** — cursor should move to a new line.
4. Type more text, press Enter again — should create multiple lines.
5. Save the product.
6. Re-open the same product — previously entered lines should display one per
   line in the textarea.
7. Check public page — the `lines` field should render as a `<ul>` with each line
   as a separate `<li>`.

## Detection Queries

If users report "I can't enter multiple lines" but no error appears:

- **Console check:** open browser DevTools → Console → press Enter in textarea.
  If a parent element logs something, it's intercepting the event.
- **Event listener check:** in DevTools Elements panel, inspect the `<textarea>`
  → Event Listeners → look for `keydown` listeners on ancestors.

## Related

- `references/admin-template-lines-field.md` — three-way sync rule for migrating
  `text` → `lines` fields (DB + editor + React template)
