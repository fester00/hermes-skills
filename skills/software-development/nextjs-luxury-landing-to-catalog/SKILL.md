---
name: nextjs-luxury-landing-to-catalog
description: |
  Class-level patterns for extending a polished Next.js landing page into a
  multi-page product catalog while preserving its existing visual identity,
  motion language, and luxury feel.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [software-development, nextjs, react, typescript, tailwind, gsap, framer-motion, catalog, luxury, app-router]
triggers:
  - Extend Next.js landing page into product catalog
  - Add category pages to existing Next.js site without breaking homepage style
  - Preserve color palette and motion effects across new pages
  - Build Next.js product detail pages that match existing brand site
  - Avoid horizontal scroll on new pages while keeping it on homepage
  - Dynamic routes for categories and products in Next.js App Router
  - Placeholder image strategy for new product folders
---

# Next.js Luxury Landing → Product Catalog

A class-level runbook for expanding a visually rich Next.js landing page into a full product catalog (sections → categories → products) without losing the established brand language.

## 1. When to use this skill

Use when a user has a polished, animation-heavy Next.js landing page and wants to add:
- section landing pages (e.g. `/art`, `/textile`)
- category listing pages (e.g. `/art/[categorySlug]`)
- product detail pages (e.g. `/product/[productSlug]`)
- navigation links and breadcrumbs across new pages

The key constraint: **preserve the existing visual identity** (colors, typography, motion patterns) and **do not degrade the homepage experience**.

## 2. Pre-flight study

**CRITICAL — load skills first.** Before writing code, scan `skills_list()` and load any skill that matches the task domain. For this pattern, at minimum load `nextjs-luxury-landing-to-catalog` itself; for design-heavy work also load `luxury-immersive-web` and/or `ui-ux-pro-max` before proposing architecture.

Then inspect the existing project thoroughly:

1. Read `package.json` — note animation libraries (GSAP, Framer Motion, Lenis, Three.js), fonts, Tailwind config.
2. Read `src/app/page.tsx`, `layout.tsx`, `globals.css`, `tailwind.config.ts`.
3. Read every section component to understand the motion vocabulary (parallax, 3D tilt, horizontal scroll, magnetic cursor, preloader, grain overlay).
4. List existing images in `public/images/` to know what can be reused as placeholders.
5. Identify the navigation component and how it links to sections vs. pages.

Only after this study, propose a routing and data architecture for user approval.

## 3. Recommended routing architecture

Keep URLs flat and predictable:

```
/                          homepage
/art                       section landing
/textile                   section landing
/art/[categorySlug]        category listing
/textile/[categorySlug]    category listing
/product/[productSlug]    product detail (flat, works across sections)
```

Why flat product URLs?
- Product cards on the homepage can link directly to `/product/:slug`.
- Product slugs are unique across the whole catalog.
- Avoids deeply nested routes like `/art/:category/:product` that complicate `generateStaticParams` and breadcrumbs.

## 4. Shared catalog data layer

Create `src/data/catalog.ts` with typed section/category/product trees:

```ts
export interface Product {
  slug: string;
  name: string;
  shortDesc: string;
  fullDesc: string;
  priceFrom: number;
  priceTo?: number;
  material: string;
  dimensions: string;
  images: string[];
}

export interface Category {
  slug: string;
  name: string;
  description: string;
  cover: string;
  products: Product[];
}

export interface Section {
  slug: string;
  name: string;
  description: string;
  cover: string;
  accent: string;
  categories: Category[];
}

export const catalog: Section[] = [...];

export function getSectionBySlug(slug: string) { ... }
export function getCategoryBySlug(sectionSlug, categorySlug) { ... }
export function getProductBySlug(productSlug) { ... }
```

Keep it hardcoded TypeScript when there is no DB yet. It gives type safety, easy static generation, and simple migration to a CMS/DB later.

## 5. Placeholder image strategy

When real product photos are not available yet, create the folder structure and copy existing brand imagery as placeholders:

```
public/images/art/interior-paintings/
public/images/art/home-decor-vases/
public/images/art/table-decor/
public/images/textile/bed-linen/
public/images/textile/decorative-pillows/
public/images/textile/curtains/
```

Document this clearly to the user so they know exactly which files to replace. Do not block delivery waiting for real assets.

## 6. Reusable catalog components

Create shared components that match the existing motion language:

- `PageHero` — parallax background, breadcrumbs, title reveal, gold accent word.
- `CategoryGrid` — 3D tilt cards, image parallax, gold underline, hover overlay.
- `ProductGrid` — same card vocabulary as the homepage products section.
- `ProductDetail` — large hero image, thumbnail gallery, specs grid, CTA button.
- `ContactCTA` — closing section linking to contacts/phone/email.

Reuse `Navigation`, `Footer`, `MagneticCursor`, `Preloader`, and `useLenis` from the homepage to keep global behavior consistent.

## 7. Preserving the homepage-only experience

If the homepage has a signature effect that would be exhausting on every page (e.g. horizontal scroll or an animated preloader), **keep it only on the homepage**. On internal pages:

- Use vertical scroll.
- Reuse the visual elements (parallax, reveal, tilt) but in calmer doses.
- Keep the same color palette, grain overlay, cursor, and optionally the preloader if the user wants it globally; if the user wants the preloader only on the root page, wrap it with a toggle.

A reusable `PageShell` component is the cleanest way to manage this:

```tsx
// src/components/PageShell.tsx
"use client";
import { useState } from "react";
import { useLenis } from "@/hooks/useLenis";
import Preloader from "@/components/Preloader";
import Navigation from "@/components/Navigation";
import MagneticCursor from "@/components/MagneticCursor";
import Footer from "@/components/Footer";

export default function PageShell({
  children,
  preloader = true,
}: {
  children: React.ReactNode;
  preloader?: boolean;
}) {
  useLenis();
  const [loaded, setLoaded] = useState(false);
  return (
    <>
      {preloader && !loaded && <Preloader onDone={() => setLoaded(true)} />}
      <main className={`grain ${loaded || !preloader ? "opacity-100" : "opacity-0"} transition-opacity duration-500`}>
        <MagneticCursor />
        <Navigation />
        {children}
        <Footer />
      </main>
    </>
  );
}
```

Usage:
- Homepage: `<PageShell preloader={true}>...`
- Inner pages: `<PageShell preloader={false}>...`

This avoids duplicating `useLenis`, `MagneticCursor`, `Navigation`, and `Footer` on every page.

This makes the homepage the "hero moment" while the rest of the site feels like a coherent extension.

## 8. Server vs. client split for dynamic routes

Use a server page that calls catalog helpers and passes data to a client wrapper:

```tsx
// app/art/[categorySlug]/page.tsx
import { notFound } from "next/navigation";
import ArtCategoryClient from "./ArtCategoryClient";
import { getCategoryBySlug } from "@/data/catalog";

export default function Page({ params }: { params: { categorySlug: string } }) {
  const data = getCategoryBySlug("art", params.categorySlug);
  if (!data) return notFound();
  return <ArtCategoryClient section={data.section} category={data.category} />;
}
```

The client wrapper imports `useLenis`, `Preloader`, `MagneticCursor`, `Navigation`, etc. This keeps route-level logic server-side while interactive components stay client-side.

## 9. Navigation update rules

Update the existing navigation so it works on every page:

- Logo links to `/`.
- Menu items route to section pages (e.g. `/art`, `/textile`) or, on the homepage, scroll to the matching section.
- Use `usePathname()` to detect if the user is on the homepage.
- Prefer `Link` from `next/link` for internal routes; avoid `window.location.href` because it causes a full reload and loses Lenis smooth-scroll state.
- Add focus-visible rings and `cursor-pointer` on all interactive elements for accessibility.

## 10. Footer and CTA update rules

- Add real links to new section/category pages in the footer.
- Add a `ContactCTA` section with email and phone placeholders (clearly marked for replacement).
- Use the same button style as the rest of the site.
- Add an "About" section on the homepage if the footer references `#about`, so the anchor works.

## 11. Contact button pattern

When a cart/purchase flow is not needed, use a "Связаться с нами" button that links to the contacts section or a contact page:

```tsx
<Link href="/#contacts" className="...">
  <Phone size={18} /> Связаться с нами
</Link>
```

Keep the CTA visible on category, product, and section pages.

## 12. Pitfalls from VIDVIS session

- **Skills must be discovered with `skills_list()` first.** The system-prompt skill list is only a hint. Obsidian indexes may lag. Load the most specific skill (this one) plus `luxury-immersive-web` / `ui-ux-pro-max` before proposing architecture.
- **Don't assume `lucide-react` version is current.** A stale `^1.x` release may lack icons that exist in the modern `0.x` line. Pin a recent version if icons like `Sparkles` are needed.
- **Respect `prefers-reduced-motion`.** All GSAP/Lenis animations should read a `useReducedMotion()` hook and degrade gracefully; otherwise accessibility checkers and motion-sensitive users suffer.
- **Homepage-only effects need a toggle.** Use a `PageShell` with a `preloader` boolean (and later a `horizontalScroll` boolean if needed) so internal pages can opt out cleanly.
- **Navigation should use `Link`, not `window.location.href`.** A full reload breaks Lenis smooth scroll and resets component state.
- **Breadcrumbs are optional by user decision.** The default checklist says add them, but ask the user. In VIDVIS the user explicitly opted out.

## 13. Workflow for future landing→catalog tasks

1. `skills_list()` → load this skill, `luxury-immersive-web`, `ui-ux-pro-max`, `writing-plans`.
2. `writing-plans` → produce a formal implementation plan saved to `docs/plans/` or `.hermes/plans/`.
3. Execute plan with `tsc` + `npm run build` gates after every major step.
4. Verify in browser on the requested port (e.g. `localhost:3001`).
5. Commit and push with clear conventional-commit messages.

## 14. Verification checklist

- [ ] `npx tsc --noEmit` passes.
- [ ] `npm run build` succeeds and generates all expected routes.
- [ ] New pages use the same colors, fonts, grain, cursor, and preloader as the homepage.
- [ ] Horizontal scroll or other homepage-only signatures do not leak onto internal pages.
- [ ] Navigation links work from every page and use `Link` rather than `window.location.href`.
- [ ] Breadcrumbs are present on section, category, and product pages unless the user explicitly opted out.
- [ ] Product detail pages have a clear "back" link.
- [ ] Placeholder images are organized in `public/images/<section>/<category>/`.
- [ ] User is told which files are placeholders and where to put real photos.
- [ ] CTA button links to a real contact method or placeholder is clearly marked.
- [ ] If preloader is homepage-only, verify inner pages load immediately without it.
- [ ] Preferably run a browser check on `localhost` for the new routes.
- [ ] `prefers-reduced-motion` is handled in `useLenis`, GSAP components, and the magnetic cursor.

## References

- `references/vidvis-landing-to-catalog-session.md` — concrete session notes from the VIDVIS project: route plan, catalog data shape, component breakdown, placeholder image layout, build verification, and pitfalls encountered.
- `references/vidvis-refactor-session.md` — follow-up session: PageShell refactor, accessibility improvements, navigation fix, preloader scope, and homepage deep-linking to sections/categories.
