# Migrating Heavy Directories to a Secondary Disk

## Trigger

Root filesystem `/` is nearly full (e.g., >90%) while a second physical disk exists and is mostly empty, typically mounted at `/mnt/data`.

## Diagnosis

```bash
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINT,TYPE
df -h /
df -h /mnt/data
du -h /home/$USER --max-depth=1 2>/dev/null | sort -h | tail -20
```

Verify the secondary disk is permanently mounted in `/etc/fstab` (not just a temporary mount):

```bash
cat /etc/fstab | grep /mnt/data
```

## What to move

Move directories that are large, relatively self-contained, and not required to live on root by the OS or Hermes core.

| Candidate | Typical size | Safe to move? | Notes |
|---|---|---|---|
| `~/.npm` | 1-3 GB | ✅ Yes | npm cache; recreate with `npm cache clean --force` or move + symlink |
| `~/.nvm/versions` | 1-3 GB | ✅ Yes | Node binaries; symlink the whole `~/.nvm` or versions subdir |
| `~/.rustup` | 1-2 GB | ✅ Yes | Rust toolchains; keep `~/.cargo` unless it is also large |
| `~/.chrome-*-profile` | 1-5 GB | ⚠️ Only if Chrome not currently running | Must stop Chrome first, then move + symlink |
| `~/downloads` | varies | ✅ Yes | User downloads |
| `~/workspace`, `~/projects` | varies | ✅ Yes | Project working trees |
| `~/pentajunior-v2`, `~/vidvis` | varies | ✅ Yes | Specific projects; update systemd/PM2 units if they point to the old path |
| `~/.hermes` | 5-10 GB | ⚠️ Partial | `~/.hermes/hermes-agent` (source + venv) and some caches can be moved, but `profiles/`, `sessions/`, `state-snapshots/` should stay or be moved with extreme care — Hermes expects them at `~/.hermes`. Test thoroughly if symlinking the whole directory. |
| `~/.cache`, `~/.local`, `~/.config` | varies | ❌ No | Application state and settings; moving breaks many programs |

## How to move safely

### Generic pattern

```bash
SRC="/home/$USER/.npm"
DST="/mnt/data/home-$USER/.npm"

# 1. Stop anything using the directory
pkill -f npm  # example

# 2. Create destination parent
sudo mkdir -p "$(dirname "$DST")"
sudo chown "$USER:$USER" "$(dirname "$DST")"

# 3. Copy with permissions preserved
rsync -aHAX --progress "$SRC/" "$DST/"

# 4. Verify copy
du -sh "$SRC" "$DST"

# 5. Rename original (do not delete yet!)
mv "$SRC" "$SRC.bak.$(date +%Y%m%d)"

# 6. Create symlink
ln -s "$DST" "$SRC"

# 7. Test that tools still work
npm --version
npm cache verify

# 8. After a day or two of stable operation, remove the backup
rm -rf "$SRC.bak.20250704"
```

### Node/npm stack example

```bash
# Move npm cache and nvm versions
DST_ROOT="/mnt/data/home-$USER"
mkdir -p "$DST_ROOT"

# npm cache
rsync -aHAX --progress ~/.npm/ "$DST_ROOT/.npm/"
mv ~/.npm ~/.npm.bak.$(date +%Y%m%d)
ln -s "$DST_ROOT/.npm" ~/.npm

# nvm versions (symlink the whole nvm directory)
rsync -aHAX --progress ~/.nvm/ "$DST_ROOT/.nvm/"
mv ~/.nvm ~/.nvm.bak.$(date +%Y%m%d)
ln -s "$DST_ROOT/.nvm" ~/.nvm

# Update shell rc if it hardcodes ~/.nvm path (usually not needed)
grep -n NVM_DIR ~/.zshrc ~/.bashrc 2>/dev/null
```

### Chrome profile example

```bash
PROFILE="$HOME/.chrome-vk-profile"
PROFILE_NAME="$(basename "$PROFILE")"
DST="/mnt/data/home-$USER/$PROFILE_NAME"

# Must stop Chrome completely
pkill -f "user-data-dir=$PROFILE"
sleep 2

rsync -aHAX --progress "$PROFILE/" "$DST/"
mv "$PROFILE" "$PROFILE.bak.$(date +%Y%m%d)"
ln -s "$DST" "$PROFILE"

# Restart Chrome pointing at the symlinked path
DISPLAY=:100 google-chrome --user-data-dir="$PROFILE" ...
```

## What NOT to move

- `/home/$USER/.hermes` as a whole unless you have tested Hermes restart after the move and confirmed profiles/sessions load.
- Dotfiles that apps look up via `$HOME` resolution (`~/.bashrc`, `~/.zshrc`, `~/.ssh`, `~/.gnupg`).
- Active service directories referenced by systemd/PM2 units without updating those units.

## Pitfalls

| Pitfall | Why it happens | Fix |
|---|---|---|
| Symlink created inside destination instead of pointing to it | `ln -s` target path wrong | Check with `ls -l ~/`; remove bad link and recreate carefully |
| Service fails after move | Unit file or PM2 config has hardcoded old path | Update `ExecStart=`, `WorkingDirectory=`, or PM2 `cwd` |
| Chrome says profile is in use | Old Chrome process still holds files | `pkill -f chrome`, verify with `lsof +D "$PROFILE"` |
| `npm` or `nvm` not found after move | Shell cached old PATH or rc file has hardcoded path | Open new shell, check `which npm`, `nvm list` |
| rsync copies symlink loops | Source contained absolute symlinks | Use `rsync -aHAX` to preserve hardlinks/xattrs, but review first with `rsync -avn` |

## Verification checklist

After moving each directory:

1. `ls -l ~/<name>` shows symlink → `/mnt/data/...`
2. `df -h /` shows used space decreased
3. Target application starts and behaves normally
4. No process references the old `.bak` directory: `lsof +D ~/<name>.bak.YYYYMMDD`

## When to stop

Do not chase every megabyte. If root drops below 80% and services are stable, pause. Moving too many dotdirs increases the chance of a subtle path break later.
