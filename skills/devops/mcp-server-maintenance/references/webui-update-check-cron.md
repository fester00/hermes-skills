# Hermes WebUI update check in weekly cron job

How to add a WebUI git-update check to the existing `mcp-update-checker` cron job.

## Why only check, not auto-update

The Hermes WebUI is a live service. Auto-pulling `origin/master` and restarting could:
- introduce incompatible API changes,
- break a running session,
- leave the gateway/WebUI out of sync.

The cron job should **report** that updates are available and provide the exact manual command. The user applies it when ready.

## Cron job additions

Add this section to the existing `mcp-update-checker` prompt:

```
4. Hermes WebUI: git repository at /home/natan/hermes-webui
   (origin https://github.com/nesquena/hermes-webui.git)
   - Run `git fetch origin master` (use https_proxy=http://127.0.0.1:1081 if needed).
   - Compare HEAD with origin/master using `git log --oneline HEAD..origin/master`.
   - Report how many commits behind and the latest commit on origin/master.
   - Do NOT run `git pull` or restart the service automatically.
   - Provide the exact manual update command:
     cd /home/natan/hermes-webui && git pull origin master && systemctl --user restart hermes-webui.service
```

## Commands the cron agent should run

```bash
cd /home/natan/hermes-webui
git fetch origin master
behind=$(git rev-list --count HEAD..origin/master)
latest=$(git log --oneline -1 origin/master)
echo "WebUI is $behind commits behind origin/master (latest: $latest)"
```

## Expected output format

```
4. **Hermes WebUI** — update available
   - Installed: 5f3117f8 (Merge pull request #6788)
   - Latest: e168b67e (exp-v0.52.264)
   - $behind commits behind.
   - Update: cd /home/natan/hermes-webui && git pull origin master && systemctl --user restart hermes-webui.service
```

If `behind == 0`, output:
```
4. **Hermes WebUI** — up to date
```

## Updating the cron job

```bash
hermes cron list
hermes cron update <job_id> --prompt "...updated prompt..."
```

## Real example from 2026-08-27

The repo was 255 commits behind `origin/master` (5f3117f8 → e168b67e, exp-v0.52.264). Update applied manually with:

```bash
cd /home/natan/hermes-webui
cp .env /tmp/hermes-webui.env.backup
git pull origin master
/mnt/data/natan-storage/.hermes/hermes-agent/venv/bin/pip install -r requirements.txt  # if changed
systemctl --user restart hermes-webui.service
curl -s http://127.0.0.1:18789/health | head -c 100
```

In this case `requirements.txt` did not change.
