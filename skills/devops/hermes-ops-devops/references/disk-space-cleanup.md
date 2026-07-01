# Disk Space Cleanup on Small Root + Large Secondary Disk

## Trigger

Root filesystem `/` is tight (e.g., 57G LV at 86-90% used) while a secondary disk such as `/mnt/data` has hundreds of gigabytes free.

## Diagnosis

```bash
df -h / /home
```

Then find the biggest consumers:

```bash
du -sh ~/* 2>/dev/null | sort -rh | head -10
du -sh ~/.hermes/* 2>/dev/null | sort -rh | head -20
```

Common Hermes-related large targets:
- `~/.hermes/hermes-agent` — source + venv (~2-3GB)
- `~/.hermes/profiles/<profile>/state-snapshots` — can exceed 500MB
- `~/.hermes/profiles/<profile>/state.db` — can exceed 200MB
- `~/.hermes/webui` — state + uploaded files
- `~/.hermes/logs` — old gateway/webui logs
- `~/.npm`, duplicate `node_modules`, `~/.cache`

## Safe Big Wins

### 1. Delete an obsolete whole project repo
When the user explicitly says "delete `<repo>`" (e.g., `~/pentajunior-v3`):

1. Check no active process references it:
```bash
ps aux | grep -iE '<repo>' | grep -v grep
lsof +D ~/<repo> 2>/dev/null | head -5
```
2. Verify it is not a currently served production directory (check nginx, systemd, PM2, or common ports).
3. Remove it:
```bash
rm -rf ~/<repo>
```
4. Recheck disk space:
```bash
df -h /
```

### 2. Incremental cleanup (when user wants to keep projects)

Rotate old logs:
```bash
find ~/.hermes -name "*.log" -mtime +7 -delete
```

Clear npm cache (can exceed 6GB):
```bash
npm cache clean --force
```

Find stale build outputs / duplicate `node_modules`:
```bash
find ~ -maxdepth 3 -type d \( -name node_modules -o -name .next \) -mtime +30 -exec du -sh {} \; 2>/dev/null | sort -rh | head -20
```

Vacuum Hermes session store only after warning the user that history will be compacted (this is usually not necessary; deleting old sessions is safer):
```bash
# sqlite3 ~/.hermes/state.db "VACUUM;"
```

## Moving Data to Secondary Disk

If root is still tight, move large directories to the secondary disk and replace them with symlinks.

Good candidates:
- `~/projects`
- `~/workspace`
- `~/.hermes/profiles`
- `~/.hermes/sessions`

Example:
```bash
# Move
mv ~/.hermes/profiles /mnt/data/hermes-profiles
# Link back
ln -s /mnt/data/hermes-profiles ~/.hermes/profiles
```

Always restart services after moving state directories, and verify paths in `config.yaml` or systemd units.

## Decision Tree

```
User asks to free space
  → df -h (identify tight filesystem)
  → du -sh ~/* / ~/.hermes/* (find top consumers)
  → Is there a clearly obsolete project/duplicate?
     YES → check active processes → rm -rf → df -h
     NO  → incremental cleanup: logs, npm cache, .next builds → recheck
  → Still >90%? → consider moving data to secondary disk
```

## Local Example

On this user's host:
- `/` is 57G, typically 86-88% used
- `/mnt/data` is ~916G with ~870G free
- The user is comfortable deleting whole obsolete repos (e.g., `~/pentajunior-v3`) after a quick process check.
