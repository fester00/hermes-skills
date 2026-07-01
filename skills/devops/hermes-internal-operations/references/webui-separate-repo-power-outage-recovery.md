# WebUI Restart Recipe — Separate `~/hermes-webui` Install

Use this reference when the user reports that the Hermes WebUI is down after a power outage or reboot, and the install is the standalone `hermes-webui` repository on port 18789.

## Context

The user runs Hermes WebUI from `/home/natan/hermes-webui` on `127.0.0.1:18789`, fronted by nginx at `https://130.255.9.9:8443/`. After a power outage the process does not auto-restart and nginx returns 502 Bad Gateway.

## Quick restart command

```bash
cd /home/natan/hermes-webui && ./ctl.sh start
```

Then wait 5–10 seconds and verify:

```bash
cd /home/natan/hermes-webui && ./ctl.sh status
```

Expected healthy output:

```
● hermes-webui — running
  PID:     <number>
  Uptime:  00:06
  Bound:   127.0.0.1:18789
  Log:     /home/natan/.hermes/webui.log
  Health:  ok
```

## Diagnosis if it still does not answer

1. Check whether anything is listening on the port:
   ```bash
   ss -tlnp | grep 18789
   ```
2. Check the latest log lines:
   ```bash
   tail -50 /home/natan/.hermes/webui.log
   ```
3. Common failure: `OSError: [Errno 98] Address already in use` means a stale process still holds port 18789. Stop, verify, then start again:
   ```bash
   cd /home/natan/hermes-webui && ./ctl.sh stop
   ss -tlnp | grep 18789
   pgrep -f "hermes-webui/server.py"
   # if any process remains, kill it manually
   cd /home/natan/hermes-webui && ./ctl.sh start
   ```
4. If nginx still returns 502, restart nginx:
   ```bash
   sudo systemctl restart nginx
   ```

## Auto-start after reboot

`ctl.sh` does not auto-start. For systems with frequent power outages, add a systemd user unit or a cron `@reboot` entry:

```cron
@reboot cd /home/natan/hermes-webui && ./ctl.sh start
```

Use `crontab -e` as the user that owns the WebUI process.

## Notes

- The `.env` file at `/home/natan/hermes-webui/.env` sets `HERMES_WEBUI_PORT=18789` and `HERMES_WEBUI_ALLOWED_ORIGINS=https://130.255.9.9:8443`.
- Password protection is configured via `HERMES_WEBUI_PASSWORD` in the same `.env`.
- This reference was created from the recovery performed on 2026-06-27.
