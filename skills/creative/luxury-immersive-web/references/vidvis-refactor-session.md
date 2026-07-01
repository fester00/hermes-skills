# VIDVIS Refactor Session — June 2026

Session context: extending a Next.js 14 luxury landing page (`vidvis`) into a multi-page product catalog with sections, categories, and product pages.

## Decisions Made

1. **Preloader only on homepage.** The cinematic preloader should not delay navigation on inner pages. Use `PageShell preloader={boolean}` to control it per page.
2. **Homepage as navigation hub.** The `ArtGallery` and `HomeTextile` sections on `/` now link to their respective routes:
   - Art Gallery title and cards → `/art`
   - Textile title, panel images, headings, and list items → `/textile/<categorySlug>`
3. **Centralised layout via `PageShell`.** Replaced duplicated `useLenis`/`MagneticCursor`/`Navigation`/`Footer` imports on every page with a single wrapper.
4. **Accessibility pass.** Added `useReducedMotion`, focus-visible rings, cursor-pointer on all interactive elements, and proper keyboard navigation.

## Code Patterns Captured

### PageShell

```tsx
// src/components/PageShell.tsx
"use client";
import { useState } from "react";
import { useLenis } from "@/hooks/useLenis";
import Preloader from "@/components/Preloader";
import Navigation from "@/components/Navigation";
import MagneticCursor from "@/components/MagneticCursor";
import Footer from "@/components/Footer";

interface PageShellProps {
  children: React.ReactNode;
  preloader?: boolean;
}

export default function PageShell({ children, preloader = true }: PageShellProps) {
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

### useReducedMotion Hook

```tsx
// src/hooks/useReducedMotion.ts
"use client";
import { useEffect, useState } from "react";

export function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(mq.matches);
    const onChange = (e: MediaQueryListEvent) => setReduced(e.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);
  return reduced;
}
```

Use inside `useLenis` to skip smooth scroll, and inside GSAP/Motion components to skip scroll-triggered animations.

### Link-Wrapped Section Cards

When converting a decorative card into a link, keep the same visual hover/3D tilt effects by replacing the outer `div` with `next/link` and moving interaction styles to the link:

```tsx
<Link href="/art" className="group relative aspect-[4/5] overflow-hidden cursor-pointer block focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-vidvis-gold/60 rounded-sm" style={{ transformStyle: "preserve-3d" }} data-magnetic>
  {/* image and overlay */}
  {/* text */}
</Link>
```

## Pitfall: lucide-react Versioning

`lucide-react@1.22.0` is an old release and is missing modern icons such as `Sparkles`. The maintained line at the time of this session is `0.x` (e.g. `^0.487.0`). If an installed icon import fails with "Can't resolve 'lucide-react'", check the version before assuming the package is missing.

```bash
npm install lucide-react@^0.487.0
```

## Project URLs After Refactor

| Page | Route |
|---|---|
| Home | `/` |
| Art Gallery section | `/art` |
| Textile section | `/textile` |
| Interior paintings category | `/art/interior-paintings` |
| Home decor vases category | `/art/home-decor-vases` |
| Table decor category | `/art/table-decor` |
| Bed linen category | `/textile/bed-linen` |
| Decorative pillows category | `/textile/decorative-pillows` |
| Curtains category | `/textile/curtains` |
| Product detail | `/product/<productSlug>` |

## Verification Commands

```bash
cd /home/natan/vidvis
npx tsc --noEmit
npm run build
npm run dev -- -p 3001
```
