# Client/server boundary and shared types — pentajunior-v2

## Rule

**Client components must never import from `@/lib/db.ts`.**

`src/lib/db.ts` imports `better-sqlite3`, which is a Node/native module. If a client component (or a shared UI component used in the admin panel) imports anything from `lib/db.ts`, Next.js includes the module in the browser bundle and `npm run build` fails with:

```
Module not found: Can't resolve 'fs'
Module not found: Can't resolve 'path'
```

## Solution

Split data types from runtime database code:

```
src/lib/types.ts   # pure TypeScript interfaces (client-safe)
src/lib/db.ts      # better-sqlite3 queries + runtime helpers (server-only)
```

### What goes in `lib/types.ts`

All entity interfaces used by both server and client:

- `Category`
- `Subcategory`
- `Product`
- `SpecTable`
- `CategoryTemplate`
- `TemplateField`

### What stays in `lib/db.ts`

- Database connection (`new Database(...)`)
- `db.prepare(...)` queries
- `getAllCategories`, `getProductById`, etc.
- Currency/format helpers that are only used server-side
- Migration code

## Usage rules

| Consumer | Import from |
|----------|-------------|
| Server components (`page.tsx` in app routes) | `@/lib/db` for data + `@/lib/types` for types |
| API routes (`route.ts`) | `@/lib/db` |
| Client components (`"use client"`) | `@/lib/types` only |
| Shared UI components used in admin | `@/lib/types` only |

## Example

Before (dangerous):

```tsx
"use client";
import type { Category } from "@/lib/db"; // type-only, currently safe
```

After (safe and explicit):

```tsx
"use client";
import type { Category } from "@/lib/types";
```

Even though a `type` import from `lib/db.ts` does not pull `better-sqlite3` into the bundle today, relying on that is fragile. A future refactor may switch the import to a value import, or add a runtime helper to `lib/db.ts`, and the build will break. Importing from `lib/types.ts` makes the boundary visible and enforceable.

## How to migrate an existing client component

1. Check the file for any `from "@/lib/db"` import.
2. If it only uses types, move the types to `src/lib/types.ts` and change the import.
3. If it imports a runtime helper (e.g., `formatPriceFull`), copy or reimplement the helper locally, or compute the value on the server and pass it as a prop.
4. Run `tsc --noEmit && rm -rf .next && npm run build` to verify.

## Related components

This rule directly applies to:

- `src/components/UI/Cards/CompactProductCard.tsx`
- `src/components/UI/Cards/ProductCard.tsx`
- `src/components/UI/CategorySidebarClient.tsx`
- `src/components/UI/Forms/FormField.tsx`
- `src/components/UI/Forms/TextAreaField.tsx`
- `src/components/UI/Forms/SelectField.tsx`
- `src/components/UI/PriceDisplay.tsx`

## Replacing `any` in shared/client data shapes

When a client or shared component receives free-form data (e.g. `template_data`, `stock_info`), do not type it as `Record<string, any>`. That reintroduces `any` into the client bundle and disables the boundary. Use this pattern instead:

```ts
// src/lib/types.ts (or a shared component file)
interface StockProduct {
  id: string;
  name: string;
  price: string | null;
  // ...
  template_data: Record<string, unknown>;
  stock_info: { newPrice?: string; condition?: string } | null;
}
```

Then narrow at the usage site:

```tsx
{typeof item.template_data.intro === 'string' && item.template_data.intro && (
  <div className="small text-muted">
    <MarkdownParagraph>{item.template_data.intro}</MarkdownParagraph>
  </div>
)}
```

Why `Record<string, unknown>` rather than a precise union?

- `template_data` is loaded from SQLite JSON and can contain strings, arrays, booleans, numbers, or nested objects depending on the template.
- A narrow union (`string | string[] | ...`) forces every consumer to satisfy the union and breaks when the DB adds a new field shape.
- `unknown` preserves type safety while allowing any JSON-serializable value. The consumer must prove the type it expects, which is exactly the right contract for data that crosses the server/client boundary.

Apply the same rule to admin editors that emit free-form template data:

```ts
interface TemplateDataEditorProps {
  templateData: Record<string, unknown>;
  onChange: (data: Record<string, unknown>) => void;
}
```

## Verification

Run a search to catch accidental violations:

```bash
cd /home/natan/pentajunior-v2
grep -R "from '@/lib/db'" src/components/ src/app/ --include="*.tsx" --include="*.ts"
grep -R "Record<string, any>" src/components/ src/app/ --include="*.tsx" --include="*.ts"
```

Any `from "@/lib/db"` match inside a `"use client"` file or shared UI component is a bug waiting to happen. Any `Record<string, any>` in shared code is a type-safety regression.
