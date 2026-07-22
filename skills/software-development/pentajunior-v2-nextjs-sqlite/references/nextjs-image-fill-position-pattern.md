# Next.js Image `fill` — position and sizes warnings

When `next/image` is used with the `fill` prop in pentajunior-v2, the browser console may warn:

- `Image with src "..." has "fill" but is missing "sizes" prop.`
- `Image with src "..." has "fill" and parent element with invalid "position". Provided "static" should be one of absolute,fixed,relative.`

These warnings are not cosmetic: `fill` removes the image from document flow and sizes it relative to the nearest positioned ancestor. If the ancestor is `position: static` (the default), Next.js cannot calculate layout correctly, and Lighthouse/Core Web Vitals may suffer.

## Root cause in this project

Several card components use `fill` inside a `<Link>` or other wrapper whose `position: relative` comes only from a CSS class. If that class loses specificity, is overridden by a media query, or the component is reused in a context where the class is not present, the parent becomes `static`.

Affected components: `CompactProductCard`, `ProductCard`, `RelatedProducts`.

## Safe fix

Do not rely on a CSS class to make the parent positioned. Wrap the `Image` in an explicit `<div>` with Bootstrap `position-relative` (or an inline `position: "relative"`) so the ancestor is guaranteed positioned regardless of context.

### Example: `CompactProductCard` catalog media

```tsx
<div className="catalog-product-media m-auto mt-2" style={{ height: "250px", width: "250px" }}>
  <Link href={href} className="d-block w-100 h-100 position-relative">
    {image ? (
      <Image
        src={image}
        alt={name}
        fill
        className="object-fit-cover"
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
      />
    ) : (
      <ProductImagePlaceholder title={name} className="h-100 w-100" />
    )}
    {(news || stockInfo?.newPrice) && (
      <ProductBadges news={news} stockInfo={stockInfo} variant="catalog" />
    )}
  </Link>
</div>
```

### Example: `ProductCard` detail image

```tsx
<div className="col-12 col-md-5 bg-light p-4 d-flex align-items-center justify-content-center m-0 product-image-container">
  {product.image ? (
    <div className="position-relative w-100 h-100">
      <Image
        src={product.image}
        alt={`${product.title} — ${category?.title || 'Каталог'}`}
        fill
        className="object-fit-contain rounded"
        sizes="(max-width: 768px) 100vw, 50vw"
      />
    </div>
  ) : (
    <ProductImagePlaceholder title={product.title} className="h-100 w-100 fs-1" />
  )}
  ...
</div>
```

### Example: `RelatedProducts` thumbnail

```tsx
<div className="flex-shrink-0" style={{ width: 64, height: 64, position: "relative" }}>
  <Image
    src={rp.image}
    alt={rp.name}
    fill
    className="object-fit-contain rounded-2"
    sizes="64px"
  />
</div>
```

### Common mistake: positioning the wrong ancestor

A developer may add `style={{ position: "relative" }}` to a higher ancestor such as the outer `<Link>` and expect the `Image fill` warning to disappear. It will not: Next.js looks at the **immediate parent** of `<Image>`.

Wrong:
```tsx
<Link href={href} style={{ position: "relative" }}>
  <div className="service-card-media category-card-media mb-3">
    <div className="category-image-wrapper">
      <Image src={imageSrc} alt={title} fill sizes="..." />
    </div>
  </div>
</Link>
```

The immediate parent here is `.category-image-wrapper`, which is `static`. Move `position: relative` to that wrapper:

Correct:
```tsx
<Link href={href}>
  <div className="service-card-media category-card-media mb-3">
    <div className="category-image-wrapper" style={{ position: "relative" }}>
      <Image src={imageSrc} alt={title} fill sizes="..." />
    </div>
  </div>
</Link>
```

Or add `position: relative` to the `.category-image-wrapper` CSS rule.

## Diagnostic recipe

1. Open DevTools console and note the `src` path from the warning.
2. Search the project for that path in `pentajunior.db` or rendered HTML to identify which component renders it.
3. Find `Image` components with `fill`:
   ```bash
   grep -R "\bfill\b" src/components src/app --include="*.tsx"
   ```
4. For each, verify the immediate parent has `position: relative` (or `absolute`/`fixed`) in the rendered DOM.
5. If not, insert an explicit positioned wrapper and add/keep a `sizes` prop.

## Anti-patterns to avoid

- Removing `fill` and switching to `width`/`height` without updating the surrounding layout.
- Relying solely on `.catalog-product-media { position: relative }` when the component is reused outside its expected CSS scope.
- Omitting `sizes` on `fill` images — it prevents Next.js from choosing the optimal responsive source.

## Verification

After the fix:

```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
cd /home/natan/pentajunior-v2
./node_modules/.bin/tsc --noEmit
rm -rf .next tsconfig.tsbuildinfo
npm run build
```

Then open a category page in the browser and confirm the console warnings are gone.
