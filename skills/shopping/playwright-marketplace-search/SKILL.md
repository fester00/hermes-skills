---
name: playwright-marketplace-search
description: |
  Search Russian marketplaces (Ozon, Wildberries, Yandex Market) via Playwright.
  Uses a real Chrome profile and an Xvfb viewport to bypass anti-bot protection.
category: shopping
related_skills:
  - playwright-web-search
---

# Playwright Marketplace Search

Search Russian e-commerce sites (Ozon, Wildberries, Yandex Market) programmatically
using Playwright with a persistent Chrome profile and a virtual display.

## When to use this skill

Use this skill whenever a task requires interacting with Russian e-commerce sites
that block the built-in Hermes browser from a data-center IP. Typical use cases:

- **Product search** on marketplaces: Ozon, Wildberries, Yandex Market.
- **Price monitoring** and comparison across Russian e-commerce sites.
- **Online stores** that require a real browser profile and viewport.

For general web search (Yandex/Google) when the built-in browser is blocked, use
the sibling skill `playwright-web-search` instead.

Rule of thumb:

> If `browser_navigate` returns a captcha/anti-bot page on a marketplace or
> e-commerce site, switch to this Playwright + profile approach. For search
> engines, switch to `playwright-web-search`.

## What this skill is NOT for

- Static API documentation, raw files or GitHub — use `curl` or `browser_navigate`.
- Sites that explicitly allow headless access — built-in browser is faster.
- Tasks that require JavaScript execution but no anti-bot — built-in browser is enough.

## Tested sites

| Site | Built-in browser | Playwright + profile |
|---|---|---|
| Ozon | ❌ Anti-bot | ✅ Works |
| Wildberries | ⚠️ Untested | likely works with profile + xvfb |
| Yandex Market | ⚠️ Heavy anti-bot | may need extra stealth/proxy |

For Yandex/Google **general web search**, use the sibling skill `playwright-web-search`.

## Why this works

Most Russian sites and search engines block headless/anonymous browsers from data-center IPs.
This skill uses:

- **Persistent Chrome profile** — reuses cookies, localStorage and login state.
- **Xvfb virtual display** — gives the browser a real viewport so sites don't detect headless mode.
- **Real Chromium binary** — downloaded by Playwright, not the system browser.
- **DOM-based extraction** — fast and reliable for content cards.

## Standard launch command

Always run Playwright scripts through `xvfb-run` with a 1920x1080 virtual screen:

```bash
cd /mnt/data/natan-storage/playwright-search
source .venv/bin/activate
xvfb-run -a --server-args="-screen 0 1920x1080x24" python <script>.py
```

## Chrome profile

The persistent profile is stored at:

```
/mnt/data/natan-storage/.chrome-vk-profile
```

Do not delete this directory. If a site asks for login inside the browser, run the
script once, log in manually, and the cookies will persist.

## Search scripts

- `scripts/ozon_search.py` — search Ozon product cards by query and price limit.

Use `ozon_search.py` as a selector template when adding a new marketplace or online store.

## Adding a new site

1. Open the target site in a normal browser with DevTools.
2. Find the container selector for content/product cards.
3. Map the selectors for:
   - card root
   - title/name
   - price (if applicable)
   - link
   - rating / reviews (optional)
4. Copy one of the reference scripts and replace the selectors.
5. Test with `headless=False` under `xvfb-run`.

## Anti-bot tips

- Always use `headless=False` under Xvfb; real headless is detected.
- Keep `--disable-blink-features=AutomationControlled` in args.
- Use a realistic viewport (1920x1080) and user-agent.
- Avoid very fast consecutive requests; add `sleep` between page loads.
- If a site shows CAPTCHA, stop and retry later or switch site.
- Test the built-in browser first; only switch to Playwright when blocked.

## Known working sites

| Site | Status | Notes |
|---|---|---|
| Ozon | ✅ Working | Product grid uses `data-widget="tileGridDesktop"` / `.tile-root` |
| Wildberries | ⚠️ Untested | Likely similar anti-bot, needs profile + xvfb |
| Yandex Market | ⚠️ Heavy anti-bot | May need extra stealth or residential proxy |
| DNS / Citilink / Regard | ❌ Usually blocked | Heavy bot protection from data-center IPs |

## Output format

Scripts print results as plain text:

```
💰 9 657 ₽
   Digma 1 ТБ Внутренний SSD-диск Run S9 SATA III 2.5"
   4.9
   https://ozon.ru/product/digma-...
```

Add `--json` for machine-readable output.

## References

- `scripts/ozon_search.py` — reusable Ozon search script
- `scripts/test_search_engines.py` — quick smoke test for Yandex/Google
- `templates/generic_anti_bot_scraper.py` — starter scaffold for any new anti-bot site
- `references/anti-bot-browser-patterns.md` — why built-in and `browser-use` failed, and why Playwright + profile works
- `browser-automation` skill — Hermes native browser tools and CDP patterns
- `playwright-web-search` skill — same anti-bot stack for Yandex/Google general web search

## Browser-use caveat

`browser-use` can manage a real Chrome profile and viewport, but it requires an
LLM that emits strict JSON matching the `AgentOutput` schema. Local and
OpenAI-compatible models that wrap output in markdown code fences or text
preludes will fail repeatedly with `Invalid JSON` / validation errors. Prefer
Playwright for anti-bot tasks unless you are using `ChatBrowserUse`, GPT-4o,
or another model explicitly tuned for structured JSON tool output.

