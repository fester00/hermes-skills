# Product links inside blog articles

Blog articles in pentajunior-v2 are stored as raw HTML in `src/data/blog/article-*.ts`. Product references are written as markers:

```html
<p>Компаунд {product:pentelast-711} — двухкомпонентный ...</p>
```

`src/app/blog/[articleId]/page.tsx` replaces those markers with real `<a>` links at render time.

## Use `product.name`, not `product.title`

The `Product` interface in `src/lib/db.ts` has two name fields:

| Field | Purpose | Example |
| :-- | :-- | :-- |
| `name` | Short display name | `Пентэласт-711` |
| `title` | SEO / long title for `<title>` and cards | `Заливочный компаунд Пентэласт-711 купить \| до +250°C` |

For inline links inside article paragraphs and for the "Связанные продукты" cards, always render `product.name`. Using `product.title` produces noisy, over-long link text like:

> Заливочный компаунд Пентэласт-711 купить \| до +250°C

which hurts readability and looks broken in the UI.

## Known-good code

In `src/app/blog/[articleId]/page.tsx`:

```ts
// Inline product markers
return `<a href="${href}" class="article-product-link">${product.name}</a>`;
```

And in the related-products section:

```tsx
<h3 className="blog-card-title">{product.name}</h3>
```

Leave `product.title` for `<title>` / OpenGraph / JSON-LD metadata only.

## Related pattern

For making raw-HTML tables in blog articles scrollable on mobile, see `references/blog-table-responsive-wrapper-pattern.md`.
