# JSX syntax in `dangerouslySetInnerHTML` causing hydration mismatch

## Symptom

Next.js (React 19 / App Router) throws a hydration mismatch that points to a
Server Component such as `src/app/production/[slug]/page.tsx`. The diff shows an
extra `<a>` wrapper, a missing `<i>`, or a text-node discrepancy inside HTML that
came from the database.

Example stack diff:

```
+ <a className="related-cat-link ..." ...>
- <i className="bi bi-droplet-half me-2 text-primary">
```

The `<i>` in the diff may not exist in the React component at all. It comes from
HTML stored in the database and rendered via `dangerouslySetInnerHTML`.

## Root cause

Database fields containing "HTML" were actually written in JSX syntax:

- `{/* Оловянный силикон */}` comments
- Self-closing tags: `<i class="bi bi-droplet-half" />`
- Other JSX-only constructs

When this string is passed to `dangerouslySetInnerHTML`, React on the server and
React on the client (or the browser's HTML parser) may normalize it differently,
leading to mismatched trees.

## Reproduction recipe

1. Store JSX-style HTML in a SQLite/JSON field, e.g.:

   ```html
   <section>
     {/* Оловянный силикон */}
     <h3><i class="bi bi-droplet-half" /> Оловянный силикон</h3>
   </section>
   ```

2. Render it in a Server Component:

   ```tsx
   <section dangerouslySetInnerHTML={{ __html: category.seo_text }} />
   ```

3. Open the page. Hydration mismatch appears even when the React component
   itself is clean.

## Fix

Convert the stored string to valid HTML before rendering:

1. Remove JSX comments: replace `{/* ... */}` with nothing.
2. Convert self-closing HTML-looking tags to paired tags:
   `<i class="..." />` → `<i class="..."></i>`.
3. Strip surplus blank lines left by comment removal.

Reference Python cleanup helper:

```python
import re

def fix_seo_html(text: str) -> str:
    if not text:
        return text
    text = re.sub(r'\{/?\*.*?\*/?\}', '', text, flags=re.DOTALL)
    text = re.sub(r'<i\s+([^>]*?)\s*/>', r'<i \1></i>', text)
    text = re.sub(r'\n[ \t]*\n[ \t]*\n', '\n\n', text)
    return text.strip()
```

## Prevention

- When migrating JSX content into a database to be used with
  `dangerouslySetInnerHTML`, always run it through a JSX-to-HTML sanitizer
  first.
- Do not assume self-closing tags are valid in the browser parser for all
  elements. `<img />` and `<br />` are fine; `<i />`, `<span />`, `<div />` are
  not reliable when parsed from a raw string.
- Avoid JSX comments in strings meant for `dangerouslySetInnerHTML`.

## Verification

1. Apply the cleanup to the DB.
2. Run `npm run build` (Next.js SSG/SSR must pass).
3. Hard-refresh the affected page and confirm no hydration overlay.
