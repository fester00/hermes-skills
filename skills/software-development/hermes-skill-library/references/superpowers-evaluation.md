# Case Study — Evaluating obra/superpowers

**Date:** 2026-07-10
**External repo:** https://github.com/obra/superpowers
**Decision:** Do not install as a plugin; adapt methodology into a local umbrella skill.

## What the repo offers

A popular (251k stars) agentic software-development methodology with composable
skills:

- `brainstorming` — design refinement before code
- `writing-plans` — bite-sized implementation plans
- `using-git-worktrees` — isolated workspaces
- `subagent-driven-development` — fresh subagent per task + two-stage review
- `test-driven-development` — RED-GREEN-REFACTOR
- `requesting-code-review` / `receiving-code-review`
- `finishing-a-development-branch` — merge/PR/cleanup
- `dispatching-parallel-agents` — parallel failure investigation
- `verification-before-completion` — evidence before claims

## Critical observation

Superpowers is a **methodology + skill text**, not an MCP server or external
service. It ships as plugins for Claude Code, Cursor, Codex, etc., but the
actual value is in the skill instructions. Hermes can run the same workflow
natively with `delegate_task` and local skills.

## Local overlap

| superpowers skill | Local equivalent | Coverage |
|---|---|---|
| `writing-plans` | `writing-plans` | Already had core pattern; patched with no-placeholders and self-review |
| `subagent-driven-development` | `subagent-driven-development` | Already based on it; patched stronger implementer/reviewer prompts |
| `test-driven-development` | `test-driven-development` | Already aligned; added umbrella cross-link |
| `requesting-code-review` | `requesting-code-review` | Local version adds security scan + auto-fix loop; added umbrella cross-link |
| `using-git-worktrees` | partial in `hermes-software-development-workflow` | Could be split into standalone skill if used often |
| `finishing-a-development-branch` | partial in `hermes-software-development-workflow` | Could be split if used often |
| `dispatching-parallel-agents` | partial in `hermes-software-development-workflow` | Could be split if parallel debugging becomes common |
| `verification-before-completion` | partial in `hermes-software-development-workflow` | Could be split if explicit verification gates become common |

## What we adapted

1. Created umbrella skill `superpowers-workflow` that maps the Superpowers
   stages to local Hermes skills.
2. Patched `writing-plans` with Superpowers-style no-placeholders rules,
   Global Constraints block, and self-review checklist.
3. Patched `subagent-driven-development` with stronger "ask before guessing"
   language and report-format expectations.
4. Cross-linked TDD and code-review skills to the new umbrella.

## What we did not adopt

- Superpowers plugin infrastructure (not compatible with Hermes).
- `mcp-sequential-thinking` (separate repo, same session) — not needed;
  Hermes todo/session_search/Obsidian already cover persistence.

## Lesson

When an external repo is a **methodology packaged as agent instructions**, do
not install it blindly. Map its stages to local skills, identify gaps, and
adapt the missing pieces into class-level local umbrellas. The result is
lighter, dependency-free, and tailored to the local runtime.
