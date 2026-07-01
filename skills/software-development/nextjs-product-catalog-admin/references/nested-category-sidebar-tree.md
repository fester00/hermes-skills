# Nested-tree sidebar for categories + subcategories

When subcategories exist, render the sidebar as one nested tree instead of two separate flat blocks (`Категории` + `Подкатегории`). This matches user preference from `pentajunior-v2` and improves scannability.

For a complete, production-tested component implementation (extracted into a reusable server component with smooth expand/collapse, olive/mint active states, and separated counters), see `references/category-sidebar-variant1-implementation.md`. The patterns below show the older inline markup that the component replaced.

## Target structure

```
Категории
├── Силикон для заливки форm 17 [active]
│     ├── Платиновый силикон 5
│     ├── Оловянный силикон 8
│     ├── Полиуретановые компаунды 3
│     └── Наполнители для силикона 1
├── Силиконовые смазки 7
├── Масла ПМС 9
└── ...
```

## React/Next.js pattern

Inside the catch-all category page component:

```tsx
<ul className="category-sidebar-list list-unstyled mb-0">
  {categories.map((c) => {
    const count = products.filter((p) => p.category_id === c.id).length;
    const isCurrentCategory = c.slug === categorySlug;
    const categorySubcategories = subcategories.filter((s) => s.category_id === c.id);
    const hasSubcategories = categorySubcategories.length > 0;

    return (
      <li key={c.id} className={isCurrentCategory ? "is-expanded" : ""}>
        <Link
          href={c.href}
          className={`category-sidebar-link ${isCurrentCategory && !subcategory ? "active" : ""}`}
        >
          <span>{c.title}</span>
          <span className="category-sidebar-count">{count}</span>
        </Link>

        {hasSubcategories && (
          <ul className="category-sidebar-sublist list-unstyled">
            {categorySubcategories.map((s) => {
              const subCount = getProductCountBySubcategoryId(s.id);
              const isActive = isCurrentCategory && s.slug === subcategorySlug;
              return (
                <li key={s.id}>
                  <Link
                    href={`/production/${c.slug}/${s.slug}`}
                    className={`category-sidebar-link ${isActive ? "active" : ""}`}
                  >
                    <span>{s.title}</span>
                    <span className="category-sidebar-count">{subCount}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        )}
      </li>
    );
  })}
</ul>
```

## CSS hardening

```css
.category-sidebar-sublist {
  margin-top: 0.25rem;
  margin-bottom: 0.5rem;
  padding-left: 0.75rem;
  border-left: 2px solid var(--color-border-light);
}

.category-sidebar-sublist .category-sidebar-link {
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  font-weight: 400;
}

.category-sidebar-sublist .category-sidebar-link.active {
  background: linear-gradient(135deg, var(--olive-green), var(--olive-light));
  color: #fff;
}

.category-sidebar-list > li.is-expanded > .category-sidebar-link {
  font-weight: 700;
}
```

## UX rules

- Show subcategories only under their parent category, not globally.
- Highlight the active category when no subcategory is selected; highlight the active subcategory otherwise.
- Keep counts accurate using the same helper used elsewhere (e.g. `getProductCountBySubcategoryId`).
- Do not render an additional `Подкатегории` heading or block when using this pattern.
- Active parent category can be visually expanded (`is-expanded`) so its children are visible.

## Pitfalls

- Avoid generating the subcategory list from `allSubcategories` globally. If you do, every category will appear to own every subcategory.
- Do not mix this pattern with the older separate `Подкатегории` block; remove the old block entirely.
- Ensure active-state logic distinguishes "category selected" from "subcategory selected" to avoid two active links.
