# Auth Cookie Trap: `httpOnly` + `document.cookie` Mismatch

## Symptom

After successful login (API returns 200, cookie is set), the user is NOT
redirected to the admin dashboard. Instead, the browser loops:
`login → /admin → login → /admin → ...`

Or: clicking login does nothing / stays on login page.

## Environment

- Next.js 16 App Router
- `src/app/admin/login/page.tsx` — client component with form
- `src/app/api/admin/auth/route.ts` — API route setting cookie
- `src/app/admin/layout.tsx` — client layout checking auth via `document.cookie`
- `src/middleware.ts` — optional middleware protecting `/admin/*`

## Root Cause

The API route sets the auth cookie with `httpOnly: true`:

```ts
// src/app/api/admin/auth/route.ts
response.cookies.set('admin_token', ADMIN_PASSWORD, {
  httpOnly: true,  // ← cookie invisible to JavaScript
  sameSite: 'lax',
  path: '/',
});
```

But the client-side layout reads auth state with `document.cookie`:

```ts
// src/app/admin/layout.tsx
useEffect(() => {
  const token = document.cookie.match(/admin_token=([^;]+)/);
  if (!token) {
    router.push('/admin/login');
  }
}, [pathname, router]);
```

`httpOnly` cookies are **never exposed to `document.cookie`**. So after the
API sets the cookie:

1. Browser stores cookie (visible to server, NOT to JS).
2. Login page redirects to `/admin` (`window.location.href = '/admin'`).
3. Admin layout mounts, runs `document.cookie.match(...)`.
4. Match returns `null` — cookie is httpOnly, JS can't see it.
5. Layout thinks user is unauthenticated → `router.push('/admin/login')`.
6. Infinite loop.

## Fix

### Option A: Remove `httpOnly` (simplest, client-readable)

If the auth check is client-side, the cookie must not be `httpOnly`:

```ts
response.cookies.set('admin_token', ADMIN_PASSWORD, {
  // httpOnly REMOVED
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'lax',
  maxAge: 60 * 60 * 24,
  path: '/',
});
```

Trade-off: token is readable by any JS on the page (XSS risk). Acceptable
for low-sensitivity admin panels with short-lived sessions.

### Option B: Keep `httpOnly`, move auth to server

Convert `AdminLayout` to a **server component** and read cookies from
`cookies()` (Next.js server API):

```tsx
// src/app/admin/layout.tsx — server component
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const token = cookies().get('admin_token')?.value;
  if (!token || token !== process.env.ADMIN_PASSWORD) {
    redirect('/admin/login');
  }
  return <>{children}</>;
}
```

This keeps `httpOnly` protection while correctly reading the cookie server-side.

### Option C: Keep `httpOnly`, use middleware

Let `middleware.ts` handle auth checks before the request even reaches the
layout. Middleware has access to request cookies and can redirect unauthenticated
users at the edge:

```ts
// src/middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('admin_token')?.value;
  if (!token || token !== process.env.ADMIN_PASSWORD) {
    return NextResponse.redirect(new URL('/admin/login', request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/admin/:path*'],
};
```

Then remove the client-side auth check from `AdminLayout` entirely.

## Key Takeaways

1. **`httpOnly` means JavaScript cannot read the cookie.** Any client-side
   `document.cookie` check will fail regardless of whether the cookie was
   successfully set.

2. **If the architecture uses client-side auth guards, do NOT set `httpOnly`.**
   Move auth to server components, middleware, or API routes instead.

3. **Always verify cookie visibility.** After login, open DevTools →
   Application → Cookies → check if the cookie shows under the domain.
   If it does but `document.cookie` doesn't list it = `httpOnly` is the cause.

4. **The redirect mechanism matters.** `window.location.href` forces a full
   page reload (server sees cookie). `router.push()` is client-side navigation
   (layout re-mounts, JS checks `document.cookie` again). If using
   `router.push()`, the cookie must be JS-readable.
