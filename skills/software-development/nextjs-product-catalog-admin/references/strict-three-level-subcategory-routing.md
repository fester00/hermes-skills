# Strict three-level routing: /category/subcategory/product

Use this recipe when **every product in the catalog has a `subcategory_id`**.
At that point the optional catch-all `[[...rest]]` is no longer needed and can be replaced with explicit App Router routes.

## When to switch

Run:

```sql
SELECT COUNT(*) FROM products WHERE subcategory_id IS NULL;
```

If the result is `0`, the catalog is fully three-level and you can switch.

## Route structure

```
src/app/production/[category]/page.tsx
src/app/production/[category]/[subcategory]/page.tsx
src/app/production/[category]/[subcategory]/[product]/page.tsx
```

Remove:

```
src/app/production/[categorySlug]/[[...rest]]/page.tsx
```

## DB helper needed

Add a slug-only lookup for subcategories so product/subcategory pages do not need the parent category ID:

```ts
// src/lib/db.ts
export function getSubcategoryBySlug(slug: string): Subcategory | undefined {
  const row = db.prepare('SELECT * FROM subcategories WHERE slug = ?').get(slug) as any;
  if (!row) return undefined;
  return { ...row };
}
```

Keep `getSubcategoryBySlugAndCategoryId(categoryId, slug)` if admin pages still need the stricter lookup.

## generateStaticParams

### Category page

```tsx
export function generateStaticParams() {
  return getAllCategories().map((category) => ({
    category: category.slug,
  }));
}
```

### Subcategory page

```tsx
export function generateStaticParams() {
  const params: { category: string; subcategory: string }[] = [];
  for (const category of getAllCategories()) {
    for (const sub of getSubcategoriesByCategoryId(category.id)) {
      params.push({ category: category.slug, subcategory: sub.slug });
    }
  }
  return params;
}
```

### Product page

```tsx
export function generateStaticParams() {
  const params: { category: string; subcategory: string; product: string }[] = [];
  for (const category of getAllCategories()) {
    for (const sub of getSubcategoriesByCategoryId(category.id)) {
      for (const product of getProductsBySubcategoryId(sub.id)) {
        params.push({
          category: category.slug,
          subcategory: sub.slug,
          product: product.id,
        });
      }
    }
  }
  return params;
}
```

## Validation in product page

A product page must verify that the product actually belongs to the requested category and subcategory, otherwise call `notFound()`:

```tsx
const category = getCategoryBySlug(categorySlug);
const subcategory = getSubcategoryBySlug(subcategorySlug);
const product = products.find((p) => p.id === productId);

if (!category || !subcategory || !product) notFound();
if (product.category_id !== category.id) notFound();
if (product.subcategory_id !== subcategory.id) notFound();
```

This prevents a URL like `/production/cat-A/sub-B/product-of-sub-C` from rendering the wrong product.

## Redirects from old flat URLs

Old URLs looked like `/production/[category]/[productId]`. Because the strict routes no longer define `/production/[category]/[product]`, Next.js can generate redirects for those paths without route conflicts.

Generate one redirect per product in `next.config.ts`:

```ts
async redirects() {
  const Database = (await import('better-sqlite3')).default;
  const path = (await import('path')).default;
  const db = new Database(path.join(process.cwd(), 'pentajunior.db'));

  const categories = db.prepare('SELECT id, slug FROM categories').all() as { id: number; slug: string }[];
  const subcategories = db.prepare('SELECT id, category_id, slug FROM subcategories').all() as { id: number; category_id: number; slug: string }[];
  const products = db.prepare('SELECT id, category_id, subcategory_id FROM products WHERE subcategory_id IS NOT NULL').all() as { id: string; category_id: number; subcategory_id: number }[];

  const categoryMap = new Map(categories.map((c) => [c.id, c]));
  const subcategoryMap = new Map(subcategories.map((s) => [s.id, s]));

  const productRedirects = products
    .map((p) => {
      const category = categoryMap.get(p.category_id);
      const subcategory = subcategoryMap.get(p.subcategory_id);
      if (!category || !subcategory) return null;
      return {
        source: `/production/${category.slug}/${p.id}`,
        destination: `/production/${category.slug}/${subcategory.slug}/${p.id}`,
        permanent: true,
      };
    })
    .filter(Boolean) as { source: string; destination: string; permanent: boolean }[];

  db.close();

  return [
    { source: '/sitemap', destination: '/sitemap.xml', permanent: true },
    ...productRedirects,
  ];
}
```

### What NOT to do

Do **not** use a category-level wildcard redirect like:

```ts
// WRONG
{
  source: '/production/:category/:path',
  destination: '/production/:category/:firstSubcategory/:path',
  permanent: true,
}
```

This sends every old product URL in the category to the first subcategory in the database, regardless of which subcategory actually owns the product. Test with:

```bash
curl -I http://localhost:3001/production/silikon-dlya-zalivki-form/unisil-9500
# Expect: HTTP/1.1 308 Permanent Redirect
# Location: /production/silikon-dlya-zalivki-form/silikon-platinovyj-dla-form/unisil-9500
```

## URL builders

Update every product URL helper to include the subcategory:

```ts
// src/lib/product-utils.ts
export function getProductHref(product: { id: string; category_id: number; subcategory_id?: number | null }): string {
  const category = getAllCategories().find((c) => c.id === product.category_id);
  if (!category) return `/production/${product.id}`;

  const subcategory = product.subcategory_id
    ? getAllSubcategories().find((s) => s.id === product.subcategory_id)
    : null;

  return subcategory
    ? `/production/${category.slug}/${subcategory.slug}/${product.id}`
    : `/production/${category.slug}/${product.id}`;
}
```

Also update:
- search API (`/app/api/search/route.ts`);
- stock/promo card (`StockActionsCard.tsx`);
- blog related products;
- sitemap.

## Verification

Run the verification script or manually check:

```bash
# category page
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3001/production/silikon-dlya-zalivki-form

# subcategory page
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3001/production/silikon-dlya-zalivki-form/silikon-platinovyj-dla-form

# product page
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3001/production/silikon-dlya-zalivki-form/silikon-platinovyj-dla-form/unisil-9500

# old flat URL redirect
curl -I http://localhost:3001/production/silikon-dlya-zalivki-form/unisil-9500
```

## Port separation from legacy project

If the legacy `pentajunior` project is already served by PM2 on port 3000, run `pentajunior-v2` on a different port (3001/3002) and update `ecosystem.config.js`:

```js
module.exports = {
  apps: [
    {
      name: 'pentajunior-v2',
      script: './node_modules/next/dist/bin/next',
      args: 'start --port 3001',
      cwd: '/home/natan/pentajunior-v2',
      interpreter: '/home/natan/.nvm/versions/node/v24.13.1/bin/node',
      env: {
        NODE_ENV: 'production',
        PORT: 3001,
      },
      // ... rest of config
    },
  ],
};
```

Then start/stop with PM2:

```bash
pm2 start ecosystem.config.js
pm2 save
```

When switching back to the legacy project on port 3000, restore its `ecosystem.config.js` with `PORT: 3000` and `pm2 start` it again. Do not delete the legacy config; keep both apps in separate directories with their own PM2 names.
