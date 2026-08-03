# Syncing local skills to hermes-skills repo

Use when the user asks to update the public skill-library repo so it matches the local `~/.hermes/skills` state.

## Goal

The GitHub repo at `/home/natan/hermes-skills` (origin `https://github.com/fester00/hermes-skills.git`) should reflect the locally used skills under `~/.hermes/skills`.

## Safe workflow

1. Inspect state:
   ```bash
   cd /home/natan/hermes-skills
   git status --short
   git log --oneline HEAD -5
   https_proxy=http://127.0.0.1:1081 git log --oneline origin/main -5
   ```
   Pull with `https_proxy=http://127.0.0.1:1081 git pull origin main` if remote is ahead.
2. Create backup branch:
   ```bash
   git branch backup-before-sync-$(date +%Y%m%d)
   ```
3. Ensure `.gitignore` excludes Hermes local state files:
   ```
   .bundled_manifest
   .curator_backups/
   .curator_state
   .archive/
   .usage.json
   ```
4. Sync local skills into the repo directory. Because the user wants the repo to **exactly mirror** local state, `rsync --delete` is acceptable *after* a backup branch exists and after reviewing the diff:
   ```bash
   rsync -a --delete \
     --exclude=.bundled_manifest \
     --exclude=.curator_backups \
     --exclude=.curator_state \
     --exclude=.archive \
     --exclude=.usage.json \
     --exclude=.git \
     ~/.hermes/skills/ /home/natan/hermes-skills/skills/
   ```
5. Review the diff. If the user wants the repo to match local state exactly, stage all changes including deletions. If any remote-only skill should survive, restore it with `git checkout -- <path>`.
6. Commit and push. When the user explicitly wants the repo to reflect local state and remote is confirmed not ahead, use force-with-lease:
   ```bash
   git add -A
   git commit -m "sync: mirror ~/.hermes/skills to hermes-skills repository"
   https_proxy=http://127.0.0.1:1081 git push origin main --force-with-lease
   ```

## Pitfalls

- Never `rsync --delete` without a backup branch.
- Never commit Hermes local state files.
- Do not force-push if remote may contain work from another session; pull first.
- After a force-push, inform the user that the remote is now identical to local skills.

## Provenance

- 2026-08-01: sync attempt for `/home/natan/hermes-skills` initially produced 127 deletions via `rsync --delete`. A backup branch was created, deletions were reviewed, and the repo was force-pushed to mirror local state (`caedfee`). The user confirmed the repository should reflect exactly what is used locally.
