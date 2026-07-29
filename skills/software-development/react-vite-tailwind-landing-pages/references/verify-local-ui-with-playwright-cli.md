# Verify local Vite / static UI when browser tools block internal URLs

Some Hermes environments block `file://` and `localhost:` URLs in the browser
tools (the page fails with "Blocked: URL targets a private or internal address").
When that happens, use Playwright's CLI screenshot command as a fast fallback to
inspect the built or previewed UI without writing a full test suite.

## Prerequisites

Playwright is usually already installed in React/Vite projects as a devDependency.
If not, install it:

```bash
npm install -D playwright
npx playwright install chromium
```

## Verify a built production bundle

1. Build the project.
2. Start Vite preview in the background.
3. Capture a screenshot with Playwright CLI.

```bash
cd /path/to/project
npm run build

# background preview
npx vite preview --port 4173 --host &
PREVIEW_PID=$!

# full-page screenshot
npx playwright screenshot --wait-for-timeout=5000 --full-page \
  http://localhost:4173/ ./screenshot-fullpage.png

# mobile viewport screenshot
npx playwright screenshot --wait-for-timeout=5000 --viewport-size=390,844 \
  --full-page http://localhost:4173/ ./screenshot-mobile.png

kill $PREVIEW_PID
```

Use `--wait-for-selector=<selector>` instead of `--wait-for-timeout` when you
need to wait for an element (e.g. a modal) instead of a fixed delay.

## Verify a modal or interaction state

Playwright CLI can only capture what is visible after page load. To check a
modal, you have two options:

1. **Use a Playwright script** (recommended for interactions):

```bash
cat > /tmp/capture-modal.js <<'EOF'
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:4173/');
  await page.waitForTimeout(2000);
  await page.click('button:has-text("Подробнее")');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: './screenshot-modal.png', fullPage: true });
  await browser.close();
})();
EOF
node /tmp/capture-modal.js
```

2. **Add a query parameter or dev-only prop** to force the modal open on load,
   then screenshot with `--wait-for-selector="[role=dialog]"`.

## Limitations

- Playwright CLI screenshots are static — they do not replace interactive
  testing, but they catch layout, image, and text issues quickly.
- If the page uses `framer-motion` entrance animations, increase
  `--wait-for-timeout` so elements finish rendering.
- Some Hermes browser backends *do* support `localhost`; try the browser tools
  first. Use this recipe only when they are blocked.
