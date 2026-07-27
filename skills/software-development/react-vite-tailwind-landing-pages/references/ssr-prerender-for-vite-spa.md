# SSR / Prerender for Vite SPA Landing Pages

## Problem

A Vite + React SPA serves an almost empty `index.html`. Search-engine crawlers
and social-media preview bots that do not execute JavaScript see no content,
which hurts SEO.

## Solution

Add a post-build prerender step using Playwright. It starts a tiny static
server for the `dist/` folder, renders the app in a headless Chromium browser,
waits for hydration, then injects the rendered DOM into `dist/index.html`.
The result is a fully populated HTML page that still contains the original
React bundle for client-side hydration.

## When to Use

- Landing page or one-page site where content is stable at build time.
- SEO matters: meta tags are already in `index.html`, body content must be
  visible to non-JS crawlers, and you want `robots.txt` + `sitemap.xml` in the
  final deployment.
- The project is a Vite SPA, not Next.js or another SSR framework.

## When NOT to Use

- Highly dynamic pages (user-specific dashboards, real-time data) — prerender
  would show stale or empty content.
- Very large sites with many routes — use Next.js, Astro, or Vite SSR instead.

## Steps

### 1. Install Playwright

```bash
npm install -D playwright
npx playwright install chromium
```

### 2. Add `scripts/prerender.js`

```javascript
import { chromium } from "playwright";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import http from "http";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function createServer(root, port) {
  return new Promise((resolve) => {
    const mimeTypes = {
      ".html": "text/html",
      ".js": "application/javascript",
      ".css": "text/css",
      ".json": "application/json",
      ".webp": "image/webp",
      ".mp4": "video/mp4",
      ".svg": "image/svg+xml",
    };

    const server = http.createServer((req, res) => {
      const url = req.url === "/" ? "/index.html" : req.url;
      const filePath = path.join(root, url);

      fs.readFile(filePath, (err, data) => {
        if (err) {
          res.writeHead(404);
          res.end("Not found");
          return;
        }
        const ext = path.extname(filePath);
        res.writeHead(200, { "Content-Type": mimeTypes[ext] || "application/octet-stream" });
        res.end(data);
      });
    });

    server.listen(port, () => resolve(server));
  });
}

async function prerender() {
  const distDir = path.resolve(__dirname, "../dist");
  const indexPath = path.resolve(distDir, "index.html");
  const port = 3456;

  if (!fs.existsSync(indexPath)) {
    console.error("dist/index.html not found. Run npm run build first.");
    process.exit(1);
  }

  const server = await createServer(distDir, port);
  const browser = await chromium.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });

  try {
    const page = await browser.newPage();
    await page.goto(`http://localhost:${port}/`, { waitUntil: "networkidle" });

    // Wait for React hydration: <main> must be present inside #root
    await page.waitForFunction(() => {
      const root = document.getElementById("root");
      return root \u0026\u0026 root.querySelector("main") !== null;
    }, { timeout: 20000 });

    // Wait a short time for entrance animations and lazy images
    await page.waitForTimeout(2000);

    // Extract the inner HTML of the root element directly
    const rootInnerHtml = await page.evaluate(() => {
      const root = document.getElementById("root");
      return root ? root.innerHTML : "";
    });

    if (!rootInnerHtml) {
      console.error("Could not extract root content");
      process.exit(1);
    }

    const template = fs.readFileSync(indexPath, "utf-8");

    // Inject the rendered DOM while preserving Vite's injected script tag
    const finalHtml = template.replace(
      /\u003cdiv id="root"\u003e\u003c\/div\u003e/,
      `\u003cdiv id="root"\u003e${rootInnerHtml}\u003c/div\u003e`
    );

    fs.writeFileSync(indexPath, finalHtml);
    console.log(`Prerendered ${indexPath} (${finalHtml.length} bytes)`);
  } catch (error) {
    console.error("Prerender failed:", error);
    process.exit(1);
  } finally {
    await browser.close();
    server.close();
  }
}

prerender();
```

### 3. Wire It Into `package.json`

```json
{
  "scripts": {
    "build": "tsc -b && vite build && node scripts/prerender.js",
    "prerender": "node scripts/prerender.js"
  }
}
```

### 4. Add `robots.txt` and `sitemap.xml`

Create `public/robots.txt` and `public/sitemap.xml`. Vite copies `public/`
assets into `dist/` during the build, so they are present in the final static
site and available to crawlers.

`public/robots.txt`:

```text
User-agent: *
Allow: /

Sitemap: https://your-domain.ru/sitemap.xml
```

`public/sitemap.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://your-domain.ru/</loc>
    <priority>1.0</priority>
    <changefreq>weekly</changefreq>
  </url>
</urlset>
```

If the site later grows multiple landing pages, generate the sitemap
programmatically from the same route list used by `prerender.js`.

### 5. Build and Verify

```bash
npm run build
```

Check `dist/index.html`:

- contains rendered sections, product names, prices, descriptions;
- still contains the Vite-generated `<script type="module" src="/assets/index-...js">`;
- does not contain the loading-screen text.

Also verify `dist/robots.txt` and `dist/sitemap.xml` exist after the build.

## Important Details

- **Use `http://localhost`**, not `file://`. Browsers block JavaScript execution
  for `file://` URLs in many security contexts.
- **Wait for hydration** by checking a real rendered element (e.g. `main`), not
  just `#root` being non-empty.
- **Extract via `page.evaluate`** rather than regex on the full document. The
  regex approach breaks when nested `div` elements are present.
- **Preserve the script tag** so normal users still get a hydrated SPA
  experience.
- **Close the static server and browser** in a `finally` block.

## Verification Checklist

- [ ] `npm run build` passes TypeScript and Vite build.
- [ ] `npx oxlint` shows 0 warnings, 0 errors.
- [ ] `dist/index.html` size grows from ~3 KB to 30–80 KB after prerender.
- [ ] Rendered content includes section headings, product cards, and footer.
- [ ] Script tag for client bundle is still present.
- [ ] Loading screen text is not present in the final HTML.
- [ ] `dist/robots.txt` and `dist/sitemap.xml` exist (if added).

## Testing the Built Site

After `npm run build` you can serve the `dist/` folder locally and run
automated checks. Because Hermes browser tools may block `localhost`, use
Playwright tests instead:

```bash
npx playwright test
```

Add `playwright.config.ts` that points `baseURL` at `http://localhost:3002`
(or whichever preview port you use) and start a static server or `vite preview`
before the tests run. This catches regressions in modal scroll lock, form
validation, and SEO content that manual dev-server checks miss.

For modal scroll-lock specifically, add a test that wheels over the backdrop
and over the modal's top/bottom boundaries while asserting `window.scrollY`
remains constant.
