# Next.js "This page couldn't load" Diagnosis

## Trigger

User reports their browser shows **"This page couldn't load — Reload to try again, or go back."** on a Next.js route (commonly `/blog`, `/`, `/product/[slug]`). The message is from **Google Chrome's** error fallback — not from Next.js, not from the application. It appears when Chrome cannot complete page rendering (crash, OOM, hydration failure, partial HTTP response, etc.).

This is a **class of incident**, not a single bug. Almost every "the server returns blank HTML" report on a Next.js site falls into this pattern.

---

## Why It's Almost Never a Server Bug

The phrasing is generic enough that users (and first-line agents) assume the site is broken. In practice:

- **~90% of cases:** stale browser cache after a recent deploy (Next.js chunk hashes changed; user still holds old `<script>` references).
- **~5%:** HTTP/2 stream truncation, CDN gzip/brotli mismatch, or HTTP/3 (QUIC) protocol error in the user's network path.
- **~3%:** Service Worker from a previous deployment still controlling fetches.
- **~2%:** actual server bug (rendering exception, hydration mismatch on a page that previously worked).

Before touching any server config or rolling back a deploy, you **must** confirm the server is healthy. If the server is healthy, the fix is on the user's browser — not yours.

---

## Diagnostic Checklist (server-side)

Run these in order. **Stop and report as soon as you find the bug.** Do NOT keep digging once the cause is clear.

### 1. Verify the route returns HTTP 200

```bash
curl -sS -o /dev/null -w "HTTP=%{http_code} | SIZE=%{size_download}\n" \
  https://example.com/the-broken-route
```

**Expected:** `HTTP=200 | SIZE=…` (anything > 1 KB for an HTML page).

**If HTTP=5xx:** real server bug. Skip to "Server-side bug investigation" below.
**If HTTP=200 but SIZE is suspiciously small (< 1 KB):** probably an error page served as HTML. Read it.

### 2. Verify the HTML is the actual page (not an error page)

```bash
curl -sS https://example.com/the-broken-route | head -c 2000
```

Look for:
- `<!DOCTYPE html>` at the start (not JSON, not XML error).
- Expected content keywords (e.g., your H1, your product name) in the first 2 KB.
- No string like `"Internal Server Error"`, `"Application error"`, `"stack"`, `"at Object."` (Node/Express stack traces), or `"Unhandled Runtime Error"`.

### 3. Check Next.js-specific response headers

```bash
curl -sS -D - -o /dev/null https://example.com/the-broken-route | grep -iE \
  "(x-nextjs|cache-control|content-encoding|x-powered|etag|date)"
```

Key signals:
- **`x-nextjs-cache: HIT` + `x-nextjs-prerender: 1`:** ISR-served pre-rendered page. Normal.
- **`x-nextjs-cache: MISS` + `x-nextjs-prerender: 1`:** ISR regeneration in progress. Wait 5–10 min and retry.
- **`Cache-Control: s-maxage=31536000`:** aggressive CDN cache (1 year). Browser may not even revalidate.
- **`ETag: "..."`:** stable since last successful build. Compare with prior known-good ETag if user has one.
- **`Vary: rsc, next-router-state-tree, next-router-prefetch, ...`:** confirms Next.js is in front of nginx.

### 4. Verify all referenced JS chunks return 200

```bash
# Extract chunk URLs from the page
curl -sS https://example.com/the-broken-route | \
  grep -oE '"/_next/static/chunks/[^"]+\.js"' | sort -u | head -30

# For each, check it loads
for chunk in $(...); do
  curl -sS -o /dev/null -w "$chunk -> %{http_code}\n" \
    "https://example.com${chunk//\"/}"
done
```

**Expected:** every chunk returns 200.

**If any chunk is 404:** the deploy did not finish syncing `.next/static/chunks/` to the served directory. Real server bug — investigate build artifacts.

### 5. Verify no broken `alt-svc` (HTTP/3) announcement

```bash
curl -sSI https://example.com/the-broken-route | grep -iE "alt-svc"
```

If `alt-svc` advertises `h3` but the server does not actually speak QUIC, Chrome will silently downgrade and may report "couldn't load". This is rare but worth ruling out on heavily proxied sites.

### 6. Verify CDN/edge is in sync with origin

If the site sits behind Cloudflare/Fastly/Cloudfront:
```bash
curl -sS https://example.com/the-broken-route | grep -oE "buildId\":\"[^\"]+\""
```
Then ask the user to load the page in an **Incognito window**. If Incognito works but the regular tab fails, the CDN is fine and the issue is browser state.

---

## Distinguishing Browser-Cache vs Real Bug

Use this decision tree:

```
User reports "page couldn't load"
  ├─ Server returns 5xx on the route?           → REAL BUG, investigate
  ├─ HTML is error JSON / error page?           → REAL BUG, investigate
  ├─ A JS chunk returns 404?                    → REAL BUG, deploy incomplete
  ├─ HTTP 200, valid HTML, all chunks 200?
  │   ├─ User tested Incognito → works         → BROWSER CACHE (most common)
  │   ├─ User tested other browser → works     → BROWSER CACHE / EXTENSION
  │   ├─ User tested another device → fails    → CDN / network / server
  │   └─ User has only one device               → Ask for Incognito test
  └─ User refuses to test                       → Re-verify server, give hard-refresh instructions
```

---

## What to Tell the User (when it's browser cache)

Ordered by ease-of-test:

1. **Hard refresh:** `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (macOS).
2. **Incognito / Private window:** opens with zero cache.
3. **DevTools Network → "Disable cache" checkbox → reload:** permanent until DevTools closes.
4. **Clear site data:** DevTools → Application → Storage → "Clear site data".
5. **Last resort:** clear entire browser cache + restart.

If the user is on mobile (no DevTools), only options 1 and 2 work — instruct those.

---

## When It Actually IS a Server Bug

### Hydration mismatch on a recently-edited page

A common pattern: a Server Component renders something the Client Component re-renders differently (e.g., `Date.toLocaleDateString()` without an explicit locale, `Math.random()`, `window.*` access). The browser console will show:

```
Hydration failed because the server rendered HTML didn't match the client.
```

**Fix:** make the rendering deterministic — pin locale (`'ru-RU'`), use stable seeds, or move that piece to `useEffect`.

### ISR page throws on regeneration

If `x-nextjs-cache: STALE` is followed by a regeneration that throws, the served HTML may be the previous successful build but the new build is broken. Look at server logs:
```bash
journalctl -u next-app --no-pager -n 200 | grep -iE "(error|throw|hydration)"
```
or
```bash
pm2 logs next-app --lines 200 | grep -iE "(error|throw)"
```

### `.next` directory out of sync

After a failed/incomplete `next build`, `.next/server/app/blog/page.js` may not exist even though `.next/server/app/blog/[slug]/page.js` does. Always run a **clean rebuild** before redeploying:
```bash
rm -rf .next tsconfig.tsbuildinfo
./node_modules/.bin/next build
```

---

## Prevention (long-term)

1. **Lower the ISR cache for routes users actively edit:** add per-route headers in `next.config.js`:
   ```js
   async headers() {
     return [{
       source: '/blog',
       headers: [{ key: 'Cache-Control', value: 'public, max-age=0, must-revalidate' }],
     }];
   }
   ```
   This forces browser revalidation on every visit.

2. **Bump chunk filenames on deploy:** Next.js already does this via content-hash, but if you serve `.next` from an immutable CDN, a fresh deploy with stale CDN invalidation causes 404s. Configure your CDN to purge `/_next/static/chunks/*` on deploy.

3. **Add a top-level Error Boundary in `app/error.tsx`** that renders a friendly "page crashed" message instead of letting Chrome fall back to its degraded page. This converts server-bug incidents from "page couldn't load" into "we hit an error, please reload" — easier to debug.

---

## Anti-pattern: rolling back a deploy because the user reported this

If the user reports "page couldn't load" and your server-side checks all pass:
- **DO NOT** roll back the deploy. The deploy is fine; their browser is stale.
- **DO NOT** restart Next.js, PM2, or nginx. They are fine.
- **DO** give the user the cache-invalidation instructions above.

Rolling back a known-good deploy creates real incidents (users lose new content, sometimes the rollback itself fails the build hash and propagates the same 404 problem) to fix a non-existent problem.

---

## Reference Case (pentajunior-v2 blog, 2026-09-09)

- User reported "page couldn't load" on `https://pentajunior.ru/blog`.
- `curl` to `/blog`: HTTP 200, 64 534 bytes, valid HTML with all 17 articles in JSON-LD (including new `silikon-vs-poliuretan-dlya-form`).
- `x-nextjs-cache: HIT`, `x-nextjs-prerender: 1`, `Cache-Control: s-maxage=31536000`.
- All `/_next/static/chunks/*.js` referenced from the HTML returned 200.
- Headers showed `Server: nginx/1.24.0 (Ubuntu)`, no `alt-svc`, HSTS, COOP, X-Frame-Options all correct.
- **Verdict:** browser cache. User instructed to hard-refresh.
