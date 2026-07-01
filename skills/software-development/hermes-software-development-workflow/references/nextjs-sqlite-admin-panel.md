# Next.js + better-sqlite3 Admin Panel Recipe

Condensed recipe for adding an admin panel to a Next.js 14+ project that already uses better-sqlite3 and SSG public pages.

## When This Applies

- Next.js App Router with `better-sqlite3` (synchronous, build-time DB access)
- Public pages are SSG (static site generation)
- Need admin CRUD that runs at runtime (API routes)
- Bootstrap 5 or similar already installed (no new UI deps)
- No ORM — raw SQL via better-sqlite3

## Architecture

```
Public (SSG)                Admin (Runtime)
───────────                 ─────────────
page.tsx ──→ db.ts          API route ──→ db.ts
build-time                  request-time
static HTML                 server handler
```

Both paths share `src/lib/db.ts` but admin uses it from `app/api/admin/*` (Server Components / Route Handlers) which run in Node.js runtime.

## File Inventory

### 1. Middleware: `src/middleware.ts`

```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD;

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Skip login page and auth API
  if (pathname === '/admin/login' || pathname === '/api/admin/auth') {
    return NextResponse.next();
  }

  // Protect all /admin/* and /api/admin/*
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

**⚠️ Note:** `middleware.ts` at `src/` root runs at the edge. Do NOT import `better-sqlite3` here — edge does not support native Node modules. Only do cookie checks, redirect logic.

### 2. Auth API: `src/app/api/admin/auth/route.ts`

```typescript
import { NextResponse } from 'next/server';

const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD;

export async function POST(request: Request) {
  const { password } = await request.json();
  if (password === ADMIN_PASSWORD) {
    const response = NextResponse.json({ success: true });
    response.cookies.set('admin_token', ADMIN_PASSWORD, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',              // ← NOT 'strict' — strict breaks router.push redirects
      maxAge: 60 * 60 * 24 * 7,     // 7 days
      path: '/',
    });
    return response;
  }
  return NextResponse.json({ success: false }, { status: 401 });
}
```

### 3. DB Access from API Routes

```typescript
// src/lib/admin-db.ts — separate entry to avoid importing from layout/page SSG bundles
import Database from 'better-sqlite3';
import path from 'path';

const dbPath = path.join(process.cwd(), 'pentajunior.db');
const db = new Database(dbPath);

export function getAllProductsRaw() {
  return db.prepare('SELECT * FROM products').all();
}

export function updateProduct(id: string, fields: Record<string, unknown>) {
  const setClause = Object.keys(fields).map(k => `${k} = ?`).join(', ');
  const stmt = db.prepare(`UPDATE products SET ${setClause} WHERE id = ?`);
  return stmt.run(...Object.values(fields), id);
}
```

**⚠️ Why a separate `admin-db.ts`?** If `src/lib/db.ts` has helpers that parse JSON or import Browser APIs, importing it into API routes may trigger Next.js bundling warnings. Keep admin DB access lean and Node-only.

### 4. Product List API: `src/app/api/admin/products/route.ts`

```typescript
import { NextResponse } from 'next/server';
import { getAllProductsRaw } from '@/lib/admin-db';

export async function GET() {
  const products = getAllProductsRaw();
  return NextResponse.json(products);
}
```

### 5. Upload API: `src/app/api/admin/upload/route.ts`

```typescript
import { NextResponse } from 'next/server';
import { writeFile } from 'fs/promises';
import path from 'path';

export async function POST(request: Request) {
  const formData = await request.formData();
  const file = formData.get('file') as File;
  if (!file) return NextResponse.json({ error: 'No file' }, { status: 400 });

  const allowed = ['image/jpeg', 'image/png', 'image/webp'];
  if (!allowed.includes(file.type)) {
    return NextResponse.json({ error: 'Invalid type' }, { status: 400 });
  }

  const bytes = await file.arrayBuffer();
  const buffer = Buffer.from(bytes);
  if (buffer.length > 5 * 1024 * 1024) {
    return NextResponse.json({ error: 'Max 5MB' }, { status: 400 });
  }

  const ext = file.name.split('.').pop();
  const filename = `${Date.now()}-${Math.random().toString(36).slice(2)}.${ext}`;
  const uploadDir = path.join(process.cwd(), 'public/images/admin');
  await writeFile(path.join(uploadDir, filename), buffer);

  return NextResponse.json({ url: `/images/admin/${filename}` });
}
```

### 6. Login Page: `src/app/admin/login/page.tsx`

```typescript
'use client';
import { useState } from 'react';

export default function AdminLogin() {
  const [password, setPassword] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const res = await fetch('/api/admin/auth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password }),
    });
    if (res.ok) {
      window.location.href = '/admin';  // ← full navigation ensures cookie is sent
    } else {
      alert('Неверный пароль');
    }
  }

  return (
    <div className="container mt-5" style={{ maxWidth: 400 }}>
      <h2>Админ-панель</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label>Пароль</label>
          <input
            type="password"
            className="form-control"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button type="submit" className="btn btn-primary">Войти</button>
      </form>
    </div>
  );
}
```

### 7. Dashboard Page: `src/app/admin/page.tsx`

```typescript
import Link from 'next/link';
import { getAllProductsRaw, getAllCategoriesRaw } from '@/lib/admin-db';

export default function AdminDashboard() {
  const products = getAllProductsRaw();
  const categories = getAllCategoriesRaw();

  return (
    <div className="container mt-4">
      <h1>Dashboard</h1>
      <div className="row">
        <div className="col-md-4">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Товары</h5>
              <p className="card-text">{products.length} шт.</p>
              <Link href="/admin/products" className="btn btn-primary">Управлять</Link>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Категории</h5>
              <p className="card-text">{categories.length} шт.</p>
              <Link href="/admin/categories" className="btn btn-primary">Управлять</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

**⚠️ Important:** `admin/page.tsx` is a Server Component. It can import `admin-db.ts` directly because it runs in Node.js runtime (not edge). Do NOT mark this page `'use client'`.

### 8. Admin Layout: `src/app/admin/layout.tsx`

```typescript
import Link from 'next/link';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div>
      <nav className="navbar navbar-dark bg-dark">
        <div className="container">
          <Link href="/admin" className="navbar-brand">Админка</Link>
          <div className="d-flex gap-3">
            <Link href="/admin/products" className="nav-link text-light">Товары</Link>
            <Link href="/admin/categories" className="nav-link text-light">Категории</Link>
            <Link href="/" className="nav-link text-light">На сайт →</Link>
          </div>
        </div>
      </nav>
      <main className="py-4">{children}</main>
    </div>
  );
}
```

## Verification Steps

1. `echo "ADMIN_PASSWORD=test123" >> .env.local`
2. `npx next build` — должно пройти без ошибок (admin pages не ломают SSG)
3. `npm run dev`
4. Открыть `/admin/login` — форма пароля
5. Ввести пароль → редирект на `/admin`
6. Проверить middleware: открыть `/admin` в приватном окне → редирект на login

## Common Pitfalls

- **Auth redirect loop (`sameSite: 'strict'`)** → After `fetch('/api/admin/auth')` returns success, `router.push('/admin')` triggers client-side navigation; the strict cookie is NOT sent with this navigation (no top-level cross-site GET), so middleware on `/admin` sees no token and redirects back to login. **Fix:** Set cookie with `sameSite: 'lax'` (not 'strict') and use `window.location.href = '/admin'` after login instead of `router.push`. Lax cookies are sent on same-site top-level navigations.
- **Admin modal hidden behind site header** → Public `.site-header` uses `z-index: 1100` (Bootstrap 5 default navbar) or custom CSS. Bootstrap modals default to `z-index: 1055`. When modals open inside the admin section, they render beneath the header. **Fix:** Add an admin-specific CSS override: `.admin-modal, .admin-layout .modal { z-index: 1200 !important; }` and `.admin-layout .modal-backdrop { z-index: 1190 !important; }`.
- **Middleware imports `better-sqlite3`** → Edge runtime error. Fix: only do cookie checks in middleware, DB access in API routes.
- **Admin page marked `'use client'`** → Cannot import DB. Fix: Server Component for data fetching, client components only for interactive forms.
- **SSG tries to render admin pages at build time** → Next.js App Router defaults to auto; admin pages with dynamic data should not be statically generated. Fix: use `export const dynamic = 'force-dynamic'` in admin pages, or fetch data client-side.
- **Image upload fails** → missing `public/images/admin/` directory. Fix: create it or handle in upload API.

### 5. sameSite: 'strict' on auth cookie

Setting `sameSite: 'strict'` on the `admin_token` cookie causes the cookie to **not be sent** during the redirect from `/api/admin/auth` (POST) to `/admin` (GET). The middleware at `/admin` sees no cookie and redirects back to login.

**Fix:** Use `sameSite: 'lax'` instead. `Lax` allows the cookie to be sent on top-level navigations (the redirect after login). Also use `window.location.href = '/admin'` (full page reload) rather than `router.push('/admin')` so the fresh cookie is immediately available to the middleware.

```typescript
// API route
response.cookies.set('admin_token', ADMIN_PASSWORD, {
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'lax',   // ← not 'strict'
  maxAge: 60 * 60 * 24,
  path: '/',
});

// Login page client
if (res.ok) {
  window.location.href = '/admin';  // ← not router.push
}
```

### 6. Admin modal dialogs hidden under sticky site header

If the public site uses a sticky header with `z-index: 1100+` (common with `site-header` classes), Bootstrap modals (default `z-index: 1055`) inside the admin panel will render **under** the header, making the modal header unclickable.

**Fix:** Add CSS overrides scoped to admin modals:

```css
.admin-modal-overlay {
  z-index: 1200 !important;
}
.admin-modal-dialog {
  z-index: 1201 !important;
}
```

Apply both classes to the modal wrapper and dialog in admin pages:

```tsx
<div className="modal show d-block admin-modal-overlay" ...>
  <div className="modal-dialog admin-modal-dialog" ...>
```

This lifts admin modals above any public-site sticky header without affecting the public site layout.

## Environment Variables

```
ADMIN_PASSWORD=<your-secure-password>
```

---

## Promo / New Product System via stock_info JSON in SQLite

Pattern for adding "promotions" and "new arrivals" to a Next.js + SQLite + SSG catalog without schema migration. Uses existing `stock_info` TEXT column (JSON) and a `news` INTEGER flag.

### When This Applies

- Already using SQLite for products (better-sqlite3)
- Want promo prices (old → new) without adding columns
- Want "NEW" badges on catalog cards
- Admin panel already exists (CRUD products)
- No schema migration desired (zero-downtime, zero ALTER TABLE)

### Schema (Already Exists)

```sql
CREATE TABLE products (
    id TEXT PRIMARY KEY,
    -- ... other fields ...
    news INTEGER DEFAULT 0,      -- 1 = new product
    stock_info TEXT              -- JSON: {"newPrice": "...", "condition": "..."}
);
```

`stock_info` is reused for promo data: if JSON contains `newPrice`, the product is on promotion.

### Admin Panel Fields

Add these to the product edit modal (`/admin/products`):

| Field | DB Mapping | UI Element |
|---|---|---|
| Новинка | `news` (0/1) | Checkbox |
| Акция | inferred from `stock_info` | Checkbox (enables price/condition fields) |
| Акционная цена | `stock_info.newPrice` | Text input (shown when акция checked) |
| Условие акции | `stock_info.condition` | Text input (e.g. "-20% до 31.12") |

**Save logic:**
```typescript
const stockInfo = isStock
  ? JSON.stringify({ newPrice, condition })
  : null;
// UPDATE products SET news = ?, stock_info = ? WHERE id = ?
```

### Component Badges

#### Product Card (catalog grid)

```tsx
{product.stockInfo?.newPrice && (
  <span className="catalog-badge-stock">Акция</span>
)}
{product.news === 1 && (
  <span className="catalog-badge-new">Новинка</span>
)}
```

#### Price Block

```tsx
{product.stockInfo?.newPrice ? (
  <>
    <span className="text-decoration-line-through text-muted">{product.price}</span>
    <span className="text-danger fw-bold ms-2">{product.stockInfo.newPrice}</span>
  </>
) : (
  <span>{product.price}</span>
)}
```

#### Product Detail Page

Same badges + price block, plus `condition` rendered as a subtitle or badge text.

### Styling (globals.css)

```css
.catalog-badge-stock {
  position: absolute;
  top: 10px;
  right: 10px;
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: #fff;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  z-index: 2;
}
.catalog-badge-new {
  background: linear-gradient(135deg, #28a745, #218838);
}
```

### /news Page

Split products into two groups:

```tsx
const newProducts = products.filter(p => p.news === 1);
const stockProducts = products.filter(p => p.stock_info); // has promo data
```

### Why This Pattern Works

- **Zero migration** — reuses `stock_info` and `news`
- **Backward compatible** — old data without JSON still works
- **Admin UI is obvious** — checkbox → fields → save
- **SSG unchanged** — badges render at build time from parsed JSON
- **Extensible** — add `stock_info.endDate` for promo expiration later

### References

- `nextjs-sqlite-static-generation/references/performance-ssg-sqlite.md` — SSG build performance FAQ
