---
name: stealth-browser-mcp
description: Use when anti-bot systems block Playwright or browser-use and deterministic script control is required.
category: software-development
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [browser-automation, mcp, anti-bot, nodriver]
    related_skills:
      - browser-use-agent
      - browser-automation
      - native-mcp
---

# stealth-browser-mcp

Use the local `stealth-browser-mcp` server as a Hermes-accessible browser-automation tool. It drives a real Chrome instance through `nodriver` (undetected CDP wrapper), which is useful when anti-bot systems block `browser-use` or Playwright headless modes.

## When to use

- `browser-use`/`Playwright` headless is blocked by Ozon, Yandex Market, or similar anti-bot systems.
- You need deterministic, scriptable browser control rather than LLM-driven reasoning.
- You want to extract structured data from a page after a real browser has rendered it.
- You have `stealth-browser-mcp` installed locally at `/mnt/data/natan-storage/stealth-browser-mcp`.

## Setup

Environment is already installed:

```bash
cd /mnt/data/natan-storage/stealth-browser-mcp
source .venv/bin/activate
```

Server entry point: `src/server.py`.
Persistent Chrome profile (optional): `/mnt/data/natan-storage/.chrome-vk-profile`.

## Hermes auto-discovery config

Add to `/mnt/data/natan-storage/.hermes/config.yaml` under `mcp.servers`:

```yaml
mcp:
  servers:
    stealth-browser:
      command: python
      args:
        - /mnt/data/natan-storage/stealth-browser-mcp/src/server.py
      env:
        PYTHONPATH: /mnt/data/natan-storage/stealth-browser-mcp/src
```

Also raise the discovery timeout if the server is slow to start. For a browser MCP that must launch Chrome under xvfb, 30 seconds is safer than the default:

```yaml
mcp_discovery_timeout: 30
```

Pitfall: a config with only `args` and no `command` will not register tools. Hermes' filtered PATH may also fail to resolve `python`; use an absolute path to the venv interpreter if needed:

```yaml
command: /mnt/data/natan-storage/stealth-browser-mcp/.venv/bin/python
```

### Wrapper script for headless=False servers

If you want `headless=False` (less bot fingerprint) on a headless Linux host, the MCP server itself must run under Xvfb. The cleanest Hermes config points `command` at a wrapper script instead of inlining `xvfb-run` args:

```bash
#!/bin/bash
# /mnt/data/natan-storage/stealth-browser-mcp/run_mcp_server.sh
set -e
export PATH="/mnt/data/natan-storage/stealth-browser-mcp/.venv/bin:${PATH}"
export PYTHONPATH="/mnt/data/natan-storage/stealth-browser-mcp/src"
exec xvfb-run -a --server-args="-screen 0 1920x1080x24" \
    python /mnt/data/natan-storage/stealth-browser-mcp/src/server.py
```

```yaml
mcp:
  servers:
    stealth-browser:
      command: /mnt/data/natan-storage/stealth-browser-mcp/run_mcp_server.sh
      connect_timeout: 30
```

Register via CLI (non-interactive; the command has prompts):

```bash
yes | HERMES_ACCEPT_HOOKS=1 \
  hermes mcp add stealth-browser \
  --command /mnt/data/natan-storage/stealth-browser-mcp/run_mcp_server.sh \
  --connect-timeout 30
```

Verify:

```bash
hermes mcp test stealth-browser
```

Pitfall: after `hermes mcp add` or any MCP config change, tools do not appear in the current session. Start a new Hermes session (`/reset` or new chat) for `mcp_stealth_browser_*` tools to register.

## Manual stdio_client launch pattern

If Hermes did not auto-discover the server, connect manually from `execute_code`:

```python
import asyncio
import json
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

sys.path.insert(0, '/mnt/data/natan-storage/stealth-browser-mcp/.venv/lib/python3.12/site-packages')
os.environ['PATH'] = '/mnt/data/natan-storage/stealth-browser-mcp/.venv/bin:' + os.environ.get('PATH', '')
os.environ['PYTHONPATH'] = '/mnt/data/natan-storage/stealth-browser-mcp/src'

async def call_tool(session, name, args):
    result = await session.call_tool(name, arguments=args)
    text = ''.join(c.text for c in result.content if hasattr(c, 'text'))
    try:
        return json.loads(text)
    except Exception:
        return text

async def main():
    server_params = StdioServerParameters(
        command='python',
        args=['/mnt/data/natan-storage/stealth-browser-mcp/src/server.py'],
        env={'PYTHONPATH': '/mnt/data/natan-storage/stealth-browser-mcp/src'},
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f'Tools available: {len(tools.tools)}')

asyncio.run(main())
```

## Headless=False on a server: wrap with Xvfb

`nodriver` with `headless=False` requires a display. On a headless Linux server, launch the MCP server under `xvfb-run`:

```bash
xvfb-run -a --server-args="-screen 0 1920x1080x24" python src/server.py
```

From `execute_code` set `command='xvfb-run'` and include the Xvfb server args before `python`:

```python
server_params = StdioServerParameters(
    command='xvfb-run',
    args=[
        '-a',
        '--server-args=-screen 0 1920x1080x24',
        'python',
        '/mnt/data/natan-storage/stealth-browser-mcp/src/server.py',
    ],
    env={'PYTHONPATH': '/mnt/data/natan-storage/stealth-browser-mcp/src'},
)
```

## spawn_browser

Typical Ozon-ready invocation:

```python
spawn_res = await call_tool(session, 'spawn_browser', {
    'headless': False,
    'viewport_width': 1920,
    'viewport_height': 1080,
    'sandbox': False,
    'browser_args': [
        '--disable-gpu',
        '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled',
    ],
    'user_data_dir': '/mnt/data/natan-storage/.chrome-vk-profile',
})
instance_id = spawn_res['instance_id']
```

Pitfall: `sandbox=False` alone is not enough if `headless=False` and no display exists. The misleading nodriver error "pass no_sandbox=True" actually means Chrome could not start; wrap the server in `xvfb-run`.

## navigate

Ozon search results render after network activity. Use `wait_until='networkidle'` and an additional sleep before extraction:

```python
await call_tool(session, 'navigate', {
    'instance_id': instance_id,
    'url': 'https://www.ozon.ru/search/?text=Mac+mini&from_global=true',
    'wait_until': 'networkidle',
    'timeout': 60000,
})
await asyncio.sleep(8)
```

Pitfall: `wait_until='load'` returns immediately while the page is still `chrome://new-tab-page/`. Always wait for networkidle plus a short render pause for Ozon.

## execute_script

Signature is `instance_id`, `script`, `args`. There is **no** `return_by_value` parameter.

```python
result = await call_tool(session, 'execute_script', {
    'instance_id': instance_id,
    'script': 'return {url: window.location.href, title: document.title};',
})
```

Complex objects are returned in CDP deep-serialized format: `{'type': 'object', 'value': [['key', {'type': 'string', 'value': '...'}], ...]}`.

## Extracting Ozon product cards

A robust selector strategy for Ozon search results is documented in `references/ozon-mac-mini-extraction.md`. The core idea:

```javascript
(function() {
    const out = [];
    const seen = new Set();
    document.querySelectorAll('a[href*="/product/"]').forEach(a => {
        const title = a.innerText.trim();
        if (title && title.toLowerCase().includes('mac') && !seen.has(a.href)) {
            seen.add(a.href);
            const container = a.closest('div[class*="tile"], div[class*="a0c4"]') || a.parentElement.parentElement;
            const priceEl = container ? container.querySelector('[class*="price"], span[class*="c3024"], span[class*="tsHeadline500"]') : null;
            out.push({
                title: title.slice(0, 200),
                link: a.href,
                price: priceEl ? priceEl.innerText.trim().replace(/\s+/g, ' ') : ''
            });
        }
        if (out.length >= 8) return;
    });
    return out.slice(0, 8);
})()
```

See `references/ozon-mac-mini-extraction.md` for a full working script and CDP-result parser.

## Parsing CDP deep-serialized results

```python
def parse_cdp_object(obj):
    """Recursively convert CDP Runtime.deepSerializedValue to plain Python."""
    if isinstance(obj, list):
        # list of [key, value] pairs => dict
        if obj and isinstance(obj[0], list) and len(obj[0]) == 2 and isinstance(obj[0][0], str):
            return {k: parse_cdp_object(v) for k, v in obj}
        return [parse_cdp_object(x) for x in obj]
    if isinstance(obj, dict):
        if obj.get('type') == 'string':
            return obj.get('value')
        if obj.get('type') == 'number':
            return obj.get('value')
        if obj.get('type') == 'boolean':
            return obj.get('value')
        if obj.get('type') == 'null':
            return None
        if obj.get('type') == 'undefined':
            return None
        if obj.get('type') == 'object' and 'value' in obj:
            return parse_cdp_object(obj['value'])
        if obj.get('type') == 'array' and 'value' in obj:
            return [parse_cdp_object(x) for x in obj['value']]
        return {k: parse_cdp_object(v) for k, v in obj.items()}
    return obj
```

## Common tools

| Tool | Use |
|---|---|
| `spawn_browser` | Start Chrome instance |
| `close_instance` | Clean up |
| `navigate` | Load a URL |
| `execute_script` | Run JS and get data |
| `get_page_content` | HTML/text (returns file path if too large) |
| `take_screenshot` | PNG as base64 |
| `query_elements` / `click_element` / `type_text` | DOM interaction |
| `list_network_requests` | Inspect network |
| `set_cookie` | Inject a recovered session cookie (domain + name + value + secure + httpOnly) |
| `get_cookies` | Read cookies from the current page |

## Session recovery from a real Chrome profile

After a user logs in through the VNC-assisted Chrome, you can move that session into a headless `stealth-browser` instance for automation.

### 1. Decrypt cookies from the real Chrome profile

On Linux, Chrome encrypts cookie values. Use `browser-cookie3` to read them in plain text:

```bash
python3 -m pip install browser-cookie3
```

```python
import browser_cookie3, json, os

profile_dir = os.path.expanduser('~/.config/google-chrome')
cj = browser_cookie3.chrome(domain_name='example.com', cookie_file=f'{profile_dir}/Default/Cookies')

cookies = []
for c in cj:
    if 'example.com' in c.domain:
        cookies.append({
            'domain': c.domain,
            'name': c.name,
            'value': c.value,
            'path': c.path,
            'secure': c.secure,
            'httpOnly': bool(c.get_nonstandard_attr('HttpOnly')),
            'expires': c.expires,
        })

os.makedirs('/tmp/session-recovery', exist_ok=True)
with open('/tmp/session-recovery/cookies.json', 'w') as f:
    json.dump(cookies, f, indent=2, ensure_ascii=False)

print(f'Saved {len(cookies)} cookies')
```

Pitfall: the profile must not be locked by another running Chrome process. If Chrome is still running, copy the `Cookies` SQLite file first, then point `browser-cookie3` at the copy.

### 2. Inject cookies into the stealth-browser instance

Navigate to the target site **first** so the cookie domain is valid, then use `set_cookie` for the session cookies:

```python
await call_tool(session, 'navigate', {
    'instance_id': instance_id,
    'url': 'https://example.com',
    'wait_until': 'networkidle',
})

for c in cookies:
    if c['name'] in ('session', 'session_id', 'auth_token', 'csrf_token'):
        await call_tool(session, 'set_cookie', {
            'instance_id': instance_id,
            'url': 'https://example.com',
            'domain': c['domain'],
            'name': c['name'],
            'value': c['value'],
            'path': c['path'],
            'secure': c['secure'],
            'http_only': c['httpOnly'],
        })

await call_tool(session, 'reload_page', {'instance_id': instance_id})
```

### 3. Verify auth state

Do not rely on the page title alone. Check for user-specific UI:

```python
result = await call_tool(session, 'execute_script', {
    'instance_id': instance_id,
    'script': '(() => ({ hasLoginBtn: !!document.querySelector("button").textContent.match(/вход|войти|login/i), userMenu: !!document.querySelector("[class*=user], [class*=profile], [class*=balance]"), url: location.href, title: document.title }))()',
})
```

## Why headless cookie recovery sometimes fails

Even with valid session cookies, the headless instance may not be recognized as logged in. Common reasons:

1. **Fingerprint mismatch** — the real browser and headless Chrome differ in user-agent, WebGL/Canvas fingerprint, screen size, timezone, or language. Try to mirror the real profile:
   - same `viewport_width`/`viewport_height`,
   - same `user_agent`,
   - same `user_data_dir` (if you can point both browsers at the same profile),
   - same `timezone_id` and `extra_headers`.

2. **IP/device binding** — the site tied the session to the real browser's IP, TLS fingerprint, or device ID. A new headless instance from the same machine may still look like a new device.

3. **reCAPTCHA / anti-bot binding** — the session token is only issued after the challenge was solved in the real browser. The headless browser inherits the cookie but not the "human-verified" context, so protected buttons stay disabled.

When cookie injection fails, the fallback is to keep using the **real Chrome instance** (the one the user logged into via VNC) and control it through CDP or continue in it directly. Do not try to bypass the anti-bot challenge automatically.

### Keeping the real Chrome instance alive

If you need the logged-in session for automation, do not kill the VNC Chrome. Instead, connect to it via CDP on the port you launched it with (`--remote-debugging-port=9223`), or continue issuing `execute_script` calls against it if you already have its `instance_id`.

## Clicking when `is_clickable` looks false

`query_elements` often returns `is_clickable: false` for perfectly clickable links, especially in headless mode. Use `execute_script` with a JavaScript `.click()` call rather than giving up. See `references/clicking-when-query-elements-says-not-clickable.md` for a complete worked example including verification after the click.

## Pitfalls

- **Auto-discovery fails silently**: if tools do not appear in `tool_search`, check `command` in `mcp.servers` and raise `mcp_discovery_timeout`.
- **Headless=False needs a display**: wrap the server process in `xvfb-run` on headless Linux.
- **Ozon needs networkidle**: `load` is not enough; wait for networkidle + render pause.
- **`execute_script` has no `return_by_value`**: pass only `instance_id`, `script`, optional `args`.
- **Results are CDP-serialized**: parse `{'type': ..., 'value': ...}` wrappers before use.
- **Do not rely on `get_page_content` timing alone**: it may snapshot `chrome://new-tab-page/` if called too early.

## Handling interactive blockers (reCAPTCHA, OTP, 3-D Secure)

Anti-bot systems and login flows sometimes require a real human gesture:

- reCAPTCHA keeps the submit button `disabled`.
- Login needs SMS/OTP/TOTP from the user's device.
- Bank confirmation or 3-D Secure appears.
- A cross-origin iframe cannot be clicked from the parent document.

When this happens, do not try to bypass the challenge automatically. Instead, expose the same browser window to the user through VNC + noVNC so they can complete the step manually, then return control to automation.

See `references/manual-login-vnc-novnc.md` for the full recipe:
- start `Xvfb` + `x11vnc` + Chrome on the server,
- expose it via `websockify`/`noVNC` on port 6080,
- user connects with `ssh -L 6080:localhost:6080 user@server-ip` and opens `http://localhost:6080/vnc.html`,
- capture cookies/localStorage after login and inject them back into the headless automation instance.

Always shut down x11vnc/websockify/Xvfb after the manual step to avoid leaving an open VNC port.

## See also

- `browser-use-agent` — LLM-driven alternative using the same persistent profile.
- `browser-automation` — CDP/Playwright recipes.
- `native-mcp` — Hermes MCP client configuration reference.
- `references/ozon-mac-mini-extraction.md` — complete Ozon search extraction recipe.
- `references/manual-login-vnc-novnc.md` — manual login fallback for blocked automation flows.
- `references/ssh-only-novnc-recipe.md` — same fallback when the user has only SSH and no VNC client.
