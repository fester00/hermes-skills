---
date: 2026-06-23
skill: hermes-internal-operations
topic: separate-hermes-webui-repo-start
---

# Starting a separate `~/hermes-webui` repository

This reference covers the legacy/community WebUI checkout located at `~/hermes-webui`, typically the repository linked by the user (`https://github.com/nesquena/hermes-webui`). It is distinct from the built-in `hermes dashboard` command.

## Key files

- `~/hermes-webui/.env` — port, password, `HERMES_WEBUI_ALLOWED_ORIGINS`
- `~/hermes-webui/start.sh` — pre-flight health probe, then `bootstrap.py`
- `~/hermes-webui/ctl.sh` — daemon-style PID/log management
- `~/hermes-webui/server.py` — the actual server entry point
- `~/hermes-webui/bootstrap.py` — bootstraps environment and launches `server.py`
- Log file defaults to `~/.hermes/webui.log`

## Typical configuration

```bash
HERMES_WEBUI_PORT=18789
HERMES_WEBUI_ALLOWED_ORIGINS=https://130.255.9.9:8443
HERMES_WEBUI_PASSWORD=<secret>
```

## Start recipes

### ctl.sh (preferred for persistent background)

```bash
cd ~/hermes-webui
./ctl.sh status
./ctl.sh start 18789
./ctl.sh status
```

`ctl.sh` writes a PID file under `~/.hermes/webui.pid` and logs to `~/.hermes/webui.log`.

### start.sh (manual background)

```bash
cd ~/hermes-webui && ./start.sh --no-browser > /tmp/hermes-webui.log 2>&1 &
sleep 5
ss -tlnp | grep 18789
```

`start.sh` includes a health probe that refuses to double-start if a server already answers on the configured port.

## Verification

```bash
ss -tlnp | grep 18789
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:18789/health
pgrep -af "hermes-webui/server.py"
tail -n 40 ~/.hermes/webui.log
```

## Stop

```bash
cd ~/hermes-webui && ./ctl.sh stop
# If ctl.sh is unavailable or leaves a stale process:
pgrep -f "hermes-webui/server.py" | xargs -r kill
sleep 3
pgrep -f "hermes-webui/server.py" | xargs -r kill -9
ss -tlnp | grep 18789 || echo "port free"
```

## Common gotchas

- The server process may bind successfully and answer `/health` even when `ctl.sh` reports it stopped earlier. Always verify with `ss -tlnp`.
- The log may say `FATAL: Another server is already responding` even after `ss` shows the port free; check for a second `server.py` or `bootstrap.py` process.
- nginx reverse proxy for SSE chat requires:
  ```nginx
  proxy_http_version 1.1;
  proxy_set_header Host $http_host;
  proxy_buffering off;
  proxy_cache off;
  proxy_read_timeout 86400;
  ```
- `HERMES_WEBUI_ALLOWED_ORIGINS` must match the exact public origin, including scheme and port.

## When to prefer built-in dashboard

If the user has no `~/hermes-webui` checkout, or explicitly references `hermes dashboard`, use:

```bash
hermes dashboard --port 9119 --no-open
hermes dashboard --status
hermes dashboard --stop
```

But when the user links the `nesquena/hermes-webui` repo, assume the separate checkout is the active install.
