# Script-Generation Fallback for Multi-Page Static Sites

## Context
When building a static site with 10+ HTML pages, `delegate_task` subagents frequently timeout (~600 s) because each agent tries to write many files sequentially via API tool calls. This reference documents the fallback used in production: generate ALL pages locally via a Python script using `write_file` / `terminal`, bypassing the tool-call overhead.

## Workflow

### Step 1: Prepare Content in Memory
Define a single Python dict `PAGE_CONTENT = {page_id: html_body_string}` that holds raw HTML (paragraphs, headings, code blocks) for every page. Use helper functions like `mkpre(code)` and `mkcard(title, body)` to keep content readable.

### Step 2: Define Navigation Inventory Once
Create a tree `NAV_GROUPS` with groups and items. Each item has:
- `id` — matches a key in `PAGE_CONTENT`
- `title`, `href`, `data-title`

### Step 3: Render Function
A single `make_page(title, content, active_href, depth_dots)` function:
- `depth_dots`: `""` for index, `"../"` for pages/python-core/*.html, `"../../"` for deeper pages.
- Sidebar: iterate `NAV_GROUPS`, emit `<a>` with `depth_dots + href`, add `active` class if `href == active_href`.
- Path to assets: `depth_dots + "assets/"`.

### Step 4: Write All Pages in a Loop
```python
PAGE_DEFS = [
    ("index.html", "Главная", "index.html", "", "index"),
    ("pages/python-core/intro.html", "Введение", "pages/python-core/intro.html", "../", "intro"),
    # ... 18 definitions, total runtime ~1 second
]
for filepath, title, active_href, depth_dots, key in PAGE_DEFS:
    html = make_page(title, PAGE_CONTENT[key], active_href, depth_dots)
    write_file(path=os.path.join(PROJECT, filepath), content=html)
```

### Step 5: Assets (CSS + JS + search-data.json)
Write `style.css`, `app.js`, and `search-data.json` directly via `write_file` or embed them into the same script.

## Key Pitfall: f-strings with backslashes
When generating HTML with `aria-current="page"` inside an f-string, NEVER inline `"aria-current=\"page\"" if active_cls else ""` — Python 3.11 raises `SyntaxError: f-string expression part cannot include a backslash`.

**Fix:** Pre-compute the variable BEFORE the f-string:
```python
aria = ' aria-current="page"' if active_cls else ""
lines.append(f'<a href="{...}" class="..."{aria}>...</a>')
```

## Page Inventory Example (19 pages)
```
index.html
pages/python-core/intro, syntax, variables, functions, classes, modules, exceptions
pages/frameworks/django, fastapi, flask, pandas, numpy
pages/libraries/requests, sqlalchemy, celery, pydantic, pillow, pyqt
```

## Verification After Generation
1. `find project/ -name "*.html" | wc -l` → expect 19
2. `python3 -c "import json; json.load(open('project/assets/search-data.json'))"`
3. Start `python3 -m http.server 8765` and visually verify with headless screenshot.

## Critical Pitfall: JS breaks when opened via `file://`
When a user opens pages by double-clicking `index.html` in a file manager, the URL becomes `file:///path/to/project/index.html`. The naive `searchUrl()` in `app.js` uses `location.pathname.split('/').filter(Boolean)` which yields the **full filesystem path segments** (`['path', 'to', 'project', 'index.html']`), generating `../../assets/search-data.json` which resolves **outside the project**.

This causes `fetch()` to 404, which then throws an unhandled error that breaks all remaining JS initialization (search, active sidebar, copy buttons).

**Fix in `app.js`:**
```javascript
function searchUrl() {
  const styleLink = document.querySelector('link[rel="stylesheet"]');
  if (styleLink) {
    const href = styleLink.getAttribute('href');
    if (href) {
      const cssUrl = new URL(href, location.href).href;
      return cssUrl.replace(/style\.css$/, 'search-data.json');
    }
  }
  return 'assets/search-data.json';
}
```
This resolves relative paths via the already-correct stylesheet link, working for both `http://` and `file://`.

## Result
- All 19 pages generated in ~1 second locally
- Zero subagent timeouts
- Consistent nav, paths, and markup across every page
