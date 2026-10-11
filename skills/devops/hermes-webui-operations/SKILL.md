---
name: hermes-webui-operations
description: Use when operating the Hermes WebUI. Manage process lifecycle, nginx proxy, uploads, CSRF origins, and recovery.
version: 1.0.0
author: Master Ugwai
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [hermes, webui, nginx, devops, troubleshooting, upload]
    related_skills: [hermes-internal-operations, hermes-agent]
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

#### Hard recovery: systemd lost the process but the port is still bound

If `systemctl --user status hermes-webui.service` shows `activating (auto-restart)` or the process is `deactivating`, yet `ss -tlnp | grep 18789` still shows a `python server.py` process, systemd has lost track of the actual `server.py`. A plain `systemctl restart` will keep failing with `FATAL: Another server is already responding` because the orphan process holds the port.

Recover in this exact order:

```bash
# 1. Stop the systemd unit (so it stops auto-restarting into the occupied port)
systemctl --user stop hermes-webui.service

# 2. Verify the orphan server.py is still there
ss -tlnp | grep 18789
ps aux | grep 'hermes-webui/server.py' | grep -v grep

# 3. Kill only the orphan server.py by PID (do not kill stealth-browser or other python processes)
kill <PID>

# 4. Confirm the port is free
ss -tlnp | grep 18789 || echo "port 18789 free"

# 5. Start cleanly via systemd
systemctl --user start hermes-webui.service

# 6. Verify both local and proxied endpoints
systemctl --user status hermes-webui.service --no-pager | head -5
ss -tlnp | grep 18789
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:18789/health
curl -s -o /dev/null -w "%{http_code}\n" -k https://130.255.9.9:8443/health
```

If multiple agents or supervisors are operating on WebUI concurrently, coordinate so only one of them performs the recovery — otherwise one agent kills the process another agent just started. When a second agent reports a different PID than systemd, that agent is looking at stale state; trust `systemctl --user status` and `ss -tlnp` over the second agent's narrative.

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

## Сбой модели ≠ сбой интерфейса (не перезапускай службу)

Симптом: интерфейс пишет «Request timed out. Please try again.», и первое желание — перезапустить службу. **Сначала проверь, что служба действительно виновата:**

```bash
systemctl --user is-active hermes-webui.service
journalctl --user -u hermes-webui.service --since "-15min" | grep -oE '"path": "[^"]*"[, ]*"sta[^,]*' | tail -12   # видны 200-е?
timeout 10 curl -s --noproxy '*' -o /dev/null -w '%{http_code}\n' http://127.0.0.1:18789/health
```

Если служба активна и отдаёт 200 — **перезапуск не поможет**, врет модель. Диагностика в два шага:

1. **Сессия:** модель лежит прямо в файле сессии — `/mnt/data/natan-storage/.hermes/webui/sessions/<id>.json`, поле `model`. Id сессии виден в логе (`/api/session?session_id=<id>`).
2. **Дампы падений:** рядом лежат `request_dump_<session_id>_<дата>.json` — в них готовый диагноз: `error.type`, `status_code`, `request.url` и тело запроса. Это быстрее, чем гадать по логу.

**Проверенный случай (2026-10-11).** Сессия на модели `claude-haiku-5-5` провайдера `opencode-go` падала с `400 ModelProtocolUnsupported: Model does not support this protocol`. Причина: у этого агрегатора Claude-модели говорят по **Anthropic Messages**, а Hermes шлёт OpenAI-совместимый `chat/completions`. Проба одного и того же ключа с заголовком `x-opencode-session`:

```
chat/completions + deepseek-v4.1-flash → 200        chat/completions + claude-haiku-5-5 → 400 ModelProtocolUnsupported
chat/completions + kimi-k2.7-code      → 200        POST /v1/messages + claude-haiku-5-5 → 200 (заголовки x-api-key + anthropic-version)
chat/completions + minimax-m3          → 200
```

Три следствия:

- **Лечение — сменить модель у сессии** (через интерфейс, там есть выбор модели), а не перезапускать службу.
- **Правку файла сессии вручную служба затирает:** она держит сессию в памяти и перезаписывает JSON при следующем же запросе. Меняй модель только через UI/его API (а API закрыт парольной авторизацией).
- **При пробах агрегатора обязателен заголовок `x-opencode-session`** (любой uuid): без него любой запрос отбивается 400 с текстом «Request is missing x-opencode-session» — легко принять это за поломку модели.

В коде Hermes такие провайдеры помечены `is_aggregator=True` (`hermes_cli/providers.py`), протокол определяется по метаданным модели; если модель не размечена — берётся `chat_completions`.

## Recovery checklist

1. `systemctl --user status hermes-webui.service --no-pager | head -5` — is the service active or auto-restarting?
2. `ss -tlnp | grep 18789` — who owns the port?
3. `tail -n 50 ~/.hermes/webui.log` — any Python traceback?
4. `sudo nginx -t` — nginx config valid?
5. When another agent reports conflicting process state, re-run steps 1 and 2 yourself before acting on the other agent's claim.
- `references/ctl-sh-vs-systemd-conflict.md` — when `ctl.sh` and a systemd user service both try to supervise the same port
- `references/webui-upload-limits.md` — nginx + WebUI upload tuning
- `references/webui-update-workflow.md` — safe `git pull` + `systemctl --user restart` update path
- `references/multi-agent-recovery-coordination.md` — avoid ping-pong when multiple agents try to recover WebUI concurrently

## Related

- `hermes-agent` skill for general Hermes CLI and gateway commands
- `references/ctl-sh-vs-systemd-conflict.md` — when `ctl.sh` and a systemd user service both try to supervise the same port
- `hermes-agent` skill for general Hermes CLI and gateway commands
- `hermes-internal-operations` / `hermes-ops-devops` for broader Hermes ops

## Notes

- Overlaps intentionally with `hermes-internal-operations` and `hermes-ops-devops`. This skill focuses narrowly on WebUI + nginx + upload/recovery. Background curator may consolidate later.
- Do not store credentials in this skill. Sudo password belongs in `~/.hermes/.env` if the agent needs automated sudo; keep that file mode 600.
