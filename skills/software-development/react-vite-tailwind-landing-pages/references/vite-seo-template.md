# Vite SEO Template

Drop this into `index.html` for a Russian-language product landing page.

```html
<!doctype html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta
      name="description"
      content="Купить ... продажа оптом и в розницу с доставкой."
    />
    <meta
      name="keywords"
      content="..., ..., ..."
    />
    <meta name="robots" content="index, follow" />
    <meta name="author" content="Company Name" />
    <meta name="theme-color" content="#0a0a0a" />

    <!-- Open Graph -->
    <meta property="og:title" content="..." />
    <meta property="og:description" content="..." />
    <meta property="og:type" content="website" />
    <meta property="og:image" content="/images/hero.webp" />
    <meta property="og:locale" content="ru_RU" />

    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="..." />
    <meta name="twitter:description" content="..." />
    <meta name="twitter:image" content="/images/hero.webp" />

    <link rel="canonical" href="https://example.com" />

    <title>... | Company Name</title>

    <script type="application/ld+json">
      {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Company Name",
        "url": "https://example.com",
        "email": "info@example.com",
        "telephone": "+7 ...",
        "address": {
          "@type": "PostalAddress",
          "addressLocality": "Москва",
          "addressCountry": "RU"
        }
      }
    </script>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

Also add `public/robots.txt`:

```
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

## Heading Hierarchy Checklist

- [ ] Exactly one `h1` per page (usually in Hero)
- [ ] Each major section has an `h2`
- [ ] Cards and subsections use `h3`
- [ ] No heading level is skipped (h1 → h3 without h2)
- [ ] Headings describe content, not just style
