# WebUI update recovery when stale processes fight for the port

Date: 2026-06-21  
Context: Updating `hermes-webui` from v0.51.340 to v0.51.560 on a Linux host where the WebUI was running under a user-level systemd unit (`~/.config/systemd/user/hermes-webui.service`) but a stale system-wide unit (`/etc/systemd/system/hermes-webui.service`) was still running.

## What happened

1. Fetched latest release via GitHub API: `v0.51.560` (bugfix: recovered run-journal output reaches model context).
2. Checked local version with `git describe --tags` → `v0.51.340`.
3. Stopped the user unit, checked out `v0.51.560`, restarted the user unit.
4. Service entered a crash loop with:
   ```
   [!!] FATAL: Another server is already responding on 127.0.0.1:18789. Stop the existing instance first.
   ```
5. Initial diagnosis missed the real occupant: a separate system-wide `hermes-webui.service` (started via `/etc/systemd/system/hermes-webui.service`) was still active and held the port. The user unit's restart counter climbed above 100 while the port stayed occupied.

## Recovery steps

1. **Check both systemd scopes** before any kill/restart:
   ```bash
   systemctl --user list-units --type=service | grep -i hermes-webui
   systemctl list-units --type=service | grep -i hermes-webui
   ```
2. **Stop and disable the system-wide unit** (requires sudo):
   ```bash
   sudo systemctl stop hermes-webui.service
   sudo systemctl disable hermes-webui.service
   ```
3. **Verify port is free and no stale `server.py` remains**:
   ```bash
   ss -tlnp | grep :18789
   pgrep -f "hermes-webui/server.py"
   ```
4. **If anything still holds the port**, kill it manually:
   ```bash
   ps -eo pid,lstart,cmd | grep hermes-webui/server.py | grep -v grep
   kill -9 <PID>
   ```
5. **Re-enable and start the user unit**:
   ```bash
   systemctl --user enable hermes-webui.service
   systemctl --user start hermes-webui.service
   ```
6. **Verify**:
   ```bash
   systemctl --user is-active hermes-webui.service
   curl -s http://127.0.0.1:18789/health
   cd ~/hermes-webui && git describe --tags
   ```

## Key takeaways

- A user-level systemd unit and a system-wide systemd unit can run the same service name simultaneously. They do not conflict at the systemd level, but they do conflict at the port level.
- `systemctl stop` on a unit with `Restart=always` can appear to succeed while systemd immediately respawns the process, making the restart counter explode.
- Always check **both** `systemctl --user` and `systemctl` (system-wide) listings for duplicate `hermes-webui.service` units.
- Verify the port with `ss -tlnp` and the process with `pgrep -f` — do not trust `systemctl status` alone.

## Commands to save

```bash
# Full status both scopes
systemctl --user status hermes-webui.service --no-pager
systemctl status hermes-webui.service --no-pager

# Port + process
ss -tlnp | grep :18789
pgrep -af "hermes-webui/server.py"

# Manual zombie kill (after stopping the unwanted unit)
pkill -9 -f "hermes-webui/server.py"
```
