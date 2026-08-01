# Migrating a React/Vite SPA landing page to Next.js 15 App Router

Session-specific reference distilled from building `silicone-lending-v3` (a one-page SSR landing) from the existing Vite project `silicone-landing-v2`.

## When to use this reference

- User has an existing React/Vite (or Create React App) landing page.
- User wants a Next.js version with SSR/SSG for SEO.
- Scope is a single page or a small multi-page marketing site.

## 1. Stack choices

- **Next.js 15** App Router.
- **React 19** + TypeScript.
- **Tailwind CSS 3.4.x** with `tailwind.config.js` + `postcss.config.js`. Fresh Next.js/Vite scaffolds may install Tailwind v4 by default; pin `^3.4.x` and the classic config if the existing project uses it.
- **Fonts:** use `next/font/google` with `latin` and `cyrillic` subsets. It self-hosts fonts, avoiding Google Fonts CDN blocking in some regions.
- **Icons:** `lucide-react` is a safe drop-in if the Vite project already uses it.

## 2. Project skeleton

Minimal `package.json` scripts:

```json
{
  "scripts": {
    "dev": "next dev -p 3001",
    "build": "next build",
    "start": "next start -p 3002"
  }
}
```

`next.config.js` for local preview or deployment behind a reverse proxy:

```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: { unoptimized: true },
};
module.exports = nextConfig;
```

Use `output: 'standalone'` only if you have a deployment pipeline that copies
`.next/standalone` to a container and you also copy `.next/static` into it.
Standalone server will 404 on JavaScript chunks if `.next/static` is not
present in the standalone tree.

Set `images.unoptimized: true` when you are using plain `img` tags and do not want to configure a loader. Re-enable `next/image` optimization only if `sharp` is installed and you are using `<Image />`.

## 3. Client Component boundary audit

In Next.js App Router, **Server Components are the default**. Any component that touches the following must start with `"use client"`:

- `onClick`, `onChange`, `onSubmit`, or any event handler prop
- `useState`, `useEffect`, `useRef`
- `document`, `window`, `localStorage`
- `localStorage`, `navigator` at render time

Typical landing-page components that become Client Components:

- `Navbar` (mobile menu toggle)
- `Hero` (scroll-to-anchor `onClick`)
- `Products` + `ProductCard` + `ProductModal` (modal state)
- `OrderForm` (form state and validation)

Static sections can stay Server Components:

- `Stats`
- `Contact` left column
- `Footer`

Common build error when boundaries are wrong:

```
Error: Event handlers cannot be passed to Client Component props.
  {type: "button", onClick: function onClick, ...}
```

Fix: add `"use client"` to the component that defines the handler, not to the page that imports it.

## 4. Metadata and JSON-LD

Put metadata in `app/layout.tsx`:

```tsx
export const metadata: Metadata = {
  title: '...',
  description: '...',
  keywords: ['...'],
  openGraph: { title: '...', description: '...', type: 'website', locale: 'ru_RU', url: '...' },
};
```

Inline JSON-LD Organization schema in the same layout:

```tsx
const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: '...',
  url: '...',
  email: '...',
  telephone: '...',
  address: { '@type': 'PostalAddress', ... },
};

// inside <head>
<script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
```

## 5. Reuse strategy from the prior version

When the user asks for `project-vN` and `project-v(N-1)` already exists:

1. Copy `public/images` and other static assets.
2. Reuse the data file (`src/data/site.ts` → `src/lib/data.ts`).
3. Reuse design tokens (Tailwind colors, font stack).
4. Keep humanized descriptions; refresh only where wording feels stale.
5. Do not start from scratch unless the user explicitly says so.

## 6. Verification checklist

- [ ] `npx tsc --noEmit` passes
- [ ] `npm run build` passes
- [ ] Production server starts on the requested port
- [ ] `curl` response contains `<title>`, one `<h1>`, semantic tags
- [ ] Headings hierarchy is correct (one `h1`, `h2` for sections, `h3` for cards)
- [ ] Modal opens/closes by click, Escape, and backdrop click
- [ ] Form validation fires on empty/bad fields
- [ ] Mobile screenshot shows 1-column layout and readable text
- [ ] Desktop screenshot shows intended grid and no visual regressions

## 7. Common pitfalls

- `next start` warns that it does not work with `output: 'standalone'`. For local preview use `next start -p 3002`; for real deployment use `PORT=3002 node .next/standalone/server.js` only after you have verified that `.next/static` is copied into `.next/standalone/.next/static`.
- Standalone server defaults to port 3000. Export `PORT=3002` before starting it.
- Standalone server will 404 on `/_next/static/*` chunks if `.next/static` was not copied into the standalone tree. When in doubt, use `next start` instead of standalone for local verification.
- `next/font/google` may fail during build if the network is down. It caches after first success; if blocked, fall back to system font stack but keep the font variables.
- Do not import Client Components into Server Components and try to pass event handlers. Mark the leaf component as a Client Component instead.
- When subagents create components in parallel, they may create duplicate files in both `src/components/` and `src/sections/`. Audit and remove duplicates before verification; enforce a single directory per component type in the brief.
- **Framer Motion + Next.js SSR/SSG:** never set `initial={{ opacity: 0 }}` on elements that should be visible in the first paint. With `whileInView`, the element stays at `opacity: 0` until the user scrolls, and static screenshots / `curl` / first-load will show blank content. Use `initial={{ opacity: 1, y: 20 }}` so the element is visible immediately and still animates when it enters the viewport. Apply this rule to `motion.div`, `motion.h2`, and `motion.article` in landing-page sections.
- **Heading hierarchy and semantic tags:** keep exactly one `<h1>`, use `<h2>` for section titles, `<h3>` for cards, `<main>` around sections, `<header>/<footer>` outside `<main>`. Verify with `curl | grep -oE "<(title|h1|h2|h3|header|main|footer|nav|section|article)[^/]*>"`.

## Session provenance

- Date: 2026-08-01
- From: silicone-landing-v2 (Vite) → silicone-lending-v3 (Next.js 15)
- Key fixes:
  - Added `"use client"` to `Hero.tsx` after the first build failed.
  - Removed `output: 'standalone'` after standalone server 404'd on JS chunks; verified with `next start`.
  - Removed duplicate component files in `src/components/` left by parallel subagents.
