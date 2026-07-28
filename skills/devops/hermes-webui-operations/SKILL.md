---
name: hermes-webui-operations
description: "Operate and troubleshoot the Hermes WebUI: process management, nginx reverse proxy, file upload limits, CSRF origins, and service recovery."
version: 1.0.0
author: Master Ugwai
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [hermes, webui, nginx, devops, troubleshooting, upload]
    related_skills: [hermes-internal-operations, hermes-ops-devops, hermes-agent]
---

# Hermes WebUI Operations

Runbook for operating the Hermes WebUI (https://github.com/nesquena/hermes-webui) behind nginx on a single Linux host.

## Scope

- Process lifecycle (start / stop / restart)
- nginx reverse-proxy gotchas
- File upload size limits
- CSRF / origin mismatch errors
- Quick recovery after crashes or reboots

## Key paths

| Path | Purpose |
|---|---|
| `~/hermes-webui/` | WebUI source and `ctl.sh` |
| `~/hermes-webui/.env` | WebUI-specific env vars (port, allowed origins, upload size) |
| `~/.hermes/webui.log` | Runtime log |
| `~/.hermes/hermes-agent/venv/bin/` | Hermes virtualenv with `markitdown`, `pymupdf4llm`, etc. |
| `/etc/nginx/sites-enabled/openclaw` | Example nginx site config for WebUI |

## Process management

First, determine how the WebUI is supervised on this host. Do **not** assume `ctl.sh` is the authority — check for a systemd user service first:

```bash
systemctl --user status hermes-webui.service --no-pager | head -5
systemctl list-units --type=service --user | grep hermes-webui
```

### If a systemd user service exists

Use systemd. `ctl.sh` is **not** a reliable supervisor when systemd already owns the process — it writes a PID file for the bootstrap shell, but the long-lived `server.py` may end up with a different PID (bootstrap `exec`s or systemd restarts it), making `ctl.sh status` lie and creating duplicate-process races. Running `ctl.sh start` in this state produces `FATAL: Another server is already responding` and orphan bootstrap processes.

```bash
systemctl --user restart hermes-webui.service
systemctl --user stop    hermes-webui.service
systemctl --user status  hermes-webui.service --no-pager | head -10
```

After a `git pull` update of `~/hermes-webui/`, a systemd restart is sufficient: the unit's `WorkingDirectory=/home/natan/hermes-webui` means the service will load the freshly checked-out code. See `references/webui-update-workflow.md` for the full safe-update checklist and `references/ctl-sh-vs-systemd-conflict.md` for the double-supervisor pitfall.

### If there is no systemd unit

Use the repo's launcher:

```bash
cd ~/hermes-webui
./ctl.sh status
./ctl.sh restart   # stop + start
./ctl.sh stop
./ctl.sh start --no-browser
```

The server binds `127.0.0.1:HERMES_WEBUI_PORT` (default 18789).

## nginx reverse proxy

Minimum working `location /` block when exposing WebUI on HTTPS:

```nginx
location / {
    proxy_pass http://127.0.0.1:18789;
    proxy_http_version 1.1;
    client_max_body_size 200M;        # default 1M is too small

    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_read_timeout 86400;
    proxy_send_timeout 86400;
}
```

Pitfalls:
- **CSRF 403** — set `proxy_set_header Host $http_host;` and add `HERMES_WEBUI_ALLOWED_ORIGINS=https://YOUR_HOST:PORT` in `~/hermes-webui/.env`.
- **SSE chat streaming hangs** — add `proxy_buffering off; proxy_cache off;`.
- **Upload fails silently / returns 413** — add `client_max_body_size` in nginx AND raise `HERMES_WEBUI_MAX_UPLOAD_MB` in WebUI `.env`.

## File upload limits

Two independent limits must be raised together:

1. **nginx** (`/etc/nginx/sites-enabled/<site>`):
   ```nginx
   client_max_body_size 200M;
   ```
   Then:
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

2. **WebUI** (`~/hermes-webui/.env`):
   ```bash
   HERMES_WEBUI_MAX_UPLOAD_MB=200
   ```
   Then restart WebUI:
   ```bash
   cd ~/hermes-webui && ./ctl.sh restart
   ```

Default values:
- nginx: 1 MB
- WebUI: 20 MB

## Workspace upload semantics

`/api/workspace/upload` writes into the **session workspace**, not an arbitrary absolute path. The `path` form field is a subdirectory inside that workspace. For example, if workspace is `/mnt/data/natan-storage/workspace` and user uploads into `books/js`, the file lands at `/mnt/data/natan-storage/workspace/books/js/`.

## Recovery checklist

1. `ss -tlnp | grep 18789` — is the server listening?
2. `tail -n 50 ~/.hermes/webui.log` — any Python traceback?
3. `sudo nginx -t` — nginx config valid?
- `references/ctl-sh-vs-systemd-conflict.md` — when `ctl.sh` and a systemd user service both try to supervise the same port
- `references/webui-upload-limits.md` — nginx + WebUI upload tuning
- `references/webui-update-workflow.md` — safe `git pull` + `systemctl --user restart` update path

## Related

- `hermes-agent` skill for general Hermes CLI and gateway commands
- `references/ctl-sh-vs-systemd-conflict.md` — when `ctl.sh` and a systemd user service both try to supervise the same port
- `hermes-agent` skill for general Hermes CLI and gateway commands
- `hermes-internal-operations` / `hermes-ops-devops` for broader Hermes ops

## Notes

- Overlaps intentionally with `hermes-internal-operations` and `hermes-ops-devops`. This skill focuses narrowly on WebUI + nginx + upload/recovery. Background curator may consolidate later.
- Do not store credentials in this skill. Sudo password belongs in `~/.hermes/.env` if the agent needs automated sudo; keep that file mode 600.
