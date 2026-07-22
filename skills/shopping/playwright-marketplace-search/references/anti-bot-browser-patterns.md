# Anti-Bot Browser Automation Patterns

Session: 2026-07-04

## Problem

Many Russian sites (Ozon, Yandex Search, Yandex Market, Google Search) detect and
block the built-in Hermes browser because it runs headless from a data-center IP.

## What works here

Playwright + persistent Chrome profile + Xvfb virtual display.

Key ingredients:

- `headless=False` under `xvfb-run`
- persistent `user_data_dir` at `/mnt/data/natan-storage/.chrome-vk-profile`
- realistic viewport 1920x1080
- `--disable-blink-features=AutomationControlled`
- real Chromium binary installed by Playwright

## What did NOT work

### Built-in Hermes browser (`browser_navigate`)

Yandex Search immediately returns SmartCaptcha "Вы не робот?".
Google Search returns anti-bot / IP verification page.

### browser-use 0.13.3

Installation succeeded, but the local agent could not produce the strict JSON schema
browser-use requires for action planning. Tested models:

- `gemma4:31b-cloud` (Ollama) — wraps JSON in markdown code fences
- `minimax-m3:cloud` (Ollama) — occasionally works for simple navigation, but
  often emits wrong action schema or text instead of JSON
- `kimi-k2.7-code:cloud` via OpenAI-compatible endpoint — same markdown/JSON
  issues

browser-use also failed to launch its bundled Chromium without sandbox/GPU flags
until `chromium_sandbox=False` and `--disable-gpu` were added.

Conclusion: browser-use requires a model optimized for strict structured output
(`ChatBrowserUse`, GPT-4o, Claude Sonnet). With local/cloud models that are not
JSON-tuned, it is not viable.

## Tested matrix

| Site | Built-in | Playwright + profile |
|---|---|---|
| Ozon | ❌ anti-bot | ✅ |
| Yandex Search | ❌ SmartCaptcha | ✅ |
| Google Search | ❌ anti-bot | ✅ |
| Yandex Market | ❌ heavy anti-bot | ⚠️ untested, may need proxy |
| Wildberries | ❌ expected | ⚠️ untested |
| DNS / Citilink / Regard | ❌ usually blocked | ❌ usually blocked |

## Tool selection rule

1. Try `curl` first for raw files/APIs.
2. Try `browser_navigate` / `browser_snapshot` for simple JS sites.
3. If you hit CAPTCHA/anti-bot, switch to Playwright + profile + Xvfb.
4. Only consider browser-use if you have a model that supports strict JSON
   structured output.

## Reproduction command

```bash
cd /mnt/data/natan-storage/playwright-search
source .venv/bin/activate
xvfb-run -a --server-args="-screen 0 1920x1080x24" \
  python test_search_engines.py
```

## References

- `templates/generic_anti_bot_scraper.py` — starter for a new anti-bot site
- `scripts/ozon_search.py` — marketplace product extraction
- `scripts/test_search_engines.py` — Yandex/Google smoke test
