# Russian Marketplace Bot Protection Landscape

Field notes from live probing during product-hunt sessions.

## Directly blocked (do not rely on live prices)

| Site | What happens | Notes |
|---|---|---|
| market.yandex.ru | 403 "Доступ к сервису временно запрещён" | Hard bot wall from Yandex, both curl and browser. |
| ozon.ru | Connection incident page | Blocks headless/automated sessions. |
| wildberries.ru | Empty "Почти готово..." page | Anti-bot, no content rendered. |
| dns-shop.ru | Empty + Qrator JS challenge | Requires browser JS execution + likely fingerprint. |
| citilink.ru | 429 "Слишком частые запросы" | Rate limit per IP; persistent. |
| kns.ru | Yandex SmartCaptcha | Explicit captcha gate. |
| hotline.ua | curl exit 124 / timeout | Ukrainian aggregator, not reachable from this environment. |
| e-katalog.ru | Empty response | Likely geo/IP/block. |
| price.ru | SPA shell, no product data in static HTML | Nuxt app; data loads dynamically, not via static payload. |

## Partially accessible

| Site | What works | Notes |
|---|---|---|
| regard.ru | Main catalog loads | Direct deep category URLs (e.g. /catalog/group400.htm) redirect to 404; search triggers 429 after repeated use. |
| 3dnews.ru, ixbt.com, ferra.ru, akimoff.ru | Static content accessible | Use for model background and historical reviews, not current prices. Many SSD review URLs are 404. |

## Search engines

| Engine | Status |
|---|---|
| Google | Returns blank pages for programmatic queries from this IP. |
| Bing | Returns HTML, but result parsing is fragile; can be used as last resort. |
| DuckDuckGo | Bot challenge / empty API response. |
| DuckDuckGo Instant Answer API | Returns offline test stub, not real results. |

## Recommended fallback

When automated data collection is blocked, switch to:
1. Curated model shortlist based on known market landscape.
2. Exact search strings for the user to run in their own browser.
3. Criteria for evaluating listings (official seller, warranty, reviews, NAND/controller).

Do not waste turns cycling through blocked sites.
