# Russian Retailer Probing Guide

Session-tested accessibility matrix for Russian e-commerce sites (May 2026).

## Status Table

| Site | curl | Browser | Notes |
|------|------|---------|-------|
| BigGeek | No (search via URL fails; homepage loads) | ✅ Yes (no CAPTCHA) | Search box must be interacted with; URL ?search= redirects to sale page |
| Technodeus | ✅ Yes (static HTML) | N/A | Prices in `.product-info__price` or `data-price`. JS-heavy config in `<meta data-config>` |
| Re:store | N/A | ⚠️ Partial | Search via `?query=` param returns empty query. Category links work. SPA, JS-rendered |
| DNS | ❌ 429 | ❌ Heavy block | Rate-limits curl aggressively. Not viable for automation |
| Citilink | ❌ 429 | Untested | Same aggressive rate-limiting as DNS |
| Eldorado | ❌ 503 | Untested | Unavailable for automation |
| MVideo | ❌ Empty/Block | Untested | Not viable |
| Ozon | ❌ 403/CAPTCHA | ❌ CAPTCHA | Unusable — both desktop and mobile versions |
| Wildberries | ❌ "Почти готово…" | ❌ Empty page | SPA rendered but detects Playwright, serves empty loader |
| Yandex Market | ❌ CAPTCHA | ❌ CAPTCHA | Detects Playwright even on m.pokupki. Skip entirely |
| AliExpress Russia | ❌ 403 via curl | ⚠️ Partial | Page loads in browser but Google reCaptcha iframe hidden. Products rendered via JS SPA — not in static snapshot. Requires interaction |
| Avito | Untested | ✅ Yes | No CAPTCHA. Good for B/used / secondary market searches |
| Bing (search) | N/A | ❌ Timeout | Unreliable gateway; prefer direct retailer navigation |
| DuckDuckGo HTML | ❌ Checkbox CAPTCHA | ❌ Checkbox CAPTCHA | Not viable — confirmed both curl and browser |

## Useful User-Agent for Russian retail

```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

Mobile UAs (iPhone) do NOT bypass Russian marketplace blocks better than desktop UAs.

## Anti-bot fingerprinting patterns observed

- **Yandex Market**: 403 + "Вы не робот?" challenge. ReCaptcha v3 invisible on page load.
- **Ozon**: Returns HTML with `smc.check` script injection when detected.
- **Wildberries**: Empty `<html>` with loading spinner; real content never arrives in headless.
- **AliExpress Russia**: Loads skeleton, but `google.com/recaptcha/enterprise/anchor` iframe present. Products only render after challenge or JS execution.
