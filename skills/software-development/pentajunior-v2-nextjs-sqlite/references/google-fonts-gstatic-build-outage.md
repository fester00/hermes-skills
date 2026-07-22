# Google Fonts / fonts.gstatic.com outage breaks production build

> Session: 2026-07-12. `npm run build` failed because Turbopack could not fetch Inter woff2 files from `fonts.gstatic.com`. `deploy.sh` did not detect the failure, PM2 reloaded into a partial `.next/`, and the live site served HTML but returned 500 on all CSS/JS chunks.

## Failure chain

1. `layout.tsx` imported `Inter` from `next/font/google` with subsets `latin` and `cyrillic`.
2. `npm run build` attempted to download font files from `https://fonts.gstatic.com/s/inter/v20/...`.
3. `fonts.gstatic.com` was unreachable. Turbopack emitted errors like:
   ```
   Module not found: Can't resolve '@vercel/turbopack-next/internal/font/google/font'
   src: url(@vercel/turbopack-next/internal/font/google/font?{..."url":"https://fonts.gstatic.com/..."})
   ```
4. The `next build` process exited with code 1, leaving `.next/` partially populated.
5. `deploy.sh` continued to `pm2 reload pentajunior-v2 --update-env`.
6. `next start` loaded the broken `.next/` directory.
7. Server rendered HTML successfully (Next.js cache/SSG fallback) but could not resolve `/_next/static/chunks/*.css` or `*.js` referenced by that HTML.
8. Browser showed unstyled content; `curl -I` on chunks returned `500 Internal Server Error`.
9. PM2 error log showed:
   ```
   Error [ChunkLoadError]: Failed to load chunk server/chunks/ssr/src_components_UI_0vo02vd._.js
   cause: Error: Cannot find module '/home/natan/pentajunior-v2/.next/server/chunks/ssr/...'
   Error: ENOENT: no such file or directory, open '/home/natan/pentajunior-v2/.next/prerender-manifest.json'
   ```

## Immediate fix

On the production host:

```bash
cd /home/natan/pentajunior-v2
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1

# Remove partial build
rm -rf .next tsconfig.tsbuildinfo

# Rebuild after removing or replacing Inter
npm run build

# Reload the running server
pm2 reload pentajunior-v2 --update-env
```

## Temporary Inter fallback

In `src/app/layout.tsx`:

```tsx
// import { Inter } from "next/font/google";

export default function RootLayout({ children }) {
  return (
    <html lang="ru" data-scroll-behavior="smooth">
      <body>{children}</body>
    </html>
  );
}
```

Keep `globals.css` font stack on system fonts until `fonts.gstatic.com` is stable.

## Verification after recovery

```bash
# Main HTML
curl -s -o /dev/null -w "%{http_code}\n" https://pentajunior.ru/

# Extract chunk URLs and verify they return 200
for path in $(curl -s https://pentajunior.ru/ | grep -oP '/_next/static/[^"]+\.(css|js)' | sort -u); do
  echo -n "$path -> "
  curl -sI "https://pentajunior.ru$path" | head -1 | tr -d '\r\n'
  echo
done
```

Expected: all CSS → `200 OK` with `Content-Type: text/css`; all JS → `200 OK` with `application/javascript`.

## Long-term prevention

- Make `deploy.sh` fail fast if `npm run build` fails (`set -e` already present, but confirm it is not overridden by `pm2 reload` success).
- Consider vendoring the Inter font files into `public/fonts/` and loading them via CSS `@font-face`, removing the runtime dependency on `fonts.gstatic.com`.
- Add a post-deploy smoke test that checks one HTML page plus a sample CSS and JS chunk.
