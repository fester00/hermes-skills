# Yandex SEO research — browser blocks and workarounds (2025-2026)

Session-specific notes from the 2026-06-29 Yandex SEO research run.

## Search environment in mid-2026

- **Google / Yandex / DuckDuckGo** frequently serve CAPTCHA or SmartCaptcha to automated browser sessions.
- Direct navigation to known authoritative URLs is more reliable than search when endpoints are blocked.
- Many deep-link patterns in older blog posts / skill references have changed (404).
- Russian SEO expert sites (SEOnews, PR-CY, ConvertMonster) load, but internal search often returns 404 for specific slugs; browsing the homepage/category feed works better.

## Verified working official entry points

| Source | Working path | Notes |
|---|---|---|
| Yandex Webmaster Help (Russian) | `https://yandex.ru/support/webmaster/ru/` | Current help hub. Replace old `/webmaster/...` URLs with `/webmaster/ru/...` |
| Recommendations intro | `/recommendations/intro.html` | Entry point to quality guidelines |
| Indexing | `/recommendations/indexing.html` | Technical indexing rules |
| Mobile sites | `/recommendations/mobile-site.html` | Mobile requirements |
| Robots / Sitemap | `/robot-workings/robot` | Crawler behaviour |
| Webmaster blog | `https://webmaster.yandex.ru/blog` | 2025–2026 announcements |
| Search blog | `https://yandex.ru/blog/search` | Search product updates |

## Verified expert sources loaded in 2026

- SEOnews: `seonews.ru` — loads, search works, specific AI-search articles verified (June 2026).
- PR-CY: `pr-cy.ru/news/` — loads, Yandex Commerce Protocol case studies on current feed.
- ConvertMonster: `convertmonster.ru/blog/` — loads, 2025 SEO/content articles accessible.
- Serpstat blog, Netology, Searchengines.guru — intermittent timeouts or blank pages in browser tool during this session.

## Fallback strategy

When search is blocked:
1. Use `browser_navigate` directly to the working URLs above.
2. Use site homepage/category feed to find recent articles.
3. Use `browser_vision` with full viewport for pages that may render content lazily.
4. For Yandex support docs, always try `/ru/` prefix first.

## Pitfalls

- Don't rely on guessed deep URLs for Yandex support; start at `/ru/` hub and navigate.
- Don't assume a 404 means the doc was removed; the URL scheme may have changed.
- Don't trust "estimated 2025/2026" dates on PR-CY homepage listings without opening the article.
- Subagents hit tool-call limits quickly when navigating CAPTCHA-blocked search; prefer focused direct URLs.
