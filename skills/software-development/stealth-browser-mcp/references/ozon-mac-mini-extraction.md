# Ozon Mac mini extraction recipe

Verified working recipe for extracting Mac mini product cards from Ozon search results using the `stealth-browser-mcp` server.

## Context

- Server: `stealth-browser-mcp` at `/mnt/data/natan-storage/stealth-browser-mcp`
- Transport: stdio via `mcp.client.stdio` from `execute_code`
- Browser: Chrome via `nodriver`, `headless=False`, wrapped in `xvfb-run`
- Profile: `/mnt/data/natan-storage/.chrome-vk-profile` (optional)
- Search URL: `https://www.ozon.ru/search/?text=Mac+mini&from_global=true`

## Verified environment

```python
import asyncio
import json
import os
import sys
import base64

sys.path.insert(0, '/mnt/data/natan-storage/stealth-browser-mcp/.venv/lib/python3.12/site-packages')
os.environ['PATH'] = '/mnt/data/natan-storage/stealth-browser-mcp/.venv/bin:' + os.environ.get('PATH', '')
os.environ['PYTHONPATH'] = '/mnt/data/natan-storage/stealth-browser-mcp/src'

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
```

## Server launch under Xvfb

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

## Helper to call tools and parse JSON

```python
async def call_tool(session, name, args):
    result = await session.call_tool(name, arguments=args)
    text = ''.join(c.text for c in result.content if hasattr(c, 'text'))
    try:
        return json.loads(text)
    except Exception:
        return text
```

## Open Ozon and wait for render

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

await call_tool(session, 'navigate', {
    'instance_id': instance_id,
    'url': 'https://www.ozon.ru/search/?text=Mac+mini&from_global=true',
    'wait_until': 'networkidle',
    'timeout': 60000,
})
await asyncio.sleep(8)  # Ozon renders tiles after networkidle
```

Note: Ozon may redirect the search URL to a category page. The actual URL observed was:
`https://www.ozon.ru/category/mini-pk-15705/apple-26303000/?brand_was_predicted=true&category_was_predicted=true&deny_category_prediction=true&from_global=true&text=Mac+mini`.
This is normal; the extraction script still works on the rendered tiles.

## Screenshot

```python
screenshot_res = await call_tool(session, 'take_screenshot', {
    'instance_id': instance_id,
    'full_page': False,
})
if isinstance(screenshot_res, dict) and screenshot_res.get('screenshot'):
    img_path = '/mnt/data/natan-storage/tmp/ozon_mac_mini.png'
    with open(img_path, 'wb') as f:
        f.write(base64.b64decode(screenshot_res['screenshot']))
    print('Screenshot saved to', img_path)
```

## Extraction script

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

Execute via MCP:

```python
script_res = await call_tool(session, 'execute_script', {
    'instance_id': instance_id,
    'script': script,
})
```

## Parse CDP deep-serialized result

```python
def parse_cdp_object(obj):
    if isinstance(obj, list):
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

products = [parse_cdp_object(item) for item in script_res['result']]
for p in products:
    print(p['title'], p['price'], p['link'])
```

## Sample output

```
Apple Мини-ПК (Apple M4 Pro, RAM 24 ГБ, SSD 512 ГБ, Apple M4 Pro, macOS), серебристый — 153 492 ₽
Apple Мини-ПК Apple Mac Mini host M4 (10 ядер+10 ядер) ... — 66 848 ₽
Apple Мини-ПК Mac Mini M4 (Apple M4, RAM 16 ГБ, SSD 256 ГБ, ...), MU9D3 — 72 560 ₽
```

## Cleanup

```python
await call_tool(session, 'close_instance', {'instance_id': instance_id})
```

## Notes

- `wait_until='load'` returns too early; use `networkidle` plus an explicit sleep.
- `execute_script` accepts only `instance_id`, `script`, and optional `args`.
- `get_page_content` is unreliable as a primary extraction source because it may snapshot `chrome://new-tab-page/` if called too early.
- Screenshot is the fastest way to visually verify that Ozon tiles rendered.
