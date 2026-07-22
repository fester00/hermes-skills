# Browser Automation Options for Tasks Requiring a Real User Profile

Quick reference for choosing the right browser-automation approach when Hermes' built-in headless CDP browser is blocked by bot protection or lacks a persistent profile.

## Built-in Hermes browser (CDP headless Chromium)

- Toolset: `browser_navigate`, `browser_click`, `browser_snapshot`, etc.
- Profile: none; each session is a fresh headless instance.
- Use case: simple page inspection, screenshots, form interaction on sites that do not aggressively block bots.
- Limitations:
  - No persistent cookies, logins, or saved passwords.
  - Russian marketplaces (Ozon, Wildberries, Yandex Market, DNS, Citilink, KNS) usually return 403/429/captcha immediately.
  - Cannot drive the user's already-installed Chrome/Edge/Firefox.

## browser-use (open-source Python library / CLI)

- URL: https://github.com/browser-use/browser-use
- How it works: Python `Agent` + LLM controls a real browser instance (local Chrome by default). Can use the user's `user-data-dir` and persistent profile.
- Best for: "find me the best SSD on marketplaces", automated shopping, form filling, job applications, any task needing real login state.
- Integration with coding agents: paste the README prompt into Claude Code / Codex:
  ```text
  Install or upgrade browser-use to the latest stable version with uv using Python 3.12, register the skill from `browser-use skill`, and connect it to my browser. Follow https://github.com/browser-use/browser-use if setup or connection fails.
  ```
- Cloud option: Browser Use Cloud provides stealth, proxy rotation, captcha solving, and more integrations.
- Caveat: not integrated into Hermes; must be installed and run separately.

## Comet

- What it is: an AI-first browser (similar concept to Arc/Opera but built around agent control) that lets an AI agent browse with the user's real profile.
- Best for: end-user tasks like shopping, research, bookings where the AI should act like the logged-in user.
- Caveat: separate product; Hermes does not control it directly.

## Connecting Hermes to the user's real browser

Hermes cannot directly attach to an already-running browser window. Options if you need that:

| Approach | How | Notes |
|---|---|---|
| Chrome CDP remote debugging | `google-chrome --remote-debugging-port=9222 --user-data-dir=/path/to/profile` | Hermes can then connect via CDP, but there is no ready `browser_navigate`-like wrapper for remote CDP in current Hermes tooling. |
| Playwright / Selenium script | Hermes writes the script, user runs it | Flexible, but requires the user to execute the script. |
| Browser extension + WebSocket | Extension listens to Hermes commands inside the user's browser | Highest engineering effort. |
| VNC / remote desktop | Hermes controls the whole desktop | Heavy and risky; only with explicit user approval. |

## Playwright + persistent Chrome profile + xvfb

When `browser-use` fails to launch or when you want direct control, use Playwright with a real Chrome `user-data-dir`, a viewport, and a virtual X server (`xvfb`). This combination successfully bypasses Ozon's antibot page and extracts live marketplace data.

### Recipe

1. Install Playwright and a Chromium build:
   ```bash
   source /mnt/data/natan-storage/browser-use/.venv/bin/activate
   uv pip install playwright
   playwright install chromium
   ```

2. Launch Chrome persistently with a real profile and a viewport:
   ```python
   from playwright.async_api import async_playwright
   import asyncio

   async def main():
       async with async_playwright() as p:
           context = await p.chromium.launch_persistent_context(
               user_data_dir='/mnt/data/natan-storage/.chrome-vk-profile',
               headless=False,
               args=['--disable-blink-features=AutomationControlled'],
               viewport={'width': 1920, 'height': 1080},
               user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
           )
           page = context.pages[0] if context.pages else await context.new_page()
           await page.goto('https://www.ozon.ru/search/?text=SSD+M2+NVMe+1TB&price_to=10000',
                           wait_until='networkidle', timeout=60000)
           await asyncio.sleep(3)
           print(await page.title())
   ```

3. Run under a virtual display (no physical monitor needed):
   ```bash
   xvfb-run -a --server-args="-screen 0 1920x1080x24" python script.py
   ```

4. Ozon product cards live in `div[data-widget="tileGridDesktop"] .tile-root`.

### Why this works

- `headless=False` + `xvfb` makes Chrome look like a normal desktop browser.
- A persistent `user_data_dir` carries real cookies, local storage, and fingerprinting state.
- A fixed viewport size avoids the “headless” footprint.
- The site sees the same browser the user already trusts.

### Pitfalls

| Pitfall | Cause | Fix |
|---|---|---|
| `Missing X server or $DISPLAY` | Running `headless=False` without xvfb | Wrap with `xvfb-run` |
| `browser-use` times out launching Chrome | It expects a display or its bundled Chromium is incompatible | Switch to direct Playwright; install `playwright` explicitly |
| Ozon shows “Antibot Challenge Page” | Fresh profile / headless fingerprint | Use persistent `user_data_dir` and a viewport |
| Product cards not found | Classes are hashed; `data-widget` names vary | Use `div[data-widget="tileGridDesktop"] .tile-root` for Ozon; inspect HTML for other sites |

### Ready-to-use starter

See `templates/playwright_persistent_chrome_search.py` for a copy-and-modify example.

## Practical recommendation

- For occasional marketplace/product searches: ask the user to open the site themselves and share URLs/screenshots, or use the Playwright + xvfb + persistent profile recipe above.
- For recurring automated workflows where an LLM must drive the browser: try `browser-use` first; if it fails to launch on a headless server, fall back to the Playwright recipe.
- For tasks that fit the built-in Hermes browser (no login wall, no bot detection): keep using the native CDP tools.
