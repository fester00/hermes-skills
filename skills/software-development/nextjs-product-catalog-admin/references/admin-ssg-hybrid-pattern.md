# Admin Panel + SSG Hybrid Pattern

## Context

A Next.js site serves public catalog/product pages as **static HTML** (SSG) for
performance and SEO. The same project also needs a **runtime admin panel** for
content management (CRUD products, categories, prices) without rebuilding the
entire site on every data change.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Project                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │  Public SSG  │    │  Admin API   │    │  Admin UI    │   │
│  │  /products   │    │  /api/admin  │    │  /admin/*    │   │
│  │  /categories │    │  POST/PUT    │    │  Client-side │   │
│  │  Static HTML │    │  SQLite CRUD │    │  rendered    │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│         ↑                  ↑                    ↑             │
│    build-time only    runtime (admin visits)  runtime       │
│    SQLite queries     SQLite read/write       cookie auth   │
└─────────────────────────────────────────────────────────────┘
```

**Key principle:** Public visitors hit pre-built static files. Zero runtime DB
load for them. Admin users hit API routes that read/write SQLite.

## File Structure

```
src/
  lib/db.ts              # better-sqlite3 wrapper + TypeScript types
  app/
    (public)/            # SSG pages (product detail, category, home)
      product/[slug]/
      category/[slug]/
    admin/               # Client-side admin shell
      layout.tsx         # Auth check, sidebar, topbar
      page.tsx           # Dashboard
      products/
        page.tsx         # Product CRUD table + modal
      categories/
        page.tsx         # Category CRUD table + modal
      login/
        page.tsx         # Login form
    api/admin/
      auth/route.ts      # POST login → set admin_token cookie
      products/route.ts  # GET/POST/PUT/DELETE
      categories/route.ts # GET/POST/PUT/DELETE
  middleware.ts          # Protect /admin/* and /api/admin/*
```

## Cookie Auth Pattern

### The `httpOnly` trap

If the API sets `httpOnly: true`:

```ts
// src/app/api/admin/auth/route.ts  — BROKEN for client guards
response.cookies.set('admin_token', token, {
  httpOnly: true,   // ← invisible to document.cookie
  sameSite: 'lax',
  path: '/',
});
```

And the client layout checks auth with:

```ts
// src/app/admin/layout.tsx
const token = document.cookie.match(/admin_token=([^;]+)/);
if (!token) router.push('/admin/login');
```

Then after successful login the cookie exists server-side but **the client
never sees it**, causing an infinite redirect loop:
`login → /admin (no cookie seen) → login → /admin → ...`

### Fix

Remove `httpOnly` if the client needs to read the cookie:

```ts
response.cookies.set('admin_token', token, {
  // httpOnly removed — client-side readable
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'lax',
  maxAge: 60 * 60 * 24,
  path: '/',
});
```

Alternative: keep `httpOnly` and move auth check to **middleware** (which has
access to request cookies), then pass the auth state to the client via props
or context.

## Middleware Protection

```ts
// src/middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const ADMIN_PASSWORD=proces...WORD || 'fallback';

export function middleware(request: NextRequest) {
  const isAdminRoute = request.nextUrl.pathname.startsWith('/admin');
  const isAdminApi = request.nextUrl.pathname.startsWith('/api/admin');

  if (!isAdminRoute && !isAdminApi) return NextResponse.next();

  const token = request.cookies.get('admin_token')?.value;
  if (token !== ADMIN_PASSWORD) {
    if (isAdminApi) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
    return NextResponse.redirect(new URL('/admin/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/admin/:path*', '/api/admin/:path*'],
};
```

## Hiding Public Chrome on Admin Routes

The public site has `Header`, `Footer`, `FloatingActionButton`, `ScrollProgress`.
These should not appear on `/admin/*`.

**Solution:** `ClientLayout` component wrapping the root layout, using
`usePathname()` to conditionally render public chrome:

```tsx
// src/components/ClientLayout.tsx
'use client';
import { usePathname } from 'next/navigation';

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isAdmin = pathname?.startsWith('/admin');

  return (
    <>
      {!isAdmin && <Header />}
      {!isAdmin && <ScrollProgress />}
      {children}
      {!isAdmin && <Footer />}
      {!isAdmin && <FloatingActionButton />}
    </>
  );
}
```

The root layout (`src/app/layout.tsx`) renders `<ClientLayout>{children}</ClientLayout>`
instead of rendering `Header`/`Footer` directly.

## Admin Shell Layout

```tsx
// src/app/admin/layout.tsx
'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  useEffect(() => {
    const token = document.cookie.match(/admin_token=([^;]+)/);
    if (!token) router.push('/admin/login');
  }, [router]);

  return (
    <div className="admin-app">
      <aside className="admin-sidebar">...</aside>
      <div className="admin-main-wrapper">
        <header className="admin-topbar">...</header>
        <main className="admin-main">{children}</main>
      </div>
    </div>
  );
}
```

## Data Flow: Build-Time vs Runtime

| Phase | SQLite Access | Pages Affected |
|---|---|---|
| `npm run build` | Read-only via `better-sqlite3` in `generateStaticParams` | All public product/category pages |
| Admin visits `/admin/products` | Read via fetch → API route | Admin UI only |
| Admin saves product | Write via API route → UPDATE/INSERT | Admin UI refreshes; public pages stale until rebuild |
| `npm run build` (after admin edits) | Read updated data | Public pages refreshed with new content |

## Database: `.gitignore` Rules

```gitignore
# Database files — never commit
*.db
*.sqlite
*.sqlite3

# Environment
.env*
```

The SQLite file (`pentajunior.db`) is local-only. Each deployment environment
(production server, local dev, CI) maintains its own copy. For backup/transfer,
use `sqlite3 pentajunior.db .dump > backup.sql`.

## Security Checklist

- [ ] `ADMIN_PASSWORD` is long and random, stored only in `.env.local`
- [ ] `admin_token` cookie is NOT `httpOnly` (only if client layout reads it)
- [ ] Middleware validates token on every `/admin/*` and `/api/admin/*` request
- [ ] API routes return 401 for invalid tokens, not redirects
- [ ] No SQL injection — use parameterized queries in `better-sqlite3`
- [ ] No `.db` or `.env*` files in git history

## Performance Notes

**Q: Does runtime admin CRUD slow the public site?**

**A:** No. Public pages are static HTML files generated at build time. The
admin API routes execute only when an admin is actively using the panel. Regular
visitors never trigger DB queries.

**Q: How to refresh public pages after admin edits?**

**A:** Options:
1. Manual: `npm run build` + redeploy
2. ISR (Incremental Static Regeneration): add `revalidate = 60` to public pages
3. Webhook: admin save triggers a build hook on your hosting platform
4. SSR fallback: rare product pages as SSR instead of SSG (slower but always fresh)

## Real-World Usage

Applied in PentaJunior v2:
- Public site: 60+ product pages, 12 category pages — all SSG from SQLite
- Admin panel: CRUD for products/categories with dark theme, modals, tables
- Cookie auth with client-side readable token
- `ClientLayout` hides public header/footer on `/admin/*`
- `middleware.ts` guards all admin routes
- `better-sqlite3` for synchronous build-time queries + runtime API CRUD