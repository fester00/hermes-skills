# file:// Protocol Debug Log — Session Notes

## Session: top-secret-python (19 pages, May 2026)

### Bugs Found and Fixes Applied

#### 1. `pages/pages/` — double folder duplication in inter-page links
**Symptom:** Clicking a nav link from `pages/python-core/intro.html` to `pages/frameworks/django.html` produced `pages/pages/frameworks/django.html` → ERR_FILE_NOT_FOUND.

**Root cause:** HTML nav links were written as `../pages/frameworks/django.html` instead of `../frameworks/django.html`. The `../` already exits `pages/python-core/`, landing in `pages/`. Appending `pages/frameworks/...` adds an extra `pages/` segment.

**Fix:** Mass replace `../pages/` → `../` in all nested HTML files. After fix, verify with:
```bash
grep -rn '../pages/' pages/
# expect 0 matches
```

**Lesson:** When generating links from `pages/<topic>/<page>.html`, the `depth_dots` must be exactly right:
- `pages/python-core/intro.html` → to `pages/frameworks/django.html` = `../frameworks/django.html`
- `pages/libraries/requests.html` → to `index.html` = `../../index.html`

#### 2. `search-data.json` hrefs must be root-relative; inline script rewrites them per-file
**Symptom:** Search on `file://` worked from `index.html` but broke from nested pages — clicking a result went to the wrong relative path.

**Root cause:** `inline-assets.py` v1.0 injected the SAME `window.__SEARCH_DATA__` into every HTML. Hrefs like `pages/python-core/intro.html` were correct for `index.html` but wrong for `pages/frameworks/django.html` (would resolve to `pages/frameworks/pages/python-core/intro.html`).

**Fix:** `inline-assets.py` now rewrites every href per-file using `os.path.relpath`:
```python
from_dir = os.path.dirname(html_path)
to_path = os.path.join(project_dir, href)  # href is root-relative
rel = os.path.relpath(to_path, from_dir).replace("\\", "/")
```

Result:
- `index.html` gets `href="pages/python-core/intro.html"`
- `pages/frameworks/django.html` gets `href="../python-core/intro.html"`
- `pages/libraries/requests.html` gets `href="../python-core/intro.html"`

**Critical rule:** `search-data.json` must store root-relative hrefs (`pages/core/intro.html`, NOT `../core/intro.html`). The inliner converts them. If you store relative hrefs, `os.path.relpath` produces double-escaped nonsense.

#### 3. `calc()` without spaces silently drops entire rule block
**Symptom:** `.content` had no `padding-top`, text was hidden under fixed header, background missing, but browser DevTools showed NO error.

**Root cause:** CSS: `calc(var(--nav-h)+24px)` — missing spaces around `+`. Browsers silently discard the entire declaration block containing this invalid `calc()`.

**Fix:** `calc(var(--nav-h) + 24px)` (spaces around operator).

**Detection:** When you see "styles look half-missing but no console error", grep for `calc(` immediately.

#### 4. `fetch()` forbidden on `file://`
**Symptom:** Search and copy buttons dead on `file://`, but work on `http://`.

**Fix:** Inline `search-data.json` as `window.__SEARCH_DATA__` and patch JS to use `Promise.resolve(window.__SEARCH_DATA__ || [])` instead of `fetch()`. See `scripts/inline-assets.py`.

#### 5. `navigator.clipboard` unavailable on `file://`
**Symptom:** Copy button does nothing locally.

**Fix:** Fallback via `textarea.select() + document.execCommand("copy")`. Already in `app.js` template.

### Verification Commands Used

```bash
# Check for remaining bad paths
grep -rn '../pages/' pages/

# Verify JSON validity
python3 -c "import json; json.load(open('assets/search-data.json'))"

# Count HTML
find . -name "*.html" | wc -l

# Start temp server and screenshot
cd project/ && python3 -m http.server 8766 --bind 127.0.0.1 &
google-chrome --headless --disable-gpu --no-sandbox \
  --screenshot=/tmp/screenshot.png --window-size=1400,900 \
  --virtual-time-budget=3000 http://127.0.0.1:8766
```

### File Inventory for This Session
```
19 HTML pages:
  index.html
  pages/python-core/intro, syntax, variables, functions, classes, modules, exceptions
  pages/frameworks/django, fastapi, flask, pandas, numpy
  pages/libraries/requests, sqlalchemy, celery, pydantic, pillow, pyqt
3 assets:
  assets/style.css, assets/app.js, assets/search-data.json
```
