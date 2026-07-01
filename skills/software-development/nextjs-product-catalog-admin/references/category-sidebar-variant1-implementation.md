# CategorySidebar component — Variant 1 (minimalism with accent line + accordion)

This is the concrete implementation used in `pentajunior-v2` after the user selected "Variant 1" from a side-by-side HTML prototype. It replaces the older inline nested-tree sidebar markup with a reusable, animated accordion sidebar.

## Architecture: split server/client

`better-sqlite3` cannot run in the browser bundle. Therefore the sidebar is split into two files:

- `src/components/UI/CategorySidebar.tsx` — **server component**, reads categories/products from `better-sqlite3` and passes plain data down.
- `src/components/UI/CategorySidebarClient.tsx` — **client component** (`"use client"`), holds the expand/collapse state and renders the interactive UI.

This split keeps the production pages static and avoids the `Module not found: Can't resolve 'fs'` build error that occurs if a client component imports `@/lib/db`.

## Server component

`src/components/UI/CategorySidebar.tsx`

```tsx
import {
  getAllCategories,
  getAllProducts,
  getSubcategoriesByCategoryId,
  getProductCountBySubcategoryId,
} from "@/lib/db";
import CategorySidebarClient from "./CategorySidebarClient";

interface CategorySidebarProps {
  activeCategorySlug: string;
  activeSubcategorySlug?: string;
  title?: string;
}

export default function CategorySidebar({
  activeCategorySlug,
  activeSubcategorySlug,
  title = "Категории",
}: CategorySidebarProps) {
  const categories = getAllCategories();
  const products = getAllProducts();

  const subcategoriesByCategory: Record<number, ReturnType<typeof getSubcategoriesByCategoryId>> = {};
  const productCountBySubcategory: Record<number, number> = {};

  for (const category of categories) {
    const subs = getSubcategoriesByCategoryId(category.id);
    subcategoriesByCategory[category.id] = subs;
    for (const sub of subs) {
      productCountBySubcategory[sub.id] = getProductCountBySubcategoryId(sub.id);
    }
  }

  return (
    <CategorySidebarClient
      categories={categories}
      products={products}
      subcategoriesByCategory={subcategoriesByCategory}
      productCountBySubcategory={productCountBySubcategory}
      activeCategorySlug={activeCategorySlug}
      activeSubcategorySlug={activeSubcategorySlug}
      title={title}
    />
  );
}
```

## Client component

`src/components/UI/CategorySidebarClient.tsx`

```tsx
"use client";

import { useState } from "react";
import Link from "next/link";
import type { Category, Product, Subcategory } from "@/lib/db";

interface CategorySidebarClientProps {
  categories: Category[];
  products: Product[];
  subcategoriesByCategory: Record<number, Subcategory[]>;
  productCountBySubcategory: Record<number, number>;
  activeCategorySlug: string;
  activeSubcategorySlug?: string;
  title?: string;
}

export default function CategorySidebarClient({
  categories,
  products,
  subcategoriesByCategory,
  productCountBySubcategory,
  activeCategorySlug,
  activeSubcategorySlug,
  title = "Категории",
}: CategorySidebarClientProps) {
  const [expanded, setExpanded] = useState<Set<number>>(() => {
    const activeId = categories.find((c) => c.slug === activeCategorySlug)?.id;
    return activeId ? new Set([activeId]) : new Set<number>();
  });

  const toggleCategory = (categoryId: number, hasSubcategories: boolean) => {
    if (!hasSubcategories) return;
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(categoryId)) {
        next.delete(categoryId);
      } else {
        next.add(categoryId);
      }
      return next;
    });
  };

  return (
    <aside className="col-lg-4 d-none d-lg-block z-0">
      <div className="category-sidebar">
        <h3 className="category-sidebar-title">{title}</h3>
        <ul className="category-sidebar-list list-unstyled mb-0">
          {categories.map((category) => {
            const categoryCount = products.filter(
              (p) => p.category_id === category.id
            ).length;
            const isCurrentCategory = category.slug === activeCategorySlug;
            const subcategories = subcategoriesByCategory[category.id] || [];
            const hasSubcategories = subcategories.length > 0;
            const isExpanded = expanded.has(category.id);

            return (
              <li
                key={category.id}
                className={`category-sidebar-item ${
                  isExpanded ? "is-expanded" : ""
                }`}
              >
                <div className="category-sidebar-row">
                  <Link
                    href={`/production/${category.slug}`}
                    className={`category-sidebar-link ${
                      isCurrentCategory ? "active" : ""
                    }`}
                  >
                    <span className="category-sidebar-label">
                      {category.title}
                    </span>
                    <span className="category-sidebar-count">
                      {categoryCount}
                    </span>
                  </Link>

                  {hasSubcategories && (
                    <button
                      type="button"
                      onClick={() =>
                        toggleCategory(category.id, hasSubcategories)
                      }
                      className={`category-sidebar-toggle-btn ${
                        isExpanded ? "is-expanded" : ""
                      }`}
                      aria-expanded={isExpanded}
                      aria-label={
                        isExpanded
                          ? `Свернуть подкатегории ${category.title}`
                          : `Развернуть подкатегории ${category.title}`
                      }
                    >
                      <i
                        className={`bi bi-chevron-down category-sidebar-chevron ${
                          isExpanded ? "is-rotated" : ""
                        }`}
                        aria-hidden="true"
                      />
                    </button>
                  )}
                </div>

                {hasSubcategories && (
                  <ul className="category-sidebar-sublist list-unstyled">
                    {subcategories.map((sub) => {
                      const subCount = productCountBySubcategory[sub.id] ?? 0;
                      const isActive =
                        isCurrentCategory &&
                        sub.slug === activeSubcategorySlug;
                      return (
                        <li key={sub.id}>
                          <Link
                            href={`/production/${category.slug}/${sub.slug}`}
                            className={`category-sidebar-link ${
                              isActive ? "active" : ""
                            }`}
                          >
                            <span className="category-sidebar-label">
                              {sub.title}
                            </span>
                            <span className="category-sidebar-count">
                              {subCount}
                            </span>
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
      </div>
    </aside>
  );
}
```

### Variant-1 toggle mechanic — split link + chevron button

The original HTML prototype (Variant 1) shows the category row itself as an `<a>` tag. In production, however, a single `Link` with `preventDefault()` does **not** reliably perform both jobs (navigation + accordion) because Next.js intercepts clicks and the user may expect the category name to navigate while the chevron only expands the tree. The durable React pattern is:

- **Category name** → a `Link` that always navigates to `/production/{category.slug}`. This updates the right-hand content area to the category page.
- **Chevron button** → a separate `<button type="button">` that toggles the subcategory list inside the sidebar only.
- **Categories without subcategories** → only the `Link`, no chevron button.
- **Subcategory links** → plain `Link` elements that always navigate.

This gives two independent hit targets and matches the user's mental model: "click the name to go there, click the arrow to see children."

## Usage on production routes

Use inside each production page that needs the sidebar:

```tsx
// /production/[category]/page.tsx
<div className="row">
  <CategorySidebar activeCategorySlug={categorySlug} />
  <div className="col-lg-8">{/* main content */}</div>
</div>

// /production/[category]/[subcategory]/page.tsx
<div className="row">
  <CategorySidebar
    activeCategorySlug={categorySlug}
    activeSubcategorySlug={subcategorySlug}
  />
  <div className="col-lg-8">{/* main content */}</div>
</div>

// /production/[category]/[subcategory]/[product]/page.tsx
<div className="row">
  <CategorySidebar
    activeCategorySlug={categorySlug}
    activeSubcategorySlug={subcategorySlug}
  />
  <div className="col-lg-8">{/* ProductCard and related blocks */}</div>
</div>
```

## CSS

Add or replace the existing `.category-sidebar-*` block in `src/app/globals.css`:

```css
.category-sidebar-wrap {
  position: relative;
  width: 100%;
}

.category-sidebar {
  background: #fff;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 1.25rem;
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 90px;
  min-width: 250px;
}

.category-sidebar-title {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-text-muted);
  margin-bottom: 1.25rem;
  padding-bottom: 0.875rem;
  border-bottom: 1px solid var(--color-border-light);
  text-align: left;
}

.category-sidebar-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.category-sidebar-item {
  margin-bottom: 0.25rem;
}

.category-sidebar-row {
  display: flex;
  align-items: stretch;
  gap: 0.25rem;
}

.category-sidebar-link {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex: 1 1 auto;
  min-width: 0;
  padding: 0.75rem 0.875rem;
  border-radius: var(--radius-md);
  text-decoration: none;
  color: var(--color-text);
  font-size: 0.9375rem;
  font-weight: 500;
  transition: all var(--transition-fast);
  position: relative;
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  gap: 0.75rem;
}

.category-sidebar-link:hover {
  background: #f8f9fa;
  color: var(--color-primary-hover);
}

.category-sidebar-link.active {
  background: var(--olive-green) !important;
  color: var(--color-dark) !important;
  font-weight: 600 !important;
}

.category-sidebar-link.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  bottom: 8px;
  width: 4px;
  background: var(--color-dark);
  border-radius: 0 4px 4px 0;
}

.category-sidebar-label {
  flex: 1 1 auto;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.category-sidebar-count {
  flex: 0 0 auto;
  font-size: 0.8rem;
  color: var(--color-text-muted);
  font-weight: 500;
  transition: color var(--transition-fast);
  background: transparent;
  padding: 0;
  min-width: auto;
}

.category-sidebar-link.active .category-sidebar-count,
.category-sidebar-link:hover .category-sidebar-count {
  color: var(--color-dark);
}

.category-sidebar-toggle-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  flex: 0 0 auto;
  padding: 0;
  border: none;
  background: transparent;
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.category-sidebar-toggle-btn:hover {
  background: #f8f9fa;
  color: var(--color-primary-hover);
}

.category-sidebar-chevron {
  font-size: 0.875rem;
  transition: transform 0.35s ease;
}

.category-sidebar-chevron.is-rotated {
  transform: rotate(180deg);
}

.category-sidebar-item.is-expanded > .category-sidebar-row > .category-sidebar-link {
  font-weight: 700;
}

.category-sidebar-item.is-expanded > .category-sidebar-row > .category-sidebar-link.active {
  font-weight: 600;
}

.category-sidebar-sublist {
  margin: 0.25rem 0 0.5rem 1rem;
  padding: 0 0 0 1rem;
  border-left: 2px solid var(--color-border-light);
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition: max-height 0.35s ease, opacity 0.3s ease;
}

.category-sidebar-item.is-expanded .category-sidebar-sublist {
  max-height: 600px;
  opacity: 1;
}

.category-sidebar-sublist .category-sidebar-link {
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  font-weight: 400;
  color: var(--color-text-muted);
}

.category-sidebar-sublist .category-sidebar-link:hover {
  background: #f8f9fa;
  color: var(--color-primary-hover);
}

.category-sidebar-sublist .category-sidebar-link.active {
  background: rgba(109, 219, 133, 0.15) !important;
  color: var(--color-dark) !important;
  font-weight: 600 !important;
}

.category-sidebar-sublist .category-sidebar-link.active::before {
  display: none;
}

.category-sidebar-sublist .category-sidebar-link.active .category-sidebar-count,
.category-sidebar-sublist .category-sidebar-link:hover .category-sidebar-count {
  color: var(--color-dark);
}

@media (max-width: 991.98px) {
  .category-sidebar-wrap,
  aside.col-lg-4.d-none.d-lg-block.z-0 {
    display: none !important;
  }
}
```

## Design decisions

- **Active category** → olive green background (`var(--olive-green)`), dark text, left accent bar.
- **Active subcategory** → mint green wash (`rgba(109, 219, 133, 0.15)`), dark text, no accent bar (to avoid visual competition with the parent).
- **Counters** are pushed to the right with a separate meta wrapper so they never stick to the label text.
- **Smooth expand** uses `max-height` transition on `.category-sidebar-sublist` controlled by parent `.is-expanded`.
- **Chevron** rotates 180° when the category is expanded.
- **Ellipsis** on labels prevents long subcategory names from breaking the row layout.
- **Mobile** is hidden with `d-none d-lg-block` on the wrapper.

## Why split server/client?

Do **not** import `@/lib/db` directly into a client component (`"use client"`). `better-sqlite3` depends on Node.js built-ins (`fs`, `path`, bindings) and the build will fail with:

```
Module not found: Can't resolve 'fs'
```

Instead:

1. Read data in a server component or server action.
2. Serialize the data into JSON-serializable props.
3. Pass the props to a small client component that only handles interactivity.

This pattern also applies to any other component that needs both DB data and React state/effects/event handlers.

## Pitfalls

1. **Do not use a single `Link` with `preventDefault()` for both navigation and accordion.** Next.js `Link` intercepts clicks; a single link that sometimes navigates and sometimes toggles is confusing and unreliable. Use a **separate chevron button** for expand/collapse and keep the category name as a normal navigation `Link`.
2. **Do not omit the `col-lg-4` wrapper class.** The outer element of the sidebar must carry Bootstrap's `col-lg-4` class so it sits in the left column of the page's `.row`. If the component is placed directly inside `.row` without a column class, it will render full-width above the content.
3. **Active-state collision:** if you only highlight the category when `!activeSubcategorySlug`, the parent category will not be highlighted on subcategory pages. Highlight the parent category whenever it matches `activeCategorySlug`.
4. **Counter sticking to label:** use `gap` on the flex row (or a separate `.category-sidebar-meta` wrapper with `margin-left`) so the count is visually separated from the label. Never render `{title}{count}` as adjacent text nodes.
5. **Client component importing DB helpers:** never do `import { getAllCategories } from "@/lib/db"` inside a `"use client"` file. `better-sqlite3` depends on Node.js built-ins and the build will fail with `Module not found: Can't resolve 'fs'`. Split the component instead.
6. **Hydration mismatch with default expanded state:** initialize the `expanded` Set lazily inside the `useState` callback so the server-rendered HTML and the client initial state agree. If you compute it conditionally after mount, the markup will differ.
7. **Make sure the chevron button does not submit forms.** Always use `type="button"` on the toggle button; the default `type="submit"` can accidentally submit an admin or search form if the sidebar is rendered inside one.
8. **Categories without subcategories must not render an expand button.** Check `subcategories.length > 0` before rendering the toggle button; otherwise users see a useless chevron that does nothing.

## Verification

After implementing:

```bash
curl -s http://localhost:3001/production/silikon-dlya-zalivki-form/silikon-platinovyj-dla-form \
  | grep -E "category-sidebar-link active|category-sidebar-sublist" | head -10
```

Visually and interactively confirm:
- clicking a category **name** navigates to the category page and updates the right-hand content;
- clicking a category **chevron** expands/collapses its subcategory list in the sidebar without navigation;
- active category has olive background;
- active subcategory has mint wash;
- counts are separated from labels;
- the menu sits in a left column, not full-width above content;
- only categories with subcategories show a chevron.

## See also

- `references/nested-category-sidebar-tree.md` — general nested-tree pattern.
- `references/design-variant-prototyping.md` — how the variant-1 design was chosen via an HTML prototype.
- `references/nextjs-dev-server-cache-invalidation.md` — restart `next start` after each build when verifying CSS/JS changes.
