---
name: superpowers-workflow
description: |
  Umbrella workflow for Hermes: adapt the Superpowers software development
  methodology (design → plan → delegate → execute → verify → finish) inside a
  single Hermes session. Use whenever building or refactoring software.
category: software-development
related_skills:
  - hermes-software-development-workflow
  - codebase-memory-audit
  - writing-plans
  - subagent-driven-development
  - test-driven-development
  - requesting-code-review
  - using-git-worktrees
  - finishing-a-development-branch
  - dispatching-parallel-agents
  - verification-before-completion
---

# Superpowers Workflow for Hermes

Apply the Superpowers software-development methodology inside Hermes.

**Core loop:**

```
Design → Plan → Isolate → Execute → Verify → Finish
```

This is an umbrella skill. It does not replace the focused skills above; it tells
you which one to load at each stage and how to move between stages.

---

## When to use

Use this skill whenever the user asks to:
- build a feature
- refactor code
- fix a complex bug
- add or modify software in any project

Do NOT use for:
- one-liner shell commands
- pure explanations or consultations
- tasks the user explicitly wants done without a plan

---

## Phase 0: Knowledge Discovery (before design)

Before Phase 1 (Design), load the most relevant prior knowledge:

1. `session_search` — prior conversations about this project.
2. `skills_list` + `skill_view` — project-specific skills.
3. Obsidian vault — project notes, runbooks, prior audits.
4. Project files — README, recent commits, directory structure.

### Karpathy lens (applied throughout)

Four principles from Andrej Karpathy's coding guidelines, used as a filter in every phase:

1. **Think Before Coding** — state assumptions explicitly, present multiple interpretations, surface tradeoffs, stop and ask when confused.
2. **Simplicity First** — minimum code that solves the problem; no speculative features, single-use abstractions, or unnecessary flexibility.
3. **Surgical Changes** — touch only what the request requires; clean up only the mess your changes create.
4. **Goal-Driven Execution** — every task must have verifiable success criteria before implementation begins.

These principles do not replace the workflow stages; they shape how each stage is executed.

### Optional: codebase-memory-audit

If the user is asking about a project with **more than 5 files**, or asks
architecture/refactoring/dependency questions, or this is the first exploration:
- Load `codebase-memory-audit`.
- Ensure the project is indexed via the `codebase-memory` MCP server or the CBM CLI.
- Run `get_architecture(aspects=['all'])` to get hotspots, layers, boundaries, clusters, entry points.
- Save summary to `~/obsidian-memory/Projects/<project>/codebase-memory-audit.md`.
- Use the audit in design and planning.

Skip for single files, one-liners, throwaway prototypes.

> **Why CBM:** codebase-memory-mcp is faster than graphify, exposes 14 structural
> query tools (search_graph, trace_path, search_code, query_graph, etc.), supports
> 158 languages, and needs no LLM API key. The index persists in `~/.cache/codebase-memory-mcp`
> and can be refreshed incrementally.

### Optional: lazy-review mode

If the user says any of these, or you detect over-engineering risk, treat the
session as **lazy-review informed**:

- "be lazy", "minimal solution", "do less", "shortest path"
- "what can we delete?", "is this over-engineered?", "simplify"
- "ponytail", "lazy senior dev"

**What changes in the workflow:**
- Design phase explicitly asks: "Can we solve this by deleting or reusing existing code?"
- Plan tasks include a **deletion/simplification scan** before adding new files.
- Execution phase: when touching a file, check nearby code for duplication, dead code, stdlib/native alternatives.
- Review phase: run `lazy-review` (internal check or subagent) to catch over-engineering.

**What does NOT change:**
- Master Ugwai persona stays the same.
- Approval gates, verification, TDD, and `codebase-memory-audit` remain in force.
- No automatic commits or pushes without explicit "задеплой".

> **Karpathy + Ponytail principle embedded:** The best code is the code you never wrote.
> Before adding, check the Karpathy lens: assumptions stated, simplicity first, surgical scope, verifiable goal.
> Then rung the ladder: YAGNI → reuse in codebase → stdlib → native → installed
> dependency → one line → minimum code. Never cut validation, security, error
> handling, accessibility, or explicitly requested behavior.

---

## Phase 1: Design (Brainstorm)

**Goal:** agree on *what* to build before writing code.

1. Load the most specific skill for the project (`skills_list` → `skill_view`).
2. Check memory (`session_search`) and Obsidian for prior work.
3. State assumptions explicitly. If multiple interpretations exist, present them — don't pick silently.
4. Ask clarifying questions **one at a time**.
5. Propose 2–3 approaches with trade-offs.
6. Get explicit approval before any code.

**Hard gate:** no implementation until the user approves the design.

> **Karpathy check:** before claiming the design is ready, confirm assumptions are named, interpretations surfaced, and success criteria defined.

---

## Phase 2: Plan

**Goal:** produce a detailed, task-by-task implementation plan.

1. Load `writing-plans`.
2. Save plan to `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md` or `docs/plans/`.
3. Every task must be 2–5 minutes, with exact file paths and verification commands.
4. End plan with hand-off marker:
   > "Use `superpowers-workflow` → `subagent-driven-development` to implement task-by-task."

---

## Phase 3: Isolate

**Goal:** work in a safe, isolated workspace.

1. Load `using-git-worktrees` (or follow its logic).
2. Detect existing isolation first (`GIT_DIR` vs `GIT_COMMON`).
3. If not isolated, ask user whether to create a worktree.
4. Verify clean baseline: run tests, confirm passing.

---

## Phase 4: Execute

Pick the execution strategy based on task shape.

### 4A: Single session (small or tightly coupled)
- Load `executing-plans`.
- Work through tasks in the main session.
- Run verifications exactly as written in the plan.
- Before editing any function, grep its callers and nearby helpers. Prefer updating the shared function once over adding parallel guards in every caller.
- When touching a file, scan the surrounding code for:
  - duplication that can be merged,
  - dead code that can be deleted,
  - old helpers that can be generalized or removed,
  - hand-rolled logic replaceable by stdlib, native platform features, or an already-installed dependency.

### 4B: Subagent-driven (recommended for multi-task plans)
- Load `subagent-driven-development`.
- Fresh `delegate_task` subagent per task.
- In each task context, include the lazy-first ladder and the "scan nearby code" rule.
- Two-stage review after each task:
  1. Spec compliance — did it match the plan?
  2. Code quality — is it well-built?
- Fix and re-review before moving on.

### 4C: Parallel dispatch (independent failures)
- Load `dispatching-parallel-agents`.
- Dispatch up to 3 `delegate_task` subagents concurrently.
- After they return, integrate, run full suite.

**Constraints on this setup:**
- Max 3 concurrent `delegate_task` subagents.
- Max 2 concurrent heavy CLI agents (OpenCode / Claude Code / Codex).
- Do NOT delegate web search or browser tasks to subagents.

---

## Phase 5: Verify

**Goal:** evidence before claims.

1. Load `verification-before-completion`.
2. Identify the command that proves the claim.
3. Run it fresh. Read the full output.
4. Only then claim success.

For new features / bugfixes:
- Load `test-driven-development`.
- Write failing test first (RED).
- Make it pass (GREEN).
- Clean up (REFACTOR).

> **Karpathy check:** every task should have been stated with verifiable success criteria before execution. If it wasn't, define them now before verifying.

---

## Phase 6: Review

**Goal:** catch issues before they cascade.

1. Load `requesting-code-review`.
2. Dispatch reviewer subagent after each task in SDD mode.
3. Fix Critical issues immediately.
4. Fix Important issues before proceeding.
5. Note Minor issues for later.

---

## Phase 7: Finish

**Goal:** integrate the work cleanly.

1. Load `finishing-a-development-branch`.
2. Run full test suite.
3. Detect workspace state (normal repo / worktree / detached HEAD).
4. Present 4 options:
   1. Merge locally
   2. Push and create PR
   3. Keep as-is
   4. Discard
5. Execute chosen option.
6. Only clean up worktrees we created under `.worktrees/` or `worktrees/`.

---

## Quick reference

| Stage | Skill to load | Output |
|---|---|---|
| Design | project-specific skills + questions | approved design |
| Plan | `writing-plans` | plan file |
| Isolate | `using-git-worktrees` | clean workspace |
| Execute | `subagent-driven-development` / `executing-plans` / `dispatching-parallel-agents` | implemented tasks |
| Verify | `verification-before-completion` + `test-driven-development` | fresh evidence |
| Review | `requesting-code-review` | reviewed code |
| Finish | `finishing-a-development-branch` | merged/PR/kept/discarded |

---

## Anti-patterns

- Skipping design for "simple" changes.
- Writing code before a failing test.
- Claiming completion without running verification.
- Trusting subagent success reports blindly.
- Cleaning up a worktree the user needs for PR iteration.
- Delegating web search or browser navigation to subagents.

---

## References

- `hermes-software-development-workflow` — full lifecycle with Hermes-specific details
- `writing-plans` — plan authorship
- `subagent-driven-development` — task-by-task delegation with two-stage review
- `test-driven-development` — RED-GREEN-REFACTOR
- `requesting-code-review` — pre-merge review
- `using-git-worktrees` — workspace isolation
- `finishing-a-development-branch` — merge/PR/cleanup
- `dispatching-parallel-agents` — parallel failure investigation
- `verification-before-completion` — evidence before claims
- `references/lazy-review-prompts.md` — Ponytail-style minimalism without a second persona
- `references/platform-native-patterns.md` — quick-reference for stdlib/native/platform solutions before adding dependencies
