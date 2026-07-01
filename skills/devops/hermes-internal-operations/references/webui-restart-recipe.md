# Hermes WebUI Restart Recipe

## Stop

```bash
OLD_PID=$(pgrep -f "hermes-webui/server.py")
[ -n "$OLD_PID" ] && kill "$OLD_PID"
sleep 3
# If still there:
# kill -9 "$OLD_PID"
```

If a second process (bootstrap or stale server) keeps the port busy, list all matching PIDs by start time and stop the older one:
```bash
ps -eo pid,lstart,cmd | grep hermes-webui/server.py | grep -v grep
```

## Confirm port free

```bash
ss -tlnp | grep "${HERMES_WEBUI_PORT:-18789}" || echo "Port is free"
```

## Start

Prefer the project's launcher if it exists:
```bash
cd ~/hermes-webui && ./start.sh --no-browser > /tmp/hermes-webui-restart.log 2>&1 &
```

If `start.sh` is missing or fails, start the server directly with the WebUI's own Python:
```bash
cd ~/hermes-webui && /home/natan/.hermes/hermes-agent/venv/bin/python /home/natan/hermes-webui/server.py > /tmp/hermes-webui-restart.log 2>&1 &
```

## Verify

```bash
sleep 5
HEALTH=$(curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:"${HERMES_WEBUI_PORT:-18789}"/health)
echo "HTTP status: $HEALTH"
curl -s http://127.0.0.1:"${HERMES_WEBUI_PORT:-18789}"/health
```

Expected: `200` with JSON `{ "status": "ok", ... }`.
Also confirm exactly one process owns the port:
```bash
ss -tlnp | grep "${HERMES_WEBUI_PORT:-18789}"
```

## Preferred local launchers

| Install type | Primary command | Notes |
|--------------|-----------------|-------|
| Built-in Hermes dashboard | `hermes dashboard --port 9119 --no-open` | Modern default; use when `hermes dashboard` exists |
| Separate `~/hermes-webui` checkout | `cd ~/hermes-webui && ./start.sh --no-browser` | Legacy/community WebUI; respects `.env` |
| Separate checkout, ctl wrapper | `cd ~/hermes-webui && ./ctl.sh start 18789` | Daemon-style with PID/log files; use for persistent background runs |

Choose the launcher that matches the user's actual WebUI install. If `hermes dashboard --help` works, the dashboard path is the modern route. If only `~/hermes-webui` exists, use `start.sh` or `ctl.sh`.

## If behind nginx

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://YOUR_PUBLIC_ENDPOINT/
# If 403/connection refused, check nginx upstream and HERMES_WEBUI_ALLOWED_ORIGINS.
```

## Common gotchas

- `start.sh` may complain "Another server is already responding" right after kill. Wait 5s and retry, or verify port is free first.
- WebUI password lives in `~/hermes-webui/.env`, not `~/.hermes/.env`.
- `HERMES_WEBUI_ALLOWED_ORIGINS` must include the exact public origin including port, e.g. `https://130.255.9.9:8443`.
- For SSE chat behind nginx, `proxy_buffering off; proxy_cache off;` are mandatory.
- The WebUI process may be auto-respawned by an external watcher or by a duplicate systemd unit after a manual kill. Always confirm with `pgrep` and `ss -tlnp` before assuming the restart succeeded.
- `ctl.sh` may report `Started Hermes WebUI` even when the child has not finished binding yet. Always verify the port with `ss` a few seconds after `ctl.sh start`, and check `ps -eo pid,lstart,cmd | grep server.py` to see the actual process state.
