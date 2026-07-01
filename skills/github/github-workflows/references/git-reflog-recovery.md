---
name: git-reflog-recovery
description: Recover deleted commits after git reset --hard, force-push, or branch deletion using reflog + cherry-pick. Restore lost work without rewriting public history when possible.
version: 1.0.0
author: Master Ugwai
updated: 2026-05-13
tags: [git, recovery, reflog, cherry-pick, undo, history]
metadata:
  hermes:
    tags: [git, recovery, reflog, cherry-pick, undo, history]
---

# Git Reflog Recovery

Recover commits that were "lost" after `git reset --hard`, `git rebase`, force-push, or branch deletion. The reflog keeps a local history of HEAD movements for 90 days by default.

## Anatomy of Data Loss

### What survives
- `git reflog` — tracks **all** HEAD movements locally in your repo
- `git fsck --lost-found` — finds **unreachable commits** (detached objects)
- `git log --all --oneline --graph` — shows references across all refs

### What does NOT survive
- Commits already garbage-collected (`gc`) — typically after reflog expiry (90 days for reachable, 30 days for unreachable)
- Commits on a different machine (unless they were pushed and still exist on remote)
- `git clean -fdx` deletes untracked files, NOT commits

---

## Core Workflow

### Step 1: Inspect reflog

```bash
# Full reflog with timestamps
git reflog --date=iso

# Compact view — hash + action + subject
git reflog --format="%h %gd %gs"
```

Key entries to look for:
- `HEAD@{n}: commit:` — a commit that still exists in DAG
- `HEAD@{n}: reset: moving to <hash>` — the point where commits were discarded
- `HEAD@{n}: rebase` — commits moved during rebase
- `HEAD@{n}: merge:` — merge points

### Step 2: Identify target commits

```bash
# View a specific reflog entry's diff
git show HEAD@{4}

# Show stats for quick scanning
git show --stat HEAD@{4}

# Check which commits are unreachable but still stored
# (detached from all branches/tags)
git fsck --lost-found --unreachable 2>&1 | grep commit | head -20
```

### Step 3: Preview the commit

```bash
# See full diff
git cherry-pick <hash> --no-commit
git diff --cached
# ... inspect ...
git reset --hard HEAD  # if bad
```

### Step 4: Cherry-pick (preferred for linear restore)

```bash
# Apply a single commit to current branch
git cherry-pick <hash>

# Apply without auto-commit, for inspection
git cherry-pick <hash> --no-commit
# Later: git add -A && git commit -m "..."    OR    git reset --hard HEAD

# Apply multiple consecutive commits (range)
git cherry-pick <hash1>^..<hashN>

# Apply without creating a commit if all three are already reviewed
git cherry-pick <hash1> --no-commit
git cherry-pick <hash2> --no-commit
git cherry-pick <hash3> --no-commit
git add -A && git commit -m "restore: recovered 3 lost commits via reflog"
```

### Step 5: Re-create branch from lost commit

```bash
# If a branch was deleted, create it again at the old commit
git checkout -b recovered-branch <hash>

# Or if you already have a branch and want to fast-forward it
git checkout main
git merge <hash>
```

---

## Scenario: Force-Pushed Deleted Commits

This is the most common data-loss scenario for teams.

### State
- User force-pushed `main` to an earlier commit
- Remote now lacks commits A, B, C
- Your local reflog still has them (if you pulled before force-push)
- Or the commit hashes are visible in GitHub/GitLab "Recent pushes" / event API

### Recovery

```bash
# Step 1 — find the lost commits in reflog
git reflog | head -30

# Example output:
# 60a35fa HEAD@{0}: reset: moving to 1e64f4e
# 71f1fa4 HEAD@{1}: commit: refactor(phinance): use useFullStatistics...
# 1b78d73 HEAD@{2}: commit: refactor: unified notifications system...
# 7d16a4c HEAD@{3}: commit: fix: remove API v2 remnants...
# 1e64f4e HEAD@{4}: reset: moving to 1e64f4e

# Step 2 — cherry-pick in order (oldest first if they depend on each other)
# Use --no-commit to batch them into a single commit
git cherry-pick 7d16a4c --no-commit
git cherry-pick 1b78d73 --no-commit
git cherry-pick 71f1fa4 --no-commit

# Step 3 — verify
git diff --staged --stat

# Step 4 — commit
git add -A
git commit -m "restore: recover N deleted commits via reflog cherry-pick"

# Step 5 — push (force-push if you already force-pushed, otherwise normal)
git push origin main
# Or if you already force-pushed earlier:
# git push --force-with-lease origin main
```

---

## Scenario: Branch Accidentally Deleted

```bash
# Find the branch HEAD in reflog
git reflog | grep "checkout:.+old-branch-name"

# Or search by commit message
git log --all --oneline --grep="feature name"

# Re-create
git checkout -b old-branch-name <hash>
```

---

## Scenario: `git reset --hard` Overwrote Working Tree

```bash
# The commits are still in reflog
git reflog
# HEAD@{1} was the state before reset

# Option A: cherry-pick back
git cherry-pick HEAD@{1}

# Option B: restore working tree without creating a commit
git checkout HEAD@{1} -- .
# (restores files only, no new commit)

# Option C: move branch pointer back
git reset --hard HEAD@{1}
```

---

## Scenario: Merge Accidentally Undone

```bash
git reflog | grep "merge"
git cherry-pick <merge-commit-hash> --no-commit
# Manually resolve, then commit
```

---

## Advanced: Recovery Without Reflog

If reflog is unavailable (e.g., fresh clone, or `git gc --prune=now`):

```bash
# Find dangling commits via fsck
git fsck --lost-found --dangling --unreachable 2>&1 | grep commit | head -20

# Inspect each one
git show 7d16a4c

# Or export them
git fsck --lost-found --dangling > /tmp/dangling.txt
```

---

## Recovery Decision Tree

```
Commits lost?
├── Was it on your machine and reflog exists?
│   ├─ YES → use git reflog → cherry-pick
│   └─ NO  → go to next question
├── Were the commits pushed (even if then force-pushed away)?
│   ├─ YES → check remote reflog / GitHub events API / ask teammate
│   └─ NO  → go to next question
├── Was gc run recently (<30 days)?
│   ├─ YES → git fsck --lost-found, inspect dangling commits
│   └─ NO  → probably gone forever
└── Was there another clone (teammate, CI, backup)?
   └─ YES → recover from that clone's reflog
```

---

## Pitfalls

1. **Cherry-pick creates NEW commit hashes** — the recovered commits have different hashes than originals. If someone else references the old hashes, the references break.

2. **Conflicts during cherry-pick** — if the current branch diverged from the lost commits, cherry-pick will throw conflicts. Resolve manually or use `git cherry-pick --abort`.

3. **Cherry-picking in wrong order** — if commit B depends on A's changes, always cherry-pick A first, then B. Use `--no-commit` to batch without intermediate states.

4. **Reflog is LOCAL** — it doesn't travel with `git clone`. If you only have a fresh clone, reflog won't help. Always keep a local backup before destructive operations.

5. **Force-push is DANGEROUS** — prefer `git push --force-with-lease` which aborts if someone else pushed since you last pulled.

6. **Don't cherry-pick merge commits** — unless you use `git cherry-pick -m 1 <merge-hash>`. For non-merge commits it's always safe.

---

## Verification Checklist

After recovery, always verify before pushing:

```bash
git log --oneline -10                    # Check commit messages
git diff HEAD~<N> --stat                 # Check files changed
git diff HEAD~<N>~1..HEAD~<N> --name-only   # Per-commit files
```

---

## See Also

- `github-repo-management` — force-push safety (`--force-with-lease`)
- `github-pr-workflow` — protecting branches to prevent force-push
- `references/case-force-push-squashed-recovery.md` — real case: user force-pushed, recovered via cherry-pick, squashed, then wanted to "delete" the original commits
- Git official docs: `git help reflog`
