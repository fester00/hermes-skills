# HTML-validate workflow for pentajunior-v2

One-off HTML validation of compiled pages: one page per template type is enough because pages are template-based.

## Steps

1. Build the project:
   ```bash
   cd /home/natan/pentajunior-v2 && npm run build
   ```
2. Pick one compiled HTML per template from `.next/server/app/`:
   - `index.html` — home
   - `production/<category>.html` — category
   - `production/<category>/<subcategory>.html` — subcategory
   - `production/<category>/<subcategory>/<product>.html` — product
   - `news.html`, `blog/<slug>.html`, `info.html`, `price.html`, `contacts.html`, `policy.html`
3. Run `html-validate`:
   ```bash
   cd /home/natan/pentajunior-v2
   npx html-validate .next/server/app/index.html \
     .next/server/app/production/<category>.html \
     .next/server/app/production/<category>/<subcategory>.html \
     .next/server/app/production/<category>/<subcategory>/<product>.html \
     .next/server/app/news.html \
     .next/server/app/blog/<slug>.html \
     .next/server/app/info.html \
     .next/server/app/price.html \
     .next/server/app/contacts.html \
     .next/server/app/policy.html
   ```

## Interpreting results

Most warnings from `html-validate` on Next.js output are non-actionable:

| Rule | Why it fires | Action |
|------|--------------|--------|
| `void-style` | Next.js emits `<hr/>`, `<meta/>`, `<img/>`, `<input/>`, `<link/>` | Ignore — valid HTML5 |
| `attr-case` | React attributes like `noModule`, `rowSpan` | Ignore |
| `attribute-boolean-style` | `async="true"`, `hidden="until-found"` | Ignore |
| `no-inline-style` | Bootstrap / Next.js DevTools inject inline styles | Ignore unless from own code |
| `prefer-native-element` | Next.js DevTools `<div role="progressbar">` | Ignore |
| `valid-id` | DevTools `_R_` ID | Ignore |

Actionable findings to fix:

- `unique-landmark` — multiple `<nav>` without `aria-label`; add `aria-label` to each.
- `no-dup-class` — duplicate CSS class like `text-light text-light`.
- Heading hierarchy skips (H1 → H3, H2 → H5) — replace footer/service headings with styled `<p>`/`<div>` or adjust levels.
- Actual unclosed tags or wrong nesting (rare).

## Checking heading hierarchy programmatically

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, 'html.parser')
headings = [(int(t.name[1]), t.get_text(strip=True)) for t in soup.find_all(['h1','h2','h3','h4','h5','h6'])]
prev = 0
for lvl, text in headings:
    if prev and lvl > prev + 1:
        print(f'Skip H{prev} -> H{lvl}: {text[:60]}')
    prev = lvl
```

## Related

- `references/seo_jsonld_audit.py` — run before validating HTML.
- `pentajunior-v2-nextjs-sqlite` skill for project build gate rules.
