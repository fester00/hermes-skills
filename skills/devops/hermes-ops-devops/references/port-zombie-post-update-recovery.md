# Post-Update Port Zombie Recovery

## Real Case: Hermes WebUI After System Update (2026-05-29)

### Problem
User updated the system. Hermes WebUI systemd service (`hermes-webui`) entered an endless crash-restart loop (restart counter at **68,409**). `systemctl status` showed `Result: exit-code`, logs showed `OSError: [Errno 98] Address already in use`.

### Root Cause
The old `python /home/natan/hermes-webui/server.py` process (PID 1011, started 24 May, **5 days before** the update) survived the update. It continued holding `127.0.0.1:18789`. systemd tried to spawn a new process, which immediately failed on bind, then systemd auto-restarted — 68 thousand times.

### Diagnosis Steps
```bash
# 1. Show systemd status — note the restart counter
systemctl --user status hermes-webui --no-pager | head -10
# Output showed: restart counter is at 68409

# 2. Check who holds the port
ss -tlnp | grep :18789
# LISTEN 0  64  127.0.0.1:18789  *:*  users:(("python",pid=1011,fd=4))

# 3. Compare PID ages
systemctl --user status hermes-webui --no-pager | grep "Main PID"
# Main PID: 591540 (new process, kept dying)
ps -fp 1011 | cat
# STIME: May24 (old process, the zombie)
```

### Fix
```bash
# Kill the zombie (older PID)
kill 1011
sleep 2

# Restart service — now new process gets the port
systemctl --user restart hermes-webui
sleep 3
systemctl --user is-active hermes-webui
# → active
```

### Verification
```bash
ss -tlnp | grep :18789
curl -s http://127.0.0.1:18789/health
# {"status":"ok","sessions":0,"active_streams":0,"uptime_seconds":7.1}
```

### Lesson: Restart Counter as Diagnostic Signal
An absurdly high restart counter (>1000) is never normal. It implies:
1. The service is in a tight crash-restart loop
2. The crash is instantaneous (not a startup timeout)
3. The most common cause is a **port conflict from a surviving old process**

Always `ss -tlnp | grep :PORT` and `ps -fp PID` to verify whether the port holder is older than the current Main PID.

## Applicability
Any Python HTTP server (WebUI, gateway, MCP, custom) started via systemd where `ExecStart` uses a direct script path. Less common with `pm2` or docker because those manage process lifecycle differently — but still possible if a container's bind mount leaks the port.
