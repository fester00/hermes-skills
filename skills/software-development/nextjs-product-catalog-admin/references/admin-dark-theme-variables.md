# Admin Dark Theme CSS Variables (PentaJunior v2)

## Context

When adding an admin panel to an existing Next.js + Bootstrap site, the default
Bootstrap light theme clashes with a dark admin aesthetic. The public site
uses light Bootstrap cards/buttons, but the admin area needs a dark graphite
surface with olive accent colors.

## Variable System

Define these CSS custom properties in `globals.css` (or a dedicated
`admin-theme.css`):

```css
/* ── Admin Theme Tokens ── */
.admin-app {
  --admin-bg: #1a1a2e;            /* deepest background */
  --admin-surface: #242430;        /* cards, modals, table rows */
  --admin-surface-hover: #2a2a3a; /* row hover */
  --admin-border: rgba(139, 148, 158, 0.2);
  --admin-text: #c9d1d9;           /* primary readable text */
  --admin-muted: #8b949e;          /* secondary/muted text */
  --admin-olive: #6b8e23;          /* accent color (buttons, focus) */
  --admin-olive-light: #8fbc8f;
  --admin-input-bg: #2a2a3a;

  background: var(--admin-bg);
  color: var(--admin-text);
  min-height: 100vh;
}
```

## Page Title Visibility Fix

Bootstrap `h2` defaults to dark color (`#212529`), which becomes invisible on
the dark admin background. Never rely on default Bootstrap heading colors in a
dark theme.

```css
.admin-page-title {
  color: var(--admin-text) !important;
  font-weight: 600;
  margin-bottom: 1.5rem;
}
```

Usage in page components:
```tsx
<h2 className="admin-page-title">Категории <span className="text-muted">(12)</span></h2>
```

## Component Token Mapping

| Element | Class | Key properties |
|---|---|---|
| App shell | `.admin-app` | `background: var(--admin-bg)` |
| Topbar | `.admin-topbar` | `background: var(--admin-surface)`, `border-bottom` |
| Sidebar | `.admin-sidebar` | `background: var(--admin-surface)`, `border-right` |
| Nav item | `.admin-nav-item` | `color: var(--admin-muted)`, `border-left` active indicator |
| Main content | `.admin-main` | `background: var(--admin-bg)`, `padding` |
| Table | `.admin-table` | `color: var(--admin-text)`, row hover `var(--admin-surface-hover)` |
| Table header | `.admin-table thead th` | `color: var(--admin-muted)`, `border-bottom` |
| Card | `.admin-card` | `background: var(--admin-surface)`, `border`, `shadow` |
| Button primary | `.btn-admin-primary` | `background: var(--admin-olive)`, `border: none` |
| Button default | `.btn-admin` | `background: var(--admin-surface-hover)`, `border` |
| Input | `.admin-input` | `background: var(--admin-input-bg)`, `border`, `color` |
| Login bg | `.admin-login-bg` | `background: var(--admin-bg)`, `min-height: 100vh` |

## Mobile Adaptation

```css
@media (max-width: 768px) {
  .admin-sidebar {
    position: fixed;
    z-index: 1040;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  .admin-sidebar.is-open {
    transform: translateX(0);
  }
  .admin-main {
    margin-left: 0 !important;
  }
}
```

## Integration Notes

- The `.admin-app` wrapper should be applied at the admin layout level
  (`src/app/admin/layout.tsx`) so all admin pages inherit the dark palette.
- Public pages (outside `/admin/*`) should NOT have `.admin-app` — they
  continue using the default Bootstrap light theme.
- The `!important` in `.admin-page-title` is defensive: Bootstrap's `h2`
  color rule has high specificity, and without `!important` the title
  can remain dark-on-dark invisible.

## Real-World Usage

Applied in PentaJunior v2 admin panel:
- `.admin-page-title` on `/admin`, `/admin/products`, `/admin/categories`
- `.admin-modal-dialog`, `.admin-modal-content`, `.admin-modal-header`,
  `.admin-modal-footer`, `.admin-modal-body` in product/category CRUD modals
- `.admin-table` for product/category listing tables
- `.admin-input`, `.admin-label` for all form fields in modals