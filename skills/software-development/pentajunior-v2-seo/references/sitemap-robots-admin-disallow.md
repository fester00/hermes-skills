# Sitemap / robots maintenance for pentajunior-v2

Checked 2026-06-23. Use this as the reference for keeping admin and service routes out of search indexes.

## Current setup

- `src/app/sitemap.ts` — generates `/sitemap.xml`.
- `src/app/robots.ts` — generates `/robots.txt`.

## What should NOT be in sitemap

- `/admin` and `/admin/*`
- `/api/*`
- `/_next/*`
- Any auth, login, or private routes

## What should be in disallow of robots.txt

- `/api/`
- `/_next/`
- `/admin/`

## How to add a new disallow rule

Edit `src/app/robots.ts`:

```ts
import { MetadataRoute } from "next";
import CONFIG from "@/app/syte-config";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: [
          "/api/",
          "/_next/",
          "/admin/",
        ],
      },
      {
        userAgent: "Yandex",
        allow: "/",
        disallow: [
          "/api/",
          "/_next/",
          "/admin/",
        ],
      },
    ],
    host: CONFIG.baseUrl,
    sitemap: `${CONFIG.baseUrl}/sitemap.xml`,
  };
}
```

Then run:

```bash
cd /home/natan/pentajunior-v2
npx tsc --noEmit && npm run build
```

## Verification

Check generated robots.txt:

```bash
curl -s https://pentajunior.ru/robots.txt
```

Expected output:

```
User-Agent: *
Allow: /
Disallow: /api/
Disallow: /_next/
Disallow: /admin/

User-Agent: Yandex
Allow: /
Disallow: /api/
Disallow: /_next/
Disallow: /admin/

Host: https://pentajunior.ru
Sitemap: https://pentajunior.ru/sitemap.xml
```

## When to revisit

- Adding a new private route (cart, account, checkout, admin sub-section).
- Adding a new service path that should not be indexed.
- Migrating domains or base URL.
