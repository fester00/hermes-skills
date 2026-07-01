# VIDVIS Landing-to-Catalog Session Notes

Session: 2026-06-29
Project: VIDVIS at /home/natan/vidvis (Next.js 14 luxury art gallery & home textile)
Goal: Extend existing landing page into a full product catalog with sections, categories, and product detail pages.

## Key decisions

- Routing:
  - `/` homepage (horizontal scroll signature stays here)
  - `/art` and `/textile` section landing pages
  - `/art/[categorySlug]` and `/textile/[categorySlug]` category pages
  - `/product/[productSlug]` flat product detail (works across sections)

- Data layer: hardcoded TypeScript catalog in `src/data/catalog.ts` with typed `Section / Category / Product` trees, plus helper functions `getSectionBySlug`, `getCategoryBySlug`, `getProductBySlug`.

- Placeholder images: organized under `public/images/<section>/<category>/` and reusing existing nature imagery until real photos are available.

- Reusable catalog components:
  - `PageHero` — parallax hero with title reveal
  - `CategoryGrid` — 3D tilt cards
  - `ProductGrid` — product card grid
  - `ProductDetail` — gallery + specs + contact CTA
  - `ContactCTA` — closing contact block
  - `PageShell` — shared wrapper with preloader toggle

- Preloader: animated preloader only on `/`; inner pages use `PageShell preloader={false}`.

- Homepage navigation:
  - Art Gallery title + cards link to `/art`
  - Home Textile title links to `/textile`
  - Category images + headings + list items link to `/textile/<categorySlug>`

- Verification gate: `npx tsc --noEmit` and `npm run build` must pass before commit/push. Browser smoke test on `localhost:3001`.

## Pitfalls encountered

- `lucide-react@1.22.0` lacked `Sparkles` icon. Resolved by downgrading to `lucide-react@^0.487.0`.
- `MagneticCursor` had SSR-incompatible `window.innerWidth` at component top level. Fixed by moving check into `useEffect`.
- `Navigation` used `window.location.href` causing full reloads. Fixed to use `next/link` and active state.

## Remaining todos for future sessions

- Replace placeholder images with real product photos.
- Update contact email/phone placeholders to real values.
- Add SEO metadata to category and product pages.
- Consider mobile hamburger menu for `Navigation`.
