---
date: 2026-07-04
context: Hermes WebUI separate repository at /home/natan/hermes-webui, systemd user service hermes-webui.service
---

# WebUI update v0.51.560 → v0.51.866

## What happened

The user asked to update the separate `hermes-webui` repository from `v0.51.560` to latest. During the update we discovered:

1. The systemd unit `~/.config/systemd/user/hermes-webui.service` pointed to a missing script:
   ```
   ExecStart=/home/natan/.hermes/hermes-agent/hwebui_start.sh
   ```
2. This caused the service to fail forever with `status=203/EXEC` and a restart counter climbing past 117,000.
3. After fixing the unit to use the repo's own `start.sh`, the WebUI started correctly.
4. After the update, some existing terminals reported `Command 'hermes' not found` because bash had cached the old "command not found" result for `hermes`.

## Final working unit

```ini
[Unit]
Description=Hermes Agent WebUI
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/natan/hermes-webui
EnvironmentFile=-/home/natan/hermes-webui/.env
ExecStart=/home/natan/hermes-webui/start.sh --host 127.0.0.1 18789 --no-browser
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

## Shell cache fix

Added to `~/.profile` after the `.local/bin` PATH block:

```bash
hash -r 2>/dev/null || true
```

For an already-open terminal:

```bash
export PATH="$HOME/.local/bin:$PATH"
hash -r
```

## Verification

```bash
curl -s http://127.0.0.1:18789/health
systemctl --user status hermes-webui.service --no-pager
which hermes
hermes --version
```

## Backup location

`/mnt/data/natan-storage/backups/hermes-webui-20260704-224343/`
