# Admin Auth + Middleware + Logout Flow

Complete auth system from PentaJunior project (2025-06-12). Covers middleware
protection, login API with client-readable cookie, logout, and the site-header
isolation pattern.

## File: `src/middleware.ts`

```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Skip login page and auth API
  if (pathname === '/admin/login' || pathname.startsWith('/api/admin/auth')) {
    return NextResponse.next();
  }

  // Protect all admin pages and API
  if (pathname.startsWith('/admin') || pathname.startsWith('/api/admin')) {
    const token = request.cookies.get('admin_token')?.value;
    if (token !== ADMIN_PASSWORD) {
      return NextResponse.redirect(new URL('/admin/login', request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/admin/:path*', '/api/admin/:path*'],
};
```

**Key rules:**
- Skip `/admin/login` and `/api/admin/auth` — otherwise unauthenticated users
can never reach the login page or submit credentials.
- Check `request.cookies.get('admin_token')?.value` — this reads cookies from
the incoming request (available in middleware).
- Redirect with `new URL('/admin/login', request.url)` — preserves the origin
during redirects.

## File: `src/app/api/admin/auth/route.ts`

```typescript
import { NextResponse } from 'next/server';

const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123';

export async function POST(request: Request) {
  const { password } = await request.json();

  if (password === ADMIN_PASSWORD) {
    const response = NextResponse.json({ success: true });
    response.cookies.set('admin_token', password, {
      // NO httpOnly — client layout checks document.cookie
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24,   // 24 hours
      path: '/',
    });
    return response;
  }

  return NextResponse.json({ success: false }, { status: 401 });
}

export async function DELETE() {
  const response = NextResponse.json({ success: true });
  response.cookies.delete('admin_token');
  return response;
}
```

**Why no `httpOnly`?**
The admin layout (`src/app/admin/layout.tsx`) is a `'use client'` component
that checks `document.cookie` for the `admin_token`. If the cookie were
`httpOnly`, `document.cookie` would never include it → the layout would
always redirect to login → infinite redirect loop.

For low-sensitivity admin panels (no financial data, short-lived sessions), this
trade-off is acceptable. For higher security, convert the layout to a server
component and read cookies via `cookies()` from `next/headers`.

## File: `src/app/admin/login/page.tsx`

```tsx
'use client';
import { useState } from 'react';

export default function AdminLoginPage() {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');

    const res = await fetch('/api/admin/auth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password }),
    });

    if (res.ok) {
      window.location.href = '/admin';   // ← full reload, not router.push
    } else {
      setError('Неверный пароль');
    }
  }

  return (
    <div className="container py-5" style={{ maxWidth: 400 }}>
      <h2 className="text-center mb-4">Админ-панель</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label">Пароль</label>
          <input
            type="password"
            className="form-control"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <div className="alert alert-danger">{error}</div>}
        <button type="submit" className="btn btn-primary w-100">
          Войти
        </button>
      </form>
    </div>
  );
}
```

**Why `window.location.href` instead of `router.push`?**
`window.location.href` triggers a full page reload, which sends the freshly-set
cookie to the server immediately. `router.push` is client-side navigation — the
cookie may not be sent on the first navigation, causing middleware to redirect
back to login.

## File: `src/app/admin/layout.tsx`

```tsx
'use client';
import { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import Link from 'next/link';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = document.cookie.match(/admin_token=([^;]+)/);
    if (!token) {
      router.push('/admin/login');
    } else {
      setLoading(false);
    }
  }, [pathname, router]);

  async function handleLogout() {
    await fetch('/api/admin/auth', { method: 'DELETE' });
    document.cookie = 'admin_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    router.push('/');
  }

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center vh-100">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Загрузка...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-layout d-flex vh-100">
      {/* Sidebar */}
      <aside className="admin-sidebar"
        style={{ width: 250, background: '#212529', color: '#fff' }}
      >
        <div className="p-3 border-bottom border-secondary">
          <h5 className="mb-0">Админ-панель</h5>
          <small className="text-muted">Администратор</small>
        </div>
        <nav className="nav flex-column p-3">
          <Link href="/admin" className="nav-link text-light">Dashboard</Link>
          <Link href="/admin/products" className="nav-link text-light">Товары</Link>
          <Link href="/admin/categories" className="nav-link text-light">Категории</Link>
        </nav>
        <div className="mt-auto p-3 border-top border-secondary">
          <button className="btn btn-sm btn-outline-light w-100" onClick={handleLogout}>
            🚪 Выйти
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-grow-1 overflow-auto">
        <header className="admin-topbar px-4 py-3 border-bottom"
          style={{ background: '#f8f9fa' }}
        >
          <span className="text-muted">
            PentaJunior / {pathname === '/admin' ? 'Dashboard' : pathname.split('/').pop()}
          </span>
        </header>
        <main className="p-4">{children}</main>
      </div>
    </div>
  );
}
```

**Logout flow:**
1. `DELETE /api/admin/auth` — server-side cookie deletion.
2. `document.cookie = 'admin_token=; expires=...'` — client-side cookie deletion
(for immediate effect, since the server response may not update `document.cookie` instantly).
3. `router.push('/')` — redirect to public homepage.

## File: `src/components/ClientLayout.tsx` (site header isolation)

```tsx
'use client';
import { usePathname } from 'next/navigation';
import Navbar from './Navbar';
import Footer from './Footer';

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isAdmin = pathname?.startsWith('/admin');

  return (
    <>
      {!isAdmin && <Navbar />}
      {children}
      {!isAdmin && <Footer />}
    </>
  );
}
```

Wrap the root layout in `src/app/layout.tsx`:

```tsx
import ClientLayout from '@/components/ClientLayout';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>
        <ClientLayout>{children}</ClientLayout>
      </body>
    </html>
  );
}
```

## Common Pitfalls

- **Pitfall: `httpOnly` cookie + `document.cookie` check = infinite redirect loop.**
  If the login API sets `httpOnly: true` but the layout reads `document.cookie`,
  the cookie is invisible to JS. After login, the layout never sees the token
  and redirects back to login forever. Fix: remove `httpOnly` from the cookie
  OR convert the layout to a server component using `cookies()` from `next/headers`.

- **Pitfall: `sameSite: 'strict'` on auth cookie.** After `fetch('/api/admin/auth')`
  returns success, `router.push('/admin')` triggers client-side navigation. A
  `strict` cookie is NOT sent with this navigation (no top-level cross-site GET),
  so middleware at `/admin` sees no token and redirects back. Fix: use
  `sameSite: 'lax'` and `window.location.href = '/admin'` after login.

- **Pitfall: Admin modals hidden under public site header.** Even with
  `ClientLayout`, if the public navbar has `z-index: 1100+`, Bootstrap modals
  (default `z-index: 1055`) inside admin pages render beneath it. Fix: add
  `.admin-layout .modal { z-index: 1200 !important; }` and
  `.admin-layout .modal-backdrop { z-index: 1190 !important; }`.

- **Pitfall: Forgetting to skip `/admin/login` in middleware.** If the matcher
  includes `/admin/:path*` without exception for `/admin/login`, even the login
  page itself is protected — unauthenticated users can never reach it. Always
  add `pathname === '/admin/login'` as an early return.
