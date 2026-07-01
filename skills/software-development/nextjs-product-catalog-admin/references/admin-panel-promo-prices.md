# Promo/New Product Price Display on Public Site

Pattern for displaying promotional (old → new) prices and "NEW" / "Акция" badges
on product cards and detail pages, from PentaJunior project (2025-06-12).

## When This Applies

- Products have `oldPrice` field (set when on promotion)
- Products have `isNew` flag (new arrivals)
- Admin panel can toggle promo and set old price
- Public site needs visual cues: crossed-out old price + new price + badges

## Product Type Extension

```typescript
interface Product {
  id: string;
  name: string;
  price: string;        // current price (promo price when on sale)
  oldPrice?: string;    // original price when on promotion
  isNew?: boolean;
  image: string;
  // ... other fields
}
```

**Admin toggle logic:**
- Checkbox "Акция" in product edit form
- When checked: show "Старая цена" input, save to `oldPrice`
- When unchecked: `oldPrice` is undefined (or empty string)
- Promo price is the current `price` field

## ProductCard Component (Catalog Grid)

```tsx
// src/components/ProductCard.tsx or inline in catalog page
export default function ProductCard({ product }: { product: Product }) {
  const isPromo = product.oldPrice && product.oldPrice !== product.price;

  return (
    <div className="card product-card position-relative">
      {/* Badges */}
      {product.isNew && (
        <span className="badge badge-new position-absolute"
          style={{ top: 10, left: 10, zIndex: 2 }}>
          Новинка
        </span>
      )}
      {isPromo && (
        <span className="badge badge-promo position-absolute"
          style={{ top: 10, right: 10, zIndex: 2 }}>
          Акция
        </span>
      )}

      <img src={product.image} className="card-img-top" alt={product.name} />

      <div className="card-body">
        <h5 className="card-title">{product.name}</h5>
        <div className="price-block">
          {isPromo ? (
            <>
              <span className="price-old">{product.oldPrice} ₽</span>
              <span className="price-new ms-2">{product.price} ₽</span>
            </>
          ) : (
            <span className="price-regular">{product.price} ₽</span>
          )}
        </div>
      </div>
    </div>
  );
}
```

## Product Detail Page (Single Product)

```tsx
// src/app/production/[slug]/[productId]/page.tsx
export default function ProductDetailPage({ product }: { product: Product }) {
  const isPromo = product.oldPrice && product.oldPrice !== product.price;

  return (
    <div className="container py-5">
      <div className="row">
        <div className="col-md-6">
          <img src={product.image} className="img-fluid rounded" alt={product.name} />
        </div>
        <div className="col-md-6">
          <h1>{product.name}</h1>

          {product.isNew && <span className="badge badge-new me-2">Новинка</span>}
          {isPromo && <span className="badge badge-promo">Акция</span>}

          <div className="price-block mt-3">
            {isPromo ? (
              <>
                <span className="price-old" style={{ fontSize: '1.1rem' }}>
                  {product.oldPrice} ₽
                </span>
                <span className="price-new ms-3" style={{ fontSize: '1.5rem' }}>
                  {product.price} ₽
                </span>
              </>
            ) : (
              <span className="price-regular" style={{ fontSize: '1.5rem' }}>
                {product.price} ₽
              </span>
            )}
          </div>

          {/* ... specs, advantages, etc. ... */}
        </div>
      </div>
    </div>
  );
}
```

## CSS Styles (add to globals.css or admin.css)

```css
/* Promo price display */
.price-old {
  text-decoration: line-through;
  color: #adb5bd;
  font-size: 0.9rem;
}

.price-new {
  color: #6BDB85;           /* bright green — matches project accent */
  font-weight: 700;
  font-size: 1.25rem;
}

.price-regular {
  color: #212529;
  font-weight: 600;
  font-size: 1.25rem;
}

/* Badges */
.badge-new {
  background: linear-gradient(135deg, #28a745, #218838);
  color: #fff;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-promo {
  background: linear-gradient(135deg, #ff6b6b, #c0392b);
  color: #fff;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

/* Admin-specific modal z-index overrides */
.admin-layout .modal {
  z-index: 1200 !important;
}
.admin-layout .modal-backdrop {
  z-index: 1190 !important;
}
.admin-layout .modal-dialog {
  z-index: 1201 !important;
}
```

## Admin Panel Fields

In the product edit modal (`/admin/products`), add these fields:

```tsx
<div className="mb-3 form-check">
  <input
    type="checkbox"
    className="form-check-input"
    id="isNew"
    checked={form.isNew || false}
    onChange={(e) => setForm({ ...form, isNew: e.target.checked })}
  />
  <label className="form-check-label" htmlFor="isNew">Новинка</label>
</div>

<div className="mb-3 form-check">
  <input
    type="checkbox"
    className="form-check-input"
    id="isPromo"
    checked={!!form.oldPrice}
    onChange={(e) => setForm({
      ...form,
      oldPrice: e.target.checked ? form.oldPrice || '' : undefined
    })}
  />
  <label className="form-check-label" htmlFor="isPromo">Акция</label>
</div>

{form.oldPrice !== undefined && (
  <div className="mb-3">
    <label className="form-label">Старая цена</label>
    <input
      type="text"
      className="form-control"
      value={form.oldPrice}
      onChange={(e) => setForm({ ...form, oldPrice: e.target.value })}
      placeholder="Например: 25 500"
    />
    <small className="text-muted">
      Текущая цена {form.price} будет отображаться как акционная
    </small>
  </div>
)}
```

## Why This Pattern Works

- **Zero schema migration** — `oldPrice` is optional, existing products without it render normally.
- **Backward compatible** — old data without `oldPrice` shows regular price.
- **Admin UI is obvious** — checkbox → old price field → save.
- **Visual impact** — crossed-out old price + bright green new price + "Акция" badge immediately communicates the promotion.
- **Flexible** — can extend with `promoEndDate`, `promoCondition` later in the same optional field pattern.

## Alternative: Using `stock_info` JSON Column (SQLite)

If using SQLite instead of JSON file, reuse an existing `stock_info` TEXT column:

```sql
CREATE TABLE products (
    id TEXT PRIMARY KEY,
    price TEXT,
    stock_info TEXT,      -- JSON: {"newPrice": "...", "condition": "..."}
    news INTEGER DEFAULT 0
);
```

Admin saves:
```typescript
const stockInfo = isStock
  ? JSON.stringify({ newPrice: promoPrice, condition: promoText })
  : null;
// UPDATE products SET stock_info = ?, news = ? WHERE id = ?
```

Component renders:
```tsx
const stockInfo = product.stock_info ? JSON.parse(product.stock_info) : null;
const isPromo = stockInfo?.newPrice;
```

See `references/nextjs-sqlite-admin-panel.md` in `hermes-software-development-workflow` skill for full SQLite variant.
