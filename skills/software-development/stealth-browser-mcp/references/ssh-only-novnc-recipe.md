# SSH-only noVNC manual-login recipe

Use this reference when the user has **only SSH access** from their machine and no VNC client installed. The workflow is the same as `manual-login-vnc-novnc.md`, but the connection path is SSH tunnel + web browser.

## Connection path

On the user's machine:

```bash
ssh -L 6080:localhost:6080 user@server-ip
```

Then open in a local browser:

```
http://localhost:6080/vnc.html
```

Click **Connect** with an empty password (when `x11vnc` was started with `-nopw`).

## Typical error: "localhost sent an invalid response"

If the user sees:

```
Сайт localhost отправил недействительный ответ.
```

It means they opened `http://localhost:5900` or `https://localhost:6080` in the browser, or they connected to the raw VNC port instead of noVNC. Correct address is `http://localhost:6080/vnc.html` after the SSH tunnel is active.

## Safe shutdown after the manual step

Because the services were started as Hermes background processes, stop them by killing the specific processes rather than running `pkill` blindly:

```bash
# Find the sessions
hermes process list
# or
ps aux | grep -E 'x11vnc|websockify|Xvfb :99|chrome.*9223'

# Kill each service
kill <x11vnc-pid> <websockify-pid> <chrome-pid>
# Xvfb can be left running if you plan to reuse the display, otherwise kill it too.
```

If you used `terminal(background=true)` to start them, note down the returned `session_id`s and use `process(action="kill", session_id=...)` from Hermes, or call `process(action="list")` to see them.

## Security note

`-nopw` is convenient for a one-time manual step but leaves VNC open without authentication. Always:

1. Restrict `x11vnc` to localhost and tunnel through SSH (the recipe above does this).
2. Kill `x11vnc` and `websockify` immediately after the user finishes.
3. Do not leave Chrome running on `0.0.0.0` with `--remote-debugging-address=0.0.0.0` unless the firewall blocks external access.

## Full startup using Hermes background processes

```python
# 1. Xvfb
terminal(background=True, command="pkill -f 'Xvfb :99' || true; sleep 1; Xvfb :99 -screen 0 1920x1080x24 +extension GLX +render -noreset")

# 2. x11vnc (wait for Xvfb)
terminal(background=True, command="sleep 3; x11vnc -display :99 -forever -shared -nopw -rfbport 5900")

# 3. Chrome on the target site
terminal(background=True, command="export DISPLAY=:99; /opt/google/chrome/chrome --no-sandbox --disable-dev-shm-usage --disable-gpu --window-size=1920,1080 --start-maximized --remote-debugging-port=9223 https://example.com")

# 4. noVNC / websockify
terminal(background=True, command="pkill -f 'websockify.*6080' || true; sleep 1; websockify --web /usr/share/novnc --cert none --key none 6080 localhost:5900")
```

Wait a few seconds, verify:

```bash
ss -tlnp | grep -E '5900|6080'
curl -s -o /dev/null -w '%{http_code}' http://localhost:6080/vnc.html
```

Then give the user the SSH tunnel command and the `http://localhost:6080/vnc.html` URL.
