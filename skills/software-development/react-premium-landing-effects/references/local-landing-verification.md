# Local Landing Verification with Playwright

Hermes `browser_navigate` blocks private/internal addresses (`localhost`, `127.0.0.1`, `192.168.x.x`). For local landing-page verification, use Playwright directly from the project directory.

## One-shot screenshot command

```bash
cd <project-root>
npx playwright install chromium   # one-time
node scripts/final-screenshots.mjs
```

## Reusable script

Save as `scripts/final-screenshots.mjs`:

```js
import { chromium } from 'playwright';

const base = process.argv[2] || 'http://127.0.0.1:3002';
const outDir = process.argv[3] || '.';
const browser = await chromium.launch();

async function screenshot(name, viewport, clickCardIndex = null) {
  const page = await browser.newPage({ viewport });
  await page.goto(base, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  if (clickCardIndex !== null) {
    const cards = await page.locator('button:has(h3)').all();
    if (cards[clickCardIndex]) {
      await cards[clickCardIndex].click();
      await page.waitForTimeout(800);
    }
  }
  await page.screenshot({ path: `${outDir}/${name}.png`, fullPage: !clickCardIndex });
  await page.close();
}

await screenshot('audit-after-desktop', { width: 1440, height: 900 });
await screenshot('audit-after-mobile', { width: 390, height: 844 });
await screenshot('audit-after-modal', { width: 1440, height: 900 }, 2);

await browser.close();
```

## Required states

- Desktop full page (1440×900).
- Mobile full page (390×844 or similar).
- Modal open (click a product card).
- Form error state (submit empty form if validation exists).

## Verify against before screenshots

Keep `audit-before-*.png` and `audit-after-*.png` in the project root. Compare them visually or with `diff`/`compare` from ImageMagick:

```bash
compare audit-before-desktop.png audit-after-desktop.png diff-desktop.png
```

## Pitfall: video backgrounds in screenshots

Playwright captures the first video frame. If the first frame is black, the screenshot may look empty. Add `await page.waitForTimeout(1500)` after navigation to let the video advance before capturing.
