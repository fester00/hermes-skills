# Token Audit Checklist

Paste this into a terminal (or execute step-by-step) when investigating unexpected token spend.

```bash
# 1. Last 24h high-level usage
hermes insights --days 1

# 2. Recent sessions
hermes sessions list --limit 30

# 3. Gateway activity in the last ~60 lines
#    Adjust tail count based on log volume.
grep -E 'inbound|response ready|api_calls|token|cost|compression|curator' \
  ~/.hermes/logs/gateway.log | tail -n 80

# 4. Autonomous jobs / background agents
hermes cron list
ps aux | grep -iE 'hermes chat|opencode|codex|claude' | grep -v grep

# 5. WebUI running and listening?
pgrep -f "hermes-webui/server.py"
ss -tlnp | grep "${HERMES_WEBUI_PORT:-18789}"

# 6. Provider-side recent usage (manual)
#    Open provider dashboard and compare billed request timestamps with the
#    gateway log timestamps above.
```

## What each answer means

- `insights` shows the heavy platform → focus there.
- No `inbound` in gateway log during the window → Telegram gateway is not the spender.
- WebUI is running but user left the tab open → WebUI session may be compressing context in background.
- Provider dashboard timestamps lag behind wall-clock → delayed billing, not an active leak.
