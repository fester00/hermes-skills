# obra/superpowers → Hermes Skill Mapping

Source: https://github.com/obra/superpowers (cloned to /tmp/superpowers)
Date: 2026-05-06

## Duplicate Skills (skip these)

| Superpowers Skill | Hermes Equivalent | Status |
|-------------------|-------------------|--------|
| subagent-driven-development | software-development/subagent-driven-development | ✅ exists |
| systematic-debugging | software-development/systematic-debugging | ✅ exists |
| test-driven-development | software-development/test-driven-development | ✅ exists |
| writing-plans | software-development/writing-plans | ✅ exists |
| requesting-code-review | software-development/requesting-code-review | ✅ exists |

## Adapted Skills (migrated)

| Superpowers Skill | Hermes Path | Notes |
|-------------------|-------------|-------|
| brainstorming | software-development/brainstorming | Removed Visual Companion, universalized paths |
| finishing-a-development-branch | software-development/finishing-a-development-branch | Removed harness-specific options, generic git workflow |
| verification-before-completion | software-development/verification-before-completion | Universalized, removed "human partner" refs |
| using-git-worktrees | software-development/git-worktrees | Removed harness-specific tools, kept git worktree fallback |
| receiving-code-review | software-development/receiving-code-review | Universalized for any code review |
| executing-plans | software-development/executing-plans | Removed external session refs |
| dispatching-parallel-agents | software-development/dispatching-parallel-agents | Adapted for delegate_task with tasks array |

## Skipped Skills (not applicable)

| Superpowers Skill | Reason |
|-------------------|--------|
| using-superpowers | Bootstrap plugin for Claude Code/Codex harnesses only |

## Key Adaptation Decisions

1. **Naming**: Removed "using-" and "dispatching-" prefixes where redundant in Hermes context
2. **Paths**: `docs/superpowers/specs/` → `docs/designs/` with user-preference override note
3. **Commands**: Stripped all `/plugin install`, `/add-plugin`, harness-specific commands
4. **Tables**: Converted pipe tables to bullet lists for Telegram compatibility
5. **Human partner** → **user**: Universal terminology shift
6. **Frontmatter**: Added `metadata.hermes.tags` and `metadata.hermes.related_skills` to all

## Verification

All migrated skills verified via:
```bash
hermes skills list | grep -E "brainstorming|finishing|verification|git-worktrees|receiving|executing|parallel"
hermes skills view <name>  # Content inspection
```
