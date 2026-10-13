# Task Reviewer Subagent — `delegate_task` Dispatch

The reviewer is a **fresh child** that has never seen the implementation. It verdicts two things
separately: spec compliance and code quality. It is read-only.

```python
delegate_task(tasks=[{
  "goal": "Review Task [N] of the approved plan: verdict spec compliance and code quality of the diff, with file:line evidence.",

  "context": """
You are reviewing one task's implementation: first whether it matches its requirements, then whether it is
well-built. This is a task-scoped gate, not a merge review — a broad whole-branch review happens separately
after all tasks are complete.

## What was requested
Read the task brief: [BRIEF_FILE]
Global constraints from the spec that bind this task: [GLOBAL_CONSTRAINTS]

## What the implementer claims
Read the implementer's report: [REPORT_FILE]

## Diff under review
Base: [BASE_SHA]   Head: [HEAD_SHA]
Diff file: [DIFF_FILE]

Read the diff file once — it holds the commit list, a stat summary and the full diff with context, and it is
your view of the change. Do not crawl the codebase; inspect code outside the diff only to evaluate a concrete
risk you can name (one focused check per named risk, and name both the risk and the check in your report).
Cross-cutting changes are legitimate named risks: if the diff changes lock ordering, an API contract or
shared mutable state, checking the call sites is the right method.
Your review is read-only on this checkout: do not mutate the working tree, the index, HEAD or branch state.

## Do not trust the report
Treat the report as unverified claims. It may be incomplete or optimistic. "Left it per YAGNI" and similar
rationales are the implementer grading their own work — judge the code on its merits and never let a stated
rationale downgrade a finding's severity.

## Tests
The implementer already ran the tests and reported results for exactly this code. Do not re-run the suite to
confirm. Run a focused test only when reading the code raises a specific doubt no existing run answers.
Noise in reported test output is itself a finding — output should be pristine.

## Part 1: spec compliance
Compare the diff against what was requested:
- Missing: requirements skipped, or claimed but not implemented.
- Extra: unrequested features, over-engineering, nice-to-haves.
- Misunderstood: the right feature built the wrong way.
If a requirement cannot be verified from the diff alone, report it as an item for the controller instead of
broadening your search.

## Part 2: code quality
Separation of concerns, error handling, DRY without premature abstraction, edge cases; tests verify real
behaviour rather than mocks and cover the task's edge cases; each file has one clear responsibility and
follows the plan's structure; flag only size/complexity this change introduced.

Cite file:line for every finding and for any check you would otherwise answer with a bare "yes".

## Calibration
Important means the task cannot be trusted until fixed: incorrect or fragile behaviour, a missed requirement,
maintainability damage worth blocking a merge over (verbatim duplication of a logic block, swallowed errors,
tests that assert nothing). "Coverage could be broader" and polish are Minor. If the brief explicitly mandates
something this rubric calls a defect, report it as Important, labelled plan-mandated — the human decides,
not the plan's author. Note what was done well before the issues.

## Output (your final message is the report — no preamble, no process narration)
### Spec Compliance
- ✅ compliant | ❌ issues found (what's missing/extra/misunderstood, with file:line)
- ⚠️ cannot verify from diff: [what the controller should check]
### Strengths
### Issues — Critical (must fix) / Important (should fix) / Minor (nice to have), each with file:line, what's wrong, why it matters, how to fix
### Assessment
Task quality: Approved | Needs fixes — one or two sentences of technical reasoning.
""",

  "output_schema": {
    "type": "object",
    "properties": {
      "spec_verdict": {"type": "string", "enum": ["compliant", "issues_found", "cannot_verify"]},
      "task_quality": {"type": "string", "enum": ["approved", "needs_fixes"]},
      "critical": {"type": "array", "items": {"type": "string"}},
      "important": {"type": "array", "items": {"type": "string"}},
      "minor": {"type": "array", "items": {"type": "string"}},
      "cannot_verify": {"type": "array", "items": {"type": "string"}},
      "report_file": {"type": "string"}
    },
    "required": ["spec_verdict", "task_quality"]
  }
}])
```

## Placeholders

- `[BRIEF_FILE]` — the same brief the implementer worked from (`scripts/task-brief PLAN N`)
- `[GLOBAL_CONSTRAINTS]` — binding requirements copied verbatim (exact values, formats, relationships)
- `[REPORT_FILE]` — the implementer's report file
- `[BASE_SHA]` / `[HEAD_SHA]` — commit before the task / current commit
- `[DIFF_FILE]` — path printed by `scripts/review-package PLAN_FILE BASE HEAD`

## Controller notes

- The reviewer must **not** be the implementer, and must not be a child that has already seen the plan's
  implementation conversation — fresh context is the point.
- Both verdicts are required. `needs_fixes` with empty `critical`/`important` lists → reject the review and
  re-dispatch with the contract restated.
- Findings go back to the implementer **verbatim**, not summarised by you.
- Reviewer children run on the same model as implementers unless `delegation.model` is pinned.
