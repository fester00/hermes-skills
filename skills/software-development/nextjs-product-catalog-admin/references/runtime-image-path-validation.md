# Runtime Image Path Validation: Broken File Cleanup

## Context

In a Next.js project using `next/image` (or standard `<img>`), if a product's
`image` field in the database points to a file that does NOT exist in
`public/`, the image component fails silently — the block renders empty or
shows a broken-image icon instead of a fallback placeholder.

This was discovered in PentaJunior v2 (2025-06-12) where 5 products
(`unicast-100`, `uniflex-110`, `unisil-9510`, `unisil-9520`, `unisil-9629`)
had `image` values like `/images/RTV/unicast100.png` but the actual PNG files
were missing. The `ProductImage` component checked `product.image ? <Image ...>
: <ProductImagePlaceholder />`, but `product.image` was truthy (a string),
so `Image` attempted to load a 404 URL — rendering a blank block instead of
the colorful 2-letter placeholder.

## The Problem

```tsx
// ProductImage.tsx — checks truthiness, not file existence
{product.image ? (
  <Image src={product.image} alt={product.title} width={200} height={150} />
) : (
  <ProductImagePlaceholder title={product.title} />
)}
// If product.image = '/images/RTV/missing.png' → truthy → blank block
```

## Fix: Runtime Cleanup at Module Load

Add a one-time check in `lib/db.ts` that validates all `image` paths against
the filesystem at application startup:

```typescript
import fs from 'fs';
import path from 'path';

// ── One-time startup: clear broken image paths ──
const broken: string[] = [];
const allWithImages = db.prepare('SELECT id, image FROM products WHERE image IS NOT NULL').all() as any[];
for (const r of allWithImages) {
  const fullPath = path.join(process.cwd(), 'public', r.image);
  if (!fs.existsSync(fullPath)) {
    db.prepare('UPDATE products SET image = NULL WHERE id = ?').run(r.id);
    broken.push(r.id);
  }
}
if (broken.length > 0) {
  console.log(`[DB] Cleared ${broken.length} broken image paths: ${broken.join(', ')}`);
}
```

**Why at module load?** `lib/db.ts` is imported by every API route and page
that reads products. The check runs once per server process (not per request),
is idempotent (running again finds no broken paths), and fixes the DB
automatically without manual SQL intervention.

## Alternative: Component-Level Check

If you cannot modify `lib/db.ts`, add a runtime check in the image component:

```tsx
import fs from 'fs';
import path from 'path';

function imageExists(relPath: string): boolean {
  return fs.existsSync(path.join(process.cwd(), 'public', relPath));
}

// In JSX:
{product.image && imageExists(product.image) ? (
  <Image src={product.image} alt={product.title} width={200} height={150} />
) : (
  <ProductImagePlaceholder title={product.title} />
)}
```

**Downside:** File-system check on every render (or every SSR). The `lib/db.ts`
startup approach is more efficient — it fixes the data once, and all subsequent
reads use the cleaned `NULL` value.

## Prevention

1. **Upload workflow:** When admin uploads an image, store the path only after
   confirming the file was written successfully.
2. **Build-time validation:** Add a build step that scans `public/images/` and
   reports DB paths with no matching files:
   ```bash
   node -e "require('./src/lib/db').validateImagePaths()"
   ```
3. **Placeholder component:** Ensure `ProductImagePlaceholder` always renders
   something visible (colorful background + 2 initials), never an empty block.

## Related

- `references/sqlite-json-column-parsing.md` — same `lib/db.ts` layer, same
  startup-time data-fixing pattern.
- `references/admin-panel-promo-prices.md` — product card display system.
