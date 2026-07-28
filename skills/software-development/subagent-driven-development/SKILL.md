---
name: subagent-driven-development
description: "Execute plans via delegate_task and OpenCode (2-stage review)."
version: 1.2.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [delegation, subagent, implementation, workflow, parallel, opencode]
    related_skills: [writing-plans, requesting-code-review, test-driven-development, opencode, orchestrator-mode, hermes-software-development-workflow]
---

# Subagent-Driven Development

## Overview

Execute implementation plans by dispatching fresh subagents per task with systematic two-stage review.

**Core principle:** Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration.

**Concurrency limits on this setup:**
- Native Hermes `delegate_task` subagents: up to 3 in parallel (config supports 4, but practical limit is 3).
- Heavy standalone CLI agents (OpenCode, Codex, Claude Code): up to 2 in parallel, launched via terminal/process tools, not counted in the `delegate_task` pool.
- Do not mix too many long-running heavy agents with many `delegate_task` subagents — total context and model throughput remain finite.

**Routing guidance:**
- Short/isolated tasks (read/write/search under ~15 min) → `delegate_task`.
- Long coding/refactoring sessions that must survive new Telegram messages → standalone CLI agent (OpenCode) launched with `terminal(background=true)`.
- Tasks needing Hermes skills/memory/browser during execution → `delegate_task`.

## When to Use

Use this skill when:
- You have an implementation plan (from writing-plans skill or user requirements)
- Tasks are mostly independent
- Quality and spec compliance are important
- You want automated review between tasks

**vs. manual execution:**
- Fresh context per task (no confusion from accumulated state)
- Automated review process catches issues early
- Consistent quality checks across all tasks
- Subagents can ask questions before starting work

## The Process

### 1. Read and Parse Plan

Read the plan file. Extract ALL tasks with their full text and context upfront. Decide execution strategy per task:

- **Lightweight tasks** (1–3 files, ≤15 min) → native `delegate_task`
- **Medium tasks** (3–5 files) → native `delegate_task` if isolated
- **Heavy tasks** (>5 files, refactoring, new site/project) → OpenCode heavy agent
- **Parallel streams** → up to 2 OpenCode agents in background
- **Web/SEO/browser tasks** → never OpenCode; keep in main session or use native subagents

### 2. Per-Task Workflow

#### Path A: Native `delegate_task` (small/medium tasks)

Use when task is isolated and fits within 25 minutes.

##### Step 1: Dispatch Implementer Subagent

Use `delegate_task` with complete context. Include:

- Full task text from the plan (files, code, commands, expected output)
- Scene-setting context (where this fits, dependencies, conventions)
- Coding principles (TDD, code quality gates) quoted below
- Explicit instruction to ask questions before guessing
- Expected report format

**Coding principles to include in every implementer context:**

```
CODE PRINCIPLES (follow strictly):
1. TDD: write the failing test first, watch it fail, write minimal code, watch it pass, refactor.
2. No production code without a failing test first.
3. One behavior per test; clear descriptive names; test real code, not mocks when possible.
4. After implementation, run the exact verification command from the plan.
5. No hardcoded secrets, SQL injection, shell injection, eval/exec with user input, or path traversal.
6. Validate user inputs; handle errors for I/O, network, DB calls.
7. Keep changes surgical — only touch files required by the task.
8. DRY and YAGNI: reuse existing helpers, prefer stdlib, no speculative abstractions.
9. Commit after every task.
10. If stuck, ask before guessing.
```

##### Step 2: Dispatch Spec Compliance Reviewer

After the implementer completes, verify against the original spec.

##### Step 3: Dispatch Code Quality Reviewer

After spec compliance passes, review code quality.

#### Path B: OpenCode heavy agent (heavy tasks)

Use when task spans >5 files, requires refactoring, or builds a site/project from a written plan.

##### Step 1: Prepare OpenCode Brief

Use the template at `templates/opencode-brief.md` in this skill. Fill:

- **Goal** — one sentence
- **Plan** — copy-pasteable tasks from the written plan
- **Project context** — tech stack, file structure, conventions
- **Coding principles** — quoted from TDD / code-quality-gates / requesting-code-review
- **Files to touch / not touch**
- **Verification commands** per task
- **Output format** — git status, test results, concerns

##### Step 2: Launch OpenCode

Use `terminal` with `background=true, notify_on_complete=true`:

```python
terminal(
    command="opencode run -f /tmp/brief.md 'Implement the attached plan task-by-task. Report status after each task.'",
    workdir="/path/to/project",
    background=True,
    notify_on_complete=True
)
```

For interactive sessions requiring iteration, use `pty=True`.

##### Step 3: Monitor

```python
process(action="list")
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")
```

##### Step 4: Verify Results

After OpenCode reports completion:
- `git status --short`
- `git diff --stat`
- Run full verification command (tests / lint / build)
- Re-read modified files

##### Step 5: Iterate

If gaps found, redispatch OpenCode with specific feedback or take over directly if partial state is broken.

### 3. Parallel Execution

- **Max 2 OpenCode agents concurrently** to avoid credential/model pool exhaustion.
- Use isolated worktrees or separate workdirs for parallel agents.
- Never let two agents edit the same files.
- Web/SEO/browser tasks never run in OpenCode; they stay in the main Hermes session.

### 4. Final Review

After all tasks complete, dispatch a final integration reviewer or run integration tests.

### 5. Verify and Commit

```bash
pytest tests/ -q
git diff --stat
git add -A && git commit -m "feat: complete [feature name] implementation"
```

## Task Granularity

**Each task = 2-5 minutes of focused work.**

**Too big:**
- "Implement user authentication system"

**Right size:**
- "Create User model with email and password fields"
- "Add password hashing function"
- "Create login endpoint"
- "Add JWT token generation"
- "Create registration endpoint"

## Red Flags — Never Do These

- Start implementation without a plan
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed critical/important issues
- Dispatch multiple implementation subagents for tasks that touch the same files
- Make subagent read the plan file (provide full text in context instead)
- Skip scene-setting context (subagent needs to understand where the task fits)
- Ignore subagent questions (answer before letting them proceed)
- Accept "close enough" on spec compliance
- Skip review loops (reviewer found issues → implementer fixes → review again)
- Let implementer self-review replace actual review (both are needed)
- **Start code quality review before spec compliance is PASS** (wrong order)
- Move to next task while either review has open issues
- Dispatch a heavy OpenCode task without a written brief containing coding principles and verification steps
- Let OpenCode perform web search, browser navigation, or SEO analysis
- Run more than 2 OpenCode agents concurrently
- Allow two parallel agents to edit the same files or share a workdir without isolation

## Handling Issues

### If Subagent Asks Questions

- Answer clearly and completely
- Provide additional context if needed
- Don't rush them into implementation

### If Reviewer Finds Issues

- Implementer subagent (or a new one) fixes them
- Reviewer reviews again
- Repeat until approved
- Don't skip the re-review

### If ACP delegation fails

If you attempted `delegate_task(acp_command="opencode")` or similar ACP-based delegation and it failed (e.g., "Could not start Copilot ACP command"), **immediately fall back to native Hermes `delegate_task` without `acp_command`**. The native subagent has the same model, terminal/file tools, and can complete the same tasks. Do NOT retry the ACP call or waste time debugging ACP setup mid-session.

### If Subagent's Work Looks Correct But the User Reports It Still Fails

A subagent may run `tsc` + `build` successfully and claim a fix is complete,
yet the user sees the original bug in the browser. Common causes:

1. **Incomplete edge coverage in the subagent's logic.** The subagent tested the
   example case the user mentioned (e.g. `unicast-trans`) but missed another
   variant (`unicast-6v`) because the matching map or normalization was
   incomplete.
2. **Stale dev/build cache.** The subagent ran `npm run build`, but the user is
   viewing an old `next dev` process that has not picked up the new build.

Controller response:

1. Verify the fix yourself in the browser against **all** related cases, not
   just the one the user originally named.
2. Check matching logic edge cases by reading the database (column headers vs
   product IDs). Look for mixed-script strings (`v` vs `В`), case differences,
   or brand prefixes that need stripping.
3. If the subagent used a partial normalization/transliteration map, extend it
   and re-test all cases.
4. Restart the local dev server on the correct port and re-test before
   deciding the subagent failed.
5. Only after your own verification fails, send the work back to a fresh
   subagent with explicit reproduction steps and the missing cases.

### If Subagent Fails a Task

- Dispatch a new fix subagent with specific instructions about what went wrong
- Don't try to fix manually in the controller session (context pollution)

## Efficiency Notes

**Why fresh subagent per task:**
- Prevents context pollution from accumulated state
- Each subagent gets clean, focused context
- No confusion from prior tasks' code or reasoning

**Why two-stage review:**
- Spec review catches under/over-building early
- Quality review ensures the implementation is well-built
- Catches issues before they compound across tasks

**Cost trade-off:**
- More subagent invocations (implementer + 2 reviewers per task)
- But catches issues early (cheaper than debugging compounded problems later)

## Integration with Other Skills

### With writing-plans

This skill EXECUTES plans created by the writing-plans skill:
1. User requirements → writing-plans → implementation plan
2. Implementation plan → subagent-driven-development → working code

### With test-driven-development

Implementer subagents should follow TDD:
1. Write failing test first
2. Implement minimal code
3. Verify test passes
4. Commit

Include TDD instructions in every implementer context.

### With requesting-code-review

The two-stage review process IS the code review. For final integration review, use the requesting-code-review skill's review dimensions.

### With systematic-debugging

If a subagent encounters bugs during implementation:
1. Follow systematic-debugging process
2. Find root cause before fixing
3. Write regression test
4. Resume implementation

## Example Workflow

```
[Read plan: docs/plans/auth-feature.md]
[Create todo list with 5 tasks]

--- Task 1: Create User model ---
[Dispatch implementer subagent]
  Implementer: "Should email be unique?"
  You: "Yes, email must be unique"
  Implementer: Implemented, 3/3 tests passing, committed.

[Dispatch spec reviewer]
  Spec reviewer: ✅ PASS — all requirements met

[Dispatch quality reviewer]
  Quality reviewer: ✅ APPROVED — clean code, good tests

[Mark Task 1 complete]

--- Task 2: Password hashing ---
[Dispatch implementer subagent]
  Implementer: No questions, implemented, 5/5 tests passing.

[Dispatch spec reviewer]
  Spec reviewer: ❌ Missing: password strength validation (spec says "min 8 chars")

[Implementer fixes]
  Implementer: Added validation, 7/7 tests passing.

[Dispatch spec reviewer again]
  Spec reviewer: ✅ PASS

[Dispatch quality reviewer]
  Quality reviewer: Important: Magic number 8, extract to constant
  Implementer: Extracted MIN_PASSWORD_LENGTH constant
  Quality reviewer: ✅ APPROVED

[Mark Task 2 complete]

... (continue for all tasks)

[After all tasks: dispatch final integration reviewer]
[Run full test suite: all passing]
[Done!]
```

## Remember

```
Fresh subagent per task
Two-stage review every time
Spec compliance FIRST
Code quality SECOND
Never skip reviews
Catch issues early
```

**Quality is not an accident. It's the result of systematic process.**

## Further reading (load when relevant)

When the orchestration involves significant context usage, long review loops, or complex validation checkpoints, load these references for the specific discipline:

- **`references/context-budget-discipline.md`** — Four-tier context degradation model (PEAK / GOOD / DEGRADING / POOR), read-depth rules that scale with context window size, and early warning signs of silent degradation. Load when a run will clearly consume significant context (multi-phase plans, many subagents, large artifacts).
- **`references/gates-taxonomy.md`** — The four canonical gate types (Pre-flight, Revision, Escalation, Abort) with behavior, recovery, and examples. Load when designing or reviewing any workflow that has validation checkpoints — use the vocabulary explicitly so each gate has defined entry, failure behavior, and resumption rules.

Both references adapted from gsd-build/get-shit-done (MIT © 2025 Lex Christopherson).
