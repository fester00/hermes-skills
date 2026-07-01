# Responsive tables in blog article HTML

Blog articles in pentajunior-v2 store raw HTML in `src/data/blog/article-*.ts` and render it via `dangerouslySetInnerHTML` in `src/app/blog/[articleId]/page.tsx`.

By default the project styled tables with `width: 100%`, which forces them to squeeze instead of scrolling. On narrow viewports a wide table can break the page layout.

## Known-good fix

### 1. Wrap tables at render time

In `src/app/blog/[articleId]/page.tsx`, extend `renderArticleContent` so every `<table>` is wrapped in a scrollable container:

```ts
function renderArticleContent(content: string): string {
  const products = getAllProducts();
  const categories = getAllCategories();

  let rendered = content.replace(/\{product:([^}]+)\}/g, (_match, productId) => {
    const product = products.find((p) => p.id === productId);
    if (!product) return productId;
    const category = categories.find((c) => c.id === product.category_id);
    const href = `/production/${category?.slug ?? "production"}/${product.id}`;
    return `<a href="${href}" class="article-product-link">${product.name}</a>`;
  });

  // Wrap raw-HTML tables for horizontal scrolling on mobile
  if (!rendered.includes('blog-table-scroll')) {
    rendered = rendered
      .replace(/<table\b/gi, '<div class="blog-table-scroll"><table')
      .replace(/<\/table>/gi, '</table></div>');
  }

  return rendered;
}
```

Guard (`includes('blog-table-scroll')`) prevents double-wrapping if an article already contains the wrapper class.

### 2. Move table borders/margins to the wrapper

In `src/app/globals.css`, add the wrapper and remove `width: 100%` / margin / border from the table itself:

```css
.blog-page-dark .blog-article-content .blog-table-scroll {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  margin: 1.75rem 0 2rem;
  border: 1px solid rgba(209, 197, 198, 0.2);
  border-radius: var(--radius-lg);
}

.blog-page-dark .blog-article-content table {
  width: auto;
  min-width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  margin: 0;
  border: none;
  border-radius: 0;
  font-size: 0.95rem;
}
```

### 3. Fix adjacent heading selector

Because the table is now inside the wrapper, update the spacing selector from `table + h2` to `.blog-table-scroll + h2`:

```css
.blog-page-dark .blog-article-content .blog-table-scroll + h2 {
  margin-top: 3.5rem;
}
```

## How to verify

1. Start the dev server on port 3001:
   ```bash
   export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
   cd /home/natan/pentajunior-v2
   ./node_modules/.bin/next dev -p 3001
   ```
2. Open any blog page with a table, e.g. `/blog/germetiki-dlya-elektroniki`.
3. In DevTools, narrow the article content to ~320 px and confirm the table's `scrollWidth` exceeds the wrapper's `clientWidth`:
   ```js
   const w = document.querySelector('.blog-table-scroll');
   ({ client: w.clientWidth, scroll: w.scrollWidth });
   ```
4. Run the build gate:
   ```bash
   ./node_modules/.bin/tsc --noEmit
   rm -rf .next
   npm run build
   ```

## Why not just `display: block; overflow-x: auto` on the table?

Making `<table>` a block creates the scroll container on the table itself, but `border-radius` + `overflow: hidden` on the table conflict with `overflow-x: auto`, and the scroll container role becomes less predictable for screen readers. A wrapping `<div>` keeps the table semantics intact and gives a clean place for borders and rounded corners.
