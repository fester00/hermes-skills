---
title: "WebUI: ctl.sh vs systemd double-supervisor conflict"
date: 2026-07-22
tags: [hermes, webui, systemd, ctl.sh, pitfall]
---

# WebUI: `ctl.sh` vs systemd double-supervisor conflict

## Symptom

- `cd ~/hermes-webui && ./ctl.sh start` prints `Started Hermes WebUI (PID X)`.
- `./ctl.sh status` immediately says `hermes-webui — stopped`.
- Logs show: `[!!] FATAL: Another server is already responding on 127.0.0.1:18789. Stop the existing instance first.`
- Each `ctl.sh start` attempt increments the crash counter; the port never frees.
- `ss -tlnp | grep 18789` shows a `server.py` whose PPID is `systemd --user` (PID 1152 or similar), not the bootstrap shell.

## Root cause

The host runs WebUI under a **systemd user service** (`hermes-webui.service`), typically via `ExecStart=/home/natan/hermes-webui/start.sh ...` with `Restart=always`. `start.sh` invokes `bootstrap.py --foreground`, which `exec`s `server.py` in the same cgroup.

When you later run `./ctl.sh start`, `ctl.sh`:
1. Spawns `bootstrap.py` in a subshell,
2. Writes the subshell's PID into `~/.hermes/webui.pid`,
3. `bootstrap.py --foreground` then `exec`s `server.py`, **replacing** the subshell process image.

Result:
- The PID in `webui.pid` now points to a dead or different process.
- If systemd already has a `server.py` on the port, the new bootstrap sees `Address already in use` and exits.
- `ctl.sh status` checks `webui.pid`, finds it stale, and reports "stopped" even though systemd's instance is healthy.

## Diagnosis

```bash
# 1. Check for a systemd user service
systemctl --user status hermes-webui.service --no-pager | head -5

# 2. Check who owns the port
ss -tlnp | grep 18789
# Example output:
# LISTEN 0 64 127.0.0.1:18789 0.0.0.0:* users:(("python",pid=311061,fd=7))

# 3. Confirm the owner is under systemd
ps -o pid,ppid,cmd -p 311061
# PPID should be systemd --user (e.g. 1152), not a bash/ctl.sh process.
```

## Fix

Use systemd directly. Do **not** fight it with `ctl.sh` or manual `kill` loops.

```bash
# Restart into the freshly checked-out code
systemctl --user restart hermes-webui.service

# Verify
systemctl --user status hermes-webui.service --no-pager | head -10
ss -tlnp | grep 18789
curl -s http://127.0.0.1:18789/health | python3 -m json.tool
```

If you really need the port free first:

```bash
systemctl --user stop hermes-webui.service
# Wait for the port to drain
ss -tlnp | grep 18789 || echo "port free"
```

## After a code update

When `~/hermes-webui` is updated via `git pull`:

```bash
cd ~/hermes-webui
git fetch origin
git log --oneline HEAD..origin/master | head -5   # inspect upcoming changes
git pull --ff-only origin master
systemctl --user restart hermes-webui.service
```

No need for manual process cleanup — systemd's `WorkingDirectory=/home/natan/hermes-webui` ensures the restart loads the new code.

## Anti-patterns

| Don't | Why |
|-------|-----|
| `kill $(lsof -t -i:18789)` in a loop | systemd immediately restarts it; you wage war against `Restart=always` |
| Trust `./ctl.sh status` when systemd owns the service | PID file tracks the wrong process; it will say "stopped" while the service is healthy |
| Run `./ctl.sh start` after `systemctl restart` | Two supervisors race for the same port; logs fill with `Address already in use` |
| Run `ctl.sh start --no-browser` to "update" after a `git pull` | `ctl.sh` will keep spawning orphan bootstrap processes that crash with `Address already in use` while the systemd instance continues running the old code. Always use `systemctl --user restart hermes-webui.service` instead. |

## Why `ctl.sh` is not a supervisor

`ctl.sh` is a convenience wrapper for interactive development. It is **not** a process supervisor:
- It cannot see a `server.py` started by systemd.
- Its `status` checks `~/.hermes/webui.pid`, which may point to a dead bootstrap shell after `execv`.
- Its `start` does not prevent concurrent instances when another supervisor is active.

On hosts where WebUI is enabled as a systemd user service, treat `ctl.sh` as a diagnostic helper (`./ctl.sh logs` or `./ctl.sh env`) and use `systemctl` for lifecycle.

## Related

- Skill: `hermes-webui-operations`
- Skill: `hermes-ops-devops` (systemd / live service debugging)
- Upstream repo: https://github.com/nesquena/hermes-webui
