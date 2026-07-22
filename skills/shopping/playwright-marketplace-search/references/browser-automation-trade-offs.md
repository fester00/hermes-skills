# Browser automation trade-offs for Russian sites

## Context

The server runs from a data-center IP. Russian sites and search engines detect
and block the default Hermes headless browser quickly.

We tested three approaches.

## 1. Hermes built-in browser (`browser_navigate`)

What it is: headless Chromium via CDP, no persistent profile, no residential proxy.

| Site | Result |
|---|---|
| `ya.ru` homepage | ✅ Loads |
| `google.com` homepage | ✅ Loads |
| Yandex Search results | ❌ SmartCaptcha "Вы не робот?" |
| Google Search results | ❌ Anti-bot / IP check page |
| Ozon | ❌ Anti-bot / Cloudflare challenge |

Verdict: fine for static docs, GitHub, raw files. Fails for search and marketplaces.

## 2. `browser-use` open-source agent

What it is: AI agent framework that can control a local Chrome via CDP.

Why it failed on this server:

- Chrome would not start without sandbox flags on Ubuntu.
  - Fix: `chromium_sandbox=False` adds `--no-sandbox`.
  - Fix: add `--disable-gpu` and `--disable-setuid-sandbox` to `args`.
  - Fix: run under `xvfb-run` for a virtual display.
- Even after Chrome started, every tested LLM returned the response wrapped in
  markdown JSON fences or with the wrong action schema, causing repeated
  `Invalid JSON` and Pydantic validation errors.
  - `gemma4:31b-cloud` (Ollama) wrapped JSON in ````json ... `````.
  - `minimax-m3:cloud` (Ollama) occasionally worked but often used wrong action keys.
  - `kimi-k2.7-code:cloud` via OpenAI-compatible endpoint also wrapped JSON and
    hallucinated action shapes.
- `browser-use` has no simple `response_format={"type":"json_object"}` passthrough
  in its `ChatOpenAI` wrapper, and the local models are not optimized for its
  strict `AgentOutput` schema.

Verdict: not viable here without an LLM that is explicitly optimized for
`browser-use` (e.g. `ChatBrowserUse` cloud model). Removed.

## 3. Plain Playwright + persistent Chrome profile + Xvfb

What it is: Playwright launches a real Chromium with a persistent user-data-dir
and a virtual 1920x1080 display.

| Site | Result |
|---|---|
| Yandex Search | ✅ Loads results |
| Google Search | ✅ Loads results |
| Ozon product search | ✅ Loads results, extracts cards |

Verdict: this is the working baseline for anti-bot sites from this server.

## Reusable formula

```bash
xvfb-run -a --server-args="-screen 0 1920x1080x24" \
  python <playwright_script>.py
```

Required in Playwright:

```python
context = await p.chromium.launch_persistent_context(
    user_data_dir='/mnt/data/natan-storage/.chrome-vk-profile',
    headless=False,
    args=['--disable-blink-features=AutomationControlled'],
    viewport={'width': 1920, 'height': 1080},
)
```

## When to escalate

- If `browser_navigate` returns a captcha/anti-bot page for a simple static site,
  use Playwright + profile.
- If Playwright + profile also fails, the site may require a residential proxy
  or manual login inside the persistent profile.
- For API docs, raw files, and GitHub, keep using `curl` or the built-in browser.
