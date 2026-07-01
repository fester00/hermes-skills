# Admin Dashboard: Modal UI Pattern (PentaJunior v2)

## Context

When building a custom admin panel inside a Next.js + Bootstrap project, the
default Bootstrap modal (`modal-lg`, `modal-xl`) has fixed widths that don't
match the content density of CRUD forms. The standard Bootstrap modal also lacks
dark-theme styling when the admin uses a custom dark palette.

## Pattern

### 1. Custom modal dialog class (replaces Bootstrap `modal-lg`)

```css
.admin-modal-dialog {
  max-width: 960px;          /* content-driven, not Bootstrap-fixed */
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  margin: 1.75rem auto;
}

.admin-modal-dialog--compact {
  max-width: 720px;          /* for simpler forms (categories, tags) */
}
```

**Why not `modal-lg`:** Bootstrap `modal-lg` is 800px — too narrow for
product forms with ~15 fields, side-by-side inputs, and image previews.
Removing the Bootstrap class entirely prevents width conflicts.

### 2. Sticky header + footer with scrollable body

```css
.admin-modal-content {
  background: var(--admin-surface);
  border: 1px solid var(--admin-border);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  overflow: hidden;
}

.admin-modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--admin-border);
  background: var(--admin-surface);
  position: sticky;
  top: 0;
  z-index: 10;
  flex-shrink: 0;
}

.admin-modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--admin-border);
  background: var(--admin-surface);
  position: sticky;
  bottom: 0;
  z-index: 10;
  flex-shrink: 0;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.admin-modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1 1 auto;
}
```

**Why sticky:** The modal body scrolls, but header (title + close) and footer
(submit/cancel buttons) remain visible at all times. This is critical for
long forms — the user never loses the context of what they're editing or how
to save.

### 3. Form styling inside modal

```css
.admin-input {
  background: var(--admin-input-bg);
  border: 1px solid var(--admin-border);
  color: var(--admin-text);
  padding: 0.625rem 0.875rem;
  border-radius: 8px;
  width: 100%;
}

.admin-input:focus {
  border-color: var(--admin-olive);
  box-shadow: 0 0 0 3px rgba(107, 142, 35, 0.15);
  outline: none;
}

.admin-label {
  display: block;
  margin-bottom: 0.375rem;
  font-weight: 500;
  color: var(--admin-text);
  font-size: 0.875rem;
}
```

### 4. Modal markup structure

```tsx
<div className="modal show" style={{ display: 'block', background: 'rgba(0,0,0,0.6)' }}>
  <div className="modal-dialog admin-modal-dialog">
    <div className="modal-content admin-modal-content">
      <div className="modal-header admin-modal-header">
        <h5 className="modal-title">Редактировать товар</h5>
        <button type="button" className="btn-close" onClick={onClose} />
      </div>
      <div className="modal-body admin-modal-body">
        {/* form fields */}
      </div>
      <div className="modal-footer admin-modal-footer">
        <button className="btn btn-secondary" onClick={onClose}>Отмена</button>
        <button className="btn btn-primary" onClick={onSave}>Сохранить</button>
      </div>
    </div>
  </div>
</div>
```

### 5. Compact variant for simple forms

For forms with ≤ 8 fields (e.g. categories, tags, simple entities), use the
compact class to avoid excessive whitespace:

```tsx
<div className="modal-dialog admin-modal-dialog admin-modal-dialog--compact">
```

## Integration Notes

- Remove Bootstrap `modal-lg` class from the markup — it conflicts with custom `max-width`.
- The modal overlay (`style={{ background: 'rgba(0,0,0,0.6)' }}`) replaces Bootstrap's
  default backdrop opacity for a darker, more focused admin feel.
- CSS variables (`--admin-surface`, `--admin-border`, etc.) must be defined in
  `globals.css` or a dedicated admin theme file. See `references/admin-dark-theme-variables.md`
  for the full variable system.

## Real-World Usage

Applied in PentaJunior v2 admin panel for:
- Product CRUD modal (~15 fields, images, prices, stock info) — full width (960px)
- Category CRUD modal (~7 fields) — compact (720px)
- Both with sticky header/footer, dark theme, custom form inputs