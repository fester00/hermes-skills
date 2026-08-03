# Sync Hermes skills and profiles to GitHub

## Goal

Keep the user's GitHub repositories (`fester00/hermes-skills`, `fester00/maximus-hermes-profile`, or similar) as durable mirrors of local Hermes state so that another machine or session can reconstruct the working environment.

## When to use

- User says "обнови репозиторий со скиллами" or "sync skills to GitHub".
- User says the remote repository must match local state exactly.
- A profile (`maximus`, `shifu`, etc.) needs to be backed up or mirrored.

## Network prerequisites

GitHub HTTPS may be blocked at TLS level for direct `git`/`curl`. Use the configured proxy:

```bash
export https_proxy=http://127.0.0.1:1081
```

This proxy is required for `git push`, `git fetch`, `gh repo list`, and `curl -I https://api.github.com`.

## Part 1: Sync `~/.hermes/skills` to `hermes-skills` repo

Local repo path: `/home/natan/hermes-skills`  
Remote: `https://github.com/fester00/hermes-skills.git`

```bash
cd /home/natan/hermes-skills

# Ensure local state files are ignored
cat > .gitignore <<'EOF'
# Hermes local state — do not commit
.bundled_manifest
.curator_backups/
.curator_state/
.archive/
.usage.json
.usage.json.lock
EOF

# Sync from active skills, excluding local-only metadata
rsync -av --delete \
  --exclude='.archive' \
  --exclude='.curator_backups' \
  --exclude='.curator_state' \
  --exclude='.hub' \
  --exclude='__pycache__' \
  --exclude='.usage.json' \
  --exclude='.usage.json.lock' \
  --exclude='.bundled_manifest' \
  ~/.hermes/skills/ skills/

find skills -type d -name '__pycache__' -exec rm -rf {} +

# Review changes before push
git status --short | head -50
git diff --stat

# Commit and push with proxy
git add -A
git commit -m "sync: mirror ~/.hermes/skills ($(date +%F))" || true
https_proxy=http://127.0.0.1:1081 git push origin main --force-with-lease
```

## Part 2: Sync a Hermes profile to GitHub

A profile contains config, memories, cron, plugins, and skills. The goal is to mirror it exactly.

1. Find the profile path:
   ```bash
   ls -la ~/.hermes/profiles/
   ```

2. Find or create the remote repository:
   ```bash
   https_proxy=http://127.0.0.1:1081 gh repo list fester00 --limit 50
   ```

   If the repo does not exist:
   ```bash
   https_proxy=http://127.0.0.1:1081 gh repo create fester00/maximus-hermes-profile --public --description "Hermes profile mirror for maximus" --source=. --remote=origin --push
   ```

3. If the repo exists but is not cloned locally, clone it:
   ```bash
   https_proxy=http://127.0.0.1:1081 git clone https://github.com/fester00/maximus-hermes-profile.git /tmp/maximus-profile
   cd /tmp/maximus-profile
   rm -rf * .gitignore
   ```

4. Sync profile contents:
   ```bash
   rsync -av --delete \
     --exclude='sessions/' \
     --exclude='state.db*' \
     --exclude='.hermes_history' \
     --exclude='audio_cache/' \
     --exclude='image_cache/' \
     --exclude='logs/' \
     --exclude='secrets/' \
     --exclude='pastes/' \
     --exclude='checkpoints/' \
     ~/.hermes/profiles/maximus/ .
   ```

   Note: `secrets/` should be excluded by default. If the user explicitly asks to include credentials, stop and ask for approval.

5. Add `.gitignore` for runtime state:
   ```bash
   cat > .gitignore <<'EOF'
   state.db
   state.db-*
   .hermes_history
   sessions/
   logs/
   audio_cache/
   image_cache/
   secrets/
   pastes/
   checkpoints/
   EOF
   ```

6. Commit and push:
   ```bash
   git add -A
   git commit -m "sync: mirror maximus profile ($(date +%F))"
   https_proxy=http://127.0.0.1:1081 git push origin main --force-with-lease
   ```

## Part 3: Verify the mirrors

```bash
https_proxy=http://127.0.0.1:1081 gh repo view fester00/hermes-skills --json url,description,updatedAt
https_proxy=http://127.0.0.1:1081 gh repo view fester00/maximus-hermes-profile --json url,description,updatedAt
```

## Pitfalls

- Do **not** commit `state.db`, `sessions/`, or `secrets/` — these contain sensitive/transient data.
- Do **not** commit local Hermes metadata (`.usage.json`, `.curator_state`, `.bundled_manifest`).
- Always create a backup branch before destructive sync:
  ```bash
  git branch backup-before-sync-$(date +%Y%m%d)
  ```
- Use `--force-with-lease` instead of `--force` when pushing to avoid overwriting remote work.
- Always check `git diff --stat` before push and warn the user about deletions.

## Session provenance

- 2026-08-01: Synced `~/.hermes/skills/` to `fester00/hermes-skills` with 217 changed files (10251 insertions, 22579 deletions). Used `https_proxy=http://127.0.0.1:1081` for GitHub access. Excluded `.archive`, `.curator_backups`, `.curator_state`, `.hub`, `__pycache__`, and usage metadata.
