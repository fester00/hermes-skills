# Related products section on product detail pages

On `/production/[category]/[subcategory]/[product]/page.tsx` the "Другие товары в ..." section is **not a separate component**. It is inline JSX inside the page component (lines ~286–350). Do not look for a `RelatedProducts.tsx` component when changing it.

## Use `product.name`, not `product.title`

The related-product cards show the same name fields as blog links:

| Field | Purpose | Example |
| :-- | :-- | :-- |
| `name` | Short display name | `Пентэласт-711` |
| `title` | SEO / long title | `Заливочный компаунд Пентэласт-711 купить \| до +250°C` |

In the inline section, update three places:

```tsx
{rp.image ? (
  <Image src={rp.image} alt={rp.name} fill ... />
) : (
  <span className="product-related-icon flex-shrink-0">
    {rp.name.substring(0, 2).toUpperCase()}
  </span>
)}
...
<h3 className="product-related-name mb-1">{rp.name}</h3>
```

Using `rp.title` produced noisy card titles and alt text.

```tsx
{rp.price && (
  <span className="product-related-price fw-medium">
    от {rp.price} {rp.price_currency === 'USD' ? '$' : '₽'}
    {rp.price_unit && (
      <span className="text-muted small">/{rp.price_unit}</span>
    )}
  </span>
)}
```

Using `rp.price_currency` avoids printing a bare number without `₽`/`$`.

The inline block uses local variables (`category`, `subcategory`, `relatedProducts`) and `Image` from `next/image`. If you extract it, pass:
- `categorySlug`, `subcategorySlug`
- `relatedProducts: Product[]`

Keep the same responsive column classes (`col-12 col-md-6 col-lg-4`) and card CSS classes so the layout does not change.

## Related pattern

For the same naming convention in blog articles, see `references/blog-article-product-link-pattern.md`.
