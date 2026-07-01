# PM2 + Next.js Service — Configuration Reference

## Real Config Applied (Session 2026-05-15, pentajunior.ru)

### Context
- Next.js 16.2.1 app
- Node v24.13.1 via nvm
- PM2 v6.0.14
- nginx reverse proxy on port 443 → localhost:3000
- Server: Ubuntu, systemd

### What Was Wrong
```
pm2 status pentajunior:
  script: /home/natan/.nvm/versions/node/v24.13.1/bin/npm
  args: start
  mode: fork
  restarts: 5 (all manual SIGINT — no crash protection configured)
  max_memory_restart: undefined
  max_restarts: undefined
```

### Fixed Configuration

`ecosystem.config.js` placed in project root (`/home/natan/pentajunior/`):

```javascript
module.exports = {
  apps: [{
    name: 'pentajunior',
    // PM2 runs the script directly with `interpreter`; it cannot execute a shell
    // wrapper. Do NOT use ./node_modules/.bin/next here — it is a shell stub.
    script: './node_modules/next/dist/bin/next',
    args: 'start',
    cwd: '/home/natan/pentajunior',
    interpreter: '/home/natan/.nvm/versions/node/v24.13.1/bin/node',
    exec_mode: 'fork',
    instances: 1,

    autorestart: true,
    restart_delay: 3000,
    exp_backoff_restart_delay: 100,
    max_restarts: 10,
    min_uptime: '10s',

    max_memory_restart: '512M',

    kill_timeout: 5000,
    listen_timeout: 5000,

    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },

    watch: false
  }]
};
```

### Verification After Fix
- `pm2 show pentajunior` → script path: `./node_modules/.bin/next` (no npm)
- `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000` → `200`
- `pm2 save` performed → dump.pm2 updated with new config
- systemd unit `pm2-natan.service` enabled → reboot survival confirmed

### Key Lessons
1. `script: './node_modules/next/dist/bin/next'` is correct for PM2 — it executes the script directly and cannot use the shell wrapper at `./node_modules/.bin/next`.
2. `pm2 save` must follow every config change, not just process start
3. Deploy scripts should use `pm2 reload ecosystem.config.js --env production`, not bare `pm2 restart`
4. `max_memory_restart` prevents kernel OOM kills on memory leaks
5. `max_restarts` + `exp_backoff_restart_delay` prevents crash-loop DoS

### Common Failure Patterns

| Pattern | Symptom | Fix |
|---------|---------|-----|
| **Shell-wrapper crash** | `SyntaxError: missing ) after argument list` at `node_modules/.bin/next:2` | Change `script` from `./node_modules/.bin/next` to `./node_modules/next/dist/bin/next` |
| **PM2 tracks npm, not Node** | App down but PM2 shows "online" | Switch to direct script path in ecosystem.config.js |
```bash
#!/bin/bash
set -e
cd ~/project
git pull origin main
npm install      # FAILS: npm: command not found
npm run build
pm2 restart app  # FAILS: pm2: command not found
```

### Correct (nvm-loaded)
```bash
#!/bin/bash
set -e

# CRITICAL: nvm.sh alone does NOT activate a node version in non-interactive shells
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 24 >/dev/null 2>&1   # <-- Must explicitly select version

cd ~/project
echo "📥 Pulling..."
git pull origin main

echo "📦 Installing..."
npm install

echo "🔨 Building..."
npm run build

echo "🔄 Restarting..."
pm2 restart app --update-env

echo "✅ Done!"
```

### Common Pitfalls
| Problem | Symptom | Fix |
|---------|---------|-----|
| `nvm use` missing | `npm: command not found` even with `nvm.sh` sourced | Add `nvm use <version>` after sourcing nvm.sh |
| Wrong node version activated | Build fails with module version mismatch | Pin exact version: `nvm use 24` or `nvm use 24.13.1` |
| Script in unexpected location | `cat ./deploy.sh: No such file or directory` | Search: `find ~ -maxdepth 2 -name "deploy.sh" -type f` |

---

## Disk Space Emergency Cleanup

When `fatal: Out of diskspace` appears during git operations or `npm install`:

### Quick Diagnosis
```bash
df -h /
du -sh ~/.npm /var/log ~/.cache 2>/dev/null
```

### Common Space Hogs
| Location | Typical Size | Safe to Clean? | Command |
|----------|-------------|----------------|---------|
| `~/.npm` (npm cache) | 2-6GB | Yes | `npm cache clean --force` |
| `/var/log` (system logs) | 1-5GB | Partially | `sudo journalctl --vacuum-time=3d` |
| `~/.next/` (build output) | 50-300MB per project | Yes (rebuilds) | `rm -rf .next/` |
| `node_modules/` | 200MB-2GB per project | No (runtime deps) | — |

### Safe Cleanup Script
```bash
# npm cache (via nvm — requires nvm use first)
bash -lic "nvm use 24 >/dev/null 2>&1; npm cache clean --force"

# System logs (journalctl)
sudo journalctl --vacuum-time=3d

# Old compressed logs
sudo find /var/log -name "*.gz" -mtime +7 -delete
sudo find /var/log -name "*.log.*" -mtime +7 -delete
```

### If still critical
1. Check `du -sh ~/* | sort -rh | head -10`
2. Alert user — may need to move large projects to secondary disk (e.g., `/mnt/data`)
