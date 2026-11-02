# WordPress black-box surface checklist

Everything below is a GET (or one benign POST) against a public site — status code plus a byte count is enough
of an observation to report. `scripts/wp-blackbox-recon.sh` runs the sweep.

## Fingerprint

| What | Where | Example value |
|---|---|---|
| Core version | `<meta name="generator">`, `/feed/` `<generator>`, `/readme.html`, `/license.txt` year | `WordPress 5.6.22` |
| Plugins | `/wp-content/plugins/<slug>/readme.txt` → `Stable tag:` | `wp-optimize` → `3.2.1` |
| Plugins (fallback) | `/wp-json/` → `namespaces` | `yoast/v1`, `monsterinsights/v1`, `omapp/v1` |
| Theme | `/wp-content/themes/<slug>/style.css` (`Version:`, `Tested up to:`) | `penta` 1.0.0, tested up to 5.4 |
| Hosting/WAF | `server`, `via`, `x-cache`, `wpo-cache-status` headers, whois netname | Apache behind nginx/openresty |
| Current release | `https://api.wordpress.org/core/version-check/1.7/?version=<ver>` | offers `upgrade 7.1.3` |

Slugs worth trying in bulk (each is a `readme.txt` request): `wp-optimize`, `wordpress-seo`, `updraftplus`,
`google-sitemap-generator`, `google-analytics-for-wordpress` (MonsterInsights), `optinmonster`,
`tinymce-advanced`, `wp-yandex-metrika`, `taxonomy-images`, `woocommerce`, `contact-form-7`, `elementor`,
`wordfence`, `better-wp-security`, `all-in-one-wp-migration`, `duplicator`, `wp-mail-smtp`, `cyr2lat`.
A 200 with a body means installed (and gives the version); 404 means absent.

## Unauthenticated surface (what actually gets exploited)

- **XML-RPC** — `POST /xmlrpc.php` with `system.listMethods`: presence of `system.multicall` = brute-force
  amplification (~1000 login attempts per request, bypasses `wp-login.php` throttles), `pingback.ping` =
  unauthenticated blind SSRF and DDoS reflector. Prove evaluation with one multicall batch carrying a throwaway
  login: `faultCode 403 «Неверное имя пользователя или пароль»` is the evidence. Never ping a foreign URL.
- **REST API** — `/wp-json/` (route count, namespaces). `/wp-json/wp/v2/users` blocked (403) is good news;
  `/?author=1` redirecting to the home page is hardened author enumeration.
- **Backups** — `/wp-content/updraft/` (UpdraftPlus), `/wp-content/ai1wm-backups/`, `/wp-content/backups-dup-lite/`,
  `/wp-content/uploads/backup/`. `403` = the directory exists and holds archives; `404` = absent. Say which.
- **Install/upgrade leftovers** — `/wp-admin/install.php` («Уже установлен» = harmless), `/wp-admin/setup-config.php`,
  `/wp-config.php.bak|.old|.txt`, `/.env`, `/.git/config`.
- **Logs and listings** — `/wp-content/debug.log`, `/wp-content/uploads/` (403 = no listing), `/wp-content/mu-plugins/`
  (404 is common and normal).
- **Search reflection** — `/?s=<marker>` must come back escaped (`&lt;img …&gt;`). Escaped output is a finding of
  *absence*; quote the observed entity in the report so it is not re-tested next time.
- **oEmbed proxy** — `/wp-json/oembed/1.0/proxy?url=` → 401/403 means the SSRF path is closed.
- **robots.txt** — announces backup/dump paths by `Disallow`; a plugin's static reference file there is noise,
  not a leak (open it and confirm before writing otherwise).
- **Headers** — `TRACE` → 405 is correct; missing HSTS/CSP/X-Frame-Options/X-Content-Type-Options/Referrer-Policy
  is a real finding (clickjacking on order/contact forms, downgrade on first request).
- **Cookies** — `Set-Cookie` on `/wp-login.php` without `Secure`/`HttpOnly`/`SameSite`.

## Hardening snippets to propose (into the fix plan, not silently applied)

Disable XML-RPC survivably (mu-plugin survives theme updates), plus a server-level block:

```php
<?php // wp-content/mu-plugins/disable-xmlrpc.php
add_filter('xmlrpc_enabled', '__return_false');
add_filter('pings_open', '__return_false');
add_filter('wp_headers', function ($h) { unset($h['X-Pingback']); return $h; });
```

```apache
<Files "xmlrpc.php">
    Require all denied
</Files>
```

Security headers, with a deliberately soft CSP first (unsafe-inline for scripts) so Metrika/analytics/popups do
not break — tighten in a second pass after each widget is confirmed alive:

```apache
<IfModule mod_headers.c>
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
    Header always set Permissions-Policy "geolocation=(), microphone=(), camera=()"
</IfModule>
```

Backup directories: `Require all denied` in `wp-content/updraft/.htaccess`, and verify by requesting a real
archive filename taken from the UpdraftPlus admin — a 403 on the directory alone does not prove the files are
protected.

Version disclosure: drop the `generator` meta via a filter, delete `readme.html` and `license.txt` from the root,
and remove the dump-path line from `robots.txt`.

TLS floor belongs to the hosting panel (shared hosting) — hand that step to the owner and verify yourself with
`-cipher 'DEFAULT@SECLEVEL=0'` as the baseline comparison.
