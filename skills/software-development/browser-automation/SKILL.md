---
name: browser-automation
description: Browser automation via Chrome DevTools Protocol (CDP) and Hermes browser tools. Navigate, interact with forms, handle cross-origin iframes, capture and crop screenshots, extract data from web pages.
---

# Browser Automation

Use Hermes browser tools (`browser_navigate`, `browser_click`, `browser_type`, `browser_vision`, `browser_cdp`) combined with Chrome DevTools Protocol for advanced interactions.

## Basic Navigation & Interaction

```bash
# Navigate
browser_navigate → URL

# Get interactive snapshot
browser_snapshot → returns refs (e1, e2...)

# Click / type by ref
browser_click(ref=e4)
browser_type(ref=e8, text="hello")
```

## Handling Cross-Origin Iframes

**Problem:** Login forms, payment widgets, or auth flows are often embedded in `<iframe>` from a different origin (e.g. `id.vk.com` inside `vk.com`).

- `browser_click` and `browser_type` target elements by `ref` from the outer page snapshot.
- **If the target element is inside a cross-origin iframe, refs from the outer snapshot are INVALID** — clicks fail silently or target wrong elements.

**Solution — Navigate directly to the iframe src:**

```bash
# 1. Inspect iframe src via console
browser_console: window.location.href  # outer page
browser_console: document.querySelector('iframe').src  # get iframe URL

# 2. Navigate directly to the iframe URL
browser_navigate → "https://id.vk.com/auth?..."

# 3. Now snapshot gives refs for elements inside the iframe
browser_snapshot → e8 (textbox), e4 (button)
```

**Pitfall:** After navigating to iframe src, the page may be a standalone auth flow (not embedded). Design may differ slightly from the embedded version.

## Screenshot Cropping & Framing

### Method A: Resize viewport (recommended for composition)

Use CDP `Emulation.setDeviceMetricsOverride` to change the browser window size before capturing:

```json
{
  "method": "Emulation.setDeviceMetricsOverride",
  "params": {
    "width": 1280,
    "height": 380,
    "deviceScaleFactor": 1,
    "mobile": false
  },
  "target_id": "PAGE_TARGET_ID"
}
```

**How to get `target_id`:**
```json
{
  "method": "Target.getTargets"
}
# Result → targetInfos[].targetId for type="page"
```

**After use, restore normal size:**
```json
{
  "method": "Emulation.clearDeviceMetricsOverride",
  "target_id": "PAGE_TARGET_ID"
}
```

### Method B: Clip during capture (fine-grained)

Use CDP `Page.captureScreenshot` with `clip`:

```json
{
  "method": "Page.captureScreenshot",
  "params": {
    "format": "png",
    "clip": {
      "x": 0,
      "y": 0,
      "width": 1280,
      "height": 395,
      "scale": 1
    }
  },
  "target_id": "PAGE_TARGET_ID"
}
```

**Warning:** Result is base64-encoded PNG. Output may be **truncated** by the tool if very large (>100KB). Method A (resize) is more reliable for sharing screenshots via `browser_vision`.

### Method C: Clean screenshot via browser_vision

```json
{
  "annotate": false,
  "question": "Describe the current page"
}
```

- `annotate: false` removes red numbered boxes from the screenshot.
- Screenshot is saved to `~/.hermes/cache/screenshots/` and can be sent via Telegram/Discord.

**Pitfall:** `send_message` with `MEDIA:path` may timeout on large screenshots. Use `telegram:` target explicitly.

## Form Interaction Patterns

### Phone / numeric input with prefix

```bash
# Field shows "+7" prefix, type only the remaining digits
browser_type(ref=textbox, text="9773134407")
# Result: +7 977 313 44 07
```

### Disabled button until valid input

- Snapshot before typing: button shows `[disabled]`
- Snapshot after typing: button becomes active
- Always re-snapshot after typing before clicking

### QR-code auth flows (VK, Telegram Web, etc.)

After submitting credentials, some services redirect to QR-code confirmation instead of SMS/password:

- Page shows large QR code with app logo in center
- Instruction: "Scan with phone camera"
- Agent **cannot proceed** without physical device with the required app installed
- Only option: capture screenshot and ask user to scan, or abort

## Data Extraction from Web Pages

Use `browser_console` with JavaScript to extract structured data:

```javascript
// Get all links
Array.from(document.querySelectorAll('a')).map(a => ({text: a.innerText, href: a.href}))

// Get form fields
Array.from(document.querySelectorAll('input, button')).map(el => ({tag: el.tagName, type: el.type, name: el.name}))

// Get iframe sources
document.querySelector('iframe')?.src
```

## Cookie Analysis for Auth State

When user provides cookies for "I'm already logged in" automation:

**Distinguish tracking cookies from auth cookies:**

| Cookie | Type | Meaning |
|--------|------|---------|
| `_ga`, `_ym_*` | Tracking | Google Analytics / Яндекс.Метрика |
| `remixscreen_*`, `remixlang` | Preference | Screen size, language |
| `remixrefkey`, `remixua`, `remixgp` | Tracking | Referral, user-agent fingerprint |
| `remixstlid`, `remixstid` | Session | Session tracking (NOT login session) |
| **`remixsid`** | **Auth** | **Main VK login session — present only after successful auth** |
| `remixttpid` | Auth | Device trust token (after 2FA/device confirmation) |
| `remixusid` | Auth | User identity token |

**Always check for `remixsid` presence** — if absent, the user is not actually logged in regardless of how many other cookies exist.

**Pitfall:** Users often copy "all cookies from browser devtools" and think that enables auth. Most of those are analytics/preference cookies. Use `browser_console: document.cookie` on the target site to verify actual auth state, or ask user to filter cookies by `.vk.com` domain and look for `remixsid`.

## Advanced Iframe Interaction via CDP

**Problem:** Cross-origin iframe elements don't appear in outer-page snapshot refs. Direct `browser_click(ref=...)` on iframe elements fails.

**Solution — CDP Runtime.evaluate on the child frame_id:**

```json
// 1. Get child frame_id from browser_snapshot frame_tree
//    (browser_snapshot includes "frame_tree" with child frames and their frame_ids)

// 2. Use browser_cdp with the child frame_id to execute JS inside the iframe
{
  "method": "Runtime.evaluate",
  "frame_id": "A3FC1AD24772ED15D6D54CD9415BB18A",
  "params": {
    "expression": "document.querySelector('button').click()"
  }
}

// 3. For complex selectors (e.g. text-match), evaluate JS that searches and clicks
{
  "method": "Runtime.evaluate",
  "frame_id": "CHILD_FRAME_ID",
  "params": {
    "expression": "(() => { const btns = document.querySelectorAll('button'); for (let b of btns) { if (b.textContent.includes('другим')) { b.click(); return 'clicked'; } } return 'no button'; })()"
  }
}
```

**Advantage:** No need to navigate away from the parent page. The iframe stays embedded, preserving parent-frame context, return URLs, and postMessage handlers.

**Pitfall:** `setTimeout` inside `Runtime.evaluate` may not execute reliably. Use synchronous JS evaluation, or add explicit `browser_cdp` + `Runtime.evaluate` calls with delays between them.

## Headless Chrome with Persistent Profile on Remote Server

**Problem:** SSH-only access to Ubuntu server, no desktop environment. Need to log into web services (VK, Yandex, Ozon, Telegram Web) and preserve cookies for later automation.

**Solution — Xvfb + Chrome CDP:**

```bash
# 1. Install Xvfb (virtual framebuffer for headful Chrome)
sudo apt install -y xvfb

# 2. Create persistent profile directory
mkdir -p ~/.chrome-vk-profile

# 3. Start Xvfb in background FIRST (critical!)
#    Chrome will crash with "Missing X server or $DISPLAY" without this
Xvfb :100 -screen 0 1920x1080x24 -nolisten tcp &
sleep 2

# 4. Start Chrome with CDP on the virtual display
#    --remote-allow-origins=* REQUIRED for WebSocket connections from localhost
#    --no-sandbox REQUIRED in containers/VMs (AppArmor blocks unprivileged namespaces)
DISPLAY=:100 /usr/bin/google-chrome-stable \
  --no-sandbox --disable-gpu \
  --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --remote-debugging-address=0.0.0.0 \
  --user-data-dir=/home/natan/.chrome-vk-profile \
  --disable-dev-shm-usage \
  --disable-setuid-sandbox \
  --window-size=1920,1080 \
  "https://vk.com" &
```

**Critical flags explained:**

| Flag | Why Required |
|------|------------|
| `--no-sandbox` | Ubuntu 23.10+ disables unprivileged user namespaces via AppArmor. Without this, Chrome exits with `FATAL:zygote_host_impl_linux.cc:128 No usable sandbox!` |
| `--remote-allow-origins=*` | CDP WebSocket rejects connections with `403 Forbidden` if origin is not explicitly allowed. Required for all WebSocket CDP clients |
| `--disable-gpu` | Prevents GPU initialization errors in headless/virtual environments |
| `--disable-dev-shm-usage` | Avoids `/dev/shm` size limits in Docker/containers |

**Verification:**
```bash
# Check Chrome is listening
curl -s http://127.0.0.1:9222/json/version | grep webSocketDebuggerUrl

# Check Xvfb is running
ps aux | grep Xvfb
```

**If Chrome exits immediately** — check `/tmp/chrome.log` for `Missing X server or $DISPLAY`. Ensure Xvfb started BEFORE Chrome and `DISPLAY=:100` is exported.

**Remote GUI access options for login:**

| Method | Setup | Access |
|--------|-------|--------|
| **Xpra** (recommended) | `sudo apt install xpra; xpra start :100 --html=on --bind-tcp=0.0.0.0:14500 --start-child="google-chrome-stable ..."` | Browser opens at `http://server:14500` via SSH tunnel `ssh -L 14500:localhost:14500 user@server` |
| **noVNC** | `vncserver :1 -geometry 1920x1080; websockify --web /usr/share/novnc 6080 localhost:5901` | VNC via browser at `http://localhost:6080/vnc.html` |

**Critical:** Always use `--user-data-dir=/path/to/profile` — without it Chrome starts with a temporary profile and cookies are lost on restart. Verify profile persistence by checking `~/.chrome-vk-profile/Default/Cookies` exists after login.

**CDP URL changes on every Chrome restart.** After relaunch, update `~/.hermes/config.yaml`:
```yaml
browser:
  cdp_url: 'ws://localhost:9222/devtools/browser/<NEW-UUID>'
```

Or automate the update:
```bash
CDP_URL=$(curl -s http://localhost:9222/json/version | grep -o 'ws://[^"]*' | head -1)
hermes config set browser.cdp_url "$CDP_URL"
```

## QR-Code Auth Flows

Some services (VK, Telegram Web, WeChat Web) show a QR code as the **default** login method:

1. User opens site → sees QR code + "Scan with phone camera"
2. Button "Log in another way" / "Войти другим способом" reveals password form
3. After password entry, may redirect back to QR confirmation (device auth)

**Agent limitation:** Cannot scan QR codes. Options:
- Capture screenshot (`browser_vision` with `annotate: false`) and ask user to scan
- Look for "another way" button via CDP iframe evaluation
- Abort and recommend API-based auth instead (e.g. VK API with access_token)

**Recommendation for VK specifically:** Use VK API (standalone app + access_token) for automation instead of browser auth. More reliable, not affected by UI redesigns or anti-bot detection.

## Direct CDP via WebSocket (Bypass Playwright Failures)

**Problem:** Hermes Playwright tools (`browser_navigate`, `browser_click`) sometimes fail to connect to CDP even though the port responds. Error patterns:
- `Auto-launch failed: CDP WebSocket connect failed: HTTP error: 404 Not Found`
- `CDP WebSocket connect failed: IO error: Connection refused`

**Root cause:** The `browser.cdp_url` in `~/.hermes/config.yaml` may be stale (UUID changes on every Chrome restart), or Playwright's WebSocket handshake has compatibility issues with the current Chrome version.

**Solution — Use `browser_cdp` directly (Hermes handles session internally):**

```json
{
  "method": "Target.getTargets",
  "params": {}
}
# Result → find target with type="page" and url matching your site
# Use that target_id for subsequent calls:
{
  "method": "Page.captureScreenshot",
  "params": {"format":"png","fromSurface":true},
  "target_id": "PAGE_TARGET_ID"
}
```

**If `browser_cdp` also fails with WebSocket errors** — bypass Hermes entirely and use direct Python WebSocket:

```python
import websocket, json, base64

ws_url = "ws://127.0.0.1:9222/devtools/browser/<UUID>"
ws = websocket.create_connection(ws_url)

# 1. Attach to page target
ws.send(json.dumps({
    "id":1,"method":"Target.attachToTarget",
    "params":{"flatten":True,"targetId":"PAGE_TARGET_ID"}
}))
resp = ws.recv()
msg = json.loads(resp)
session_id = msg["params"]["sessionId"]  # from Target.attachedToTarget event

# 2. Navigate
ws.send(json.dumps({
    "id":2,"method":"Page.navigate","params":{"url":"https://vk.com/im"},
    "sessionId":session_id
}))

# 3. Evaluate JS (e.g., click element by text)
js = """
(function() {
    const els = document.querySelectorAll('*');
    for (const el of els) {
        if (el.textContent && el.textContent.trim() === 'Exact Text') {
            let node = el;
            for (let i = 0; i < 10; i++) {
                if (node.click) { node.click(); return 'clicked'; }
                node = node.parentElement;
                if (!node) break;
            }
        }
    }
    return 'not found';
})()
"""
ws.send(json.dumps({
    "id":3,"method":"Runtime.evaluate",
    "params":{"expression":js,"returnByValue":True},
    "sessionId":session_id
}))

# 4. Capture screenshot to file (avoids Hermes truncation)
ws.send(json.dumps({
    "id":4,"method":"Page.captureScreenshot",
    "params":{"format":"png","fromSurface":True},
    "sessionId":session_id
}))
resp = ws.recv()
data = json.loads(resp)["result"]["data"]
with open("/tmp/screenshot.png", "wb") as f:
    f.write(base64.b64decode(data))

ws.close()
```

**Advantages of direct WebSocket:**
- Works even when Hermes Playwright layer is broken
- Full control over CDP session lifecycle
- Can save large responses (e.g., screenshots) directly to files without tool truncation
- Supports all CDP methods including `Page.navigate`, `Runtime.evaluate`, `Input.dispatchMouseEvent`, etc.

**Pitfall:** `Target.attachToTarget` returns `sessionId` via the `Target.attachedToTarget` event, NOT in the `result` object. Listen for the event to get the session ID.

### Alternative CDP port (fallback)

When the default CDP port 9222 is occupied or the endpoint is stale, Chrome can be launched on an alternative port:

```bash
# Kill old Chrome, relaunch on port 9223
kill $(pgrep -f "chrome.*user-data-dir=/home/$USER/.chrome-vk-profile") 2>/dev/null
DISPLAY=:100 google-chrome --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --remote-debugging-port=9223 --remote-allow-origins=* \
  --user-data-dir=/home/$USER/.chrome-vk-profile \
  --no-first-run --no-default-browser-check https://vk.com/im &
```

Then update Hermes config to use the new port:
```bash
curl -s http://127.0.0.1:9223/json/version | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(d['webSocketDebuggerUrl'])"
hermes config set browser.cdp_url "ws://127.0.0.1:9223/devtools/browser/<UUID>"
```

## CDP URL Lifecycle & Stale Endpoint Fix

**The browser endpoint UUID changes on every Chrome restart.** If Chrome crashes or is restarted, the old `cdp_url` in `~/.hermes/config.yaml` becomes invalid.

**Quick fix after Chrome restart:**
```bash
# Get fresh CDP URL
curl -s http://127.0.0.1:9222/json/version | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['webSocketDebuggerUrl'])"

# Update Hermes config
hermes config set browser.cdp_url "ws://127.0.0.1:9222/devtools/browser/<NEW-UUID>"
```

**If you changed the Chrome CDP port** (e.g., from 9222 to 9223 after a conflict), update both the curl port and the config:
```bash
curl -s http://127.0.0.1:9223/json/version | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['webSocketDebuggerUrl'])"
hermes config set browser.cdp_url "ws://127.0.0.1:9223/devtools/browser/<NEW-UUID>"
```

**Auto-update script:**
```bash
#!/bin/bash
PORT=${1:-9222}
CDP_URL=$(curl -s "http://127.0.0.1:$PORT/json/version" | grep -oP 'ws://[^"]+' | head -1)
hermes config set browser.cdp_url "$CDP_URL"
echo "Updated cdp_url to: $CDP_URL"
```

## Saving Screenshots via Direct CDP (Avoid Truncation)

**Problem:** `browser_cdp` with `Page.captureScreenshot` returns base64 data, but Hermes may truncate very large responses (>100KB). You get the screenshot data but it's cut off mid-stream.

**Solution:** Use direct WebSocket (Python script above) or write to file via CDP:

```python
# After getting screenshot data from CDP
import base64
with open("/tmp/screenshot.png", "wb") as f:
    f.write(base64.b64decode(data))
```

Then send the file via Telegram:
```
MEDIA:/tmp/screenshot.png
```

**Alternative:** Use `Emulation.setDeviceMetricsOverride` to reduce viewport size before capture, producing smaller PNG files:
```json
{
  "method": "Emulation.setDeviceMetricsOverride",
  "params": {"width":1280,"height":800,"deviceScaleFactor":1,"mobile":False},
  "sessionId": "SESSION_ID"
}
```

## CDP Search Result Extraction (When curl Fails)

**Problem:** On data-center IPs (e.g. 130.255.9.9), `curl` to search engines immediately triggers CAPTCHA — DuckDuckGo, Bing, and Google all block raw HTTP requests. `browser_navigate` may also fail with stale CDP URL.

**Working solution — `browser_cdp` direct navigation + JS extraction:**

```bash
# Step 1: Navigate via CDP
browser_cdp:
  method: Page.navigate
  params: {"url": "https://html.duckduckgo.com/html/?q=QUERY"}
  target_id: PAGE_TARGET_ID

# Step 2: Wait 4 seconds for load

# Step 3: Verify results loaded
browser_cdp:
  method: Runtime.evaluate
  params: {"expression": "document.querySelectorAll('a.result__a').length"}
  target_id: PAGE_TARGET_ID
# → Expect value > 0

# Step 4: Extract structured results
browser_cdp:
  method: Runtime.evaluate
  params:
    expression: |
      (() => {
        const r = [];
        const links = document.querySelectorAll('a.result__a');
        const snippets = document.querySelectorAll('a.result__snippet');
        for (let i = 0; i < Math.min(links.length, 10); i++) {
          const a = links[i];
          let url = a.href;
          if (url.includes('/l/?')) {
            const m = url.match(/uddg=([^&]+)/);
            if (m) url = decodeURIComponent(m[1]);
          }
          r.push({
            title: a.innerText.trim(),
            url: url,
            snippet: snippets[i] ? snippets[i].innerText.trim().substring(0, 200) : '',
            engine: 'duckduckgo'
          });
        }
        return JSON.stringify(r, null, 2);
      })()
    returnByValue: true
  target_id: PAGE_TARGET_ID
```

**Google variant (add `gl=us` to skip EU consent):**
```javascript
// Navigate to: https://www.google.com/search?q=QUERY&gl=us&hl=en
// Then extract:
(() => {
  const results = [];
  const containers = document.querySelectorAll("div[data-ved]");
  for (const container of containers.slice(0, 10)) {
    const h3 = container.querySelector("h3");
    const link = container.querySelector("a[href^='http']");
    const spans = container.querySelectorAll("span");
    let snippet = "";
    for (const s of spans) {
      const text = s.innerText;
      if (text.length > 30 && text.length < 300) {
        snippet = text.substring(0, 200);
        break;
      }
    }
    if (h3 && link) {
      results.push({ title: h3.innerText.trim(), url: link.href, snippet, engine: 'google' });
    }
  }
  return JSON.stringify(results, null, 2);
})()
```

**Pitfall:** If `document.querySelectorAll('a.result__a')` returns 0, DuckDuckGo may be showing CAPTCHA. Check with `browser_vision` (annotate: false) or query the page title via console.

## Price Search & Market Research Fallback Workflow

**When user asks for product price comparisons (electronics, hardware, etc.) on Russian market:**

### Attempt 1: Direct Browser/CDP Search (Preferred)

```json
// Option A: DuckDuckGo (most reliable from server)
browser_cdp:
  method: Page.navigate
  params: {"url": "https://html.duckduckgo.com/html/?q=MODEL+site:market.yandex.ru"}
  target_id: PAGE_TARGET_ID

// Option B: Google with geo-bypass
curl -sL -A "Mozilla/5.0" "https://www.google.com/search?q=SSD+M2+1TB+price+May+2025&gl=us"
  | strings | grep -iE "price|₽|€|\$"

// Option C: Wikipedia for specs baseline
curl -sL -A "Mozilla/5.0" "https://en.wikipedia.org/wiki/SNV2"
  | strings | grep -iE "[0-9]+\s*MB/s|[0-9]+\s*GB/s|controller|TLC|QLC|PCIe"
```

### Attempt 2: Aggregator & Review Sites (Bypass Anti-Bot)

When all Russian retailers block access (CAPTCHA, empty responses):

| Fallback Site | Endpoint | Why It Works | Extract From |
|---------------|----------|--------------|------------|
| **TechPowerUp** | `techpowerup.com/ssd-specs/` | No anti-bot, static DB | Model names, controllers, speeds |
| **Tom's Hardware** | `tomshardware.com/reviews/best-ssds` | US-based, no RU restrictions | Price tiers, recommendations |
| **AnandTech** | `anandtech.com/show/XXXX` | Static articles | Model lists, specs |
| **Wikipedia** | `en.wikipedia.org/wiki/Drive_model` | Always accessible | Base specs, release dates |
| **3DNews price** | `3dnews.ru/price/ssd-nvme-m2` | Russian tech site, lighter anti-bot | Model names, price ranges |
| **DNS Citilink snippets** | Search engine cached | Cached pages bypass live anti-bot | Product names, rough pricing |

**Command pattern:**
```bash
curl -sL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0" \
  "URL" | strings | grep -oP "MODEL|PATTERN" | sort | uniq -c | head -20
```

### Attempt 3: Knowledge-Based Synthesis (When Live Data Is Blocked)

**If NO live pricing is accessible, do NOT give up and abort. Instead:**

1. **Search for product reviews / roundups** that include current models
   ```bash
   curl -sL "https://html.duckduckgo.com/html/?q=best+SSD+M2+1TB+2025+review"
   ```

2. **Extract model names** from review articles (always accessible)

3. **Build price-agnostic recommendation table:**
   - Known manufacturer MSRP or typical market price ranges
   - Specs (controller, NAND type, PCIe gen, sequential/random speeds)
   - Relative value tier (budget/mid-range/premium)
   - Links to product pages on major retailers (even if not verified live)

4. **Flag the limitation honestly:** "Live pricing currently blocked by anti-bot, prices are approximate based on typical market ranges"

### Key Pitfall: Do Not Block on Anti-Bot

- **Never let CAPTCHA or empty cURL responses stop the workflow**
- If all Russian retailers (Ozon, DNS, Yandex Market, Citilink, Wildberries) return empty/captcha → immediately switch to fallback sources
- Users prefer a **structured knowledge-based recommendation** to "I couldn't check prices"

#### Binary Decomposition Extraction (Anti-Bot Bypass)

When sites return binary/compressed responses that defeat text parsing, use `strings` + grep as a frequency filter:

```bash
# Extract product names and specs from garbled anti-bot responses
curl -sL -A "Mozilla/5.0" "https://citilink.ru/catalog/nakopiteli-m2/?text=ssd+1tb+m2" \
  | strings | grep -oP "WD|Kingston|Samsung|SN770|SN850|980|990|NV2|PCIe|7000|5000|3500|TLC" \
  | sort | uniq -c | sort -rn | head -20
```

**What this reveals:** Product names and specs buried in compressed/minified payloads, even when the HTML is unreadable.

**Limitation:** No pricing, no URLs, no structured data. Use only for **model identification** before switching to knowledge synthesis.

### The Repetition Trap

**Pitfall:** When curl fails on Site A, trying the same curl pattern on Sites B, C, D, E, F is wasted time if they share the same anti-bot stack (CloudFlare, Akamai, Yandex SmartCaptcha).

**Rule of thumb:** After 2 failures with the same technique on different sites in the same market → switch technique entirely (browser → knowledge synthesis → API → give up, NEVER loop).

## Verified Site Matrix (Server Environment)

| Site | curl | Browser/CDP | Notes |
|------|------|-------------|-------|
| DuckDuckGo HTML | ❌ CAPTCHA | ✅ | Primary search method |
| Bing | ❌ CAPTCHA | ⚠️ | Sometimes works via browser |
| Google | ❌ "Unusual traffic" | ✅ | Add `&gl=us` for EU skip |
| Yandex / Yandex Market | ❌ / CAPTCHA | ❌ / 403 | "Вы не робот?" or 403 even with persistent CDP profile and SOCKS5 proxy; cannot automate auth or search |
| Wikipedia | ✅ | ✅ | curl always works |
| GitHub | ✅ | ✅ | curl usually works |
| Habr / Stack Overflow | ✅ | ✅ | curl works |
| Ozon / Wildberries | ❌ | ❌ | Heavy anti-bot, skip |
| VK (with auth) | N/A | ✅ | Via CDP, see VK references |

**Rule:** On this server, always try browser/CDP first for search engines; use curl only for direct content sites.

## CDP Target Lifecycle

- `browser_cdp` requires `target_id` for page-specific methods.
- `Target.getTargets` returns all targets including service workers.
- Filter by `type: "page"` to get the main page target.
- After Chrome restart, all `target_id` values change. Re-query `Target.getTargets`.

## AI-Native Browser Agents (browser-use, Comet, etc.)

**Problem:** Hermes' built-in `browser_*` tools run a fresh headless/anonymous Chromium profile. They cannot see the user's logged-in sessions, saved passwords, or cookies. This makes them unsuitable for tasks that require personal accounts on marketplaces, banks, social networks, or 2FA-protected services.

**Solution class:** dedicated AI browser agents that drive the user's real browser (or a persistent copy of it) and can reuse an existing profile.

| Tool | What it does | Integration with Hermes | When to mention |
|---|---|---|---|
| **browser-use** | Open-source Python library + CLI. Launches Chrome with `--user-data-dir`, lets an LLM navigate, click, fill forms, extract data. Has its own cloud option with stealth/proxy. | **Not integrated.** User installs it separately (`uv add browser-use` or `pip install browser-use`) and runs it via Cursor/Codex/Claude Code. Hermes cannot call it directly. | When user asks "how do I search marketplaces while logged in?" or "can you control my real browser?" |
| **Comet** | Commercial AI browser with built-in agent and persistent profile. | **Not integrated.** Standalone product. | Same as above; note it exists but Hermes cannot drive it. |
| **Playwright / Selenium with persistent profile** | Scripting libraries. Can point to an existing `user-data-dir`. | Hermes can write the Python/Node script; user runs it. | When user needs automation they execute themselves. |
| **Chrome remote debugging (`--remote-debugging-port=9222`)** | Connect CDP client to an already-running Chrome on the user's machine. | Hermes `browser_cdp` can connect if the port and origin allow-list are configured. | When user wants the cheapest bridge without installing new tools. |

### Typical setup: Chrome CDP on user's own profile

```bash
# 1. Start Chrome with a persistent profile and remote debugging
/path/to/google-chrome \
  --user-data-dir="$HOME/.chrome-my-profile" \
  --remote-debugging-port=9222 \
  --remote-allow-origins='*' \
  --no-sandbox

# 2. Verify endpoint
curl -s http://127.0.0.1:9222/json/version | grep webSocketDebuggerUrl

# 3. Point Hermes browser_cdp at the page target, or use a direct WebSocket script
```

**Caveats:**
- The CDP browser UUID changes on every Chrome restart — refresh the URL.
- Anti-bot on marketplaces (Ozon, Wildberries, Yandex Market, DNS) may still challenge even a real browser from a data-center IP.
- For true "log in once, reuse forever" experience, browser-use's local profile mode or a tool like Comet is usually simpler than hand-wiring CDP.

### browser-use headless-server recipe

For a concrete browser-use launch recipe on a headless Ubuntu server (Xvfb + persistent profile + sandbox flags) and the common `Invalid JSON` / `Field required` failures with non-strict LLMs, see `references/playwright-persistent-chrome-ozon-template.md`.

### Recommended workflow for marketplace price/product search

1. If user is fine with anonymous search → use Hermes `browser_*` / `browser_cdp`.
2. If user needs to be logged in → recommend installing **browser-use** locally with their Chrome profile, or share screenshots/links with Hermes for analysis.
3. Hermes should **not** attempt to drive browser-use itself; it can only explain how to set it up or review the script it produces.

## References
- `references/text-field-extraction-patterns.md` — JavaScript snippets for extracting text from interactive elements via CDP
- `references/server-ip-search-restrictions.md` — Search engine anti-bot behavior from data-center IPs
- `references/web-bundlers-comparison.md` — Quick reference: Bun, Vite, esbuild, webpack, Parcel
- `references/russian-retailers-probing-guide.md` — Early probing notes for Russian e-commerce sites
- `references/russian-retailers-anti-bot-may2025.md` — **Session-tested matrix:** DNS (403), Citilink (SSR shell), Ozon/Yandex (CAPTCHA). Verified anti-bot patterns and recommended fallback workflow for price search tasks
- `references/vk-messenger-cdp-scripts.md` — VK IM automation via raw CDP WebSocket
- `references/vk-auth-flow.md` — VK ID auth flow: iframe architecture, cookies, QR-first design, API alternative
- `references/vk-automation-cdp-patterns.md` — VK IM, marketplace, and community automation via raw CDP WebSocket
- `references/playwright-persistent-chrome-ozon-template.md` — Proven Playwright script for Ozon product search on a headless server using Xvfb + persistent Chrome profile + viewport; also covers `browser-use` headless-server setup and LLM JSON pitfalls
- `references/skill-hubs-directory.md` — Index of skill reference directories
- `references/skill-hubs-directory.md` — Index of skill reference directories