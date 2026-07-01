## Pentajunior-v2 sidebar — variant 1 implementation

Reference file: `/home/natan/workspace/sidebar-design-variants.html`

### Component split
- `src/components/UI/CategorySidebar.tsx` — server component, loads categories/subcategories/products and passes data.
- `src/components/UI/CategorySidebarClient.tsx` — client component (`"use client"`), owns expansion state.

### Mechanics
1. Categories with subcategories render as `<Link>` with `onClick` handler that calls `e.preventDefault()` and toggles `is-expanded` via `useState`.
2. Categories without subcategories render as plain `<Link>`.
3. Subcategories render as plain `<Link>`.
4. Active category is expanded by default.
5. CSS uses `max-height: 0` → `max-height: 600px` with `transition` for smooth animation.

### Visual style
- Title: uppercase, small, muted, left-aligned.
- Active category: `background: var(--olive-green)`.
- Active subcategory: `background: rgba(109, 219, 133, 0.15)`.
- Accent line: 4px dark bar on the left of active category.
- Count badge: right-aligned, muted, no background pill.
- No chevrons/accordions icons (matches variant 1 exactly).

### Integration
```tsx
// on category page
<CategorySidebar activeCategorySlug={categorySlug} />

// on subcategory / product pages
<CategorySidebar
  activeCategorySlug={categorySlug}
  activeSubcategorySlug={subcategorySlug}
/>
```

### CSS classes
- `.category-sidebar`
- `.category-sidebar-title`
- `.category-sidebar-list`
- `.category-sidebar-item`
- `.category-sidebar-link`
- `.category-sidebar-count`
- `.category-sidebar-sublist`
- `.is-expanded`
