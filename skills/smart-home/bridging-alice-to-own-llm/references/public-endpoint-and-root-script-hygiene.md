# Publishing the webhook & authoring the root-run setup script

Depth for the deployment half of a speaker bridge: making the endpoint publicly
reachable without breaking the machine, and handing the privileged part to the user
safely.

## 1. The localhost-proxy trap

**Symptom:** every call to the local model endpoint dies after the full timeout with an
**empty** error message. The service looks connected and never answers. Nothing in the
error names a proxy.

**Cause:** `HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY` are honoured *by default* by httpx
and by curl. A request to `127.0.0.1:<port>` is then routed to the proxy — even when the
proxy itself listens on 127.0.0.1 — and the response never comes back.

Diagnose in one shot:

```bash
env | grep -i proxy        # is a proxy even present in this shell?
python3 - <<'PY'
import httpx, time
for trust in (True, False):
    t0 = time.perf_counter()
    try:
        r = httpx.get("http://127.0.0.1:11434/v1/models", timeout=6, trust_env=trust)
        print(f"trust_env={trust} -> HTTP {r.status_code} in {time.perf_counter()-t0:.2f}s")
    except Exception as e:
        print(f"trust_env={trust} -> {type(e).__name__} in {time.perf_counter()-t0:.2f}s: {e}")
PY
```

Typical result: `True` → ReadTimeout after the whole 6 s; `False` → HTTP 200 in ~0.03 s.

**Fixes**
- httpx: `httpx.AsyncClient(timeout=..., trust_env=False)`.
- curl: `curl --noproxy '*' ...` on every local check (shell proxies apply otherwise).
- Do not "fix" it by unsetting the proxies globally — other tooling on the box may need them.

**Regression test that keeps it fixed** (no network, no fixtures):

```python
import http.server, json, threading, httpx, pytest

@pytest.mark.asyncio
async def test_client_ignores_env_proxies(monkeypatch):
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            self.rfile.read(int(self.headers["Content-Length"]))
            body = json.dumps({"choices": [{"message": {"content": "local"}}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:9")
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:9")
    monkeypatch.setenv("ALL_PROXY", "http://127.0.0.1:9")
    try:
        client = YourClient(f"http://127.0.0.1:{srv.server_port}/v1")   # must set trust_env=False
        assert await client.call("hi") == "local"
    finally:
        srv.shutdown()
```

## 2. Authoring the root-run setup script

The agent cannot answer a sudo password prompt, so every privileged step becomes a script
the **user** runs in their own terminal. Rules that keep that hand-off from damaging the box:

1. **Never put flags or wildcards inside a shell variable.**
   `CURL="curl -fsSL --noproxy *"` followed by `$CURL <url>` expands `*` to the working
   directory listing; curl treats each file name as a hostname and whatever those bogus
   hosts return (frequently an HTML page from a catch-all vhost) is written wherever the
   command was redirected. That is how an apt sources list fills with HTML and package
   management breaks. Write flags inline and quoted: `curl -fsSL --noproxy '*' ...`.
2. **Download to /tmp, validate, then install.**

```bash
curl -fsSL --noproxy '*' -o /tmp/key.gpg "$KEY_URL"
file -b /tmp/key.gpg | grep -qi 'OpenPGP' || { echo "not a key:"; head -c 160 /tmp/key.gpg; exit 1; }
sudo install -m 644 /tmp/key.gpg /usr/share/keyrings/example.gpg

curl -fsSL --noproxy '*' -o /tmp/pkg.list "$LIST_URL"
grep -q '^deb' /tmp/pkg.list || { echo "not a sources file:"; head -c 160 /tmp/pkg.list; exit 1; }
sudo install -m 644 /tmp/pkg.list /etc/apt/sources.list.d/example.list
```

   `install` overwrites; a failed validation must `exit 1` **before** it, never after.
3. **Make step 0 a repair step.** A previous bad run may have left garbage behind:

```bash
if [ -e "$LIST" ] && { grep -qi '<!DOCTYPE' "$LIST" || grep -qi '<html' "$LIST" || ! grep -q '^deb' "$LIST"; }; then
  sudo rm -f "$LIST"
fi
```

   Test for **both** the wrong content type and the missing expected line — a corrupted file
   can contain the right line far below the junk, so a single `grep` is not enough.
4. **Be idempotent.** `command -v tool >/dev/null || install it`; a second run must be a no-op
   rather than a duplicate configuration.
5. **Verify the download + validation path yourself as the unprivileged user** before handing
   the script over — that catches quoting and glob bugs without needing root. Then the user
   runs the whole thing once.
6. **Print the result, not just the actions.** End with the concrete value the user needs
   (the public URL) plus a self-check (`curl` the health endpoint from outside).

## 3. Passwords

- Never accept, type, store or repeat a password from chat. If the user pastes one anyway,
  say plainly that it is now exposed in the chat history and the local session logs, and that
  they should change it — and not reuse the same password for other services (a router admin
  panel, for instance).
- The privileged path is the user running the script in their own terminal, where the prompt
  belongs to them.
- A `NOPASSWD` sudoers rule is a security downgrade: raise it only if the user does, and scope
  it to one command if they insist.

## 4. Proving the endpoint is reachable from outside

- A LAN-side check proves nothing about whether the platform can reach you. Fetch the public
  URL from a path that leaves the network (an external proxy, a mobile hotspot).
- Inspect the certificate the platform will see: public CA issuer, SAN contains the host, full
  chain, not expired. Self-signed is rejected outright by the skill platform.
- Only after both checks, paste the URL into the skill settings and run the voice test.

## 5. Tunnel lifecycle & blaming the right layer

A throwaway tunnel is for the first test, never for a live skill.

- **Idle drop.** `localhost.run` closes an idle session (`Received disconnect ... tunnel activity
  timeout`); the URL then answers `no tunnel`/502. Keep activity flowing through the tunnel with a
  background ping of the *public* health endpoint:

```bash
while true; do
  curl -s --noproxy '*' -o /dev/null --max-time 10 "https://$PUBLIC_HOST/health"
  sleep 120
done
```

- **The public URL changes on every restart**, forcing another edit in the skill settings. For an
  endpoint that must last, publish through a tunnel with a stable hostname — Tailscale Funnel
  terminates HTTPS for you and needs neither a domain nor a white IP:

```bash
sudo tailscale funnel --bg --https=443 http://127.0.0.1:$LOCAL_PORT
sudo tailscale funnel status          # prints the stable https://<host>.<tailnet>.ts.net
sudo tailscale funnel --https=443 off # turn it off again
```

- **Correlate before you code.** The platform error names no layer. Read both sides at the same
  minute:

```bash
journalctl -u <unit> --since "15 min ago" --no-pager | grep -E "POST|Traceback|rejected"
```

  No matching request ⇒ the call never reached the app (stale URL in the skill settings, dead tunnel,
  edge error). A request with a non-200 ⇒ the app failed; read the traceback. Only the second case is
  an application bug.
- **Put diagnostics in the layer you can restart without root.** A userspace proxy in front of the
  systemd unit can be restarted freely and survives the tunnel untouched, so per-request logging
  (caller, `user_id`, session id, status, question, answer) belongs there.
- **Log the caller header, and read it as ingress identity.** Cloudflare-style edges set
  `X-Forwarded-For`, so the real client IP appears; an SSH reverse tunnel does not, so the caller
  shows as `127.0.0.1`. That one field tells you which ingress actually served a request — it is how
  you discover that the skill is still pointing at the previous tunnel's URL while a freshly minted
  one sits unused.
- **Do not grind on a provider whose edge will not dial from this network.** If the tunnel's own log
  shows it cannot reach its edge at all, the platform will never be reached no matter how the app is
  changed: switch provider, or go straight to the stable-hostname option. The local app and proxy
  layers stay proven and untouched either way — do not re-debug them because a remote edge is
  unreachable.
