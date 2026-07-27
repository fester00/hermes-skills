# Obsidian + hermes-skills Combined Sync

End-to-end recipe for keeping the Obsidian knowledge base and the public
`hermes-skills` GitHub repository consistent with the active `~/.hermes/skills/`
library.

## When to use

- User says "sync Obsidian and skills to GitHub" or "make the vault/skills repo public".
- After a skill update session where both the skill files and their Obsidian documentation changed.
- When a repository visibility change is needed (private → public).

## Preconditions

- `~/obsidian-memory/` is a git repo with `origin` pointing to GitHub.
- `~/hermes-skills/` is a git repo with `origin` pointing to GitHub.
- `gh` CLI is authenticated and can read/write both repositories.
- The user has approved publishing or visibility changes.

## Step-by-step

### 1. Inspect current state

```bash
cd ~/obsidian-memory
git status --short
git log --oneline -5
git remote -v

cd ~/hermes-skills
git status --short
git log --oneline -5
git remote -v
```

### 2. Check repo visibility on GitHub

```bash
gh repo view fester00/obsidian-memory --json isPrivate,visibility,url,name
gh repo view fester00/hermes-skills   --json isPrivate,visibility,url,name
```

### 3. Sync skill files to hermes-skills

```bash
cd ~/hermes-skills
rsync -av --delete \
  --exclude='.archive' \
  --exclude='.curator_backups' \
  --exclude='.hub' \
  --exclude='.git' \
  ~/.hermes/skills/ skills/

# Remove runtime artefacts that should never be committed
find skills -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null

# Verify counts
find skills -maxdepth 3 -type f -name 'SKILL.md' | wc -l
```

### 4. Update hermes-skills README

Refresh the README so its structure, stats, and cross-links match the actual
directory tree. Common changes:

- Add/remove top-level categories.
- Update the active skill count.
- Add new key skills to the spotlight table.
- Ensure cross-links to Obsidian still point to valid paths.

### 5. Audit Obsidian skill indices

Check and update at least these files:

- `Operations/MOC — Skills.md`
- `Operations/Skills/Hermes — Skills Registry.md`
- `Operations/Skills/Hermes Skills Repository.md`
- `Operations/Skills/Hermes — Loaded Skills Reference.md` (if links become stale)

Look for:
- Missing categories (e.g., `shopping`).
- Skills that moved to archive but still listed as active.
- Broken links to renamed skills.
- Duplicate rows.
- Count mismatches between the registry and the actual `~/.hermes/skills/` tree.

### 6. Commit and push hermes-skills

```bash
cd ~/hermes-skills
git add -A
git status --short | wc -l
git commit -m "sync: update skills from ~/.hermes/skills (YYYY-MM-DD)

- <high-level changes, categories, counts>"
git push origin main
```

### 7. Commit and push obsidian-memory

```bash
cd ~/obsidian-memory
git add -A
git status --short
git commit -m "docs(skills): sync skill indices with ~/.hermes/skills (YYYY-MM-DD)

- <which files changed and why>"
git push origin main
```

### 8. Change visibility if needed

```bash
# Make public via API (gh repo edit --visibility does not accept --confirm)
gh api repos/<owner>/<repo> -X PATCH -f visibility=public
```

Verify:

```bash
gh repo view <owner>/<repo> --json isPrivate,visibility,url,name
```

## Verification checklist

- [ ] `git status` clean in both repos.
- [ ] Skill count in `hermes-skills` matches `~/.hermes/skills/` active count.
- [ ] No `__pycache__`, `.env`, or SSH keys committed.
- [ ] README cross-links open in browser.
- [ ] Obsidian links resolve (no red links in Obsidian graph if applicable).
- [ ] Both repos pushed to `origin/main`.
- [ ] Visibility matches user request.

## Common pitfalls

- `rsync --delete` without excludes will wipe `.archive/`, `.curator_backups/`,
  and `.hub/` from the source if the destination is the source path. Always
  double-check source vs destination before running.
- `gh repo edit --visibility public --confirm` does not exist; use the API.
- Counting skills only at depth 2 misses nested mlops subcategories; scan to
  depth 3 or inspect the `.bundled_manifest`.
- A clean `git status` in Obsidian does not mean indices are correct; always
  compare lists with the actual `~/.hermes/skills/` tree.
