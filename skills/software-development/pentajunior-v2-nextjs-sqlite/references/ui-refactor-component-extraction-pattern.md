# UI component extraction pattern — pentajunior-v2

Session context: refactor of repeated page UI blocks into shared components under `src/components/UI/`, July 2026.

## Components extracted in this session

| Component | File | Replaced | Notes |
|-----------|------|----------|-------|
| `Breadcrumbs` | `src/components/UI/Breadcrumbs.tsx` | inline `<nav aria-label="Breadcrumb">` | Server component; accepts `items: { label, href? }[]` and `className?`. Last item gets `aria-current="page"`. |
| `PageHeader` | `src/components/UI/PageHeader.tsx` | inline `<h1>` + subtitle blocks | Server component; props `title`, `subtitle?`, `children?`, plus className props. Extended with `subtitleStyle?` for pages that need custom color. |
| `EmptyState` | `src/components/UI/EmptyState.tsx` | inline empty-section JSX | Server component; `icon`, `title`, `text`. Used for empty categories/subcategories/news. |
| `ProductBadges` | `src/components/UI/ProductBadges.tsx` | inline news/stock badges | Has `variant`: `card`, `catalog`, `related`, `admin`, `news`. Preserves exact badge labels and classes per context. |
| `PriceDisplay` | `src/components/UI/PriceDisplay.tsx` | inline price blocks | Initially imported `formatPriceFull` from `lib/db.ts`; this failed in admin client bundle because `better-sqlite3` needs Node `fs`. Fixed by keeping a local, dependency-free formatter. |
| `SeoTextSection` | `src/components/UI/SeoTextSection.tsx` | inline SEO text sections | Server component; `title`, `html`, optional `headingId`. |
| `CategoryCard` | `src/components/UI/Cards/CategoryCard.tsx` | `ProductsCard` + `SubcategoryCard` | Unified category + subcategory card. **Pitfall:** original `ProductsCard` had `col-xl-3`, which produced 4 cards per row on wide screens after unification. Removed to keep max 3 per row. |
| `CompactProductCard` | `src/components/UI/Cards/CompactProductCard.tsx` | inline product cards in catalog/news | Supports `variant="catalog"` and `variant="news"`. |
| `RelatedProducts` | `src/components/UI/RelatedProducts.tsx` | inline related-products block on product page | Keeps small 64×64 image layout, price with currency/unit, features. |
| `AdminModal` | `src/components/UI/AdminModal.tsx` | inline modal markup in admin pages | Supports sizes `default`, `compact`, `xl`. Footer with Save/Cancel is optional; product form supplies its own buttons. |
| `StatusToggle` | `src/components/UI/StatusToggle.tsx` | inline news/stock checkboxes | `variant="danger"` for акция. |
| `MetaFields` | `src/components/UI/MetaFields.tsx` | inline meta_title/meta_description fields | Used in admin categories (both modals) and product form. |
| `FormField` | `src/components/UI/Forms/FormField.tsx` | inline label + input fields in admin forms | Reusable text/number input with label, hint, and `wrapperClassName`. |
| `TextAreaField` | `src/components/UI/Forms/TextAreaField.tsx` | inline label + textarea fields in admin forms | Reusable textarea with configurable `rows`. |
| `SelectField` | `src/components/UI/Forms/SelectField.tsx` | inline `<select>` fields in admin forms | Reusable select with label, `options: { value, label }[]`, and `wrapperClassName`. Used for category, subcategory, currency, and unit selects. |

## Safety rules that emerged

1. **Preserve CSS classes exactly.** Pass them via props (`className`, `titleClassName`, `subtitleClassName`) rather than hard-coding in the component. This keeps `globals.css` rules attached to the same elements.
2. **Build gate after every group.** Run `tsc --noEmit && rm -rf .next && npm run build` before moving to the next component group. With 156 static pages, this catches type and bundling regressions early.
3. **Do not import `lib/db.ts` from shared UI components.** `lib/db.ts` imports `better-sqlite3`, which pulls Node `fs` into the client bundle and breaks `npm run build` with `Module not found: Can't resolve 'fs'`. Keep formatters local or pass pre-computed strings as props.
4. **Watch grid breakpoints.** When unifying cards, verify the original `col-*` classes. A stray `col-xl-3` can change 3-per-row to 4-per-row on large screens.
5. **Respect form control semantics.** `FormField` covers plain text/number inputs; keep `<select>` fields inline or create a dedicated `SelectField`, because selects need `options`, `value` coercion, and often cascade behavior (category → subcategory).
6. **Remove dead components.** After replacement, check `git grep OldComponentName` and delete old files. Stale components mislead future refactoring.
7. **Badge visibility depends on correct conditions.** In `CompactProductCard` (catalog variant) the badge block was wrapped in `{news && (...)}`, which hid the "Акция" badge when only `stock_info.newPrice` was set. The correct guard is `{(news || stockInfo?.newPrice) && (...)}` so each badge is driven by its own data source.
8. **Keep reusable form components free of DB imports.** `FormField`, `TextAreaField`, and `SelectField` are used in the admin client bundle; they must not import `@/lib/db.ts`. Any formatting/coercion stays inside the component or is passed via props.

## Git / deploy notes

- The working tree repeatedly showed a modified `package-lock.json` and `pentajunior.db.*-backup-*` / `public/images_backup_*` files. Delete DB/image backup artifacts before committing; do not touch `package-lock.json` unless the user asks.
- Each extraction group was committed separately with a clear message and pushed to `origin/master` after passing the build gate.

## When NOT to extract

- Page headers mixed with sibling controls in a single Bootstrap `row` (e.g. `/price` title + download button). Leave them inline or extend `PageHeader` to accept `children` positioned in the same row.
- Highly page-specific markup with no second consumer. Extraction for one use case adds indirection without benefit.
