# From sketch to production: category card SEO notes

Worked example from `pentajunior-v2` (Next.js + Bootstrap + SQLite catalog).

## What we sketched

A single HTML file with 5 category-card variants for `/production`:
- Clean cards with top image
- Olive top bar cards
- Horizontal list with image
- Minimal bordered cards
- Magazine tiles with overlay

The user picked **Variant 1 — Clean cards with top image**.

## SEO insight from the session

Listing product names inside a category card **without links** adds almost no SEO value. What actually helps:
- Unique category description (used as card body text).
- Clean heading hierarchy: page `h1` → category `h2` → product `h3` on the category page.
- Image with descriptive `alt`.
- JSON-LD `ItemList` on the listing page.
- Clickable whole card or clear "Перейти в раздел" link.

## Production implementation notes

- Wrapped the card in `Link` so the whole card is clickable.
- Replaced Bootstrap `badge bg-secondary` with a custom `.category-count-badge` to match the sketch palette.
- Removed the inline product list from the card; moved discovery to the category page.
- Kept preview image centered and rounded via a `.category-image-wrapper` with `object-fit: contain`.

## Useful CSS snippet

```css
.service-card .service-card-media {
  height: 220px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.category-image-wrapper {
  width: 200px;
  height: 200px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
}

.category-image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 0.5rem;
}
```
