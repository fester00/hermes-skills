# Case: obra/superpowers

Repo: https://github.com/obra/superpowers
Stars: 251k+. MIT license.

## What it is

A complete software-development methodology for coding agents: design → plan →
delegate → execute → verify → finish. Distributed as composable skills plus
bootstrap instructions for many agent harnesses (Claude Code, Cursor, Codex, etc.).

## Strong sides

- Battle-tested, high-quality skill library (TDD, debugging, code review, planning, worktrees).
- Two-stage subagent review (spec compliance + code quality) is a strong pattern.
- Explicit anti-patterns and red flags.
- Frequent updates (daily commits at time of evaluation).

## Red flags

- 94% PR rejection rate for agent-generated PRs; maintainers are strict.
- Designed for external harnesses, not Hermes-native.
- Some skills overlap with the user's existing Hermes skill library.

## Verdict for this user

**Use as methodology, not as a plugin.** The user already has most of the
individual skills. The right move is:

1. Compare existing Hermes skills with superpowers equivalents.
2. Patch outdated ones (writing-plans, subagent-driven-development, TDD, code review).
3. Add missing class-level skills (using-git-worktrees, finishing-a-development-branch).
4. Create an umbrella skill (`superpowers-workflow`) that ties the methodology
together inside Hermes.

Outcome: created `superpowers-workflow` umbrella skill and updated dependent
skills + Obsidian notes.
