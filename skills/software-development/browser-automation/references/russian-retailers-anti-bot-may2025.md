# Russian Retailers Probing — Session Notes

## Environment Context

- Ubuntu 24.04 LTS server (no desktop)
- Chrome 147.0.7727.116 via CDP on port 9222
- User profile: `~/.chrome-vk-profile` (persistent)
- Xvfb :100 — virtual display for headful Chrome
- Server IP: 130.255.9.9 (data center, heavily rate-limited)
- SOCKS5 proxy on 127.0.0.1:10808 (xray)

---

## DNS-Shop (dns-shop.ru)

### Status: ❌ BLOCKED (403 Forbidden)

DNS actively blocks all requests from data-center IPs. The block happens at CDN/WAF layer, not application layer.

**Browser/CDP result:**
- Navigate to `https://www.dns-shop.ru/search/?q=...`
- Response: HTTP 403, plain white page
- Title: `HTTP 403`
- Body: `Доступ к сайту www.dns-shop.ru запрещен`
- Technical footer: `Guru meditation: ...` (Varnish/CloudFlare signature)

**curl result:**
- Even with full browser User-Agent headers: empty response or 403
- No product data in HTML at all

**Conclusion:** DNS is a hard block. Do not waste time retrying with different techniques.

---

## Citilink (citilink.ru)

### Status: ⚠️ PARTIAL (loads but SSR data missing)

Citilink allows connection but serves Next.js shell without product data.

**Browser/CDP result:**
- Page loads: title is correct
- URL: `https://www.citilink.ru/search/?text=...`
- Screenshot: shows header, footer, but NO product cards
- Product grid area is blank white space

**Root cause:** Citilink uses client-side hydration for search results. The SSR payload doesn't include product data — it's fetched via XHR after page load. In our headless Chrome environment, either the XHR request failed, hydration didn't complete, or the page requires interaction.

**Conclusion:** Citilink product search is not easily scrapeable via CDP without full browser session emulation. Use direct search URLs for user navigation instead.

---

## Ozon (ozon.ru)

### Status: ❌ BLOCKED (curl) / ❓ Untested (browser)

**curl result:**
- Returns redirect to `https://www.ozon.ru/search/?text=...&__rr=...`
- Exit code 47 (CURLE_TOO_MANY_REDIRECTS)
- No product data accessible via raw HTTP

**Browser/CDP:** Not tested in this session. Ozon is known to have heavy anti-bot.

---

## Yandex Market (market.yandex.ru)

### Status: ❌ BLOCKED — 403 and CAPTCHA even with persistent profile + proxy

**Direct `browser_navigate` (no proxy):**
- URL: `https://market.yandex.ru/`
- Title: `403`
- Body: `Доступ к сервису временно запрещён`
- Reason: data-center IP blocked at edge

**CDP with persistent Chrome profile (`~/.chrome-vk-profile`):**
- Same result: `403`
- Profile reuse does not bypass IP-based block

**curl via SOCKS5 proxy (`127.0.0.1:10808`):**
- ya.ru redirects to `showcaptcha` page with Yandex SmartCaptcha
- market.yandex.ru returns the same CAPTCHA HTML: "Подтвердите, что запросы отправляли вы, а не робот"
- No product/auth data accessible

**Conclusion:** Yandex Market cannot be accessed automatically from this server. Auth state cannot be verified by the agent. User must check manually in their own browser. For automation, recommend browser-use with residential proxy or API-based alternatives.

---

## Verified Matrix — Server Environment

| Retailer | curl | Browser/CDP | Recommendation |
|----------|------|-------------|----------------|
| DNS | ❌ 403 | ❌ 403 | **Skip entirely** |
| Citilink | ❌ shell | ⚠️ no products | Use for user links, not scraping |
| Ozon | ❌ redirect | ❓ likely blocked | Skip |
| Я.Маркет | ❌ 403 / CAPTCHA | ❌ 403 / CAPTCHA | **Skip; user checks manually** |
| Wildberries | ❌ untested | ❓ likely blocked | Likely blocked |

---

## Recommended Approach for Price Search Tasks

When user asks "find prices for X on Russian market":

1. **Acknowledge limitation immediately:** "Russian retailers block data-center IPs. I'll provide direct search links instead of live prices."
2. **Build product knowledge via accessible sources:** Wikipedia, TechPowerUp, DuckDuckGo cached results, review sites.
3. **Provide structured comparison table** with specs, approximate price ranges, and direct retailer search links.
4. **Never loop** through multiple retailers with the same technique after 2 failures.

---

## CDP Technical Notes from Session

### Chrome launch sequence
```bash
Xvfb :100 -screen 0 1920x1080x24 -nolisten tcp &
sleep 2
display=:100 google-chrome \
  --no-sandbox --disable-gpu \
  --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --user-data-dir=/home/natan/.chrome-vk-profile \
  about:blank
```

### WebSocket CDP access
```python
import websocket, json, requests
r = requests.put('http://127.0.0.1:9222/json/new?url=about:blank')
page = r.json()
ws_url = page['webSocketDebuggerUrl']
```

---

## Session References
- Date: 2025-05-09 / 2026-07-05
- User: natan (Russia-based)
- Task: SSD price comparison; Yandex Market auth check
- Outcome: Anti-bot blocked all live access → provided direct search links + knowledge-based recommendations
