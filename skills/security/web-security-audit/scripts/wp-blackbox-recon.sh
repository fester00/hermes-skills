#!/usr/bin/env bash
# Read-only black-box sweep of a WordPress site (GET/HEAD + one benign xmlrpc POST).
# Usage: ./wp-blackbox-recon.sh https://host.tld
# Prints one line per probe: <path> <http_code> <bytes> <first bytes of body>.
# Assumes the owner authorised the audit; changes nothing on the target.
set -u
BASE="${1:?usage: $0 https://host.tld}"
UA="Mozilla/5.0 (authorized-audit)"
UA_CURL=(curl -sS --max-time 20 -A "$UA")

probe() { # path [curl-extra...]
  local path="$1"; shift
  local out code size
  out=$("${UA_CURL[@]}" -o /tmp/recon.body -w '%{http_code} %{size_download}' "$@" "$BASE$path" 2>/dev/null)
  code=${out%% *}; size=${out##* }
  printf '%-48s %s %8s | %s\n' "$path" "$code" "$size" \
    "$(head -c 140 /tmp/recon.body | tr -d '\r\n' )"
}

echo "== TLS ==============================================================="
HOST=${BASE#https://}; HOST=${HOST%%/*}
for v in tls1 tls1_1 tls1_2; do
  printf '%-8s ' "$v"
  echo | timeout 12 openssl s_client -"$v" -cipher 'DEFAULT@SECLEVEL=0' \
        -connect "${HOST}:443" -servername "$HOST" 2>&1 \
        | grep -E 'Protocol *:' | head -1 || echo 'no handshake'
done

echo "== headers ==========================================================="
"${UA_CURL[@]}" -D - -o /dev/null "$BASE/" \
  | grep -iE '^(server|via|x-powered-by|strict-transport-security|x-frame-options|x-content-type-options|content-security-policy|referrer-policy|permissions-policy|x-cache)'
echo "-- missing security headers (expect 0) --"
"${UA_CURL[@]}" -D - -o /dev/null "$BASE/" \
  | grep -icE 'strict-transport-security|x-frame-options|x-content-type-options'

echo "== fingerprint ======================================================="
probe /
"${UA_CURL[@]}" "$BASE/" | grep -oE '<meta name="generator"[^>]*>' || echo '(no generator meta)'
"${UA_CURL[@]}" "$BASE/feed/" | grep -oE '<generator>[^<]*' || true

echo "== plugin inventory (readme.txt Stable tag) =========================="
for slug in wp-optimize wordpress-seo updraftplus google-sitemap-generator \
            google-analytics-for-wordpress optinmonster tinymce-advanced \
            wp-yandex-metrika taxonomy-images woocommerce contact-form-7 elementor \
            wordfence better-wp-security all-in-one-wp-migration duplicator wp-mail-smtp; do
  code=$("${UA_CURL[@]}" -o /tmp/recon.rd -w '%{http_code}' "$BASE/wp-content/plugins/$slug/readme.txt" 2>/dev/null)
  [ "$code" = "200" ] && printf '%-42s %s\n' "$slug" "$(grep -i 'Stable tag' /tmp/recon.rd | head -1)"
done

echo "== paths ============================================================="
for p in /wp-json/ /wp-json/wp/v2/users /?author=1 /xmlrpc.php /readme.html /license.txt \
         /wp-admin/install.php /wp-content/debug.log /wp-config.php.bak /.env /.git/config \
         /wp-content/uploads/ /wp-content/updraft/ /wp-content/ai1wm-backups/ \
         /wp-content/backups-dup-lite/ /wp-content/mu-plugins/ /wp-sitemap.xml /sitemap.xml; do
  probe "$p"
done

echo "== xmlrpc ==========================================================="
"${UA_CURL[@]}" -X POST -d '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName><params></params></methodCall>' \
  "$BASE/xmlrpc.php" | grep -oE '<string>(system\.[a-zA-Z]+|pingback\.[a-zA-Z]+)</string>' | sort -u
echo '-- multicall with throwaway creds (a 403 fault = credentials are evaluated) --'
"${UA_CURL[@]}" -X POST -d '<?xml version="1.0"?><methodCall><methodName>system.multicall</methodName><params><param><value><array><data><value><struct><member><name>methodName</name><value><string>wp.getUsersBlogs</string></value></member><member><name>params</name><value><array><data><value><string>audit</string></value><value><string>audit</string></value></data></array></value></member></struct></value></data></array></value></param></params></methodCall>' \
  "$BASE/xmlrpc.php" | head -c 400

echo
echo "== done: read-only sweep, nothing was changed on the target =="
