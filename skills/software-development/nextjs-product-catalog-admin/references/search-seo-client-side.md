# Search & SEO: Client-Side Migration Pattern

## Problem

Original project imported `products` and `categories` arrays directly into `Searcher.tsx`:

```tsx
// BEFORE — imports data at build time
import { products } from "@/data/products";
import { categories } from "@/data/categories";

export default function Searcher() {
  const [results, setResults] = useState(
    products.map(p => ({ ...p, type: 'product' }))
  );
  // ...
}
```

After SQLite migration, these imports are gone. Search must work without bundling the entire database into client JS.

## Solution: Client-Side API Fetch

### 1. Create API endpoint

```tsx
// app/api/search/route.ts
import { NextResponse } from "next/server";
import Database from "better-sqlite3";
import path from "path";

const db = new Database(path.join(process.cwd(), "pentajunior.db"), { readonly: true });

export async function GET() {
  const products = db.prepare("SELECT id, name, title, keywords FROM products").all();
  const categories = db.prepare("SELECT id, slug, title FROM categories").all();

  return NextResponse.json({
    products: products.map((p: any) => ({
      id: p.id,
      name: p.name,
      title: p.title,
      keywords: p.keywords ? JSON.parse(p.keywords) : [],
    })),
    categories: categories.map((c: any) => ({
      id: c.id,
      slug: c.slug,
      title: c.title,
    })),
  });
}
```

### 2. Client-side Searcher component

```tsx
// src/components/Searcher.tsx
"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { slugify } from "@/lib/product-utils";

interface SearchItem {
  id: string | number;
  name?: string;
  title: string;
  keywords?: string[];
  slug?: string;
  type: "product" | "category";
}

export default function Searcher() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [allItems, setAllItems] = useState<SearchItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/search")
      .then(r => r.json())
      .then(data => {
        const items: SearchItem[] = [
          ...data.products.map((p: any) => ({
            ...p, type: "product" as const,
            title: p.name || p.title,
          })),
          ...data.categories.map((c: any) => ({
            ...c, type: "category" as const,
          })),
        ];
        setAllItems(items);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const results = useMemo(() => {
    if (!query.trim()) return allItems;
    const q = query.toLowerCase();
    return allItems.filter(item =>
      item.title?.toLowerCase().includes(q) ||
      item.keywords?.some((k: string) => k.toLowerCase().includes(q))
    );
  }, [query, allItems]);

  // ... render results
}
```

## Key Principles

1. **API returns lightweight JSON** — only fields needed for search (id, name, keywords), not full product data.
2. **Client fetches once** on mount, then filters in-memory. No per-keystroke API calls.
3. **Search remains instant** — dataset is small (~60 products + 12 categories = ~5KB JSON).
4. **No database in browser** — `better-sqlite3` stays server-side only.

## Sitemap.ts After Migration

```typescript
// app/sitemap.ts
import { MetadataRoute } from "next";
import { db } from "@/lib/db";

export default function sitemap(): MetadataRoute.Sitemap {
  const categories = db.prepare("SELECT slug, title FROM categories").all();
  const products = db.prepare("SELECT id, c.slug AS category_slug FROM products p JOIN categories c ON p.category_id = c.id").all();
  const articles = db.prepare("SELECT id FROM articles").all();  // if articles in DB

  const routes: MetadataRoute.Sitemap = [
    { url: "https://pentajunior.ru", lastModified: new Date() },
    { url: "https://pentajunior.ru/contacts", lastModified: new Date() },
    { url: "https://pentajunior.ru/price", lastModified: new Date() },
    { url: "https://pentajunior.ru/news", lastModified: new Date() },
    { url: "https://pentajunior.ru/production", lastModified: new Date() },
    ...categories.map((c: any) => ({
      url: `https://pentajunior.ru/production/${c.slug}`,
      lastModified: new Date(),
      changeFrequency: "weekly" as const,
    })),
    ...products.map((p: any) => ({
      url: `https://pentajunior.ru/production/${p.category_slug}/${p.id}`,
      lastModified: new Date(),
      changeFrequency: "weekly" as const,
    })),
  ];

  return routes;
}
```

## robots.ts After Migration

```typescript
// app/robots.ts
import { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/policy", "/admin"],
    },
    sitemap: "https://pentajunior.ru/sitemap.xml",
  };
}
```

## JSON-LD After Migration

```tsx
// Inside product detail page — generate JSON-LD from DB data
const jsonLd = {
  "@context": "https://schema.org",
  "@type": "Product",
  name: product.name,
  description: product.metaDescription,
  brand: { "@type": "Brand", name: "Penta" },
  offers: {
    "@type": "Offer",
    price: product.price?.replace(/\D/g, ""),
    priceCurrency: "RUB",
    availability: "https://schema.org/InStock",
  },
};

// In JSX:
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
/>
```

## Anti-patterns

| ❌ Don't | ✅ Do |
|---|---|
| Import DB client in "use client" component | Fetch from `/api/search` endpoint |
| Return full product rows from API | Return only search-needed fields |
| Call API on every keystroke | Fetch once, filter client-side |
| Hardcode URLs in sitemap | Generate from DB query |
| Skip JSON-LD on product pages | Always include structured data |

## References

- `references/jsx-to-sqlite-migration.md` — Parsing original data into SQLite
- `references/nextjs-sqlite-types.md` — TypeScript type patterns
- `references/nextjs-sqlite-build-setup.md` — DB client and build setup
- `references/product-template-mapping.md` — Template component architecture
