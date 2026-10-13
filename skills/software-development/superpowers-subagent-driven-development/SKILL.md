---
name: superpowers-subagent-driven-development
description: Use when executing an approved multi-task plan with Hermes subagents. Ledger-tracked task loop, independent per-task review, controller-run verification.
version: 2.0.0
author: Master Ugwai
license: MIT
category: software-development
metadata:
  hermes:
    tags: [subagents, delegation, execution, review, verification, ledger]
    related_skills: [superpowers-workflow, superpowers-writing-plans, superpowers-executing-plans, code-quality-gates, superpowers-dispatching-parallel-agents, superpowers-finishing-a-development-branch, superpowers-verification-before-completion]
---

# Hermes Subagent-Driven Development

Execute an approved plan by dispatching **one fresh Hermes subagent per task**, reviewing every task with an
independent reviewer subagent, and finishing with a whole-branch review. The controller (you) owns the
ledger, the git baseline, and every verification command.

**This is the default execution path in Hermes.** OpenCode runs only when the user explicitly asks for it —
the rule and its rationale live in `superpowers-workflow` (Phase 4) and
`superpowers-workflow/references/opencode-vs-subagents.md`.

**Core principle:** fresh child per task + independent review + controller-run verification = quality
without context pollution.

**Why a fresh child per task:** no context pollution across tasks; a child that fails is replaced without
inheriting its confusion; the reviewer sees the diff, not the implementer's reasoning.

**Narration:** between tool calls, narrate at most one short line — the ledger and the tool results carry the
record.

**Continuous execution:** do not check in with the user between tasks. Stop only for: BLOCKED you cannot
resolve, ambiguity that genuinely prevents progress, or all tasks complete.

## Prerequisites (all of them, in order)

1. **A written plan the user explicitly approved.** Hard gate — see `superpowers-workflow` Phase 2. A
   detailed verbal request is not approval. No approved plan → no dispatch.
2. **A git workspace.** If the project is not a repository, **ask the user first** — do not run `git init`
   on your own; baseline commits are a side effect the user has not approved.
3. **Workspace and ledger resolved** (Step 0 below).
4. **`BASE` recorded before each task** (`git rev-parse HEAD`).

## Step 0: Setup

1. Resolve the plan's workspace and print it:
   ```bash
   bash scripts/sdd-workspace PLAN_FILE      # → <repo-root>/.superpowers/sdd/<plan-basename>/
   ```
   One directory per plan, in the working tree (not under `.git/`, which agents cannot write), with a
   self-ignoring `.gitignore`, so a stale ledger can never be mistaken for the current plan's progress.
2. Read `<workspace>/progress.md` if it exists. First line names **this** plan → resume at the first task
   without a `complete` line. Names another plan → start a fresh ledger.
3. Create the ledger with the header line (format below).
4. Read the plan once, create a todo per task, scan for contradictions before dispatching Task 1.

## The two documents, and who writes what

| | Plan file | Ledger `progress.md` |
|---|---|---|
| Written by | you, at Phase 2, approved by the user | **only the controller (you)** |
| Contents | intent: tasks, exact paths, verification commands | progress: dispatch and outcome lines |
| Changes | never edited by a child | appended after each dispatch and each verified review |

Ledger format — the first line is a binding contract:

```
# SDD ledger — plan: /abs/path/to/plan.md
Task 1: dispatched sa-0-1a2b3c4d
Task 1: complete (commits 9f8e7d6..1a2b3c4, review clean)
Task 2: dispatched sa-1-9f8e7d6a
Task 2: complete (commits 1a2b3c4..77aa11b, 2 parked: flaky test in cart.spec.ts; unused export in pricing.ts)
Task 3: blocked (needs the TMF API schema) — re-dispatched as sa-2-3c4d5e6f
Task 4: failed (child stopped mid-run; landed files up to src/api/client.ts)
```

**Why the controller owns the ledger:** only the controller sees the review verdict and the real git state.
A child that dies mid-task must never leave a `complete` line behind. Children write exactly one thing:
their own report file.

The ledger stays out of `git status` and survives context compaction — that is its whole point. Never
reconstruct progress from memory when the ledger exists.

## The task loop

### 1. Prepare the brief and the context

```bash
bash scripts/task-brief PLAN_FILE N            # → <workspace>/task-N-brief.md (prints the path)
```

`task-brief` extracts the task's text (headings `## Task N: …`) so the plan never passes through your
context. Then assemble the child's `context` — the child sees **nothing** else:

- the brief file path (**it must read that first — the brief is the single source of requirements**);
- interfaces and decisions from earlier tasks (exact names, signatures, tokens);
- the plan's Global Constraints, copied verbatim;
- the working directory and its base commit;
- the report file path it must write (`<workspace>/task-N-report.md`);
- the rule: **you cannot ask questions — if something is missing, stop and return `NEEDS_CONTEXT` with the
  exact missing piece instead of guessing.**

### 2. Dispatch

Record `BASE=$(git rev-parse HEAD)` first, then dispatch with `delegate_task` following
`implementer-prompt.md` — including the **status `output_schema`**, which is what makes the child's return
machine-readable instead of prose.

One task at a time (parallel lanes only under the disjointness rule below).

### 3. Handle the status

The child's final answer arrives as JSON: `status`, `summary`, `commits`, `tests`, `concerns`,
`blocked_on`, `report_file`.

- **DONE** → controller verification (step 4), then review (step 5).
- **DONE_WITH_CONCERNS** → read the concerns. Correctness or scope → resolve before review. Observations
  only → proceed to review.
- **NEEDS_CONTEXT** → re-dispatch the same brief **with the missing context added**, to a **new child**
  (there is no resume).
- **BLOCKED** → triage in this order: (1) context problem → re-dispatch with more context; (2) needs more
  reasoning → re-dispatch with sharper framing and a narrower task; (3) task too large → split it;
  (4) the plan itself is wrong → escalate to the user.

**Never ignore BLOCKED. Never accept a missing status.**

### 4. Controller verification (mandatory, before any review)

The child's report is a *claim*. Verify against disk:

```bash
git log --oneline BASE..HEAD
git diff --stat BASE..HEAD
npx tsc --noEmit && npm run build          # or the plan's exact verification commands
```

…plus tests, and screenshots (desktop, mobile, modal) for UI work. If the child reported green tests and
your fresh run says otherwise, that is a finding against the child, not a detail.

### 5. Review the task (independent child)

```bash
bash scripts/review-package PLAN_FILE BASE HEAD     # → <workspace>/review-<base7>..<head7>.diff
```

Use the recorded `BASE` — never `HEAD~1`, which silently truncates multi-commit tasks. Dispatch
`task-reviewer-prompt.md` to a **fresh child** (never the implementer — nobody verifies their own work) and
require **both** verdicts: spec compliance *and* code quality. A report missing either one is not a review.
Do not pre-judge findings for the reviewer.

An `approved` verdict with zero findings is credible only for a trivial diff — on anything substantive,
re-dispatch with the evidence requirement. Implementer and reviewer share the pinned `delegation.model`, so
what buys you a second opinion here is independent context, not a second model (see `task-reviewer-prompt.md`).

### 6. Fix loop

- Rounds 1–3: re-dispatch with the open findings appended to `context`, instructing the child to append a
  fix report to the same report file.
- Rounds 4–5: a fresh child with sharper framing — "a previous agent attempted this N times; you own it
  now; read the report file for what was tried."
- Every round ends with a scoped re-review (`re-review-prompt.md`) of the fix diff only.
- After five rounds: adjudicate every open finding. Load-bearing → stop and report BLOCKED to the user.
  Otherwise park the findings in the ledger with your ruling. Silent discards are forbidden.

### 7. Close the task

Append the ledger line (`complete`, `parked`, `blocked`, `failed`) and mark the todo complete. Then the next
task.

## Liveness, stalls, recovery

This is the answer to "the child went quiet and I have no idea where it stopped".

- **Live transcript while it runs:** `~/.hermes/cache/delegation/live/<delegation_id>/task-N.log`
  (append-only, human-readable). Read or `tail` it at any time — it shows the child's operations and tool
  results, not just its final summary.
- **Control while it runs:** `delegate_task(action='list')` shows ids/status/goals; `action='steer'` with
  `subagent_id` + message queues a course correction into the child's next tool result — the **only**
  mid-run communication channel; `action='stop'` ends a child and still returns its partial result.
- **No partial result before it ends.** A hung child is silent by design; the transcript is your only window.
- **State lives in files, not in the child.** Before re-dispatching a failed task, read three things: the
  transcript tail (last completed operation), `git status/log` (what actually landed), and the report file
  (what the child believed). Then dispatch a fresh child for the remainder only — "Task 3 is partially done:
  A and B landed at commit `<sha>`, C did not; finish C only" — and write the `failed` ledger line.
- **Children do not survive the session.** `/stop`, `/new`, or exiting Hermes kills the whole tree. Work that
  must outlive the session belongs in `terminal(background=True, persist_on_release=True)` or a cron job.
- **Parallelism cap:** 4 children at once (`delegation.max_concurrent_children`); extra ones do not queue.

Details and the full recovery recipe: `references/hermes-subagent-mechanics.md`.

## Parallel lanes

Follow `references/parallel-lane-pitfall.md`. Binding constraint: lanes are allowed **only when file sets
are strictly disjoint** — children share one filesystem and one working tree, so two lanes writing the same
file is a race, not a merge. After lanes finish: re-read every shared file, run the full verification suite,
take after-screenshots, and only then write ledger lines.

## Final review

```bash
bash scripts/review-package PLAN_FILE MERGE_BASE HEAD
```

Dispatch `final-reviewer-prompt.md` to a fresh child over the whole-branch diff. Findings → **one** fix
dispatch with the complete findings list, then one scoped re-review, then adjudicate what remains.
Load-bearing residuals surface to the user in the finish phase.

## Finish

Use `superpowers-finishing-a-development-branch` (merge locally / push and PR / keep / discard). Delete the
plan workspace (`rm -rf <workspace>`) only after the branch is merged.

## Model selection

- `delegate_task` has **no per-task model argument**. Children run on whatever `delegation.*` in
  `~/.hermes/config.yaml` says — check it once per session instead of assuming inheritance:
  ```bash
  grep -A6 '^delegation' ~/.hermes/config.yaml
  # verified on this machine: model: kimi-k2.7-code:cloud, provider: ollama-launch,
  # base_url: http://127.0.0.1:11434/v1, inherit_mcp_toolsets: true
  ```
  That pin is set here, so children do **not** run on the session model — they run on the pinned one and
  inherit the parent's MCP toolsets. Remove the block to fall back to plain inheritance.
- Changing the pin affects **all** children for the duration — record it in the ledger. For one lane on a
  different model, route it through OpenCode (opt-in, `references/opencode-opt-in-execution.md`).
- Turn count beats token price: for judgment-heavy work, delegate to a fresh child rather than pushing a
  struggling child through more rounds.

## Common rationalizations

| Excuse | Reality |
|--------|---------|
| "Close enough on spec compliance" | Reviewer found spec gaps = not done. Fix or hit the cap and adjudicate. |
| "I'll fix it myself, dispatching is overhead" | Controller fixes pollute your context and skip review. Dispatch. |
| "The child says the build passes" | That is a claim. Run it yourself. |
| "I'll remember where we stopped" | The ledger exists because memory does not survive compaction. |
| "One more round will converge" | Past the cap the failure is structural. Adjudicate and route. |
| "This finding is obviously wrong" | Adjudicate only at the cap, with a ledger entry. Silent discards are forbidden. |
| "The fix was small, skip the re-review" | Every round ends with a scoped re-review. |
| "Reviews slow the loop down" | Reviews are the loop's brakes and steering. |
| "The child can ask me if it's stuck" | It cannot. Say what to do instead in `context`. |

## Pre-flight gate: explicit plan approval

Execution begins only after the user approves the written plan. Never dispatch against a vague verbal
request, and never let a child invent the plan.

## References

- `implementer-prompt.md` — implementer dispatch + status `output_schema`
- `task-reviewer-prompt.md` — spec-compliance + code-quality reviewer
- `re-review-prompt.md` — scoped re-review of a fix round
- `final-reviewer-prompt.md` — whole-branch review before finishing
- `references/hermes-subagent-mechanics.md` — what a Hermes child is, what it can and cannot do, liveness and recovery recipes
- `references/parallel-lane-pitfall.md` — lane split rules and reconciliation checklist
- `references/opencode-opt-in-execution.md` — the opt-in OpenCode path on v2
- `scripts/sdd-workspace`, `scripts/task-brief`, `scripts/review-package`
