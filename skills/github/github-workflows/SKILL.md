---
name: github-workflows
description: |
  Complete GitHub lifecycle: authentication, repository management, issues, PRs,
  code review, commit recovery, and codebase inspection. Covers gh CLI and git+curl
  fallbacks for headless environments.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, git, workflow, pr, issues, code-review, auth, repository]
    related_skills: [superpowers-workflow, code-quality-gates]
---

# GitHub Workflows

Complete guide for working with GitHub repositories, issues, pull requests, code review, and authentication — from initial setup through delivery and recovery.

## Quick Auth Detection

Every workflow below starts with the same auth probe:

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:***@]*)@.*|\1|')
    fi
  fi
fi

REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

---

## 1. Authentication

See `references/github-auth.md` for full setup guide covering:
- HTTPS with Personal Access Token (recommended, no sudo)
- SSH key generation and agent setup
- `gh` CLI login and token management
- Credential helper configuration
- Troubleshooting (403, key permissions, agent not running)

**Quick start:**
```bash
gh auth login        # Interactive browser flow
gh auth status       # Verify
```

---

## 2. Repository Management

See `references/github-repo-management.md` for full guide covering:
- Clone, fork, create repos
- Remote management (rename, set-url, multiple remotes)
- Releases (create, upload assets, notes)
- Secrets and variables
- Templates and repo settings
- Archive/unarchive/delete

**Quick start:**
```bash
gh repo clone owner/repo
git remote add upstream https://github.com/upstream/repo.git
git remote -v
```

---

## 3. Issues

See `references/github-issues.md` for full guide covering:
- List, search, filter issues
- Create with labels, assignees, milestones
- Triage workflows (label, close, convert to PR)
- Bulk operations and templates

**Quick start:**
```bash
gh issue list --state open --label "bug"
gh issue view 42
gh issue create --title "Bug: ..." --body "..." --label bug
```

---

## 4. Pull Request Lifecycle

See `references/github-pr-workflow.md` for full guide covering:
- Branch naming, commit hygiene, rebase vs merge
- Opening PRs with templates
- CI status checks and required reviews
- Merge strategies (merge, squash, rebase)
- Draft PRs and auto-merge

**Quick start:**
```bash
git checkout -b feature/name
git commit -m "feat: ..."
git push -u origin feature/name
gh pr create --fill
gh pr checks
gh pr merge --squash
```

---

## 5. Code Review

See `references/github-code-review.md` for full guide covering:
- Pre-push local diff review
- Reviewing open PRs (checkout, diff, comments)
- Inline comments via `gh pr review`
- Requesting changes vs approving
- Suggesting changes with code blocks

**Quick start:**
```bash
git diff main...HEAD              # What the PR contains
gh pr diff 42                     # Review someone else's PR
gh pr review 42 --approve --body "LGTM"
```

---

## 6. Commit Recovery

See `references/git-reflog-recovery.md` for full guide covering:
- `git reflog` inspection and interpretation
- Recovery after `reset --hard`, `rebase`, force-push, branch deletion
- `git fsck --lost-found` for unreachable commits
- Cherry-pick and branch-from-reflog patterns
- When recovery is impossible (gc'd, remote-only, >90 days)

**Quick start:**
```bash
git reflog --date=iso
git show HEAD@{4}
git cherry-pick <hash>
```

---

## 7. Codebase Inspection

See `references/codebase-inspection.md` for full guide covering:
- `pygount` for LOC, language breakdown, comment ratios
- Proper folder exclusions per project type
- JSON output for programmatic consumption

**Quick start:**
```bash
pip install pygount
pygount --format=summary --folders-to-skip=".git,node_modules,venv" .
```

---

## Decision Tree

| Task | Primary skill | Secondary |
|------|--------------|-----------|
| Set up GitHub access | `github-workflows` → auth section | `superpowers-workflow` |
| Create/fork/clone repo | `github-workflows` → repo section | — |
| Open a PR | `github-workflows` → PR section | `superpowers-workflow` |
| Review someone's PR | `github-workflows` → review section | — |
| File or triage bugs | `github-workflows` → issues section | — |
| Recover lost commits | `github-workflows` → recovery section | `superpowers-systematic-debugging` (reference) / `code-quality-gates` Gate 2 |
| Measure codebase size | `github-workflows` → inspection section | — |
| Pre-commit verification | `code-quality-gates` | `github-workflows` → review section |