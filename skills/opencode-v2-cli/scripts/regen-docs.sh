#!/usr/bin/env bash
# Mirror the OpenCode v2 docs to /mnt/data/natan-storage/docs/opencode-v2 (ru + en).
# Usage: bash regen-docs.sh
#
# Non-destructive by construction: each page is downloaded to a temp file, validated, and only then
# moved into place. A network hiccup therefore leaves the existing copy untouched instead of deleting it.
#
# Two traps this script exists to avoid:
#   1. `local a="$1" b="$TMP/$(basename "$a")"` -> 'unbound variable' under `set -u` on bash 5.
#      Expand every variable on its own `local` line.
#   2. `curl -o dest` followed by `rm -f dest` on failure wipes already-mirrored pages. Fetch to a temp
#      file and `mv` only after validation.
set -uo pipefail

BASE="${BASE:-/mnt/data/natan-storage/docs/opencode-v2}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PAGES="cli config agents mcp-servers rules permissions skills plugins tools custom-tools commands tui
server sdk models acp troubleshooting share policies network ide ecosystem formatters keybinds lsp
web enterprise gitlab github references windows-wsl themes"

mkdir -p "$BASE/ru" "$BASE/en"
ok_ru=0; only_en=0; stale=0; failed=()

# fetch <url> <dest>  -> 0 when the page was downloaded and looks valid
fetch() {
  local url="$1"
  local dest="$2"
  local tmp code
  tmp="$TMP/$(basename "$dest").$$"
  for attempt in 1 2 3; do
    code=$(curl -sL --noproxy '*' --max-time 90 -o "$tmp" -w '%{http_code}' "$url" 2>/dev/null)
    if [ "$code" = "200" ] && [ "$(stat -c%s "$tmp" 2>/dev/null || echo 0)" -gt 500 ] \
       && ! head -c 40 "$tmp" | grep -q '"status"'; then
      mv -f "$tmp" "$dest"; return 0
    fi
    sleep 2
  done
  rm -f "$tmp"; return 1
}

for p in $PAGES; do
  # 1) official Russian translation, if it exists
  if fetch "https://opencode.ai/docs/ru/$p.md" "$BASE/ru/$p.md"; then
    ok_ru=$((ok_ru+1))
  elif [ -s "$BASE/ru/$p.md" ]; then
    stale=$((stale+1))          # translation unavailable this run — keep the old copy
  fi
  # 2) English original, always
  if fetch "https://opencode.ai/docs/$p.md" "$BASE/en/$p.md"; then
    [ -s "$BASE/ru/$p.md" ] || only_en=$((only_en+1))
  elif [ -s "$BASE/en/$p.md" ]; then
    stale=$((stale+1))
  else
    failed+=("$p")
  fi
done

fetch "https://opencode.ai/docs/index.md" "$BASE/en/index.md" || true

echo "CLI version:        $(command -v opencode >/dev/null && opencode --version || echo 'opencode not found')"
echo "ru pages on disk:   $(ls -1 "$BASE/ru" | wc -l)  (refreshed now: $ok_ru)"
echo "en pages on disk:   $(ls -1 "$BASE/en" | wc -l)"
echo "english-only pages: $only_en"
echo "kept from cache:    $stale"
echo "not fetched at all: ${failed[*]:-none}"
echo "mirror size:        $(du -sh "$BASE" | cut -f1)"
