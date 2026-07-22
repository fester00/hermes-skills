# Web search via search engines (Yandex, Google)

Session note: 2026-07-09. This reference captures the precise fallback path when
Hermes' built-in `browser_navigate` hits anti-bot protection and the task
requires general web search rather than marketplace product search.

## When to use this path

Use the Playwright + persistent-profile approach (defined by this skill) when:

- `browser_navigate` to `https://yandex.ru/search/?text=...` returns SmartCaptcha.
- `browser_navigate` to `https://www.google.com/search?q=...` returns an anti-bot page.
- The task needs live search snippets, current news, or recent web pages.
- Internal sources (Obsidian, project files, skills) are insufficient.

## Verified status

| Engine | Hermes built-in browser | Playwright + profile |
|---|---|---|
| Yandex Search | ❌ SmartCaptcha | ✅ Works |
| Google Search | ❌ Anti-bot | ✅ Works |

## Reference scripts

- `scripts/test_search_engines.py` — smoke test for Yandex and Google search.
- `scripts/ozon_search.py` — example of DOM card extraction; the same pattern
  applies to search-result cards on Yandex/Google.

## Standard invocation

```bash
cd /mnt/data/natan-storage/playwright-search
source .venv/bin/activate
xvfb-run -a --server-args="-screen 0 1920x1080x24" python scripts/test_search_engines.py
```

## Chrome profile

Persistent state (cookies, localStorage, login sessions) lives at:

```
/mnt/data/natan-storage/.chrome-vk-profile
```

Do not delete it. If a search engine ever asks to log in, run the script once
with `headless=False`, complete login manually, and the state will persist.

## Anti-bot essentials

- Always run under `xvfb-run` with a 1920×1080 virtual display.
- Use `headless=False`; real headless mode is detected.
- Keep `--disable-blink-features=AutomationControlled` in launch args.
- Use a realistic viewport and user-agent.
- Add human-like delays between page loads and scrolling.
- If CAPTCHA still appears, stop and retry later rather than hammering the site.

## Outdated guidance elsewhere

An older Obsidian note (`Operations/Skills/web-search.md`, dated 2026-05-03)
claims Yandex and marketplaces are unreachable. That information is stale.
The Playwright + persistent-profile approach has since been verified to work
for both Yandex Search and Google Search. Always prefer this skill's current
state over older notes when they conflict.
