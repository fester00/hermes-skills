# Remote VNC Login Recipe

Concrete copy-paste recipe for running a headed Chrome on the headless Ubuntu server and letting the user log in manually via VNC.

## Environment on this server

- `Xvfb` at `/usr/bin/Xvfb`
- `x11vnc` at `/usr/bin/x11vnc`
- `google-chrome` at `/usr/bin/google-chrome`
- Persistent profile: `/mnt/data/natan-storage/.chrome-vk-profile`
- Verified LAN IP example: `192.168.0.98`

## Start script

Save as `/tmp/start_vnc_browser.sh` and run:

```bash
#!/bin/bash
export DISPLAY=:42

# clean stale auth file
rm -f /tmp/xvfb-42.Xauthority

# 1. virtual display
Xvfb :42 -screen 0 1920x1080x24 -nolisten tcp -auth /tmp/xvfb-42.Xauthority &
sleep 2

# 2. VNC server (raw RFB, not WebSocket)
x11vnc -display :42 -rfbport 5942 -noxdamage -noxkb -nopw -forever -shared -auth /tmp/xvfb-42.Xauthority &
sleep 2

# 3. Chrome on the virtual display, with CDP for screenshots
google-chrome \
  --no-sandbox --disable-setuid-sandbox \
  --disable-gpu --disable-dev-shm-usage \
  --disable-blink-features=AutomationControlled \
  --user-data-dir=/mnt/data/natan-storage/.chrome-vk-profile \
  --window-size=1920,1080 --start-fullscreen \
  --remote-debugging-port=9223 --remote-allow-origins='*' \
  https://web.telegram.org/k/ &

echo "VNC:  <server-ip>:5942"
echo "CDP:  http://127.0.0.1:9223/json/version"
```

## Verify

```bash
ss -ltnp | grep -E '5942|9223'
curl -s http://127.0.0.1:9223/json/version | grep webSocketDebuggerUrl
```

## CDP screenshot to file

```python
import asyncio, aiohttp, json, base64
from pathlib import Path

async def screenshot(port=9223, path='/tmp/vnc_screen.png'):
    async with aiohttp.ClientSession() as s:
        r = await s.get(f'http://127.0.0.1:{port}/json/list')
        pages = await r.json()
        ws_url = [p for p in pages if p['type'] == 'page'][0]['webSocketDebuggerUrl']
        async with s.ws_connect(ws_url) as ws:
            await ws.send_str(json.dumps({'id': 1, 'method': 'Page.captureScreenshot'}))
            async for msg in ws:
                data = json.loads(msg.data)
                if data.get('id') == 1:
                    Path(path).write_bytes(base64.b64decode(data['result']['data']))
                    return path
```

## Stop everything

```bash
pkill -f 'x11vnc.*5942'
pkill -f 'google-chrome.*user-data-dir=/mnt/data/natan-storage/.chrome-vk-profile'
pkill -f 'Xvfb :42'
```

## Notes from verified use

- Telegram Web phone-number form uses `contenteditable` divs with class `input-field-input`, not real `<input>` elements. Use Playwright/CDP to click and type, or let the user type via VNC.
- Telegram Web sends the confirmation code as an in-app message; the mobile app usually offers a "Confirm login" button.
- If the user can only see digits, they must type them directly in the browser — the agent does not type one-time access codes.
