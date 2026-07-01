# VIDVIS: Catalog Links, Preloader Scope, and Accessibility Refactor

Session: 2026-06-29
Project: `https://github.com/fester00/vidvis` (Next.js 14 luxury art gallery / home textile site)

## Goal

Extend the existing single-page VIDVIS site into a multi-page catalog:

- `/art` — Art Gallery section landing
- `/textile` — Home Textile section landing
- `/art/[categorySlug]` — category product grids
- `/textile/[categorySlug]` — category product grids
- `/product/[productSlug]` — product detail pages

Then do a design-skill-driven refactor and UX cleanup.

## Design Skills Used

- `ui-ux-pro-max` — loaded mid-session at user request for design review.
- `luxury-immersive-web` — patterns for parallax, 3D tilt, Lenis, grain, magnetic cursor, preloader.

**Lesson:** load `ui-ux-pro-max` and `luxury-immersive-web` *before* implementing any luxury web task. The user explicitly corrected the agent for not loading skills first.

## Architecture

### Data

Central catalog in `src/data/catalog.ts`:

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
  id: 'art' | 'textile';
  slug: string;
  name: string;
  description: string;
  cover: string;
  accent: string;
  categories: Category[];
}
```

Helpers: `getSectionBySlug`, `getCategoryBySlug`, `getProductBySlug`, `getAllProducts`.

### Routes

| Route | File |
|-------|------|
| `/` | `src/app/page.tsx` |
| `/art` | `src/app/art/page.tsx` |
| `/textile` | `src/app/textile/page.tsx` |
| `/art/[categorySlug]` | `src/app/art/[categorySlug]/page.tsx` + `ArtCategoryClient.tsx` |
| `/textile/[categorySlug]` | `src/app/textile/[categorySlug]/page.tsx` + `TextileCategoryClient.tsx` |
| `/product/[productSlug]` | `src/app/product/[productSlug]/page.tsx` + `ProductDetailClient.tsx` |

Server page components fetch data via catalog helpers and pass to "Client" wrapper components that contain GSAP/Framer Motion effects.

### Shared Components

- `PageHero` — parallax hero for inner pages.
- `CategoryGrid` — 3D-tilt category cards.
- `ProductGrid` — product cards with hover reveal.
- `ProductDetail` — image gallery + specs + CTA.
- `ContactCTA` — contact block used on all inner pages.
- `About` — new homepage section.

## Key UX Decisions

### Preloader Scope

The dramatic `Preloader` animation is kept **only on the root page** (`/`). Inner pages render immediately to avoid repetitive loading friction.

```tsx
// src/app/page.tsx only
const [loaded, setLoaded] = useState(false);
{!loaded && <Preloader onDone={() => setLoaded(true)} />}
```

### Homepage Section Links

Art Gallery section:
- Section title links to `/art`.
- Every gallery card links to `/art`.

Home Textile section:
- Section title links to `/textile`.
- Each category panel image links to `/textile/[categorySlug]`.
- Each category heading links to `/textile/[categorySlug]`.
- List items under each category are visual-only (not individually linked).

Products section:
- All featured-product cards link to `/product/[productSlug]`.

### Accessibility Refactor

- `useReducedMotion` hook added (`src/hooks/useReducedMotion.ts`).
- All GSAP animations and Lenis respect `prefers-reduced-motion: reduce`.
- `MagneticCursor` fixed to avoid SSR `window.innerWidth` check at render time; now checks inside `useEffect`.
- `focus-visible` rings added to links, buttons, cards.
- All interactive elements get `cursor-pointer`.
- Central price formatter: `src/lib/format.ts`.

## Notable Bug: lucide-react Versioning

Symptom:
```
./src/components/About.tsx:7:1
Module not found: Can't resolve 'lucide-react'
import { Sparkles } from "lucide-react";
```

Root cause: `package.json` had `"lucide-react": "^1.22.0"`. The `1.x` line is stale and lacks modern icons. The maintained line is `0.x` (e.g. `0.487.0`).

Fix:
```bash
npm install lucide-react@0.487.0
```

See `references/lucide-react-versioning-gotcha.md` for full reproduction and prevention notes.

## Image Folders

Placeholder images were copied from existing `public/images/nature_*.jpg` into:

```
public/images/art/interior-paintings/
public/images/art/home-decor-vases/
public/images/art/table-decor/
public/images/textile/bed-linen/
public/images/textile/decorative-pillows/
public/images/textile/curtains/
```

Replace these with real product photography when available.

## Verification Commands

```bash
npx tsc --noEmit
npm run build
```

Both pass.

## Commits

- `1f7a863` — initial catalog pages
- `f35af4e` — accessibility / navigation refactor
- `4ce71f9` — lucide-react version fix
- `7e683da` — homepage links and preloader scope
