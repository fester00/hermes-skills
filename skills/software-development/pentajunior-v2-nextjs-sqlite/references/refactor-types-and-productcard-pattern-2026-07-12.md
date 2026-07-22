# Refactor session 2026-07-12: types, ProductCard, and build gates

## Context

Code review of pentajunior-v2 identified three recurring issues:

1. `any` casts in production pages, admin editors, and shared cards.
2. `ProductCard.tsx` created a React component during render (`const TemplateComponent = getTemplateComponent(...)`), which resets state on every render and triggers `react-hooks/static-components`.
3. Build pipeline intermittently fails when `fonts.gstatic.com` is unreachable.

This reference records the exact fixes so future refactors can reuse them without re-discovering the pitfalls.

---

## Fix 1: ProductCard — do not create components during render

### Problem

```tsx
// src/components/UI/Cards/ProductCard.tsx
const TemplateComponent = getTemplateComponent(product.template_type);
return (
  <TemplateComponent name={product.name} templateData={product.template_data} />
);
```

ESLint error:

```
Error: Cannot create components during render
Components created during render will reset their state each time they are created.
```

### Solution

Since the project only uses `UniversalTemplate` in practice, import it statically and render directly:

```tsx
import { UniversalTemplate } from "@/components/ProductTemplates";

export default function ProductCard({ categorySlug, subcategorySlug, product }: ProductCardProps) {
  const category = getCategoryById(product.category_id);
  return (
    <>
      {/* ... */}
      <UniversalTemplate name={product.name} templateData={product.template_data} />
    </>
  );
}
```

If multiple templates are needed later, declare the mapping outside the component:

```tsx
const TEMPLATES: Record<string, React.ComponentType<TemplateProps>> = {
  silikon: UniversalTemplate,
  oil: UniversalTemplate,
  default: UniversalTemplate,
};

const TemplateComponent = TEMPLATES[product.template_type] || TEMPLATES.default;
return <TemplateComponent ... />;
```

The mapping table itself must be declared at module scope, not inside the render body.

---

## Fix 2: Replace `any` in production JSON-LD helpers

### Problem

```tsx
function generateSubcategoryListJsonLd(
  category: any,
  subcategories: any[],
  pageUrl: string
) { ... }
```

### Solution

Import shared types from `@/lib/types` and use them:

```tsx
import type { Category, Subcategory } from "@/lib/types";

function generateSubcategoryListJsonLd(
  category: Category,
  subcategories: Subcategory[],
  pageUrl: string
) { ... }
```

Same pattern for product/subcategory pages:

```tsx
import type { Category, Product, Subcategory } from "@/lib/types";

function generateListJsonLd(
  category: Category,
  subcategory: Subcategory,
  products: Product[],
  pageUrl: string
) { ... }

function generateProductJsonLd(
  product: Product,
  category: Category,
  subcategory: Subcategory
) { ... }

function getOfferPrice(product: Product): { price: string; priceCurrency: string } | null { ... }
```

---

## Fix 3: Free-form data in shared components (`Record<string, unknown>`)

### Problem

`template_data` and `stock_info` come from SQLite JSON and have heterogeneous shapes. Typing them as `Record<string, any>` hides bugs.

### Solution

Use `Record<string, unknown>` and narrow at the usage site:

```tsx
interface StockProduct {
  // ...
  template_data: Record<string, unknown>;
  stock_info: { newPrice?: string; condition?: string } | null;
}

// usage
{typeof item.template_data.intro === 'string' && item.template_data.intro && (
  <MarkdownParagraph>{item.template_data.intro}</MarkdownParagraph>
)}
```

For admin editors that produce free-form template data:

```tsx
interface Props {
  templateData: Record<string, unknown>;
  onChange: (data: Record<string, unknown>) => void;
}
```

---

## Fix 4: Build gate order

Always run before committing:

```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
cd /home/natan/pentajunior-v2
./node_modules/.bin/tsc --noEmit
./node_modules/.bin/eslint . --ext .ts,.tsx --max-warnings=100
rm -rf .next tsconfig.tsbuildinfo
npm run build
```

Expected: `tsc` 0 errors, `eslint` does not introduce new errors, build reaches `156/156` static pages.

---

## Fix 5: Google Fonts `fonts.gstatic.com` build outage

If `npm run build` fails with:

```
[next]/internal/font/google/inter_a21f69b3.module.css:52:8
Module not found: Can't resolve '@vercel/turbopack-next/internal/font/google/font'
```

or any `fonts.gstatic.com` fetch error, wait 30–60 seconds and retry. Transient outages are common. If the outage persists, temporarily disable the `next/font/google` Inter import in `src/app/layout.tsx` (keep a system font stack in `globals.css`), build, and restore Inter once `fonts.gstatic.com` is reachable.

See the main SKILL.md "Google Fonts can fail during build" section for the temporary fallback snippet.

---

## Files changed in this session

- `src/components/UI/Cards/ProductCard.tsx`
- `src/app/production/[category]/page.tsx`
- `src/app/production/[category]/[subcategory]/page.tsx`
- `src/app/production/[category]/[subcategory]/[product]/page.tsx`
- `src/app/news/page.tsx`
- `src/app/blog/[articleId]/page.tsx`
- `src/components/ProductTemplates/index.tsx`
- `src/components/ProductTemplates/UniversalTemplate.tsx`
- `src/components/admin/TemplateDataEditor.tsx`
- `src/components/UI/Cards/StockActionsCard.tsx`
