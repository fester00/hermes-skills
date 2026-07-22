---
name: playwright-web-search
description: |
  Search the web through Yandex and Google using Playwright with a persistent
  Chrome profile and Xvfb. Fallback when the built-in Hermes browser hits
  CAPTCHA or anti-bot protection.
category: research
related_skills:
  - playwright-marketplace-search
---

# Playwright Web Search

Search the web (Yandex, Google) programmatically using Playwright with a
persistent Chrome profile and a virtual display. Use this when Hermes'
built-in browser tools are blocked.

## When to use this skill

Use this skill when a task requires finding information on the public web and
the built-in Hermes browser fails with CAPTCHA or anti-bot pages:

- General fact-checking, news, documentation lookup.
- Discovering current prices, specs, reviews (not product comparison — see
  `playwright-marketplace-search` for that).
- Verifying SEO indexing, brand mentions, competitor pages.
- Searching for code snippets, library versions, error messages.
- Any web search where `browser_navigate` returns a bot block page.

Rule of thumb:

> If `browser_navigate` / `browser_snapshot` hits CAPTCHA or anti-bot, switch to
> Playwright + profile + Xvfb.

## What this skill is NOT for

- Static APIs, GitHub raw files, documentation endpoints — prefer `curl`.
- Sites that work fine with the built-in browser — it is faster.
- Deep marketplace price comparison — use `playwright-marketplace-search`.
- Structured academic search — use `arxiv`.

## Tested search engines

| Engine | Built-in browser | Playwright + profile |
|---|---|---|
| Yandex Search | ❌ SmartCaptcha | ✅ Works |
| Google Search | ❌ Anti-bot | ✅ Works |

See `scripts/search_engines.py` for a reusable reference implementation.

## Shared infrastructure

This skill shares the same anti-bot stack with `playwright-marketplace-search`:

| Resource | Path |
|---|---|
| Virtualenv | `/mnt/data/natan-storage/playwright-search/.venv` |
| Chrome profile | `/mnt/data/natan-storage/.chrome-vk-profile` |
| Marketplace sibling skill | `playwright-marketplace-search` |

Do not delete the Chrome profile directory. If a site asks for login, run the
script once, log in manually, and the cookies will persist.

## Standard launch command

The reference script is installed with the skill at:

```
~/.hermes/skills/research/playwright-web-search/scripts/search_engines.py
```

Because the script must run inside the Playwright virtualenv, copy (or symlink) it into the working directory before running:

```bash
cp ~/.hermes/skills/research/playwright-web-search/scripts/search_engines.py \
   /mnt/data/natan-storage/playwright-search/search_engines.py

cd /mnt/data/natan-storage/playwright-search
source .venv/bin/activate
xvfb-run -a --server-args="-screen 0 1920x1080x24" python search_engines.py --engine yandex --query "QUERY" --limit 5
```

## Reference script

- `scripts/search_engines.py` — search Yandex or Google and extract organic results.

## Anti-bot tips

- Always use `headless=False` under `xvfb-run`; real headless is detected.
- Keep `--disable-blink-features=AutomationControlled` in args.
- Use a realistic viewport (1920x1080) and user-agent.
- Avoid very fast consecutive requests; add sleeps between page loads.
- If a search engine shows CAPTCHA, stop and retry later.
- Test the built-in browser first; only switch to Playwright when blocked.

## Output format

Scripts print results as plain text:

```
🔍 Yandex: SSD M.2 NVMe 1TB цена

1. Купить SSD M.2 NVMe 1TB в Москве — цены от 4 990 ₽
   example.ru/ssd-m2-nvme-1tb
   Цены на SSD M.2 NVMe 1TB в интернет-магазинах Москвы...
```

Add `--json` for machine-readable output.

## Adding a new search engine

1. Open the engine in a normal browser with DevTools.
2. Find the result container selector.
3. Map selectors for title, link, snippet.
4. Add a branch to `search_engines.py`.
5. Test under `xvfb-run` with `headless=False`.

## References

- `scripts/search_engines.py` — reusable Yandex/Google search
- `playwright-marketplace-search` — same stack, but for Ozon/WB/Yandex Market
- `browser-automation` skill — Hermes native browser tools and CDP patterns
- `references/anti-bot-browser-patterns.md` — shared anti-bot reference from `playwright-marketplace-search`
