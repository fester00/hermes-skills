---
title: "WebUI update workflow: git pull + systemd restart"
date: 2026-07-22
tags: [hermes, webui, update, systemd, git]
---

# WebUI update workflow: `git pull` + `systemctl --user restart`

Safe path for updating a running Hermes WebUI from upstream.

## When to use

- User asks to "update the WebUI" or points at https://github.com/nesquena/hermes-webui.
- The host already has a local clone at `~/hermes-webui`.
- You have just run `git pull` (or equivalent) and need the new code to become the active server.

## Procedure

### 1. Identify the supervisor

Before touching anything, determine how the server is managed:

```bash
systemctl --user status hermes-webui.service --no-pager | head -5
ss -tlnp | grep "${HERMES_WEBUI_PORT:-18789}"
```

If a systemd user service is loaded, **use systemd**, not `ctl.sh`.

### 2. Pull the new code

```bash
cd ~/hermes-webui
git remote -v                         # should point to nesquena/hermes-webui
git fetch origin
git log --oneline HEAD..origin/master | head -10   # preview
# main upstream branch is master, not main
git pull --ff-only origin master
```

Check working tree is clean after merge. If local modifications exist, either `git stash` or `git diff` them with the user before proceeding.

### 3. Restart the service

```bash
systemctl --user restart hermes-webui.service
```

This is sufficient because the unit's `WorkingDirectory=/home/natan/hermes-webui` means `start.sh`/`bootstrap.py` will load the freshly checked-out `server.py`.

### 4. Verify

```bash
systemctl --user status hermes-webui.service --no-pager | head -10
ss -tlnp | grep "${HERMES_WEBUI_PORT:-18789}"
curl -s "http://127.0.0.1:${HERMES_WEBUI_PORT:-18789}/health" | python3 -m json.tool
cd ~/hermes-webui && git log --oneline -1
```

All three should agree: the git HEAD is recent, the PID is the new one, `/health` returns `status: ok`.

## Common pitfall: duplicate "server.py" processes

If the previous server was started manually (not via systemd), or if `ctl.sh` and systemd both tried to manage the process, the old `server.py` can keep the port open. Symptom: after `git pull`, the new server crashes with:

```
[!!] FATAL: Another server is already responding on 127.0.0.1:18789.
```

Resolution:

```bash
# Stop the systemd-managed instance first
systemctl --user stop hermes-webui.service

# Kill any leftover orphan manually started earlier
for pid in $(lsof -t -iTCP:18789 -sTCP:LISTEN 2>/dev/null); do
    kill -TERM "$pid"
done
sleep 3
ss -tlnp | grep 18789 || echo "port free"

# Start cleanly through systemd
systemctl --user start hermes-webui.service
```

## Why not `ctl.sh restart` after a `git pull`?

`ctl.sh` is designed for interactive foreground/background launches. If a systemd unit already owns the port, `ctl.sh` will:

1. spawn a bootstrap shell,
2. write that shell's PID into `~/.hermes/webui.pid`,
3. `bootstrap.py --foreground` then `exec`s `server.py`, replacing the PID holder,
4. the new `server.py` fails because systemd's instance is already on the port.

So `ctl.sh status` reports "stopped" while systemd's server is actually healthy. See the sibling reference `references/ctl-sh-vs-systemd-conflict.md`.

## Checklist

- [ ] Confirmed supervisor (systemd user service / ctl.sh / manual)
- [ ] `git pull --ff-only origin master` completed
- [ ] Working tree clean (or stashed)
- [ ] `systemctl --user restart hermes-webui.service` executed
- [ ] `/health` returns `status: ok`
- [ ] Git HEAD, running PID, and `/health` uptime all reflect the update

## Related

- `references/ctl-sh-vs-systemd-conflict.md` — double-supervisor diagnosis
- `references/webui-upload-limits.md` — nginx + WebUI upload tuning
- `hermes-webui-operations/SKILL.md` — parent runbook
