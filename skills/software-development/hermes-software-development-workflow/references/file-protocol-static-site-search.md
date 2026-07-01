# Static Site Search: File-Protocol Failure & Inline Fallback Recipe

## Problem

Static HTML sites with client-side search (fetching `assets/search-data.json`) work fine
on `http://` but **fail silently on `file://` / opened from disk** because browsers block
`fetch()` across file boundaries with CORS-like restrictions (Chrome/Firefox: `Failed to load
resource: net::ERR_FAILED`; Safari: different error).

The user reports: *"поиск не работает, нет ключевых слов для поиска"* — the search box
shows nothing because `searchIndex` never gets populated.

## Root Causes Seen in This Session

1. **Hardcoded search path** — `app/assets/search-data.json` instead of depth-relative
2. **No fallback** — only `fetch()` with no `.catch()` recovery path
3. **Broken CSS** — `calc(var(--nav-h)+24px)` without spaces (invalid CSS) clips content
   under the fixed navbar, making the site look "broken" even when search might work
4. **Broken relative paths in subpages** — `../assets/app.js` in a page at depth 2
   (e.g. `pages/frameworks/django.html`) resolves wrong, so the JS never loads at all

## Solution: Inline Search Data + Depth-Aware URL

### Step 1 — Build `search-data.json` as normal
Valid JSON array. Each item: `{title, keywords, href}` where `href` is **relative to site root**.

### Step 2 — Inject inline fallback into every HTML

```python
import json

with open('assets/search-data.json') as f:
    data = json.load(f)

inline = '<script>window.__SEARCH_DATA__ = ' + json.dumps(data, ensure_ascii=False) + ';</script>'
# Insert before the <script src="assets/app.js"> tag in every .html file
```

This makes search data available synchronously — no fetch needed.

### Step 3 — Make `searchUrl()` compute from `location.pathname`

```javascript
function searchUrl() {
  const path = location.pathname;               // e.g. /pages/python-core/intro.html
  const parts = path.split('/').filter(Boolean);
  // Strip filename (.html) so depth = folder nesting
  if (parts.length && /\.[a-zA-Z]+$/.test(parts[parts.length - 1])) {
    parts.pop();
  }
  const depth = parts.length;                   // 0 = root, 2 = pages/python-core/
  if (depth === 0) return 'assets/search-data.json';
  return '../'.repeat(depth) + 'assets/search-data.json';
}
```

**Why this beats `document.currentScript.src`:** `currentScript` is unreliable in
`defer`/`async` scripts and does not work when the script is loaded via dynamic import
or inserted after DOM ready.

### Step 4 — Use absolute URL resolution for result clicks

```javascript
function renderResults(matches, q) {
  results.innerHTML = matches.map(m => {
    const url = new URL(m.href, location.href).href;  // absolute
    return `<div class="result-item" data-href="${url}">...</div>`;
  }).join('');
  results.querySelectorAll('.result-item').forEach(el => {
    el.addEventListener('click', () => { location.href = el.dataset.href; });
  });
}
```

**Why `onclick="location.href='...'"` fails:** inside `onclick` strings, relative `href`
values resolve against the **current page's directory**, not site root. If the user is
on `pages/frameworks/django.html` and clicks a result with `href="index.html"`, they
navigate to `pages/frameworks/index.html` (404) instead of the real root `index.html`.

## Verification Steps

1. Serve via HTTP (`python3 -m http.server`) → confirm search works
2. Open `index.html` directly from disk (`file://`) → confirm search still works
   (inline fallback triggers)
3. Navigate to a subpage (e.g. `pages/python-core/intro.html`) via `file://` →
   confirm search still works
4. Use the verification script from `scripts/verify-static-site.py` (checks all
   path depths, inline fallback presence, and valid JSON)

## CSS Gotcha: `calc()` Spacing

`calc(var(--nav-h)+24px)` is **invalid** in CSS — the `+` must have whitespace:
`calc(var(--nav-h) + 24px)`. Without it, the declaration is dropped and `.content`
has no top padding, causing it to slide under the fixed navbar.

Always validate CSS `calc()` expressions with a regex check during site audit:
```python
bad = re.findall(r'calc\([^)]*\+[0-9]', css_content)
```

## Pitfalls Summary

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Hardcoded `app/assets/...` path | 404 on any non-root deployment | Compute depth from `pathname` |
| No inline fallback | Search empty on `file://` | Inject `window.__SEARCH_DATA__` |
| `onclick` with relative href | Wrong navigation from subpages | Use `new URL()` + event listener |
| `calc()` without spaces | Content clipped under navbar | Add whitespace around `+`/`-` |
| Wrong `../` depth for assets | JS/CSS 404 on subpages | `../../assets/` for depth 2, verify with script |
