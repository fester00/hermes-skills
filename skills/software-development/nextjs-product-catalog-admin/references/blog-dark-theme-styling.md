# Blog dark-theme styling

Session: pentajunior-v2, 2026-06-17.

## Context
User wanted to redesign `/blog` and `/blog/[articleId]` in a dark "hero cards" style using the project palette:

- `#212529` dark graphite (background)
- `#8fb34f` olive green (primary accent)
- `#160b0d` dark bordo (text on light surfaces)
- `#6bdb85` mint green (hover/links)
- `#d1c5c6` ash rose (muted text / borders)

## Workflow

1. Create a standalone HTML prototype with multiple style variants (e.g. 5) so the user can pick one without touching the project code.
2. Once a variant is chosen, apply it to the actual Next.js components:
   - Wrap the page content in a container class (e.g. `blog-page-dark`) and set background/text globally.
   - Add a dedicated CSS block in `globals.css` instead of scattering overrides.
   - Keep Bootstrap utility classes only where they do not conflict (grid, spacing).
   - Replace Bootstrap card/button styles with custom classes to avoid theme leakage.
3. For the article page, also wrap the whole page and override article content typography, links, and related-product cards inside the same namespace.

## Key CSS patterns

```css
.blog-page-dark {
  background: var(--dark-graphite);
  color: #fff;
  min-height: 100vh;
}

.blog-page-dark .blog-card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(209,197,198,0.12);
  border-radius: 16px;
  transition: transform .25s ease, box-shadow .25s ease, background-color .25s ease, border-color .25s ease;
}

.blog-page-dark .blog-card:hover {
  background: rgba(255,255,255,0.07);
  border-color: var(--olive-green);
  box-shadow: 0 12px 32px rgba(0,0,0,0.25);
  transform: translateY(-4px);
}

.blog-page-dark .blog-filter-btn {
  padding: 8px 18px;
  border: 1.5px solid rgba(209,197,198,0.4);
  color: var(--ash-rose);
  border-radius: 999px;
  background: transparent;
}

.blog-page-dark .blog-filter-btn:hover,
.blog-page-dark .blog-filter-btn.active {
  background: var(--olive-green);
  border-color: var(--olive-green);
  color: var(--dark-bordo);
}
```

## Pitfalls

- Do not rely on Bootstrap `.card` / `.btn` classes inside the dark namespace — their variables are defined for the light theme and require heavy override.
- Breadcrumb links need explicit color overrides; the default Bootstrap `.breadcrumb-item a` may inherit light-theme primary color.
- Article content rendered via `dangerouslySetInnerHTML` must be scoped under `.blog-article-content` so inline links and lists pick up the dark theme.
- If the page is shorter than the viewport, set `min-height: 100vh` on the dark wrapper so the background covers the whole screen.
- **Stale dev-server after styling changes:** `next start` serves the existing `.next` output and does not rebuild when CSS/JS changes. If a dark-theme update is not visible, kill the server and restart it after `npm run build`.

## Related references

- `references/blog-article-typography-dark.md` — long-form article readability in dark theme (headings, tables, lists, FAQ, blockquote).
- `references/blog-filter-layout-shift.md` — filter button layout-shift hardening.

## Verification

- `npx tsc --noEmit`
- `npm run build`
- Restart `next start` if it was already running before the build.
- Check both `/blog` and at least one `/blog/[articleId]` route visually.
