# VK Messenger — CDP Automation Scripts

Session-tested scripts for automating VK (vk.com/im) messenger via raw Chrome DevTools Protocol WebSocket. Use when Hermes Playwright layer is unavailable or broken.

---

## Prerequisites

Chrome must be running with persistent profile and CDP enabled:
```bash
DISPLAY=:100 google-chrome --no-sandbox --disable-gpu \
  --disable-dev-shm-usage \
  --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --user-data-dir=/home/natan/.chrome-vk-profile \
  --no-first-run --no-default-browser-check \
  https://vk.com/im
```

User must already be logged in (cookies persisted in profile).

---

## Script: Open Dialog by Name + Screenshot Last Message

```python
import websocket, json, base64, os, time

# ===== CONFIG =====
CDP_WS = "ws://127.0.0.1:9222/devtools/browser/<UUID>"  # get from /json/version
TARGET_NAME = "Анна Ступельman"  # dialog name to open
OUT_PATH = "/tmp/vk_last_msg.png"
# ==================

ws = websocket.create_connection(CDP_WS)

# --- 1. Attach to VK page ---
ws.send(json.dumps({
    "id": 1, "method": "Target.attachToTarget",
    "params": {"flatten": True, "targetId": "PAGE_TARGET_ID"}
}))
session_id = None
for _ in range(10):
    resp = ws.recv()
    msg = json.loads(resp)
    if msg.get("method") == "Target.attachedToTarget":
        session_id = msg["params"]["sessionId"]
        break
print("Session:", session_id)

# --- 2. Navigate to messenger ---
ws.send(json.dumps({
    "id": 2, "method": "Page.navigate",
    "params": {"url": "https://vk.com/im"},
    "sessionId": session_id
}))
time.sleep(4)

# --- 3. Click dialog by name ---
js_click = """
(function() {
    const els = document.querySelectorAll('*');
    for (const el of els) {
        if (el.textContent && el.textContent.trim() === '%s') {
            let node = el;
            for (let i = 0; i < 10; i++) {
                if (node.click) { node.click(); return 'clicked ' + node.tagName; }
                node = node.parentElement;
                if (!node) break;
            }
        }
    }
    return 'not found';
})()
""" % TARGET_NAME

ws.send(json.dumps({
    "id": 3, "method": "Runtime.evaluate",
    "params": {"expression": js_click, "returnByValue": True},
    "sessionId": session_id
}))
for _ in range(5):
    r = ws.recv()
    d = json.loads(r)
    if d.get("id") == 3:
        print("Click:", d)
        break

time.sleep(3)

# --- 4. Scroll to bottom of chat ---
js_scroll = """
(function() {
    const panels = document.querySelectorAll('div');
    for (const p of panels) {
        if (p.scrollHeight > p.clientHeight && p.clientWidth > 400) {
            p.scrollTop = p.scrollHeight;
            return 'scrolled panel';
        }
    }
    window.scrollTo(0, document.body.scrollHeight);
    return 'scrolled window';
})()
"""
ws.send(json.dumps({
    "id": 4, "method": "Runtime.evaluate",
    "params": {"expression": js_scroll, "returnByValue": True},
    "sessionId": session_id
}))
time.sleep(2)

# --- 5. Screenshot ---
ws.send(json.dumps({
    "id": 5, "method": "Page.captureScreenshot",
    "params": {"format": "png", "fromSurface": True},
    "sessionId": session_id
}))
for _ in range(5):
    r = ws.recv()
    d = json.loads(r)
    if d.get("id") == 5:
        data = d["result"]["data"]
        with open(OUT_PATH, "wb") as f:
            f.write(base64.b64decode(data))
        print(f"Saved {OUT_PATH} ({os.path.getsize(OUT_PATH)} bytes)")
        break

ws.close()
```

---

## Script: Search Dialogs by Name (VK IM Search)

VK IM search field searches across dialog list. If search redirects to global search (vk.com/search), return to vk.com/im and try direct dialog click instead.

```python
js_search = """
(function() {
    const inputs = Array.from(document.querySelectorAll('input'));
    const searchInput = inputs.find(i =>
        i.placeholder && (
            i.placeholder.toLowerCase().includes('поиск') ||
            i.placeholder.toLowerCase().includes('search')
        )
    );
    if (searchInput) {
        searchInput.focus();
        searchInput.value = 'NAME_TO_SEARCH';
        searchInput.dispatchEvent(new Event('input', { bubbles: true }));
        searchInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true }));
        searchInput.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', bubbles: true }));
        return 'searched';
    }
    return 'no search input';
})()
"""
```

---

## Known Pitfalls

1. **Playwright `browser_navigate` fails with VK CDP** — use direct WebSocket approach above
2. **Target ID changes on every Chrome restart** — always re-query `Target.getTargets`
3. **Session ID from `attachToTarget`** — comes via `Target.attachedToTarget` event, not `result`
4. **VK search input** — typing + Enter may redirect to `vk.com/search?q=...` instead of filtering dialogs. Dialog click is more reliable.
5. **Scroll containers** — VK messenger uses nested scrollable divs, not `window.scroll`. Search for `scrollHeight > clientHeight` panels.
6. **Large screenshots** — Hermes `browser_cdp` may truncate >100KB responses. Use direct WebSocket file write.

---

## Session Log

- **May 2026:** Used to find "Анна Ступельman" in VK IM, open dialog, scroll to bottom, and screenshot last message (link to wfolio.pro). Screenshot sent via Telegram MEDIA:/tmp/vk_anna_bottom.png
- Chrome CDP on port 9223 after 9222 conflict. Profile at `/home/natan/.chrome-vk-profile`.
