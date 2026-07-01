# Case Study: Restoring Force-Pushed Commits That Were Squashed

## Scenario

User force-pushed `main`, deleting 3 commits:
1. `refactor(phinance): use useFullStatistics instead of useStatistics`
2. `refactor: unified notifications system with filter bar and date range`
3. `fix: remove API v2 remnants, fix tariff change, make auth volatile`

Later, user recovered them via reflog + cherry-pick, but **squashed all 3 into a single commit** `2e464fc` with message:
```
fix: restore removed fixes — auth volatile, v2 cleanup, tariff change, notifications refactor
```

## Recovery Steps (What Was Done)

```bash
cd /home/natan/workspace/ligalink

# Step 1: Inspect reflog to find lost commits
git reflog --date=iso

# Output showed:
# 60a35fa HEAD@{0}: reset: moving to 1e64f4e
# 71f1fa4 HEAD@{1}: commit: refactor(phinance): use useFullStatistics...
# 1b78d73 HEAD@{2}: commit: refactor: unified notifications system...
# 7d16a4c HEAD@{3}: commit: fix: remove API v2 remnants...

# Step 2: Cherry-pick all three (oldest first)
git cherry-pick 7d16a4c --no-commit
git cherry-pick 1b78d73 --no-commit
git cherry-pick 71f1fa4 --no-commit

# Step 3: Verify
git diff --staged --stat

# Step 4: Squash into single commit
git add -A
git commit -m "fix: restore removed fixes — auth volatile, v2 cleanup, tariff change, notifications refactor"

# Step 5: Push
git push origin main
```

## Lesson: User Then Wanted to "Delete" the Restored Commits

After restoring, user said "удали пожалуйста с репозитория ligalink вот эти коммиты" — referring to the ORIGINAL 3 commit messages. But they no longer existed as separate commits; they were squashed into `2e464fc`.

**The correct response**: Explain that the commits are now one squashed commit, and offer options:
1. `git reset --hard 60a35fa` + `git push --force-with-lease` — discard the squash entirely
2. `git revert 2e464fc` — undo changes with a new commit (safe if already pushed)

## Key Insight

When user references commits by their **message**, always check if they still exist as separate commits. After squash/rebase, the original commits are gone from the DAG — only the reflog remembers them. Don't promise to "delete 3 commits" when there's only 1 squashed commit on the branch.
