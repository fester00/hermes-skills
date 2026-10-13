#!/usr/bin/env bash
# Read-only diagnostics for the Hermes WebUI.
# Answers one question first: is the service at fault at all, and is the
# in-process agent runtime older than the agent checkout on disk?
#
# Usage: bash scripts/webui-diagnose.sh
# Optional env: WEBUI_DIR, AGENT_DIR, PORT, PROXY_URL (e.g. https://host:8443/health)
set -uo pipefail

WEBUI_DIR="${WEBUI_DIR:-$HOME/hermes-webui}"
AGENT_DIR="${AGENT_DIR:-$HOME/.hermes/hermes-agent}"
PORT="${PORT:-18789}"
PROXY_URL="${PROXY_URL:-}"

PID="$(systemctl --user show -p MainPID --value hermes-webui.service 2>/dev/null)"

printf '=== unit ===\n'
systemctl --user is-active hermes-webui.service 2>&1
printf 'MainPID=%s\n' "$PID"
if [ -n "$PID" ] && [ "$PID" != "0" ]; then
  ps -o lstart=,etime=,rss= -p "$PID"
fi

printf '=== port ===\n'
ss -tlnp 2>/dev/null | grep ":$PORT" || echo "port $PORT NOT bound"

printf '=== health (local) ===\n'
timeout 15 curl -s --noproxy '*' -o /dev/null -w '%{http_code}\n' "http://127.0.0.1:$PORT/health" || echo 'curl failed'

if [ -n "$PROXY_URL" ]; then
  printf '=== health (proxied) ===\n'
  timeout 20 curl -s -k --noproxy '*' -o /dev/null -w '%{http_code}\n' "$PROXY_URL" || echo 'curl failed'
fi

printf '=== webui checkout ===\n'
git -C "$WEBUI_DIR" log -1 --format='HEAD %h %cd %s' --date=iso 2>&1
git -C "$WEBUI_DIR" reflog --date=iso -3 2>&1
printf -- '-- pending upstream --\n'
git -C "$WEBUI_DIR" log --oneline HEAD..origin/master 2>/dev/null | head -5
printf -- '-- dirty tree --\n'
git -C "$WEBUI_DIR" status --short 2>&1 | head -5

printf '=== agent checkout ===\n'
git -C "$AGENT_DIR" log -1 --format='HEAD %h %cd %s' --date=iso 2>&1
git -C "$AGENT_DIR" reflog --date=iso -3 2>&1
printf 'NOTE: an agent commit newer than MainPID start time makes the loaded runtime stale -> 409 agent_runtime_stale on POST /api/chat/start\n'

printf '=== non-200 responses, last 2h ===\n'
journalctl --user -u hermes-webui.service --since '-2h' --no-pager 2>&1 | grep -oE '"status": [0-9]+' | sort | uniq -c
printf -- '-- last 10 non-200 request lines --\n'
journalctl --user -u hermes-webui.service --since '-2h' --no-pager 2>&1 | grep '"path":' | grep -vE '"status": 200' | tail -10
printf -- '-- startup errors since unit start --\n'
journalctl --user -u hermes-webui.service --since '-24h' --no-pager 2>&1 | grep -vE '"path":' | grep -iE 'traceback|error|fatal|exit' | tail -10

printf '=== sessions with a live stream id (newest 8) ===\n'
python3 - <<'PY' 2>/dev/null
import glob, json, os, time
paths = sorted(
    glob.glob(os.path.expanduser('~/.hermes/webui/sessions/*.json')),
    key=os.path.getmtime, reverse=True,
)[:8]
for p in paths:
    try:
        d = json.load(open(p))
    except Exception:
        continue
    if not isinstance(d, dict):
        continue
    if 'session_id' not in d:
        continue
    print(
        f"{d.get('session_id')} stream={d.get('active_stream_id')} "
        f"model={d.get('model')} prov={d.get('model_provider')} "
        f"{time.strftime('%m-%d %H:%M', time.localtime(os.path.getmtime(p)))} "
        f"{str(d.get('title'))[:28]!r}"
    )
PY
