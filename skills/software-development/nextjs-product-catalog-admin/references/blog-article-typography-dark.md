# Blog article typography in dark theme

Session: pentajunior-v2, 2026-06-18.

## Context

After switching `/blog/[articleId]` to a dark theme, long-form articles still looked dense: very wide text column, flat headings, unstyled tables, default list bullets, and no visual separation between sections. The user asked to improve readability while keeping the SEO HTML structure untouched.

## Constraints

- Keep existing HTML tags (headings, lists, tables, blockquote) for SEO — do not change markup.
- Scope all overrides under a single namespace, e.g. `.blog-page-dark .blog-article-content`.
- Limit article width for comfortable reading.
- Leave "Related products" and "Related categories" sections untouched.

## Layout

Center the article and cap the reading column:

```tsx
<article className="blog-article mx-auto" style={{ maxWidth: 820 }}>
  <div
    className="blog-article-content mx-auto"
    dangerouslySetInnerHTML={{ __html: renderedContent }}
  />
  <hr className="blog-section-divider" />
</article>
```

```css
.blog-page-dark .blog-article-content {
  max-width: 760px;
  font-size: 1.025rem;
  line-height: 1.75;
  color: rgba(255, 255, 255, 0.9);
}
```

## Heading hierarchy

- `h2`: white, 1.5rem, bottom olive border as a section separator.
- `h3`: mint green, 1.2rem — sub-section accent.
- `h4`: white, 1.1rem.
- Add extra top margin when a heading follows a paragraph, list, or table.

```css
.blog-page-dark .blog-article-content h2 {
  color: #fff;
  font-size: 1.5rem;
  font-weight: 700;
  margin-top: 3rem;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(143, 179, 79, 0.35);
}

.blog-page-dark .blog-article-content h3 {
  color: var(--mint-green);
  font-size: 1.2rem;
  font-weight: 700;
  margin-top: 2.25rem;
  margin-bottom: 1rem;
}
```

## Lists

Replace default bullets with custom markers that fit the palette:

```css
.blog-page-dark .blog-article-content ul,
.blog-page-dark .blog-article-content ol {
  margin-bottom: 1.5rem;
  padding-left: 0;
  list-style: none;
}

.blog-page-dark .blog-article-content li {
  position: relative;
  margin-bottom: 0.625rem;
  padding-left: 1.75rem;
  line-height: 1.6;
}

.blog-page-dark .blog-article-content ul li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.6rem;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--olive-green);
}

.blog-page-dark .blog-article-content ol {
  counter-reset: blog-ol;
}

.blog-page-dark .blog-article-content ol li::before {
  counter-increment: blog-ol;
  content: counter(blog-ol) '.';
  position: absolute;
  left: 0;
  color: var(--olive-green);
  font-weight: 700;
  min-width: 1.5rem;
}
```

## Tables

Style tables with rounded corners, translucent borders, and a tinted header:

```css
.blog-page-dark .blog-article-content table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  margin: 1.75rem 0 2rem;
  border: 1px solid rgba(209, 197, 198, 0.2);
  border-radius: var(--radius-lg);
  overflow: hidden;
  font-size: 0.95rem;
}

.blog-page-dark .blog-article-content thead {
  background: rgba(143, 179, 79, 0.15);
}

.blog-page-dark .blog-article-content th {
  color: #fff;
  font-weight: 700;
  padding: 0.875rem 1rem;
  text-align: left;
  border-bottom: 1px solid rgba(209, 197, 198, 0.2);
}

.blog-page-dark .blog-article-content td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(209, 197, 198, 0.12);
  color: rgba(255, 255, 255, 0.85);
  vertical-align: top;
}

.blog-page-dark .blog-article-content tbody tr:nth-child(even) {
  background: rgba(255, 255, 255, 0.025);
}
```

## FAQ (definition list)

If the article uses `<dl><dt><dd>` for Q&A, style the pair as a question card + indented answer:

```css
.blog-page-dark .blog-article-content dl {
  margin: 1.75rem 0 2.5rem;
}

.blog-page-dark .blog-article-content dt {
  position: relative;
  padding: 1rem 1rem 1rem 1.25rem;
  margin-top: 1rem;
  color: #fff;
  font-weight: 700;
  font-size: 1.05rem;
  line-height: 1.5;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(209, 197, 198, 0.15);
  border-left: 3px solid var(--olive-green);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
}

.blog-page-dark .blog-article-content dt:first-child {
  margin-top: 0;
}

.blog-page-dark .blog-article-content dt::before {
  content: 'Q';
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  margin-right: 0.75rem;
  border-radius: 50%;
  background: var(--olive-green);
  color: #160b0d;
  font-size: 0.8rem;
  font-weight: 800;
  flex-shrink: 0;
}

.blog-page-dark .blog-article-content dd {
  margin: 0 0 1rem 1.25rem;
  padding: 1rem 1.25rem;
  color: rgba(255, 255, 255, 0.85);
  background: rgba(255, 255, 255, 0.025);
  border-left: 2px solid rgba(209, 197, 198, 0.12);
  border-radius: 0 0 var(--radius-md) var(--radius-md);
  line-height: 1.7;
}
```

## Accent elements

```css
.blog-page-dark .blog-article-content strong,
.blog-page-dark .blog-article-content b {
  color: #fff;
  font-weight: 700;
}

.blog-page-dark .blog-article-content blockquote {
  margin: 1.75rem 0;
  padding: 1.25rem 1.5rem;
  border-left: 4px solid var(--olive-green);
  background: rgba(255, 255, 255, 0.04);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  font-style: italic;
  color: rgba(255, 255, 255, 0.85);
}

.blog-page-dark .blog-article-content hr {
  border: none;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(209, 197, 198, 0.3), transparent);
  margin: 2.5rem 0;
}
```

## Section divider

Place a subtle gradient rule between the article body and the untouched related sections:

```css
.blog-page-dark .blog-section-divider {
  border: none;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(209, 197, 198, 0.25), transparent);
  margin: 3rem auto 0;
  max-width: 760px;
}
```

## Pitfalls

- Do not set `max-width` on the article wrapper alone — the inner `.blog-article-content` must also be centered so headings and dividers line up.
- Default Bootstrap table styles (`.table`, `.table-striped`) will override dark styles if added inside the article content.
- `<dt>`/`<dd>` default browser margins reset inconsistently — always declare them explicitly in the dark namespace.
- If the dev server was started with `next start` on an older build, CSS/JS changes will not appear until the server is restarted because `next start` serves the existing `.next` output without rebuilding.

## Verification

- `npx tsc --noEmit`
- `npm run build`
- Restart `next start` if it was already running before the build.
- Visually inspect at least one long article containing headings, lists, tables, blockquote, and `<dl>` Q&A.
