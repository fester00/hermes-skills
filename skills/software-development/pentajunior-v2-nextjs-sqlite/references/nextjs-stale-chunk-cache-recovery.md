# Next.js stale build cache: CSS/JS chunks 404 with `text/plain`

## Symptom

- Browser console shows:
  ```
  Refused to apply style from 'https://pentajunior.ru/_next/static/chunks/17.y8.dyk.9m2.css'
  because its MIME type ('text/plain') is not a supported stylesheet MIME type.
  ```
- JavaScript chunks also fail with `404 (Not Found)` and `text/plain`.
- Layout looks unstyled or partially broken.

## Diagnostic checks

1. Confirm the files exist in the build output:
   ```bash
   ls -la /home/natan/pentajunior-v2/.next/static/chunks/17.y8.dyk.9m2.css
   ls -la /home/natan/pentajunior-v2/.next/static/chunks/0xlmwk60zvt5l.js
   ```
2. Confirm the running Next.js server still returns 404 for them:
   ```bash
   curl -I http://localhost:3000/_next/static/chunks/17.y8.dyk.9m2.css
   curl -I http://localhost:3000/_next/static/chunks/0xlmwk60zvt5l.js
   ```
   Both will return `404 Not Found` with `Content-Type: text/plain` even though the files are physically present.

## Root cause

Next.js build cache / prerender state becomes inconsistent. The HTML emitted by the server references CSS/JS chunk hashes from a previous or partially-written build, while the current `.next` directory contains chunks that the running server process cannot resolve through its internal routing table. The `text/plain` MIME is Next.js's generic 404 response body, not the actual CSS/JS file.

## Fix

Always use the project-required Node version via nvm:

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use v24.13.1

cd /home/natan/pentajunior-v2

# 1. Stop the running Next.js process
#    (find PID with `ss -tlnp | grep :3000` or `pm2 stop pentajunior-v2`)

# 2. Delete the entire build cache
rm -rf .next tsconfig.tsbuildinfo

# 3. Rebuild
npm run build

# 4. Start the production server
npm run start:3000
```

## Verification

After restart, these commands must return HTTP 200 with correct MIME types:

```bash
# CSS
$ curl -I http://localhost:3000/_next/static/chunks/17.y8.dyk.9m2.css
HTTP/1.1 200 OK
Content-Type: text/css
Cache-Control: public, max-age=31536000, immutable

# JS
$ curl -I http://localhost:3000/_next/static/chunks/0xlmwk60zvt5l.js
HTTP/1.1 200 OK
Content-Type: application/javascript
Cache-Control: public, max-age=31536000, immutable
```

Then check the failing public URL in a browser. The console errors should disappear.

## Common false leads

- **nginx**: If the site is served via `next start` directly on port 3000 (no nginx reverse proxy for `/_next/static`), nginx is not involved. Do not reload nginx; it will not help.
- **Browser cache**: A hard refresh (`Ctrl+Shift+R`) does not fix this; the server is genuinely returning 404.
- **File permissions**: Files are readable; the problem is internal Next.js chunk-to-request mapping.

## When to apply

Apply this rebuild whenever:
- Styles or JS intermittently break after a deploy.
- Console shows 404s for `/_next/static/chunks/*.css` or `*.js`.
- HTML references chunks that the server does not serve.
- A build was interrupted, ran out of disk, or was made over an existing `.next` directory.

## Prevention

- Always clean `.next` before production builds in deploy scripts.
- Avoid running `next dev` and `next start` against the same `.next` directory.
- After switching Node versions or Next.js patch releases, run `rm -rf .next` before the first build.

## Real incident

- **Date**: 2026-07-12
- **Page affected**: `https://pentajunior.ru/production/izdelija-iz-silikonovyh-rezin/plastini-monolitnie/silicon-sheet`
- **Missing chunks**: `17.y8.dyk.9m2.css`, `0xlmwk60zvt5l.js`
- **Resolution time**: < 5 minutes after `rm -rf .next && npm run build && npm run start:3000`.
