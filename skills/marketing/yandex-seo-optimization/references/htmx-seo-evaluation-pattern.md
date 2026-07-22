# Evaluating htmx for an existing project — SEO impact pattern

Use this when the user asks "should we add htmx to project X?" or "how will htmx affect our SEO?".

## Core principle

htmx preserves server-rendered HTML and normal URLs, which is SEO-friendly by default. The danger is not htmx itself, but replacing SEO-critical navigation/content with AJAX-only patterns.

## Where htmx helps

- Admin panels, dashboards, forms with partial updates
- Search-as-you-type that degrades to a normal form submit
- Inline edits, load-more, tabs inside a single page
- Applications where SEO is irrelevant (logged-in areas)

## Where htmx hurts SEO

| Pattern | Risk |
|---------|------|
| `hx-get` on category/product links | Search engines may not follow JS-driven navigation |
| Partially loading SEO text with `hx-get` | Content not in initial HTML → not indexed immediately |
| `hx-push-url` without matching SSR route | Broken canonical / soft 404 / empty metadata |
| Updating `<title>` / `<meta>` only client-side | Social crawlers and bots see old metadata |

## Decision matrix

| Context | Recommendation |
|---------|----------------|
| Public catalog, SSG/SSR already works | Keep normal links; use htmx only for non-SEO interactions |
| SPA currently harming indexation | htmx can be a step back to server-rendered HTML |
| Admin / auth-only areas | htmx is usually a good fit |
| Heavy client UI (canvas, editors, PWA) | Do not use htmx; use a real framework |

## For Next.js projects specifically

Next.js App Router already gives server components, streaming, and partial hydration. htmx rarely adds value on public pages and can fragment the architecture. Prefer htmx only for:

- Admin forms that today are heavy React forms
- Quick search dropdown
- Contact / feedback forms

## Anti-patterns to avoid

1. Replacing `<a href>` with `<button hx-get>` for crawlable pages.
2. Loading primary content via `hx-get` instead of rendering it server-side.
3. Relying on client-side head updates without server-side `generateMetadata` equivalents.

## Summary line

htmx is a good tool for *progressive enhancement*; it is a bad replacement for an already-working SSG/SSR public site architecture.
