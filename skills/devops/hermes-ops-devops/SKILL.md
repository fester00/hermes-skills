---
name: hermes-ops-devops
description: |
  Umbrella for server operations, live service debugging, health monitoring,
  and file deployment. Covers systemd/nginx diagnostics, auto-repair runbooks,
  zombie process cleanup, and FTP upload workflows.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [devops, ops, debugging, health-check, monitoring, systemd, nginx, ftp, deployment]
    related_skills: []
---

# Hermes Ops & DevOps

## When to Use

- User reports a service is down, unreachable, or crash-looping
- System infrastructure needs health monitoring or auto-repair
- Files need to be deployed to a remote server via FTP
- Any production server maintenance where co-hosted services must stay up

---

## Section 1: Live Server Service Debugging

**Trigger:** A service on a live machine is failing, unreachable, or crash-looping.
Must fix it without bringing down co-hosted production services.

**Core principle:** Diagnose thoroughly before touching anything that affects neighbours.
Read everything first, change one thing at a time, verify each change.

### Safety Rules
1. Identify neighbours before changing anything
2. Backup configs before edits (`cp` before `patch`)
3. Do NOT restart critical neighbours unless absolutely necessary — reload instead
4. One change at a time; revert if it doesn't help
5. Verify health after each change

### Diagnostic Checklist (do ALL before fixing)

1. **Discover services:**
```bash
systemctl list-units --type=service --state=running | grep -E "(nginx|target)"
systemctl list-units --type=service --state=failed | grep -i target
systemctl --user list-units --type=service | grep -i target
ps aux | grep -i target | grep -v grep
```

2. **Check network listeners:**
```bash
ss -tlnp | grep -E "(target_port|nginx)"
```

**2a. Spot zombie port grabs (critical after updates):**
When `restart counter` in `systemctl status` is absurdly high (>1000) AND the service logs show `Address already in use`, the old process likely survived the update and holds the port.
```bash
ss -tlnp | grep :PORT
# If owner PID is OLDER than current Main PID, it's a zombie
ps -fp OLD_PID | cat                # check start time (STIME)
kill OLD_PID ; sleep 2
systemctl --user restart SERVICE
```

3. **Read application config** — find in `~/.service/`, `/etc/service/`, `/opt/service/`

4. **Read recent logs:**
```bash
journalctl -u servicename --no-pager -n 50
tail -n 100 /tmp/service/latest.log
grep -E "ERROR|WARN|Fatal|crash" /tmp/service/latest.log
```

5. **Check reverse proxy / nginx:**
```bash
cat /etc/nginx/sites-enabled/service
nginx -t
ls -la /etc/nginx/ssl/
```

6. **Check for past runs (stale log evidence):**
```bash
ls -la ~/.service/logs/ /tmp/service.log ~/.service/state/
tail -n 50 ~/.service/logs/latest.log
grep -E 'ERROR|Fatal|Traceback|ModuleNotFoundError|OSError:.*Address already in use' ~/.service/logs/*.log | tail -30
```

7. **Check firewall:**
```bash
sudo ufw status
sudo iptables -L -n | grep relevant_port
```

### Common Failure Patterns

| Pattern | Symptom | Fix |
|---------|---------|-----|
| **A: Loopback-only binding** | `Connection refused` externally; works locally | Change bind from `127.0.0.1` to `0.0.0.0` |
| **B: Untrusted reverse proxy** | WebSocket fails; "Proxy headers from untrusted address" | Add `127.0.0.1` to `trustedProxies` config |
| **C: Systemd start timeout** | Service killed during startup after installing deps | Increase `TimeoutStartSec` to 120–300s |
| **D: Stale plugin references** | "Plugin not found" warnings; app refuses to start | Remove stale entries from allow-list |
| **E: SSL key permissions** | `nginx -t` fails "Permission denied" on `.key` | `chown root:www-data key; chmod 640 key` |
| **F: Health-check timeout** | "Timed out after 60s waiting for gateway port" | Increase `TimeoutStartSec` or reduce startup work |
| **G: Port already in use** | `Address already in use` on startup; systemd restart counter skyrockets | `ss -tlnp | grep PORT`, check if owner PID is OLDER than current Main PID (zombie survived update), `kill OLD_PID`, restart. **Note:** Absurdly high restart counter (>1000) is a reliable signal — investigate `ss -tlnp` immediately. |
| **G2: Stale CLI handle after gateway restart** | `send_message` times out even though `systemctl status` shows `active (running)` | Old CLI session retains stdio handle to dead gateway process. Run `/new` or use direct curl to Bot API — gateway is healthy, handle is not. |
| **G3: Git-update port grab** | `Address already in use` immediately after `git pull`/`reset --hard` | Git update changes files on disk but old process still holds the port. Kill old PID manually (`kill $(lsof -t -i:PORT)` or `kill OLD_PID`), then `systemctl restart SERVICE`. Systemd auto-restart alone won't work. **Note:** This often happens when update resolves merge conflicts via `git reset --hard` — the process survives the reset but is now running stale code while systemd tries to restart into new code. |
| **G4: Killing the wrong occupant on a shared port** | `EADDRINUSE` on port `3000` (or any common dev port); multiple projects use the same default port | Before running `kill $(lsof -t -i:PORT)`, always identify the process: `lsof -ti:PORT | xargs ps -fp` or `ss -tlnp`. Ask the user or read `package.json`/`process.title` to confirm it is the intended dev server. The user's primary production/project instance may be on that port. Prefer starting the new instance on an alternate port (`--port 3001`) rather than killing an unknown occupant. |
| **G5: Gateway restarted but Telegram still paused** | `hermes gateway restart` succeeds, status shows `active`, but logs repeat `telegram paused after N consecutive failures` or `Gateway started with no connected platforms` | The problem is not gateway — it is network reachability to `api.telegram.org` (or fallback IPs). Diagnose with `curl -m 10 https://api.telegram.org`. If that also times out, use selective SOCKS5 proxy via `TELEGRAM_PROXY=socks5://127.0.0.1:PORT`. See `references/gateway-telegram-selective-proxy.md`. |
| **G6: Next.js dev/production port conflict** | User wants pentajunior-v2 on port 3001/3002 while pentajunior (production) stays on 3000 | Identify the occupant of :3000 with `ss -tlnp | grep :3000`, then `pwdx PID` and `readlink -f /proc/PID/exe`. Read `package.json` to confirm project name. Never kill an unknown Next.js process on :3000 — it may be the production site. Start v2 on a different port via dev script or nginx upstream. |
| **G2: CLI handle stale after gateway restart** | `send_message` times out even though `systemctl status` shows `active (running)` | Old CLI session retains stdio handle to dead gateway process. Run `/new` or use direct curl to Bot API — gateway is healthy, handle is not. |
| **H: No systemd unit (manual start died)** | Port empty; nginx config exists; no `systemctl status` | Manually start service, then create systemd unit file |
| **I: CSRF 403 + SSE blocked behind nginx** | POST 403; chat hangs; Origin port mismatch | `proxy_set_header Host $http_host; proxy_buffering off;` |
| **J: Missing module behind systemd** | `ModuleNotFoundError` via systemd but works manually | Use venv python path in `ExecStart=` |
| **K: Git conflict markers → SyntaxError** | Process exists, high CPU, port not open, no logs | `grep -rn '<<<<<<<' --include="*.py"`, resolve conflict, recompile |
| **L: WebUI workspace uploads fail or land in the wrong place** | File upload to `/mnt/data/.../books/js` fails silently, returns "Upload failed", or ends up in the session workspace instead | WebUI upload uses relative `path` inside the session workspace, not absolute filesystem paths. Also verify nginx `client_max_body_size` and `HERMES_WEBUI_MAX_UPLOAD_MB`. See `references/webui-workspace-upload-pitfalls.md`. |

### Repair Procedure
1. Backup every config before editing
2. Apply ONE fix
3. Restart/reload only the target service
4. Wait for startup grace period
5. Verify: `systemctl status`, `ss -tlnp`, logs, `nginx -t`
6. If broken, revert and try next hypothesis
7. Never leave the system in a worse state

---

## Section 2: System Health Check & Auto-Repair

**Trigger:** Agent complains about `ClosedResourceError`, `TimeoutError`, MCP unavailable,
WebUI unresponsive, gateway down, or user asks to "check systems".

### Quick Status
```bash
hermes gateway status && hermes mcp test obsidian && echo "=== WebUI ===" && systemctl --user status hermes-webui --no-pager | head -5 && echo "=== MCP Procs ===" && pgrep -c "obsidian-mcp" && echo "=== Disk ===" && df -h / /home | tail -2
```

### Phase 1: MCP Obsidian — `ClosedResourceError`

**DO NOT** just restart gateway — it won't fix the stale stdio handle.

1. **Kill zombie MCP processes:**
```bash
kill $(pgrep -f "obsidian-mcp/build/main.js") 2>/dev/null; sleep 2
```

2. **Restart gateway** (spawns fresh MCP child):
```bash
systemctl --user restart hermes-gateway; sleep 3
```

3. **Start NEW session** — old CLI session keeps stale stdio handle.
   - CLI: type `/new` and press Enter
   - WebUI: refresh page (F5)
   - Telegram: new message

### Phase 2: Gateway
```bash
systemctl --user status hermes-gateway --no-pager | head -5
```
| Status | Action |
|--------|--------|
| `active` | OK, skip |
| `failed`/`inactive` | `systemctl --user restart hermes-gateway` |
| `activating` | Wait 10s, check again |

If gateway fails to start:
```bash
journalctl --user -u hermes-gateway -n 30 --no-pager
```
Look for: port already in use, `config.yaml` error, `ImportError`.

**Duplicate unit files (system vs user):**
- Check BOTH scopes: `systemctl list-units --type=service | grep -i hermes`
- Home-directory services → use **user unit**: `systemctl --user restart <name>`
- System-wide services → use **system unit**: `sudo systemctl restart <name>`

### Phase 3: WebUI
```bash
systemctl --user status hermes-webui --no-pager | head -5
```
| Status | Action |
|--------|--------|
| `active` | OK |
| `failed`/`inactive` | `systemctl --user restart hermes-webui` |
| Not installed | Run manual: `cd ~/hermes-webui && bash start.sh &` |

WebUI check endpoint:
```bash
curl -sL https://127.0.0.1:8443/api/sessions 2>/dev/null | head -1 || echo "WebUI unreachable"
```

### Phase 4: Ollama Proxy
```bash
systemctl status ollama --no-pager | head -5
curl -s http://127.0.0.1:11434/api/tags | head -c 200
```

### Phase 5: nginx / SSL
```bash
sudo systemctl status nginx | head -5
sudo nginx -t
```

**NEVER touch pentajunior (443) config** — production site.

### Phase 6: Disk Space
```bash
df -h / /home
```
Action if >90%:
1. `du -sh ~/* 2>/dev/null | sort -rh | head -10`
2. `find ~/hermes -name "*.log" -mtime +7 -delete`
3. `find ~/hermes -name "output" -type d -mtime +3 -exec rm -rf {} + 2>/dev/null`
4. If still critical → alert user

### Phase 7: Zombie Process Cleanup
```bash
pgrep -c "obsidian-mcp"
pgrep -c "python.*hermes"
pgrep -c "python.*server\.py"
```
If >1 of same type:
```bash
for pattern in "obsidian-mcp/build/main.js"; do
    PIDS=$(pgrep -f "$pattern" | sort -rn | tail -n +2)
    [ -n "$PIDS" ] && kill $PIDS && echo "Killed stale: $PIDS"
done
```
After cleanup → restart gateway to respawn clean children.

### Auto-Fix Decision Tree
```
User reports problem
  → [Run Quick Status]
  → MCP broken?       → Kill zombies → restart gateway → /new
  → Gateway dead?     → restart gateway
  → WebUI dead?       → restart webui
  → Ollama dead?      → restart ollama
  → nginx dead?       → restart nginx + check config
  → Disk >90%?       → clean logs + alert
  → [Repeat Quick Status]
```

---

## Section 3: WebUI Service Restart & Default Model Refresh

**Trigger:** User asks to restart Hermes WebUI, change the default model shown in the WebUI picker, or verify that WebUI picked up a new `config.yaml` model.

### Core Principle
WebUI reads `model.default` from `~/.hermes/config.yaml` at startup, but it also maintains its own in-memory and on-disk model cache. A config edit alone may not refresh the picker if stale cache or browser state is involved.

### Restart Procedure
```bash
# 1. Invalidate the model catalog cache so the next startup rebuilds it
python3 - <<'PY'
import sys
sys.path.insert(0, '/home/natan/hermes-webui')
from api.config import invalidate_models_cache
invalidate_models_cache()
PY

# 2. Restart the systemd service
systemctl --user restart hermes-webui.service
sleep 8
systemctl --user status hermes-webui.service --no-pager | head -10
```

### Verify the Server Is Healthy
```bash
# Port listening
ss -tlnp | grep 18789

# Service status
systemctl --user is-active hermes-webui.service
# -> active
```

Note: `/api/health/agent` returns 401 when WebUI password auth is enabled; that means auth is working, not that WebUI is broken.

### Verify the New Default Model Is Active
```bash
cd /home/natan/hermes-webui && python3 - <<'PY'
import sys
sys.path.insert(0, '/home/natan/hermes-webui')
from api.config import load_settings, get_available_models, invalidate_models_cache
invalidate_models_cache()
print('settings default_model:', load_settings().get('default_model'))
print('settings default_model_provider:', load_settings().get('default_model_provider'))
catalog = get_available_models()
print('catalog default_model:', catalog.get('default_model'))
print('catalog active_provider:', catalog.get('active_provider'))
PY
```

Expected output should show the new model (e.g. `kimi-k2.7-code:cloud`) and provider (`ollama-launch`).

### If the Browser Still Shows the Old Model
The server-side default is correct, but the front-end may have cached the previous selection.

Tell the user to do a hard refresh:
- Windows/Linux: `Ctrl + Shift + R` or `Ctrl + F5`
- macOS: `Cmd + Shift + R`

If that fails, clear front-end storage:
```javascript
localStorage.clear();
sessionStorage.clear();
location.reload(true);
```

### Pitfalls
| Problem | Cause | Fix |
|---------|-------|-----|
| WebUI picker still shows old model after config edit | Browser cache / front-end state | Hard refresh or clear `localStorage` |
| `get_available_models()` returns stale model | On-disk / in-memory cache | Call `invalidate_models_cache()` before reading |
| `/api/health/agent` returns 401 | Password auth enabled | Expected; verify with status + port instead |
| **WebUI `systemctl restart` times out** | Old process holds the port | See `references/port-zombie-post-update-recovery.md`. Also check whether WebUI is actually supervised by a systemd user service — if so, use `systemctl --user restart hermes-webui.service` and avoid `./ctl.sh`, which creates a double-supervisor race. See `hermes-webui-operations/references/ctl-sh-vs-systemd-conflict.md`. |

---

## Section 4: FTP Upload

**Trigger:** User needs to upload files/folders to a remote FTP server.

### Connection Details (user-specific; example pattern)
- Host, port, user, password stored in skill context or env

### Upload a Folder Recursively

**Preferred: `lftp`** (supports recursive mirror + mkdir)
```bash
lftp -u USER,PASS -p 21 HOST -e "set ssl:verify-certificate no; mirror -R /local/path /remote/path; quit"
```
**Caveat:** `lftp` may not be installed; `apt-get` requires root.

**Fallback: Python `ftplib`** (portable, stdlib, no install)
```python
from ftplib import FTP
import os

ftp = FTP()
ftp.connect("HOST", 21)
ftp.login("USER", "PASS")

def ensure_dir(path):
    parts = path.split('/')
    current = ''
    for part in parts:
        if not part: continue
        current += '/' + part
        try:
            ftp.cwd(current)
        except:
            ftp.mkd(current)
            ftp.cwd(current)

def upload_dir(local_path, remote_path):
    ensure_dir(remote_path)
    for item in sorted(os.listdir(local_path)):
        local_item = os.path.join(local_path, item)
        if os.path.isfile(local_item):
            with open(local_item, 'rb') as f:
                ftp.storbinary(f"STOR {item}", f)
        elif os.path.isdir(local_item):
            upload_dir(local_item, remote_path + '/' + item)
            ftp.cwd('..')

upload_dir("/local/path", "/remote/path")
ftp.quit()
```

### Upload a Single File
```bash
curl -T /local/file.txt ftp://USER:PASS@HOST:21/remote/file.txt
```

### Pitfalls
| Problem | Fix |
|---------|-----|
| `550 Permission denied` on `mkdir` | User may only have write access to a subdirectory (e.g. `G/`). Check `ftp.pwd()` and `LIST` first. |
| `lftp` not installed | Use Python `ftplib` — stdlib, no install. |
| `curl` for folders | `curl` does NOT create remote directories. Always use `--ftp-create-dirs`. |
| `ftplib` CWD tracking | After descending into subdirs, call `ftp.cwd('..')` to backtrack. |
| **LIST shows dir but CWD fails** | FTP server quirk: `cd` denied despite directory visible. Use **absolute paths with `%2f`**: `ftp://host/%2fG/path/file`. See `references/ftp-connection-profile.md`. |
| **Subdirectory uploads via curl** | `curl` won't create remote directories. Always add `--ftp-create-dirs` when uploading into nested paths. |

### Quick Server Probe
```python
from ftplib import FTP
ftp = FTP(); ftp.connect("HOST", 21); ftp.login("USER", "PASS")
print("PWD:", ftp.pwd())
ftp.retrlines('LIST')
try:
    ftp.mkd('test_dir'); ftp.rmd('test_dir')
    print("Write OK")
except Exception as e:
    print("Write denied:", e)
ftp.quit()
```

---

## Section 4: PM2 Process Management & Node.js Service Protection

**Trigger:** A Node.js app managed by PM2 is crashing, not restarting after reboot,
leaking memory, or stuck in a restart loop. Covers Next.js, Express, and any Node service.

### Core Principle
PM2 is only as reliable as its configuration. A default `pm2 start npm -- start`
is fragile — it wraps `npm` which spawns `sh` which spawns the real process.
PM2 monitors the outer shell, not the Node.js runtime. Always configure via
`ecosystem.config.js` with direct process paths and production safeguards.

### Anti-Pattern: `pm2 start npm -- start`
**Why it's dangerous:**
- `npm` is a shell wrapper; PM2 tracks `npm`'s PID, not the Node.js server
- If the server crashes but `npm` stays alive, PM2 sees "online" while the site is down
- `npm` swallows signals; graceful shutdown (`pm2 reload`) may not reach Next.js
- No fine-grained control over restart strategy, memory limits, or environment

### Correct: Direct Script Execution
```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'appname',
    // PM2 executes the script directly with the interpreter; it cannot run
    // a shell wrapper. Use the real Next.js server binary, not node_modules/.bin/next.
    script: './node_modules/next/dist/bin/next',
    args: 'start',
    cwd: '/home/user/project',
    interpreter: '/home/user/.nvm/versions/node/v24.13.1/bin/node',
    exec_mode: 'fork',
    instances: 1,

    // Restart policy
    autorestart: true,
    restart_delay: 3000,               // Wait 3s before restart
    exp_backoff_restart_delay: 100,    // Exponential backoff after failures
    max_restarts: 10,                  // Halt after 10 consecutive failures
    min_uptime: '10s',                 // Only count as "stable" after 10s

    // Memory leak protection
    max_memory_restart: '512M',        // Kill & restart if RSS > 512MB

    // Graceful shutdown
    kill_timeout: 5000,
    listen_timeout: 5000,

    // Environment
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },

    watch: false                       // Disable file-watch in production
  }]
};
```

### Startup & Reboot Survival
1. Ensure systemd unit exists:
```bash
pm2 startup systemd
# Run the generated command (requires sudo once)
```
2. Save the process list after every config change:
```bash
pm2 save
```
3. Verify the systemd unit is **enabled** and **active**:
```bash
systemctl status pm2-$(whoami).service
```

### Deploy Script Best Practice
In CI/deploy scripts, use `reload` with the config file so PM2 picks up changes:
```bash
cd /home/user/project
pm2 reload ecosystem.config.js --env production
# or, if first deploy:
pm2 start ecosystem.config.js --env production
pm2 save
```

### Diagnostic Checklist
When a PM2-managed app is "down" or misbehaving, run in this order:

1. **Status overview:**
```bash
pm2 status
pm2 show <name>
```
2. **Process structure check:**
```bash
pm2 describe <name> | grep -E "script|interpreter|exec cwd|mode"
# Verify script path points directly to node binary, NOT npm
```
3. **Recent restarts / crashes:**
```bash
pm2 logs <name> --lines 200
cat ~/.pm2/pm2.log | grep -iE "(<name>|restart|error|fatal|kill|exited)" | tail -30
```
4. **Memory & loop latency:**
```bash
pm2 monit          # Interactive dashboard
# Or non-interactive:
pm2 show <name> | grep -E "heap|memory|cpu|latency"
```
5. **Saved dump integrity:**
```bash
python3 -c "
import json
with open('/home/user/.pm2/dump.pm2') as f:
    for p in json.load(f):
        if isinstance(p, dict) and p.get('name') == '<name>':
            print('script:', p.get('pm_exec_path'))
            print('args:', p.get('args'))
            print('autorestart:', p.get('autorestart'))
            print('max_restarts:', p.get('max_restarts'))
            print('max_memory_restart:', p.get('max_memory_restart'))
"
```

### Common Failure Patterns

| Pattern | Symptom | Fix |
|---------|---------|-----|
| **PM2 tracks npm, not Node** | App down but PM2 shows "online" | Switch to `script: './node_modules/.bin/next'` in ecosystem.config.js |
| **Infinite restart loop** | Uptime always <10s; restarts skyrocket | Add `max_restarts: 10` + `exp_backoff_restart_delay` + check logs for root cause |
| **OOM not caught** | Server killed by Linux OOM; no PM2 restart | Set `max_memory_restart: '512M'` so PM2 restarts *before* kernel OOM |
| **Config lost after reboot** | `pm2 status` empty after reboot | `pm2 save` after every start/reload; verify systemd unit is enabled |
| **Graceful deploy fails** | Old connections dropped; 502s | Use `pm2 reload` (zero-downtime) instead of `restart`; ensure `kill_timeout` ≥ app shutdown time |
| **Deploy picks up stale config** | New env vars ignored after deploy | Always pass `--env production` and point to `ecosystem.config.js` |
| **nvm not loaded in deploy scripts** | `npm: command not found` or `pm2: command not found` in CI/deploy scripts | Add nvm init + `nvm use <version>` at the top of the script. `nvm.sh` alone does NOT activate a node version in non-interactive shells. |
| **Deploy script in unexpected location** | `deploy.sh` not found in project root (`./deploy.sh` fails) | Search `~` for the script: `find ~ -maxdepth 2 -name "deploy.sh" -type f` |
| **Disk full during build** | `fatal: Out of diskspace` or `npm install` fails mid-way | `npm cache clean --force` (via nvm) and `journalctl --vacuum-time=3d`; check `~/.npm` which can balloon to 6GB+ |
| **PM2 process survives manual kill** | `kill` the PID but it respawns instantly with new PID | PM2 God Daemon is auto-restarting it. Use `pm2 stop <name>` then `pm2 delete <name>`, NOT `kill` directly. |

## Section 5: Telegram Gateway / Telegram Bot API — Blocking and Fallback IPs

**Trigger:** `send_message()` hangs with `TimedOut`; gateway logs show `api.telegram.org connection failed`; Telegram Bot API is blocked by ISP (common in Russia with Rostelecom).

### Symptoms
- `send_message` times out (30s+) without returning an error code
- Gateway logs: `Primary api.telegram.org connection failed; trying fallback IPs`
- Fallback IPs also time out
- `curl https://api.telegram.org` times out, but `ping api.telegram.org` works (TCP/443 blocked, ICMP open)

### Diagnosis (perform in order)
1. **Check DNS and direct fallback IP reachability:**
```bash
dig +short api.telegram.org
curl --connect-timeout 10 -s https://api.telegram.org/bot<TOKEN>/getMe
curl --connect-timeout 10 -s --resolve "api.telegram.org:443:149.154.167.220" "https://api.telegram.org/bot<TOKEN>/getMe"
```
2. **Check gateway logs for fallback IP attempts:**
```bash
tail -30 ~/.hermes/logs/gateway.log | grep -iE "(telegram|fallback|timedout|connect)"
```
3. **Check systemd env (if gateway runs via systemd):**
```bash
systemctl --user show hermes-gateway --show-environment | grep TELEGRAM
```

### Fix: Sticky Fallback IP via systemd environment
Some Telegram IPs (e.g. `149.154.166.110`) are blocked while others (e.g. `149.154.167.220`) remain reachable. Use `systemctl --user set-environment` for persistence across restarts.

```bash
# 1. Set fallback IP
systemctl --user set-environment TELEGRAM_FALLBACK_IPS="149.154.167.220"

# 2. Reload daemon and restart gateway
systemctl --user daemon-reload
systemctl --user restart hermes-gateway

# 3. Verify gateway picked up the fallback
sleep 3
tail -20 ~/.hermes/logs/gateway.log | grep "fallback IPs active"
# Expected: "Telegram fallback IPs active: 149.154.167.220"

# 4. Check gateway status
systemctl --user status hermes-gateway --no-pager | head -5
```

### Fix: SOCKS5 Proxy (if fallback IPs also fail)
If the only working fallback IP is temporary, configure a SOCKS5 proxy (Shadowsocks, VLESS, etc.).

Add to `~/.hermes/.env`:
```
TELEGRAM_PROXY=socks5://127.0.0.1:1080
```
Requires running `ss-local` (or equivalent) to expose SOCKS5 locally.

### Post-Repair Verification
```bash
# Direct API test via fallback IP
BOT_TOKEN="..."
CHAT_ID="..."
curl -s --connect-timeout 15 --max-time 30 \
  --resolve "api.telegram.org:443:149.154.167.220" \
  "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -d "chat_id=${CHAT_ID}" -d "text=Test OK"
```

### Agent Self-Rescue When send_message Times Out Despite Active Gateway
**Trigger:** User asks to send something to Telegram; `send_message` returns `Timed out`; `systemctl --user status hermes-gateway` shows `active (running)`.

There are **THREE** distinct failure patterns. Diagnose before assuming.

**Pattern A: DNS Resolution Failure (most common)**
The gateway's own Telegram polling loop may connect fine via sticky fallback IP, but `send_message` uses a separate Python `httpx`/`urllib3` path that resolves DNS independently through the system resolver (`systemd-resolve`, `/etc/resolv.conf`).

If DNS returns a blocked IP (e.g., `149.154.166.110`), Python tries to connect there and times out — even though gateway logs show `using sticky fallback IP 149.154.167.220`.

**Diagnose DNS:**
```bash
# Check what DNS returns
resolvectl query api.telegram.org
# vs what curl sees
curl -s --connect-timeout 4 --resolve "api.telegram.org:443:149.154.167.220" \
  "https://api.telegram.org/botFAKE/getMe" -w "\nHTTP: %{http_code}\n"
```
If `resolvectl` returns blocked IPs and curl with `--resolve` works → it's a DNS problem, not a handle problem.

**Fix for DNS failure:**
```bash
# Option 1: Hardcode working IP in /etc/hosts (persistent, survives reboot)
echo "149.154.167.220 api.telegram.org" | sudo tee -a /etc/hosts

# Option 2: Use curl with --resolve (one-shot, for emergency delivery)
# See Direct Curl Rescue below

# Option 3: Set up local DNS override via systemd-resolved
sudo resolvectl dns eno1 8.8.8.8  # or other working resolver
```

**Pattern B: send_message Tool Lacks Fallback Transport**
The `send_message` tool in Hermes WebUI (`hermes_webui/tools/telegram_tools.py`) instantiates its own `Bot` via `python-telegram-bot` using `HTTPXRequest(proxy=...)` — it does **NOT** use the gateway's `TelegramFallbackTransport`. Even when gateway is healthy with sticky fallback IPs, `send_message` independently resolves DNS and tries to connect to whatever `api.telegram.org` resolves to.

**Check:** If `resolvectl query api.telegram.org` returns a working IP and gateway is active, but `send_message` still times out → likely this pattern (the tool's transport has no fallback).

**Fix:** Patch the tool to add fallback. See `references/send_message_tool_patch.md` for the exact patch.

**Pattern C: Stale CLI Handle (classic G2)**
The gateway process is healthy, but the stdio bridge between this CLI session and the gateway was severed during a previous restart. `/new` fixes this.

**DO NOT loop on send_message.** After 1 failure, diagnose, then switch to rescue mode.

**Rescue decision tree:**
```
send_message timed out
  → check resolvectl query api.telegram.org
  → returns blocked IP (149.154.166.110)?
     YES → DNS problem → /etc/hosts fix OR curl --resolve
  → returns working IP?
     YES → check if send_message tool is patched
     → tool NOT patched → apply patch from references/send_message_tool_patch.md
     → tool patched → check gateway logs
     → gateway logs show "connected" and "polling"?
        YES → stale CLI handle → /new or curl rescue
        NO  → gateway itself broken → restart gateway
```

**Direct Curl Rescue (when token is accessible):**
If the token is not masked and you can read it from env or systemd show:
```bash
TOKEN=$(systemctl --user show hermes-gateway --show-environment | grep TELEGRAM_BOT_TOKEN | cut -d= -f2-)
curl -s --connect-timeout 10 --max-time 30 \
  --resolve "api.telegram.org:443:149.154.167.220" \
  -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{"chat_id":CHAT_ID,"text":"MESSAGE"}'
```

If token is masked (`***`) in Hermes output, direct curl is impossible from the agent. Tell the user: "Gateway is healthy but DNS resolves to blocked IP and I can't read the masked token. Options: (1) I deliver here, (2) you fix /etc/hosts, (3) you run `/new` if it's a handle issue."

**Fall back to current channel**: Deliver the content in the current chat (terminal / webui) so the user doesn't lose the work. Never leave a user's request hanging because of a delivery channel failure.

**Anti-pattern observed:** Re-trying `send_message` 2+ times with identical arguments wastes time, triggers tool-loop warnings, and annoys the user. Stop after first failure, diagnose, fallback.

### CLI Handle Staleness Note
After gateway restart, the old CLI session may retain a stale handle to the dead gateway process. `send_message` may continue to time out even though the gateway is healthy. This is **expected** — start a new CLI session (`/new`) or send directly via curl.

### systemd Environment Persistence Without Sudo
User-level systemd units often don't load `.env` files automatically. To make environment variables persistent across restarts **without sudo**:

```bash
# 1. Create an override directory
mkdir -p ~/.config/systemd/user/hermes-gateway.service.d

# 2. Write an override.conf with EnvironmentFile
cat > ~/.config/systemd/user/hermes-gateway.service.d/override.conf <<'EOF'
[Service]
EnvironmentFile=/tmp/hermes-telegram.env
EOF

# 3. Reload daemon
systemctl --user daemon-reload

# 4. Restart service
systemctl --user restart hermes-gateway
```

This requires no sudo — user-level systemd overrides live in `~/.config/systemd/user/`. See `references/systemd_user_override.md` for a full template.

### Pitfalls
| Problem | Cause | Fix |
|---------|-------|-----|
| `systemctl --user set-environment` resets after reboot | Stored only in active systemd user instance | Add `Environment=TELEGRAM_FALLBACK_IPS=...` to systemd override or `.env` |
| `dig` returns a different IP than the working one | DNS round-robin / geo-DNS | Hardcode working IP via `TELEGRAM_FALLBACK_IPS` |
| `send_message` still times out after gateway fix | Old CLI session holds stale stdio handle | Run `/new` or use direct curl |
| `ss-local` on 1080 not running | Only `ss-server` configured | Run `ss-local -c /etc/shadowsocks-libev/config.json` |

---

## References

- `references/webui-default-model-refresh.md` — WebUI picker still shows an old default model after config edit: server-side verification + browser cache cleanup
- `references/webui-startup-failures.md` — Real case: git-conflict SyntaxError in Python causing WebUI CPU spin
- `references/cron-health-check-example.md` — Cron task example for recurring health checks
- `references/systemd-unit-template.md` — Template for creating user-level systemd units
- `references/nginx-csrf-sse-fix.md` — nginx config snippet for CSRF + SSE behind reverse proxy
- `references/disk-space-cleanup.md` — Freeing disk space on a small root filesystem when a large secondary disk exists; covers whole-repo deletion, incremental cleanup, and moving Hermes state to secondary storage.
- `references/secondary-disk-archive-workflow.md` — Step-by-step archive and migration of heavy developer directories (npm/nvm/rustup caches, Chrome profiles, projects, workspace) to `/mnt/data/natan-storage`, including symlink pitfalls and active-port verification.
- `references/secondary-disk-migration.md` — Step-by-step migration of heavy user directories (npm cache, nvm, rustup, Chrome profiles, projects) to a secondary disk using `rsync` + symlinks; includes safety checklist and pitfalls.
- `references/browser-automation-options.md` — Choosing between Hermes' built-in CDP browser, `browser-use`, Comet, and remote-debugging when bot protection or persistent profiles are required.
- `references/pm2-nodejs-service-config.md` — Full PM2 ecosystem config for Next.js/Node.js apps with production safeguards (memory limits, restart backoff, anti-npm-wrapper pattern)
- `references/gateway-connectivity-diagnostic.md` — Gateway connectivity diagnostic
- `references/pm2-multiversion-cwd-pitfall.md` — Detecting and fixing stale `cwd` in multi-version PM2 configs (copied ecosystem.config.js pointing to wrong project directory)
- `references/telegram-fallback-ip-fix.md` — Full runbook: diagnosing Telegram Bot API blocks, selecting working fallback IPs, systemd env persistence, and SOCKS5 setup
- `references/skill-profile-sync.md` — Syncing skills between Hermes profiles (e.g., shifu → default): inventory, diff, skip-common, copy-missing, verify, update Obsidian registry
- `references/send_message_tool_patch.md` — Exact patch for `hermes_webui/tools/telegram_tools.py` to add `TelegramFallbackTransport` to the `send_message` tool
- `references/systemd_user_override.md` — How to add `EnvironmentFile` to a user-level systemd service without sudo
- `references/hermes-profile-creation.md` — Creating profiles, custom working directories (CLI wrapper `cd` pattern), profile anatomy, switching between CLI and WebUI
- `references/gateway-telegram-selective-proxy.md` — Selective SOCKS5 proxy for Hermes Telegram adapter: Xray from a VLESS subscription, leaving nginx/Next.js traffic untouched
- `references/sqlite-binary-merge-smart.md` — Resolving git conflicts in tracked SQLite `.db` files by smart-merging structured `template_data` instead of choosing `ours`/`theirs` blindly.
## Cron Job Template

To schedule recurring health checks, use the `cronjob` tool:
```
Schedule: 0 */2 * * *   # every 2 hours
Prompt: System Health Check. Run ops-health-check phases 1-7, log results.
        If any critical issue found → alert user.
Enabled toolsets: terminal, file
Skills: hermes-ops-devops
```
