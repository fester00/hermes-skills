#!/usr/bin/env bash
# Watchdog template for a service published through a tunnel.
#
# Adapt the four variables below, keep the rest. Two duties:
#   1. if the local edge proxy is down, relaunch it;
#   2. probe the PUBLIC address from outside — a loopback probe cannot see a dead tunnel,
#      and a tunnel pointing at a dead port breaks the provider silently.
# Plus in-place log rotation, because this script itself appends lines to the service log.
#
# Install: user crontab, '@reboot' plus '*/3 * * * *', no sudo needed.
set -uo pipefail

PROJ=/path/to/project                 # project dir (logs live here)
EDGE_PORT=8788                        # loopback port of the gated edge proxy
RUN_CMD="$PROJ/scripts/proxy-run.sh"  # how to (re)start that proxy
HOST=example.ts.net                   # the public hostname the provider has stored

LOG="$PROJ/.proxy.log"
EDGE_LOG="$PROJ/.edge.log"

# ─── 1. local proxy ─────────────────────────────────────────────────────────────
if ! curl -s --noproxy '*' --max-time 5 -o /dev/null "http://127.0.0.1:$EDGE_PORT/health"; then
  # port busy but health silent: likely mid-restart, leave it alone
  if ss -tln 2>/dev/null | grep -q ":$EDGE_PORT "; then
    echo "$(date -Is) watchdog: port $EDGE_PORT busy but health silent - skipping" >>"$LOG"
  else
    echo "$(date -Is) watchdog: edge proxy down, relaunching" >>"$LOG"
    nohup "$RUN_CMD" >/dev/null 2>&1 &
    sleep 3
    if curl -s --noproxy '*' --max-time 5 -o /dev/null "http://127.0.0.1:$EDGE_PORT/health"; then
      echo "$(date -Is) watchdog: relaunched ok" >>"$LOG"
    else
      echo "$(date -Is) watchdog: RELAUNCH FAILED" >>"$LOG"
    fi
  fi
fi

# ─── 2. public address, probed from outside ─────────────────────────────────────
# --doh-url is REQUIRED for tailnet-style names: on the host that owns the tailnet the name
# resolves to a private address, so the ordinary resolver probes the wrong server.
EDGE=$(curl -s --noproxy '*' --max-time 25 --doh-url https://1.1.1.1/dns-query \
        -o /dev/null -w '%{http_code} %{time_total}' "https://$HOST/health" 2>/dev/null || echo '000 -')
case "$EDGE" in
  200*) : ;;  # healthy - stay quiet so the log stays readable
  *)
    echo "$(date -Is) edge: public address answered '$EDGE' ($HOST)" >>"$EDGE_LOG"
    echo "$(date -Is) watchdog: PUBLIC ADDRESS NOT ANSWERING - '$EDGE' ($HOST)" >>"$LOG"
    ;;
esac

# ─── 3. rotate logs in place ────────────────────────────────────────────────────
# Open the file for writing and rewrite its tail. Do NOT replace the file (mv / sed -i):
# that swaps the inode and the running service keeps appending to an unlinked file.
python3 - "$PROJ" <<'PY' 2>/dev/null || true
import sys
from pathlib import Path

proj = Path(sys.argv[1])
for path, limit, keep in (
    (proj / ".proxy.log", 1_000_000, 500),
    (Path("/tmp/service-requests.log"), 500_000, 2000),
    (proj / ".edge.log", 200_000, 500),
):
    if not path.exists() or path.stat().st_size <= limit:
        continue
    tail = path.read_text(encoding="utf-8", errors="replace").splitlines()[-keep:]
    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(tail) + "\n")
PY
