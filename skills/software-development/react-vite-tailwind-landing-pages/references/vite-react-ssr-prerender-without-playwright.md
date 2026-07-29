# Vite + React SSR Prerender Without Playwright

## Problem

A Vite + React SPA serves an almost empty `index.html`. For SEO, search bots
should see rendered content. The Playwright-based prerender works, but it is
heavy (requires browser download) and can hang on `requestAnimationFrame`
driven loading screens in headless environments.

## Lightweight Alternative

Render the app with `react-dom/server` inside a Vite SSR module during the
post-build step. This avoids Playwright/Chromium entirely and produces a
prerendered `dist/index.html` with body content.

## When to Use

- Vite + React SPA where content is stable at build time.
- You want to avoid Playwright as a build dependency.
- The app has a `LoadingScreen` or similar full-screen loader that prevents
  headless browser prerender from ever reaching content.

## When NOT to Use

- Pages that rely on `window`, `document`, or browser-only APIs during initial
  render. The SSR pass runs in Node; guard those with `typeof window` checks or
  load them lazily.
- Apps that fetch data client-side only.

## Steps

### 1. Add `src/prerender-entry.tsx`

```tsx
import { renderToString } from "react-dom/server";
import App from "./App";

export function render() {
  return renderToString(<App prerender />);
}
```

### 2. Add `scripts/prerender.js`

```javascript
import { createServer } from "vite";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.resolve(__dirname, "../dist");
const templatePath = path.join(distDir, "index.html");

async function prerender() {
  const vite = await createServer({
    root: path.resolve(__dirname, ".."),
    server: { middlewareMode: true },
    appType: "custom",
  });

  try {
    const { render } = await vite.ssrLoadModule("/src/prerender-entry.tsx");
    const appHtml = render();

    let template = fs.readFileSync(templatePath, "utf-8");
    const html = template.replace(
      '<div id="root"></div>',
      `<div id="root">${appHtml}</div>`
    );

    fs.writeFileSync(templatePath, html);
    console.log("✅ Prerendered dist/index.html");
  } finally {
    await vite.close();
  }
}

prerender().catch((err) => {
  console.error(err);
  process.exit(1);
});
```

### 3. Make `App` accept a `prerender` prop

```tsx
interface AppProps {
  prerender?: boolean;
}

export default function App({ prerender = false }: AppProps) {
  const [isLoading, setIsLoading] = useState(!prerender);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (prerender) return;
    // Initialize smooth scroll, analytics, etc. after initial paint
    const timer = setTimeout(() => setReady(true), 100);
    return () => clearTimeout(timer);
  }, [prerender]);

  return (
    <div className="grain">
      <AnimatePresence mode="wait">
        {isLoading && (
          <LoadingScreen key="loading" onComplete={() => setIsLoading(false)} />
        )}
      </AnimatePresence>

      {!isLoading && (
        <main className="animate-fade-in-up">
          <Navbar />
          <Hero />
          <Products />
          <Stats />
          <Contact />
          {ready && <LenisLoader />}
        </main>
      )}
    </div>
  );
}
```

Key point: when `prerender={true}`, the loading screen is skipped and the
content is rendered immediately.

### 4. Guard browser-only APIs

Components that use `window`, `document`, `navigator`, or browser-only
libraries (Lenis, GSAP scroll triggers) must not run during SSR unless they
are behind `typeof window !== "undefined"` or loaded only client-side.

Example for Lenis:

```tsx
function LenisLoader() {
  useEffect(() => {
    // dynamic import only runs in browser
    const init = async () => {
      const [{ default: Lenis }] = await Promise.all([import("lenis")]);
      const gsap = (await import("gsap")).default;
      const { ScrollTrigger } = await import("gsap/ScrollTrigger");
      gsap.registerPlugin(ScrollTrigger);
      // ... initialize Lenis
    };
    init();
  }, []);
  return null;
}
```

### 5. Wire into `package.json`

```json
{
  "scripts": {
    "build": "tsc -b && vite build && node scripts/prerender.js"
  }
}
```

### 6. Add SEO files

Create `public/robots.txt` and `public/sitemap.xml` so Vite copies them to
`dist/` during build.

## Verification

```bash
npm run build
wc -c dist/index.html
grep -o 'YourProductName\|Каталог' dist/index.html | sort | uniq -c
ls dist/robots.txt dist/sitemap.xml
```

Expect `dist/index.html` to grow from ~1 KB to 20–80 KB and contain product
names, section headings, and footer content.

Real-world check from a product landing session:

```bash
cd /mnt/data/natan-storage/silicone-landing
npm run build
wc -c dist/index.html
# 25110 bytes
grep -o 'Si-M\|Вс-М\|КС-М\|RTV-2\|ЮниКаст 6В\|penta@penta-junior.ru' dist/index.html | sort | uniq -c
```

## Headless Screenshot Verification

Headless Chrome may hang on `requestAnimationFrame` loading screens. For
screenshot tests, either:
- skip the loading screen by rendering `App` with `prerender` in a dedicated
  test entry, or
- use Playwright with a long wait and a ready-state selector.

This lightweight prerender path makes headless verification easier because
`dist/index.html` already contains the final DOM.

## Related

- `references/vite-dev-server-network-access.md` — accessing the dev server from
  another machine on the local network.
- `references/ssr-prerender-for-vite-spa.md` — heavier Playwright-based approach
  that fully executes the client bundle. Use it when you need to prerender
  pages that rely on client-side data or complex hydration states.
