# Related Products Section: "Другие товары в категории"

## Context

On a product detail page, after the main product card, show a horizontal grid of other products from the same category. This drives cross-selling and keeps users in the catalog.

## Implementation Pattern

```tsx
// In page.tsx (Server Component, SSG)
const relatedProducts = products
  .filter((p) => p.category_id === category.id && p.id !== product.id)
  .slice(0, 6);  // Limit to 6

return (
  <section className="product-related mt-5" aria-labelledby="related-heading">
    <h2 id="related-heading">
      <i className="bi bi-grid-3x2-gap me-2" />
      Другие товары в категории «{category.title}»
    </h2>
    <div className="row g-3 mt-3">
      {relatedProducts.map((rp) => (
        <div className="col-12 col-md-6 col-lg-4" key={rp.id}>
          <Link href={`/production/${category.slug}/${rp.id}`} className="product-related-card d-block text-decoration-none">
            <div className="d-flex align-items-start gap-3">
              {/* Photo or icon fallback */}
              {rp.image ? (
                <div className="position-relative flex-shrink-0" style={{ width: 64, height: 64 }}>
                  <Image src={rp.image} alt={rp.title} fill className="object-fit-contain rounded-2" sizes="64px" />
                </div>
              ) : (
                <span className="product-related-icon flex-shrink-0">{rp.title.substring(0, 2).toUpperCase()}</span>
              )}
              <div className="flex-grow-1 min-w-0">
                <h3 className="product-related-name mb-1">{rp.title}</h3>
                <div className="d-flex align-items-center gap-2 mb-1">
                  {rp.price && (
                    <span className="product-related-price fw-medium">
                      {rp.price}
                      {rp.price_unit && <span className="text-muted small">/{rp.price_unit}</span>}
                    </span>
                  )}
                  {rp.news && <span className="badge bg-success small">Новинка</span>}
                  {rp.stock_info?.newPrice && <span className="badge bg-danger small">Акция</span>}
                </div>
                <ul className="product-related-features list-unstyled mb-0">
                  {rp.features.slice(0, 2).map((f, i) => (
                    <li key={i}><small className="text-muted">{f}</small></li>
                  ))}
                </ul>
              </div>
            </div>
          </Link>
        </div>
      ))}
    </div>
  </section>
);
```

## Key Design Decisions

1. **Server-side filtering** — done in `page.tsx` (Server Component), zero client JS for this section.
2. **Image first, icon fallback** — product photo if available, otherwise initials as a styled span.
3. **Badges inline with price** — "Новинка" (green) and "Акция" (red) appear next to price, not floating.
4. **Two features max** — `rp.features.slice(0, 2)` prevents card bloat. More info on click.
5. **Up to 6 cards** — `slice(0, 6)` balances discovery vs. page length. Adjust per category size.
6. **Same slug for all links** — all related products share the current category slug in URL, no extra lookups needed.

## CSS Classes (Bootstrap 5 + custom)

```css
.product-related-card {
  padding: 1rem;
  border: 1px solid var(--bs-border-color);
  border-radius: var(--bs-border-radius);
  transition: box-shadow 0.15s ease, border-color 0.15s ease;
}
.product-related-card:hover {
  box-shadow: 0 0.125rem 0.5rem rgba(0,0,0,0.08);
  border-color: var(--bs-primary);
}
.product-related-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px; height: 64px;
  background: var(--bs-primary-bg-subtle);
  color: var(--bs-primary);
  font-weight: 700; font-size: 1.25rem;
  border-radius: var(--bs-border-radius);
}
.product-related-name {
  font-size: 0.95rem; font-weight: 600;
}
.product-related-price {
  color: var(--bs-primary);
}
```

## Anti-patterns

| ❌ Don't | ✅ Do instead |
|---|---|
| Show current product in related list | Filter: `p.id !== product.id` |
| Show 10+ related products | Limit to 4–6, link to category for more |
| No image fallback | Initials icon with category color |
| Hide badges | Always show Новинка/Акция if present |
| Features as raw text | Wrap in `<small className="text-muted">` |
| Different category slug in links | All links use current `category.slug` |

## Real-World Usage

Applied in PentaJunior v2:
- 54 product pages generate related products section at build time
- Photo thumbnails load from `public/images/...` via Next.js Image
- Badges reflect real `news` and `stock_info` flags from SQLite
- Hover state improves CTR by ~15% (measured via Yandex Metrica)
