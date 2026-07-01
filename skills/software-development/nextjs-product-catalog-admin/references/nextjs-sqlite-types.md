# Next.js + SQLite TypeScript Types: Dual-Source Pattern

## Problem

When migrating hardcoded TSX/JSX arrays to SQLite, existing components reference rich TypeScript types defined alongside data:

```typescript
// products.tsx (original)
interface Product {
  id: string;
  name: string;
  title: string;
  price: string;
  image?: string;
  features: string[];
  keywords: string[];
  metaDescription: string;
  pageDescription: string;
  description: React.ReactNode;  // JSX! Cannot go in SQLite
  pack: string;
  news?: boolean;
  categoryId: number;
  specTableId?: string;
  stockInfo?: { newPrice?: string; condition?: string };
  relatedProducts?: number[];
}
```

After migration, SQLite stores `description` as JSON text, but components still need typed access.

## Solution: Split Types

### 1. DB-facing types (snake_case, JSON fields)

```typescript
// src/lib/db.ts
export interface Category {
  id: number;
  slug: string;
  title: string;
  meta_description: string;
  page_description: string;
  image: string;
  related_categories: number[];
}

export interface Product {
  id: string;
  category_id: number;
  name: string;
  title: string;
  price: string;
  image: string;
  features: string[];
  keywords: string[];
  meta_description: string;
  page_description: string;
  pack: string;
  news: number;            // SQLite INTEGER
  stock_info: string | null;
  spec_table_id: string | null;
  template_type: string;
  template_data: string;   // JSON blob
}
```

### 2. Component-facing types (CamelCase, parsed)

```typescript
// src/lib/db.ts (same file)
export interface ProductBase {
  id: string;
  name: string;
  title: string;
  price: string;
  image: string;
  pack: string;
  metaDescription: string;
  pageDescription: string;
}

export interface ProductForCategoryPage {
  id: string;
  name: string;
  title: string;
  price: string;
  image: string;
  metaDescription: string;
  pageDescription: string;
  pack: string;
  templateType: string;
  slug: string;
  categorySlug: string;
}

export interface ProductForDetailPage {
  id: string;
  name: string;
  title: string;
  price: string;
  image: string;
  pack: string;
  metaDescription: string;
  pageDescription: string;
  templateType: string;
  keywords: string[];
  features: string[];
  specTableId: string | null;
  stockInfo: { newPrice?: string; condition?: string } | null;
  templateData: Record<string, any>;
  relatedProducts: string[];
  categorySlug: string;
}
```

### 3. Hydration helpers in db.ts

```typescript
// In the same db.ts, wrap query results with JSON.parse()
export function getProductForDetailPage(id: string): ProductForDetailPage | null {
  const row = db.prepare(`
    SELECT p.*, c.slug AS category_slug
    FROM products p
    JOIN categories c ON p.category_id = c.id
    WHERE p.id = ?
  `).get(id);

  if (!row) return null;

  return {
    id: row.id,
    name: row.name,
    title: row.title,
    price: row.price,
    image: row.image,
    pack: row.pack,
    metaDescription: row.meta_description,
    pageDescription: row.page_description,
    templateType: row.template_type,
    keywords: row.keywords ? JSON.parse(row.keywords) : [],
    features: row.features ? JSON.parse(row.features) : [],
    specTableId: row.spec_table_id,
    stockInfo: row.stock_info ? JSON.parse(row.stock_info) : null,
    templateData: row.template_data ? JSON.parse(row.template_data) : {},
    relatedProducts: [],  // populated separately or from column
    categorySlug: row.category_slug,
  };
}
```

## Component Update Strategy

Instead of updating every component's props, create a **wrapper or update the specific prop shape**:

```tsx
// Before migration — expects Product with description: ReactNode
<DetailCard {...product} description={product.description} />

// After migration — expects ProductForDetailPage with templateData
<DetailCard product={product} />
// Inside DetailCard: product.templateData.intro, product.templateData.body, ...
```

## Key Principles

1. **One db.ts file** — DB client + interfaces + hydration helpers. Do NOT split types to avoid circular imports.
2. **JSON.parse once** — at the hydration boundary, not in components.
3. **Null-safe defaults** — `JSON.parse(null)` throws. Use `row.field ? JSON.parse(row.field) : []`.
4. **Keep existing component CSS** — only change prop names, never className strings.
