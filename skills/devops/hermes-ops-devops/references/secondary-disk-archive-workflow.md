# Secondary-Disk Archive & Migration Workflow

Session-specific reference for moving heavy developer directories from a tight primary filesystem (`/`) to a large secondary disk (`/mnt/data`) while keeping originals intact for safety, then optionally replacing originals with symlinks to free space.

## Context

- Primary disk: small root LV (`/dev/mapper/ubuntu--vg-ubuntu--lv`, ~57 GB).
- Secondary disk: large data partition mounted at `/mnt/data` (916 GB, ~870 GB free).
- User wants cold copies first, then optionally delete originals and/or symlink back.

## Safe archive procedure

1. Create base directory on secondary disk:
   ```bash
   mkdir -p /mnt/data/natan-storage
   ```

2. Copy directories with `cp -a` to preserve permissions, timestamps, and dotfiles:
   ```bash
   for dir in .hermes .nvm .npm .chrome-vk-profile .rustup pentajunior-v2 vidvis workspace/ligalink; do
     cp -a "/home/natan/$dir" "/mnt/data/natan-storage/$(basename $dir)-copy"
   done
   ```
   (The `-copy` suffix avoids collisions and lets you review before final naming.)

3. Rename copies to final names and remove the staging container:
   ```bash
   for dir in /mnt/data/natan-storage/*-copy; do
     mv "$dir" "${dir%-copy}"
   done
   # Remove the empty staging directory if you created one
   rmdir /mnt/data/natan-storage/backups 2>/dev/null
   ```

4. Verify copy sizes match originals:
   ```bash
   du -sh /home/natan/{.hermes,.nvm,.npm,.chrome-vk-profile,.rustup,pentajunior-v2,vidvis} /home/natan/workspace/ligalink
   du -sh /mnt/data/natan-storage/{.hermes,.nvm,.npm,.chrome-vk-profile,.rustup,pentajunior-v2,vidvis,ligalink}
   ```
   Note: `du -sh /path/*` does **not** include hidden directories in the listing. Check dotfiles explicitly:
   ```bash
   du -sh /mnt/data/natan-storage/.{hermes,nvm,npm,chrome-vk-profile,rustup}
   ```

## Replacing originals with symlinks (freeing primary disk space)

Only after verifying the copies are complete.

### Toolchain directories (safe to symlink)

For `.npm`, `.nvm`, `.rustup` you must **remove the original directory first**, then create the symlink at the old path. A symlink *inside* the directory is wrong and does not free space.

```bash
rm -rf /home/natan/.npm /home/natan/.nvm /home/natan/.rustup
ln -s /mnt/data/natan-storage/.npm  /home/natan/.npm
ln -s /mnt/data/natan-storage/.nvm  /home/natan/.nvm
ln -s /mnt/data/natan-storage/.rustup /home/natan/.rustup
```

Verify tools still work:
```bash
node --version
npm --version
nvm --version      # requires: export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
cargo --version
rustc --version
```

### Project directories (verify ownership first)

Before deleting a project original, confirm which process owns its port and where its working directory points:

```bash
ss -tlnp | grep -E ':3000|:3001'
readlink -f /proc/<PID>/cwd
```

Then either symlink (if the service must keep starting from the old path):
```bash
rm -rf /home/natan/vidvis
ln -s /mnt/data/natan-storage/vidvis /home/natan/vidvis
```

Or delete the original if the copy is sufficient and the old path is no longer referenced:
```bash
rm -rf /home/natan/pentajunior
rm -rf /home/natan/.chrome-vk-profile
rm -rf /home/natan/.mozilla
```

### Workspace

The whole `~/workspace` directory can also be copied:
```bash
cp -a /home/natan/workspace /mnt/data/natan-storage/workspace
```

If you later replace `~/workspace` with a symlink, remember that skills and references may still mention `~/workspace/ligalink`. After the move, the canonical LigaLink path becomes either:
- `/mnt/data/natan-storage/ligalink` (the original separate copy), or
- `/mnt/data/natan-storage/workspace/ligalink` (if workspace was moved as a whole).

Decide on one convention and update references accordingly.

## Default location for new projects

For this user, **new projects should be created on the secondary disk by default**:

```
/mnt/data/natan-storage/<project-name>
```

Only create a project under `/home/natan/` if the user explicitly requests a specific path. The active legacy projects (`pentajunior-v2`, `~/workspace`) remain on the primary disk for now; do not move them without explicit approval.

This rule applies to:
- New code projects (Next.js, React Native, Python, Rust, etc.)
- New repositories cloned by the user via the agent
- New ad-hoc directories that are likely to grow large

When in doubt, ask: "Create in `/mnt/data/natan-storage/`?"

## What was archived/migrated in this session

| Original path | Final location | Size | Disposition | Notes |
|---|---|---|---|---|
| `~/.hermes` | `/mnt/data/natan-storage/.hermes` | 7.0 GB | Cold copy only | Hermes profiles, webui, state snapshots. Not symlinked yet due to higher risk. |
| `~/.nvm` | `/mnt/data/natan-storage/.nvm` | 2.2 GB | Symlinked back | Node versions `v24.13.0` and `v24.13.1`. Commands verified. |
| `~/.npm` | `/mnt/data/natan-storage/.npm` | 1.9 GB | Symlinked back | npm cache and npx cache. Commands verified. |
| `~/.chrome-vk-profile` | `/mnt/data/natan-storage/.chrome-vk-profile` | 2.6 GB | Deleted original | Chrome profile for VK. Copy kept on secondary disk. |
| `~/.rustup` | `/mnt/data/natan-storage/.rustup` | 1.4 GB | Symlinked back | Rust toolchain. `cargo`/`rustc` verified. |
| `~/pentajunior-v2` | `/mnt/data/natan-storage/pentajunior-v2` | 1.7 GB | Cold copy only | Active Next.js project on port 3000. Not symlinked; original kept on primary disk. |
| `~/pentajunior` | — | — | Deleted | Confirmed unused: port 3000 was served from `pentajunior-v2`, not `pentajunior`. |
| `~/vidvis` | `/mnt/data/natan-storage/vidvis` | 894 MB | Deleted original | Project for port 3001. Not running at check time; copy kept on secondary disk. |
| `~/workspace/ligalink` | `/mnt/data/natan-storage/ligalink` | 580 MB | Copied separately | Also available inside `/mnt/data/natan-storage/workspace/ligalink` after full workspace copy. |
| `~/workspace` | `/mnt/data/natan-storage/workspace` | 584 MB | Cold copy only | Entire workspace copied; original left on primary disk. |
| `~/workspace` | `/mnt/data/natan-storage/workspace` | 584 MB | Cold copy only | Entire workspace copied; original left on primary disk. |
| `~/zhopa` | `/mnt/data/natan-storage/zhopa` | 88 MB | Cold copy only | Ad-hoc archive of arbitrary heavy directory. |

## Result of this session

- Primary disk usage dropped from ~50 GB to ~40 GB (about 10 GB freed).
- Free space on `/` increased from **4.6 GB** to **15 GB**.
- All toolchain commands (`node`, `npm`, `nvm`, `cargo`, `rustc`) verified working via symlinks.
- Active project `pentajunior-v2` on port 3000 remained untouched on the primary disk.

## Common pitfalls

| Pitfall | Why it happens | Fix |
|---|---|---|
| Symlink created *inside* `.npm`/`.nvm`/`.rustup` instead of replacing it | Forgetting to `rm -rf` the original first | Remove original directory, then `ln -s` to the old path |
| `du -sh /path/*` misses hidden directories | Shell glob `*` skips dotfiles | Check `.dirs` explicitly with `du -sh /path/.{a,b,c}` or list with `ls -la` |
| Tools fail after symlink | Shell still has old directory open or `NVM_DIR` not loaded | Open a new shell, load `nvm.sh`, verify versions |
| Service breaks after deleting project original | Process was running from the old path | Verify `readlink -f /proc/<PID>/cwd` before deletion; symlink if needed |
| Workspace convention confusion | `ligalink` exists both as `/mnt/data/natan-storage/ligalink` and inside `/mnt/data/natan-storage/workspace/ligalink` | Pick one canonical path and update references. If `~/workspace` is later symlinked, `~/workspace/ligalink` still resolves correctly; otherwise prefer the direct `/mnt/data/natan-storage/ligalink` path in docs/skills. |
| Forgetting to push the migration note | Obsidian note created but repo left dirty | After writing a new system note to the vault, run `git status`, stage, commit, and push so other agents/sessions see the canonical paths. |

## Browser automation note

For tasks that require a real user profile (cookies, logins, marketplace access), Hermes' built-in headless CDP browser is insufficient because it has no persistent profile. The user explored `browser-use` (github.com/browser-use/browser-use) as a separate Python/CLI agent that can drive a local Chrome instance with the user's real profile.
