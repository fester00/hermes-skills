# Manual login fallback via VNC + noVNC

Use this recipe when browser automation hits an interactive blocker that only a human can pass: reCAPTCHA, SMS/OTP, 3-D Secure, biometric check, or a site that keeps the submit button disabled until a human gesture.

Instead of trying to bypass the protection, expose the same browser window to the user through a web-based VNC client. The user completes the step, then automation resumes.

## When to use this fallback

- Submit button stays `disabled` until reCAPTCHA is solved.
- Login requires SMS/OTP/TOTP from the user's phone.
- Bank confirmation / 3-D Secure flow opens.
- Anti-bot challenge defeats headless scripts.
- The site renders inside a cross-origin iframe that cannot be clicked from the parent document.

## Prerequisites

Install on the headless Linux server:

```bash
sudo apt update
sudo apt install -y xvfb x11vnc novnc websockify google-chrome-stable
```

## Start the GUI stack

### 1. Virtual display

```bash
pkill -f 'Xvfb :99' 2>/dev/null || true
Xvfb :99 -screen 0 1920x1080x24 +extension GLX +render -noreset &
sleep 2
```

### 2. VNC server (temporary, no password)

```bash
pkill -f 'x11vnc.*:99' 2>/dev/null || true
x11vnc -display :99 -forever -shared -nopw -rfbport 5900 &
sleep 2
```

Verify port 5900 is listening:

```bash
ss -tlnp | grep 5900
```

### 3. Chrome inside the virtual display

```bash
export DISPLAY=:99
/opt/google/chrome/chrome \
  --no-sandbox \
  --disable-dev-shm-usage \
  --disable-gpu \
  --window-size=1920,1080 \
  --start-maximized \
  --remote-debugging-port=9223 \
  https://site-to-auth.example.com
```

### 4. Web-based VNC client (noVNC)

```bash
pkill -f 'websockify.*6080' 2>/dev/null || true
websockify --web /usr/share/novnc --cert none --key none 6080 localhost:5900
```

Verify port 6080 returns HTTP 200:

```bash
curl -s -o /dev/null -w '%{http_code}' http://localhost:6080/vnc.html
```

## User connection

The user only needs an SSH client and a browser.

### SSH tunnel

On the user's machine:

```bash
ssh -L 6080:localhost:6080 user@server-ip
```

### Open noVNC

In the user's browser:

```
http://localhost:6080/vnc.html
```

Click **Connect**. Leave password empty. The user now sees the Chrome window and can complete the login / captcha / OTP step.

## Common mistakes

- **Opening `localhost:5900` in a web browser.** VNC is not HTTP. Use `:6080` for noVNC or a real VNC client for `:5900`.
- **Forgetting `export DISPLAY=:99`.** Chrome must run inside the virtual display created by Xvfb.
- **Running Chrome without `--no-sandbox` inside Docker/Xvfb.** It usually crashes unless sandboxing is explicitly disabled.
- **Leaving VNC open after the manual step.** Always shut down x11vnc/websockify when done.

## Security cleanup

After the user finishes:

```bash
pkill -f 'x11vnc.*:99'
pkill -f 'websockify.*6080'
pkill -f 'Xvfb :99'
pkill -f 'chrome --remote-debugging-port=9223'
```

If you need persistence, switch `-nopw` to a strong VNC password or restrict x11vnc to `localhost` and tunnel everything through SSH.

## Resume automation after manual login

Once the user is logged in, capture the session from the Chrome instance:

```javascript
// Run in the Chrome DevTools console or via CDP
JSON.stringify({
  cookies: document.cookie,
  localStorage: Object.entries(localStorage),
  sessionStorage: Object.entries(sessionStorage),
  url: location.href
})
```

Inject those values into the headless `stealth-browser` instance with `set_cookie` / `execute_script` to continue the automated workflow without re-authentication.

## Example: full one-liner startup

```bash
#!/bin/bash
set -e
pkill -f 'Xvfb :99' || true
pkill -f 'x11vnc.*:99' || true
pkill -f 'websockify.*6080' || true

Xvfb :99 -screen 0 1920x1080x24 +extension GLX +render -noreset &
sleep 2
x11vnc -display :99 -forever -shared -nopw -rfbport 5900 &
sleep 2

DISPLAY=:99 /opt/google/chrome/chrome \
  --no-sandbox --disable-dev-shm-usage --disable-gpu \
  --window-size=1920,1080 --start-maximized \
  https://site-to-auth.example.com &

websockify --web /usr/share/novnc --cert none --key none 6080 localhost:5900
```
