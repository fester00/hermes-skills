#!/usr/bin/env bash
# Verify strict three-level routing after migrating away from [[...rest]] catch-all.
# Adjust BASE_URL if you run the dev server on a different port.

set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:3001}"

CATEGORY_URL="$BASE_URL/production/silikon-dlya-zalivki-form"
SUBCATEGORY_URL="$BASE_URL/production/silikon-dlya-zalivki-form/silikon-platinovyj-dla-form"
PRODUCT_URL="$BASE_URL/production/silikon-dlya-zalivki-form/silikon-platinovyj-dla-form/unisil-9500"
OLD_FLAT_URL="$BASE_URL/production/silikon-dlya-zalivki-form/unisil-9500"

check_http() {
  local url="$1"
  local expected="$2"
  local label="$3"
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  if [ "$code" = "$expected" ]; then
    echo "✓ $label: $url -> $code"
  else
    echo "✗ $label: $url -> $code (expected $expected)"
    exit 1
  fi
}

check_redirect() {
  local url="$1"
  local expected_location="$2"
  local label="$3"
  local location
  location=$(curl -s -I "$url" | grep -i '^location:' | awk '{$1=""; print $0}' | tr -d '\r' | xargs)
  if [ "$location" = "$expected_location" ]; then
    echo "✓ $label: $url -> $location"
  else
    echo "✗ $label: $url -> '$location' (expected '$expected_location')"
    exit 1
  fi
}

echo "Verifying three-level routing at $BASE_URL..."
check_http "$CATEGORY_URL" "200" "category page"
check_http "$SUBCATEGORY_URL" "200" "subcategory page"
check_http "$PRODUCT_URL" "200" "product page"
check_http "$OLD_FLAT_URL" "308" "old flat product URL"
check_redirect "$OLD_FLAT_URL" "$PRODUCT_URL" "redirect target"

echo ""
echo "All checks passed."
