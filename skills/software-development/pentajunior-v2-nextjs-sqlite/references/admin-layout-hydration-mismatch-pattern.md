# Admin Layout Hydration Mismatch — pentajunior-v2

## Symptom

Browser console shows React hydration error on `/admin` routes. The diff shows the server rendered one shell (often a spinner/centered placeholder) while the client rendered another (the full `admin-app` shell with topbar).

Typical mismatch diff:

```
+ className="admin-app d-flex flex-column min-vh-100"
- className="d-flex justify-content-center align-items-center vh-100"
+ <header className="admin-topbar ...">
- <div className="spinner-border text-light">
```

## Root cause

`src/app/admin/layout.tsx` is a Client Component (`'use client'`). If the initial render branches on browser-only globals such as `document.cookie`, `typeof window !== 'undefined'`, `localStorage`, or `Date.now()`, the server and client produce different HTML.

Common anti-pattern in admin auth:

```tsx
const loading = useMemo(() => {
  if (pathname === '/admin/login') return false;
  return !hasAdminToken(); // reads document.cookie → false on server, true on client
}, [pathname]);
```

On the server `document.cookie` is empty/absent, so the component returns the spinner. On the client the cookie exists, so it returns the full layout.

## Fix

Always render the **same initial UI** on server and client. Perform auth checks and redirects inside `useEffect` after hydration. Use a local state flag to decide when the check is complete.

### Recommended implementation

```tsx
'use client';

import { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';

function hasAdminToken(): boolean {
  if (typeof document === 'undefined') return false;
  return !!document.cookie.match(/admin_token=([^;]+)/);
}

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    setAuthChecked(true);
    if (pathname === '/admin/login') return;
    if (!hasAdminToken()) {
      router.push('/admin/login');
    }
  }, [pathname, router]);

  const isLogin = pathname === '/admin/login';
  const showAppShell = isLogin || authChecked;
  const showSpinner = !isLogin && authChecked && !hasAdminToken();

  if (!showAppShell || showSpinner) {
    return (
      <div className="d-flex justify-content-center align-items-center vh-100" style={{ background: '#161b22' }}>
        <div className="spinner-border text-light" />
      </div>
    );
  }

  return (
    <div className="admin-app d-flex flex-column min-vh-100" style={{ background: '#161b22' }}>
      {/* topbar, sidebar, main */}
      {children}
    </div>
  );
}
```

Key points:
1. Do **not** read `document.cookie` / `window` / `localStorage` during the synchronous render path that runs on the server.
2. Keep the initial spinner visually consistent with the final shell background so there is no color flash.
3. For `/admin/login`, render the login form directly; do not redirect or spin.
4. The redirect belongs in `useEffect` so it only runs on the client.

## Verification

After the fix, run the build gate and check the browser console on `/admin`:

```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
cd /home/natan/pentajunior-v2
./node_modules/.bin/tsc --noEmit
rm -rf .next tsconfig.tsbuildinfo
npm run build
```

Expected: no hydration warnings; static pages count unchanged.

## See also

- `client-server-boundary-and-types-pattern.md` — keeping server-only modules out of client components.
