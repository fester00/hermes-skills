# Hermes WebUI — Systemd Service Deployment

The WebUI can run as a user-level systemd service (`hermes-webui.service`) in addition to the manual `python3 bootstrap.py` / `python3 server.py` workflow. This is how it behaves on systems where `hermes setup` or `hwebui_start.sh` was used.

## Service File

Location: `~/.config/systemd/user/hermes-webui.service`

```ini
[Unit]
Description=Hermes Agent WebUI
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/natan/hermes-webui
EnvironmentFile=-/home/natan/hermes-webui/.env
ExecStart=/home/natan/.hermes/hermes-agent/hwebui_start.sh
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

Key points:
- `Restart=always` — **killing the Python process manually triggers automatic restart within 5 seconds.**
- `EnvironmentFile` loads `~/hermes-webui/.env` on every restart.
- Port is controlled by `HERMES_WEBUI_PORT` in that `.env` file.

## Management Commands

```bash
# Check status
systemctl --user status hermes-webui

# Restart cleanly
systemctl --user restart hermes-webui

# Stop completely
systemctl --user stop hermes-webui

# Start after manual stop
systemctl --user start hermes-webui

# Enable/disable autostart
systemctl --user enable hermes-webui
systemctl --user disable hermes-webui
```

## Common Pitfall: Multiple Python Processes / Wrong Port

If the service runs with `Restart=always` and there is ALSO a manually-started `python server.py` process (e.g. from a previous dev session), you may see **two listening ports** simultaneously (e.g. 18789 from the service and 8787 from the manual process). The systemd service will keep restarting its copy regardless of pkill.

**Fix:**
1. Identify who owns each port: `ss -tlnp | grep -E '8787|18789'`
2. Kill the manual process (not the systemd one).
3. Use `systemctl --user restart hermes-webui` for all future lifecycle management.

## Logs

```bash
# Service logs
journalctl --user -u hermes-webui -f

# Or the WebUI's own log files in the repo directory
tail -f ~/hermes-webui/*.log
```

## Relation to `hwebui_start.sh`

`ExecStart` points to `hwebui_start.sh` inside the Hermes agent source tree. This script is the bootstrap wrapper that sets up the venv and runs `server.py`. Do not edit the service's `ExecStart` directly; instead change environment variables via `~/hermes-webui/.env`.
