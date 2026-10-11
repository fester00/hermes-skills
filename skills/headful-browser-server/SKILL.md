---
name: headful-browser-server
description: Use when manual login is required on a headless server. Run headed Chrome over VNC/noVNC for the user to auth.
category: software-development
related_skills:
  - browser-automation
  - browser-use-agent
---

# Headful Browser Server

Run a real headed Chrome instance on a headless Linux server and expose its display over VNC or noVNC so the user can log in manually. Use this when browser automation needs a logged-in session, but the agent cannot or must not type one-time codes, passwords, or 2FA responses.

## When to use

- A website requires login via QR code, SMS/in-app code, or 2FA that the agent cannot complete.
- A persistent Chrome profile exists and must remain writable across restarts.
- The server has no physical display, so a virtual framebuffer (Xvfb) is required.
- The user is willing to connect to a remote desktop and perform the final auth step themselves.

## Core stack

| Component | Purpose | On this server |
|-----------|---------|----------------|
| `Xvfb` | Virtual display for Chrome | `/usr/bin/Xvfb` |
| `google-chrome` | Headed browser with persistent profile | `/usr/bin/google-chrome` |
| `x11vnc` | Raw-RFB VNC server for direct viewer access | `/usr/bin/x11vnc` |
| `websockify` + `noVNC` | Browser-based VNC access (optional) | Install if needed |
| CDP port | Programmatic screenshots / verification | `--remote-debugging-port=9223` |

## Minimal working launch

```bash
#!/bin/bash
export DISPLAY=:42

rm -f /tmp/xvfb-42.Xauthority
Xvfb :42 -screen 0 1920x1080x24 -nolisten tcp -auth /tmp/xvfb-42.Xauthority &
sleep 2

x11vnc -display :42 -rfbport 5942 -noxdamage -noxkb -nopw -forever -shared -auth /tmp/xvfb-42.Xauthority &
sleep 2

google-chrome \
  --no-sandbox --disable-setuid-sandbox \
  --disable-gpu --disable-dev-shm-usage \
  --disable-blink-features=AutomationControlled \
  --user-data-dir=/mnt/data/natan-storage/.chrome-vk-profile \
  --window-size=1920,1080 --start-fullscreen \
  --remote-debugging-port=9223 --remote-allow-origins='*' \
  https://web.telegram.org/k/ &
```

Verify CDP is alive:

```bash
curl -s http://127.0.0.1:9223/json/version
```

Verify VNC is listening:

```bash
ss -ltnp | grep 5942
```

## Connecting the user

### Direct VNC (fastest)

- **Host:** `<server-lan-ip>:5942` (e.g. `192.168.0.98:5942`)
- **Password:** none (`-nopw`)
- **Client:** real VNC viewer — TightVNC, TigerVNC, RealVNC, Remmina, bVNC, etc.

**Pitfall:** `x11vnc` speaks raw RFB. Browser-based "VNC clients" and WebSocket bookmarklets will fail with `not a valid RFB client` or `unknown connection error`. Use a native viewer, or add `websockify` for browser access.

### Browser-based VNC (no native client)

Use `websockify` in front of `x11vnc`, plus `noVNC`:

```bash
# x11vnc can bind to localhost only; websockify bridges to browser WebSocket
x11vnc -display :42 -rfbport 5901 -nopw -forever -shared -localhost
websockify --web /usr/share/novnc 6080 localhost:5901
```

Then open `http://<server>:6080/vnc.html`.

## Agent responsibilities and boundaries

1. **Start the stack**, navigate the site, and (if needed) enter only non-sensitive identifiers such as the phone number.
2. **Capture screenshots** via CDP to verify the UI state and send clean images to the user.
3. **Never accept or type one-time access codes** (SMS, in-app codes like Telegram's `70790`, TOTP, PINs, passwords). If the app shows a "Confirm login" button, ask the user to press it on the phone.
4. If the app only shows digits, provide a remote GUI (VNC/noVNC) so the user types the code directly into the browser.
5. After login, **stop the stack** when the user is done, to free resources and reduce attack surface:
   ```bash
   pkill -f 'x11vnc.*5942'
   pkill -f 'google-chrome.*user-data-dir=/mnt/data/natan-storage/.chrome-vk-profile'
   pkill -f 'Xvfb :42'
   ```

## CDP-only screenshot helper

Save a screenshot directly to a file without relying on the agent tool's truncation limits:

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

# asyncio.run(screenshot())
```

## Common pitfalls

- **Chrome crashes with `Missing X server or $DISPLAY`:** Xvfb was not started, or `DISPLAY` was not exported before Chrome launched.
- **CDP returns `403 Forbidden`:** omit `--remote-allow-origins='*'`; Chrome rejects WebSocket origins by default.
- **Profile changes are lost:** verify `--user-data-dir` points to a persistent path, not `/tmp`.
- **VNC connection drops immediately:** the client is trying WebSocket/HTTP, not RFB. Use a native VNC viewer or add websockify.
- **QR code expires before scanning:** refresh the page and capture a new screenshot.
- **Phone-code login without remote GUI:** the agent can enter the phone number, but the final confirmation must happen on the user's device or via VNC.

## References

- `references/remote-vnc-login-recipe.md` — Copy-paste commands for the Telegram Web / x11vnc scenario from this environment.
- `browser-automation` skill — CDP recipes, iframe handling, and extraction patterns.
- `browser-use-agent` skill — LLM-driven browser agent with persistent profile.
