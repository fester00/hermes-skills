#!/bin/bash
# verify-static-site.sh — sanity checks before declaring a static doc site complete
# Usage: cd project/ && bash verify-static-site.sh

set -e

echo "=== HTML page count ==="
find . -name "*.html" | sort
COUNT=$(find . -name "*.html" | wc -l)
echo "Total: $COUNT pages"

echo ""
echo "=== Asset files ==="
ls -la assets/

echo ""
echo "=== search-data.json validity ==="
python3 -c "import json; json.load(open('assets/search-data.json'))" && echo "✓ Valid JSON"

echo ""
echo "=== Path consistency (nested pages use ../assets/) ==="
if grep -r 'href="assets/' pages/ 2>/dev/null; then
  echo "✗ Some nested pages use root-relative assets/ path"
  grep -rn 'href="assets/' pages/
else
  echo "✓ All nested pages use correct relative paths"
fi

echo ""
echo "=== Missing pages (compare to inventory) ==="
# Edit this array to match your PROJECT_BRIEF inventory
EXPECTED=(
  "index.html"
  "pages/php/basics.html"
  "pages/php/functions.html"
  "pages/php/arrays.html"
  "pages/php/oop.html"
  "pages/php/regex.html"
  "pages/php/files.html"
  "pages/php/superglobals.html"
  "pages/php/error.html"
  "pages/frameworks/laravel.html"
  "pages/frameworks/symfony.html"
  "pages/frameworks/codeigniter.html"
  "pages/frameworks/yii.html"
  "pages/frameworks/others.html"
  "pages/libraries/composer.html"
  "pages/libraries/phpunit.html"
  "pages/libraries/monolog.html"
  "pages/libraries/phpmailer.html"
  "pages/libraries/others.html"
)

MISSING=0
for f in "${EXPECTED[@]}"; do
  if [ ! -f "$f" ]; then
    echo "✗ MISSING: $f"
    MISSING=$((MISSING+1))
  fi
done
if [ $MISSING -eq 0 ]; then
  echo "✓ All expected pages exist"
fi

echo ""
echo "=== Start temp server for screenshot ==="
python3 -m http.server 8765 --bind 127.0.0.1 >/dev/null 2>&1 &
PID=$!
sleep 1

echo ""
echo "✓ Verification complete. Server running on http://127.0.0.1:8765 (PID $PID)"
echo "  Capture screenshot: google-chrome --headless --screenshot=/tmp/screenshot.png --window-size=1400,900 http://127.0.0.1:8765"
