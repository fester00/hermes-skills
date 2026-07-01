# VK Automation via Raw CDP — Session-Tested Patterns

Reproducible Python/JS snippets for VK automation when Hermes Playwright layer fails. Extracted from working sessions on vk.com (IM, communities, marketplace).

---

## 1. Find VK Group ID from Community Page

```javascript
// In browser console on vk.com/pentajunior
(function() {
    const results = [];
    const scripts = Array.from(document.querySelectorAll('script'));
    for (const s of scripts) {
        if (s.textContent) {
            const m = s.textContent.match(/["']group_id["']\s*:\s*(\d+)/);
            if (m) results.push('group_id: ' + m[1]);
            const m2 = s.textContent.match(/club(\d+)/);
            if (m2) results.push('club: ' + m2[1]);
        }
    }
    const m3 = document.body.innerHTML.match(/club(\d+)/);
    if (m3) results.push('body club: ' + m3[1]);
    if (window.cur && window.cur.oid) results.push('cur.oid: ' + window.cur.oid);
    return results.length ? results.join('; ') : 'no ID found';
})()
```

**Usage:** Navigate to `https://vk.com/GROUP_SHORTNAME`, run the script, extract the numeric ID. Then use it for marketplace URLs: `https://vk.com/market-{GROUP_ID}`.

---

## 2. Scroll-Screenshot Workflow for Lazy-Loaded Pages

VK product catalogs use infinite scroll. Single screenshot only captures the first viewport.

```python
import websocket, json, base64, time

ws_url = "ws://127.0.0.1:9223/devtools/browser/<UUID>"
target_id = "PAGE_TARGET_ID"

def scroll_and_capture(ws_url, target_id, scroll_count=5, scroll_step=800):
    ws = websocket.create_connection(ws_url)
    
    # Attach
    ws.send(json.dumps({"id":1,"method":"Target.attachToTarget",
        "params":{"flatten":True,"targetId":target_id}}))
    session_id = None
    for _ in range(10):
        msg = json.loads(ws.recv())
        if msg.get("method") == "Target.attachedToTarget":
            session_id = msg["params"]["sessionId"]
            break
    
    paths = []
    for i in range(scroll_count):
        # Scroll
        ws.send(json.dumps({"id":10+i,"method":"Runtime.evaluate",
            "params":{"expression":f"window.scrollTo(0, {i * scroll_step});"},
            "sessionId":session_id}))
        time.sleep(1)
        
        # Screenshot
        ws.send(json.dumps({"id":20+i,"method":"Page.captureScreenshot",
            "params":{"format":"png","fromSurface":True},
            "sessionId":session_id}))
        for _ in range(5):
            msg = json.loads(ws.recv())
            if msg.get("id") == 20+i:
                data = msg["result"]["result"]["data"]
                path = f"/tmp/screenshot_{i}.png"
                with open(path, "wb") as f:
                    f.write(base64.b64decode(data))
                paths.append(path)
                break
    
    ws.close()
    return paths
```

---

## 3. Extract Table Data from DOM

For pages with pricing tables (e.g. `pentajunior.ru/price`):

```javascript
// In browser console
(function() {
    const rows = document.querySelectorAll('table tr');
    const data = [];
    let currentName = '';
    for (const row of rows) {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 3) {
            const name = cells[0].textContent.trim();
            const volume = cells[1].textContent.trim();
            const price = cells[2].textContent.trim();
            if (name) currentName = name;
            data.push({name: currentName, volume, price, hasName: !!name});
        }
    }
    return data;
})()
```

**Pitfall:** Some table rows omit the name cell (continuation rows for the same product with different volumes). Always carry `currentName` forward across empty-name rows.

---

## 4. Click Element by Exact Text Match

When element selectors are dynamic (VK uses obfuscated class names), match by visible text:

```javascript
// Click by exact text match, walking up the DOM tree
(function(text) {
    const els = document.querySelectorAll('*');
    for (const el of els) {
        if (el.textContent && el.textContent.trim() === text) {
            let node = el;
            for (let i = 0; i < 15; i++) {
                if (node.tagName === 'A' || node.getAttribute('href') || 
                    node.getAttribute('role') === 'button' || 
                    node.getAttribute('role') === 'tab') {
                    node.click();
                    return 'Clicked ' + node.tagName + ' with href=' + (node.getAttribute('href') || 'none');
                }
                node = node.parentElement;
                if (!node) break;
            }
        }
    }
    return text + ' not found';
})('Товары')
```

**Pitfall:** VK sidebar links may be wrapped in `<li>` or `<ol>` — walking up 10-15 levels is necessary.

---

## 5. Full VK IM Dialog Screenshot (Messenger)

```python
import websocket, json, base64, time

ws_url = "ws://127.0.0.1:9223/devtools/browser/<UUID>"
target_id = "VK_PAGE_TARGET_ID"

ws = websocket.create_connection(ws_url)

# Attach
ws.send(json.dumps({"id":1,"method":"Target.attachToTarget",
    "params":{"flatten":True,"targetId":target_id}}))
session_id = None
for _ in range(10):
    msg = json.loads(ws.recv())
    if msg.get("method") == "Target.attachedToTarget":
        session_id = msg["params"]["sessionId"]
        break

# Navigate to IM
ws.send(json.dumps({"id":2,"method":"Page.navigate",
    "params":{"url":"https://vk.com/im"},"sessionId":session_id}))
time.sleep(4)

# Search for dialog by name
search_js = """
(function() {
    const inputs = Array.from(document.querySelectorAll('input'));
    const searchInput = inputs.find(i => i.placeholder && 
        (i.placeholder.toLowerCase().includes('поиск') || 
         i.placeholder.toLowerCase().includes('search')));
    if (searchInput) {
        searchInput.focus();
        searchInput.value = 'Анна Ступельман';
        searchInput.dispatchEvent(new Event('input', { bubbles: true }));
        searchInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true }));
        searchInput.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', bubbles: true }));
        return 'Search triggered';
    }
    return 'No search input found';
})()
"""
ws.send(json.dumps({"id":3,"method":"Runtime.evaluate",
    "params":{"expression":search_js,"returnByValue":True},
    "sessionId":session_id}))
time.sleep(3)

# Click dialog by text match
click_js = """
(function(name) {
    const els = document.querySelectorAll('*');
    for (const el of els) {
        if (el.textContent && el.textContent.trim() === name) {
            let node = el;
            for (let i = 0; i < 10; i++) {
                if (node.click) { node.click(); return 'clicked ' + name; }
                node = node.parentElement;
                if (!node) break;
            }
        }
    }
    return name + ' not found';
})('Анна Ступельман')
"""
ws.send(json.dumps({"id":4,"method":"Runtime.evaluate",
    "params":{"expression":click_js,"returnByValue":True},
    "sessionId":session_id}))
time.sleep(3)

# Screenshot
ws.send(json.dumps({"id":5,"method":"Page.captureScreenshot",
    "params":{"format":"png","fromSurface":True},
    "sessionId":session_id}))
for _ in range(5):
    msg = json.loads(ws.recv())
    if msg.get("id") == 5:
        data = msg["result"]["result"]["data"]
        with open("/tmp/vk_dialog.png", "wb") as f:
            f.write(base64.b64decode(data))
        break

ws.close()
```

---

## Pitfalls Summary

| Problem | Cause | Solution |
|---------|-------|----------|
| `browser_navigate` 404 | Stale `cdp_url` in config | Update via `curl` + `hermes config set` |
| Port 9222 conflicts | Another Chrome instance | Use port 9223, update config |
| `Target.attachToTarget` returns event not result | CDP protocol quirk | Listen for `Target.attachedToTarget` event |
| VK product cards not found by class name | Obfuscated dynamic classes | Use text-match or `browser_vision` on scroll screenshots |
| Table continuation rows missing name | Empty `<td>` for repeated product | Carry `currentName` variable across rows |
