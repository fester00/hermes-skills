# Russian Retailers Probing — Session Notes

## Environment Context

- Ubuntu 24.04 LTS server (no desktop)
- Chrome 147.0.7727.116 via CDP on port 9222
- User profile: `~/.chrome-vk-profile` (persistent)
- Xvfb :100 — virtual display for headful Chrome
- Server IP: 130.255.9.9 (data center, heavily rate-limited)

---

## DNS-Shop (dns-shop.ru)

### Status: ❌ BLOCKED (403 Forbidden)

DNS actively blocks all requests from data-center IPs. The block happens at CDN/WAF layer, not application layer.

**Browser/CDP result:**
- Navigate to `https://www.dns-shop.ru/search/?q=...`
- Response: HTTP 403, plain white page
- Title: `HTTP 403`
- Body: `Доступ к сайту www.dns-shop.ru запрещен`
- Technical footer: `Guru meditation: c3hhbDkwb1VBT056bXlTYnBuOW5GN2w2cFhKNjY0ODc=` (Varnish/CloudFlare signature)

**curl result:**
- Even with full browser User-Agent headers: empty response or 403
- No product data in HTML at all

**Conclusion:** DNS is a hard block. Do not waste time retrying with different techniques.

---

## Citilink (citilink.ru)

### Status: ⚠️ PARTIAL (loads but SSR data missing)

Citilink allows connection but serves Next.js shell without product data.

**Browser/CDP result:**
- Page loads: title is correct (`Kingston NV2 1TB - купить по низкой цене в Ситилинк`)
- URL: `https://www.citilink.ru/search/?text=Kingston+NV2+1TB&available=1&order=price:asc`
- Screenshot: shows header, footer, but NO product cards
- Product grid area is blank white space

**HTML inspection:**
- HTML ~300KB of Next.js CSS/JS chunks, no visible product data
- `NV2` mentioned 258 times in minified JS bundles, not in rendered DOM
- Scripts reference `data-meta-product-id` but no populated product cards

**Root cause:** Citilink uses client-side hydration for search results. The SSR payload doesn't include product data — it's fetched via XHR after page load. In our headless Chrome environment, either:
1. The XHR request failed (CORS, auth, or anti-bot)
2. The hydration didn't complete before screenshot
3. The page requires interaction (scroll, pagination click) to trigger lazy loading

**Attempts tried:**
- Scroll down 800px × 5 times → still blank product area
- Full page screenshot (clip 1200×2000) → only footer visible
- Wait 8 seconds after load → no improvement
- Runtime.evaluate product extraction → returns 1 irrelevant result (PC build, not SSD)

**Conclusion:** Citilink product search is not easily scrapeable via CDP without full browser session emulation. Use direct search URLs for user navigation instead.

---

## Ozon (ozon.ru)

### Status: ❌ BLOCKED (curl) / ❓ Untested (browser)

**curl result:**
- Returns redirect to `https://www.ozon.ru/search/?text=...&__rr=5`
- Exit code 47 (CURLE_TOO_MANY_REDIRECTS)
- No product data accessible via raw HTTP

**Browser/CDP:** Not tested in this session. Ozon is known to have heavy anti-bot (Yandex SmartCaptcha, behavioral analysis).

---

## Yandex Market (market.yandex.ru)

### Status: ❌ CAPTCHA (curl) / ❓ Untested (browser)

**curl result:**
- Redirects to `showcaptcha` page with base64-encoded challenge
- Full CAPTCHA gate — no search results accessible

---

## Verified Matrix — Server Environment (May 2025)

| Retailer | curl | Browser/CDP | Recommendation |
|----------|------|-------------|----------------|
| DNS | ❌ 403 | ❌ 403 | **Skip entirely** |
| Citilink | ❌ shell | ⚠️ no products | Use for user links, not scraping |
| Ozon | ❌ redirect | ❓ untested | Likely blocked, skip |
| Я.Маркет | ❌ CAPTCHA | ❓ untested | Likely blocked, skip |
| Wildberries | ❌ untested | ❓ untested | Likely blocked |

---

## Recommended Approach for Price Search Tasks

When user asks "find prices for X on Russian market":

1. **Acknowledge limitation immediately:** "Russian retailers block data-center IPs. I'll provide direct search links instead of live prices."

2. **Build product knowledge via accessible sources:**
   - Wikipedia / TechPowerUp for specs and MSRP
   - DuckDuckGo cached search results
   - Review sites (Tom's Hardware, AnandTech) for price tiers

3. **Provide structured comparison table** with:
   - Model names and specs
   - Typical/approximate price ranges (from knowledge, not live data)
   - Direct retailer search links (DNS, Citilink, Ozon, ЯМ)
   - Honest flag: "Live pricing blocked by anti-bot"

4. **Never loop** through multiple retailers with the same technique after 2 failures.

---

## CDP Technical Notes from Session

### Chrome launch sequence (correct order)
```bash
# CRITICAL: Xvfb must start BEFORE Chrome
Xvfb :100 -screen 0 1920x1080x24 -nolisten tcp &
sleep 2  # Wait for Xvfb to be ready

# CRITICAL: --remote-allow-origins=* required for WebSocket
display=:100 google-chrome \
  --no-sandbox --disable-gpu \
  --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --user-data-dir=/home/natan/.chrome-vk-profile \
  about:blank
```

### WebSocket CDP access
```python
import websocket, json

# Create new tab
r = requests.put('http://127.0.0.1:9222/json/new?url=about:blank')
page = r.json()
ws_url = page['webSocketDebuggerUrl']

# Connect
ws = websocket.create_connection(ws_url)
```

### Screenshot via CDP
```python
ws.send(json.dumps({
    "id": 1, "method": "Page.captureScreenshot",
    "params": {"format": "png", "fromSurface": True}
}))
resp = json.loads(ws.recv())
if "result" in resp:
    data = base64.b64decode(resp["result"]["data"])
    with open("/tmp/screenshot.png", "wb") as f:
        f.write(data)
```

---

## Session Reference
- Date: 2025-05-09
- User: Alexander (Natan), Russia-based
- Task: SSD price comparison (Kingston NV2/NV3, Samsung 980/980 PRO, WD SN770)
- Outcome: Anti-bot blocked all live pricing → provided direct search links + knowledge-based recommendations
