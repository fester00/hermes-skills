# Category SEO Text Generation Pattern

## Problem

When migrating from hardcoded TSX data arrays, many categories have empty or stub `seoText` fields (e.g., `<></>`). These must be replaced with full SEO-optimized HTML sections before launch.

## Output Format

Each category SEO text is a self-contained `<section>` with Bootstrap 5 classes:

```html
<section class="category-seo-text mt-5 pt-4 border-top" aria-label="О [категории]">
  <h2 class="h5 mb-3">[H2 title with target keywords]</h2>
  
  <p class="text-body-secondary">
    [2–3 sentences: what the product category is, key properties, temperature range, applications]
  </p>
  
  <div class="row g-4 my-1">
    <div class="col-md-6">
      <div class="h-100 p-4 rounded-3 bg-body-tertiary">
        <h3 class="h6 fw-semibold mb-2">
          <i class="bi bi-[icon] me-2 text-primary" />
          [Sub-product or use case 1]
        </h3>
        <p class="mb-0 small text-body-secondary">
          [2–3 sentences describing the sub-product. End with <strong>bold takeaway</strong>.]
        </p>
      </div>
    </div>
    <div class="col-md-6">
      <div class="h-100 p-4 rounded-3 bg-body-tertiary">
        <h3 class="h6 fw-semibold mb-2">
          <i class="bi bi-[icon] me-2 text-warning" />
          [Sub-product or use case 2]
        </h3>
        <p class="mb-0 small text-body-secondary">
          [2–3 sentences. End with <strong>bold takeaway</strong>.]
        </p>
      </div>
    </div>
  </div>
  
  <p class="mt-4 text-body-secondary">
    [2–3 sentences on broader applications: construction, design, food industry, automotive, etc.]
  </p>
  
  <div class="alert d-flex align-items-start gap-3 mt-3 mb-0" role="note">
    <i class="bi bi-patch-check-fill flex-shrink-0 fs-5 mt-1" />
    <p class="mb-0 text-bordo">
      <strong>«[Brand]»</strong> производит [product line] …
      Отгрузка от [min qty], доставка по всей России.
    </p>
  </div>
</section>
```

## Icon Reference

| Category type | Primary icon | Secondary icon |
|---|---|---|
| Silicone / fluids | `bi-droplet-half` | `bi-layers` |
| Heat / temperature | `bi-thermometer-half` | `bi-fire` |
| Electronics | `bi-motherboard` | `bi-lightning-charge` |
| Machinery / tools | `bi-gear-wide-connected` | `bi-wrench` |
| Safety / protection | `bi-shield-check` | `bi-hand-index-thumb` |
| Food / baking | `bi-egg-fried` | `bi-house-heart` |
| Shoes / leather | `bi-droplet-half` | `bi-sun` |
| Construction | `bi-shield-check` | `bi-brush` |

## Writing Rules

1. **First sentence** must contain the primary keyword phrase (e.g., "силиконовые масла ПМС")
2. **h2** should be 5–12 words, descriptive, with a benefit angle
3. **Two info blocks** — compare two sub-types, two use cases, or two product lines
4. **Bold takeaways** in each block — the single most important fact
5. **Alert at the end** — brand mention + product line + offer terms
6. **Length target**: 1800–2500 characters (adequate for SEO without bloating)
7. **No `dangerouslySetInnerHTML`** — store as plain string in DB, render with `{category.seo_text && <div dangerouslySetInnerHTML={{ __html: category.seo_text }} />}` only at the page level

## Example (Silicone oils PMS)

```html
<section class="category-seo-text mt-5 pt-4 border-top" aria-label="О силиконовых маслах ПМС">
  <h2 class="h5 mb-3">Силиконовые масла ПМС — универсальный кремнийорганический продукт</h2>
  <p class="text-body-secondary">
    Силиконовые жидкости серии ПМС (полиметилсилоксаны) — это прозрачные бесцветные масла...
  </p>
  ...
</section>
```

## Pitfall: Empty `seo_text` detection

After migration, always audit:

```sql
SELECT id, slug, title, LENGTH(seo_text) AS len 
FROM categories 
WHERE seo_text IS NULL OR seo_text = '' OR LENGTH(seo_text) < 100;
```

Any row returned needs a generated SEO text.
