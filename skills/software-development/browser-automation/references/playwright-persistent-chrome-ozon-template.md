# Playwright Persistent-Chrome Ozon Search Template

Proven recipe for searching Ozon from a headless Ubuntu server using a real Chrome profile, Xvfb virtual display, and Playwright.

## When to use this

- You need live product/pricing data from Ozon.
- Ozon blocks anonymous headless browsers (built-in Hermes CDP browser gets "no connection" / anti-bot page).
- A persistent Chrome profile with cookies/login state is available (e.g. `/mnt/data/natan-storage/.chrome-vk-profile`).
- The server has no real display, so a virtual framebuffer (Xvfb) is required.

## TL;DR working command

```bash
cd /mnt/data/natan-storage/browser-use
source .venv/bin/activate
xvfb-run -a --server-args="-screen 0 1920x1080x24" python chrome_ozon_final.py
```

## Required setup

1. Python venv with Playwright installed:
   ```bash
   uv venv --python 3.12
   source .venv/bin/activate
   uv pip install playwright
   playwright install chromium
   ```

2. Xvfb installed:
   ```bash
   sudo apt install -y xvfb
   ```

3. Persistent Chrome profile exists at the desired path.

## Template script

```python
from playwright.async_api import async_playwright
import asyncio
import json

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

        query = 'SSD M2 NVMe 1TB'
        url = f'https://www.ozon.ru/search/?text={query.replace(" ", "+")}&price_to=10000'
        await page.goto(url, wait_until='networkidle', timeout=60000)
        await asyncio.sleep(3)

        # Accept cookies if prompt appears
        try:
            cookie_btn = await page.query_selector('button:has-text("OK"), button:has-text("ОК")')
            if cookie_btn:
                await cookie_btn.click()
                await asyncio.sleep(1)
        except Exception:
            pass

        cards = await page.query_selector_all('div[data-widget="tileGridDesktop"] .tile-root')

        results = []
        for card in cards[:10]:
            try:
                text = await card.inner_text()
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                price = next((l for l in lines if '₽' in l), '')
                name = next((l for l in lines if any(k in l.lower() for k in ['ssd','тб','kingston','digma','samsung','nvme'])), '')
                results.append({'name': name, 'price': price})
            except Exception:
                pass

        for r in results[:5]:
            print(f"- {r['price']} | {r['name']}")

        await page.screenshot(path='/mnt/data/natan-storage/browser-use/ozon_result.png', full_page=False)
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
```

## Key lessons from this session

| What | Detail |
|---|---|
| Ozon layout widget | Product cards live in `div[data-widget="tileGridDesktop"] .tile-root` |
| Anti-bot bypass | Persistent Chrome profile + viewport + real User-Agent |
| Virtual display | `xvfb-run -a --server-args="-screen 0 1920x1080x24"` |
| Filter by price | Add `&price_to=10000` to search URL |
| `data-widget` names change | If `tileGridDesktop` fails, save HTML and inspect current widget name |

## Common failures and fixes

| Failure | Cause | Fix |
|---|---|---|
| `Missing X server or $DISPLAY` | Running headed without Xvfb | Wrap command in `xvfb-run` |
| `Antibot Challenge Page` | Profile missing or anonymous browser | Use persistent profile; verify it has cookies/history |
| `Found 0 cards` | Wrong selectors or page not loaded | Increase sleep; inspect saved HTML |
| Executable mismatch | Playwright browser not installed | Run `playwright install chromium` inside the venv |

## `browser-use` on a headless server

`browser-use` can work with a persistent profile and viewport, but it needs extra flags on a headless Ubuntu server and an LLM that emits strict JSON action objects.

### Minimal working launch

```python
import asyncio
from browser_use import Agent, BrowserProfile
from browser_use.llm.openai.chat import ChatOpenAI

async def main():
    agent = Agent(
        task="Open ozon.ru, find SSD M.2 NVMe 1TB up to 10000 RUB",
        llm=ChatOpenAI(
            model='kimi-k2.7-code:cloud',
            base_url='http://127.0.0.1:11434/v1',
            api_key='ollama',
            temperature=0.0,
        ),
        browser_profile=BrowserProfile(
            headless=False,
            user_data_dir='/mnt/data/natan-storage/.chrome-vk-profile',
            viewport={'width': 1920, 'height': 1080},
            allowed_domains=["*.ozon.ru", "*.ozon.com"],
            chromium_sandbox=False,          # adds --no-sandbox
            args=['--disable-gpu', '--disable-setuid-sandbox'],
        ),
    )
    result = await agent.run()
    print(result.final_result())

if __name__ == '__main__':
    asyncio.run(main())
```

Run with:

```bash
cd /mnt/data/natan-storage/browser-use
source .venv/bin/activate
xvfb-run -a --server-args="-screen 0 1920x1080x24" python browser_use_ozon.py
```

### Why it often fails

| Failure | Cause | Fix |
|---|---|---|
| `Cannot connect to host 127.0.0.1:PORT` / CDP timeout | Chrome crashes without sandbox/Xvfb | Set `chromium_sandbox=False`, add `--disable-gpu`, run under `xvfb-run` |
| `Invalid JSON` / `expected value at line 1` | LLM wraps JSON in markdown or uses wrong schema | Use an LLM with strong structured-output support (`ChatBrowserUse`, `ChatOpenAI` with `gpt-4o`, etc.); local Ollama models (`gemma4:31b-cloud`, `minimax-m3:cloud`) and OpenAI-compatible proxies (`kimi-k2.7-code:cloud` via `ollama-launch`) may fail this check |
| `Field required` / `Extra inputs are not permitted` | LLM invented fields like `keypress` or `clear` | Same as above — stricter model, or fall back to Playwright |

### Recommendation

For deterministic marketplace scraping (fixed search, price filter, product extraction), prefer a direct Playwright script. Use `browser-use` only when you need an LLM-driven agent for dynamic multi-step flows and you have an LLM that reliably outputs the required JSON schema.

## See also

- `references/russian-retail/ozon-extraction-patterns.md` — Older Ozon selectors and JS extraction snippets
- `references/russian-retail/russian-retail-search.md` — CDP/Xvfb/Chrome profile setup for Russian marketplaces
- `references/russian-retail/parallel-cdp-search.md` — Running Ozon + Yandex Market searches in parallel tabs
