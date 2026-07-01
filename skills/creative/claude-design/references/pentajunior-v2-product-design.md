# Penta Junior v2 — designing with real product data

Reference for any design task that touches products from the `pentajunior-v2` Next.js catalog.

## Why this matters

The user's previous session (product card for Si-M silicone spray) confirmed that product copy, specs, images, and pricing should come from the actual SQLite database, not be invented. Penta Junior v2 is the authoritative source.

## Project layout

| Path | Purpose |
|------|---------|
| `/home/natan/pentajunior-v2/pentajunior.db` | SQLite catalog: `products`, `categories`, `spec_tables` |
| `/home/natan/pentajunior-v2/src/app/globals.css` | Design tokens: `--olive-green`, `--mint-green`, `--dark-bordo`, radii, shadows |
| `/home/natan/pentajunior-v2/public/images/` | Product photos by category (`smazki/`, `RTV/`, `sealants/`, etc.) |
| `http://localhost:3000/` | Dev server (usually running on port 3000/3001) |

## Querying a product

```sql
SELECT id, name, title, price, price_unit, image, features, keywords,
       meta_description, pack, spec_table_id, template_type, template_data
FROM products
WHERE id = 'si-m-aero';
```

`template_data` is JSON and contains the richest source of copy: `intro`, `composition`, `temp_range`, `shelf_life`, `tu`, `bullets`, `application_*`, `properties`, `surfaces`, etc.

## Product image URLs

DB `image` value is a site-root path, e.g. `/images/smazki/si_m_smazka.webp`. On the dev server it resolves to:

```
http://localhost:3000/images/smazki/si_m_smazka.webp
```

For standalone HTML artifacts, either use the dev-server URL (when it is running) or copy the file into the artifact folder.

## Brand colors to reuse

From `globals.css`:

- Primary accent: `#8FB34F` (olive green)
- Secondary accent: `#6BDB85` (mint)
- Text / dark: `#160B0D`
- Surface / bg: `#FAFAFA`
- Card surface: `#FFFFFF`

The Si-M product itself uses cobalt blue + yellow on its packaging (`#1E4D8C`, `#F2C94C`) — useful for divergent product-specific concepts.

## Design workflow for Penta Junior products

1. Identify product ID from the user's request.
2. Query SQLite for `products` row and parse `template_data` JSON.
3. Read actual product image and inspect colors/shape.
4. Read `globals.css` and the relevant category page to match existing visual vocabulary.
5. Produce 3 variants: conservative (matches site), strong-fit (best for brief), divergent (uses product packaging personality or new layout).
6. Verify in browser with dev-server image URLs.
