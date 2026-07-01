# Static Site Verification Checklist

Run these checks after all subagents finish. If any check fails, fix before declaring the site done.

## Path Checks

### All pages get correct asset paths

```bash
cd PROJECT_ROOT
for f in $(find pages -name '*.html'); do
  if ! grep -q 'href="../../assets/style.css"' "$f"; then
    echo "MISSING CSS: $f"
  fi
  if ! grep -q 'src="../../assets/script.js"' "$f"; then
    echo "MISSING JS: $f"
  fi
  if ! grep -q 'data-base-path="../../"' "$f"; then
    echo "MISSING base-path: $f"
  fi
done
```

### Root page has root-relative paths

```bash
grep 'href="assets/style.css"' index.html || echo "FAIL: index.html missing root CSS"
grep 'src="assets/script.js"' index.html || echo "FAIL: index.html missing root JS"
```

### No `../../` leaks on root page

```bash
if grep '../../' index.html; then
  echo "FAIL: root page has ../../ paths (should be root-relative)"
fi
```

### No bare `pages/` on nested pages

```bash
for f in $(find pages -name '*.html'); do
  if grep -q 'href="pages/' "$f" && ! grep -q 'href="../../pages/' "$f"; then
    echo "BARE PATH: $f"
  fi
done
```

## Content Checks

### Every page has required sections

```bash
for f in $(find . -name '*.html'); do
  for check in 'id="search-overlay"' 'class="site-header"' \
               'id="sidebar"' 'class="main-content"' \
               'class="content-article"' 'class="page-nav"'; do
    if ! grep -q "$check" "$f"; then
      echo "MISSING $check in $f"
    fi
  done
done
```

### Code blocks have copy buttons

```bash
for f in $(find . -name '*.html'); do
  BLOCKS=$(grep -c 'class="code-block"' "$f")
  BTNS=$(grep -c 'class="copy-btn"' "$f")
  if [ "$BLOCKS" -gt 0 ] && [ "$BTNS" -lt "$BLOCKS" ]; then
    echo "COPY BTN MISMATCH: $f (blocks: $BLOCKS, buttons: $BTNS)"
  fi
done
```

## Search Integration

### search-data.json has all pages

```bash
python3 -c "
import json, os
data = json.load(open('assets/search-data.json'))
pages = [p for p in data if not p['path'].endswith('index.html')]
html_files = [os.path.relpath(p, '.') for p in __import__('glob').glob('pages/**/*.html', recursive=True)]
missing = set(html_files) - set(x['path'] for x in data)
if missing:
    print('MISSING from search:', missing)
else:
    print('All', len(html_files), 'pages indexed. OK')
"
```

## Page-Nav Continuity

Check prev/next links form a chain. No orphan pages (except first/last).

```bash
# Extract all page-nav destinations and sources
# Manual: open each page, verify prev→actual previous page, next→actual next
```

## Responsive

```bash
# CSS must have these media queries
grep -q 'max-width: 1024px' assets/style.css && echo "✓ tablet" || echo "✗ tablet"
grep -q 'max-width: 768px' assets/style.css && echo "✓ mobile" || echo "✗ mobile"
```

## Live HTTP Test

```bash
python3 -m http.server 8765 --bind 127.0.0.1 &
sleep 1
curl -s -o /dev/null -w "index: %{http_code}\n" http://127.0.0.1:8765/
curl -s -o /dev/null -w "css: %{http_code}\n" http://127.0.0.1:8765/assets/style.css
# Kill server after
curl -s http://127.0.0.1:8765/pages/promises-async/promises.html | grep -q '<title>' && echo "✓ nested page serves" || echo "✗ nested page fails"
```
