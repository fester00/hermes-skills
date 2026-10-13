# Implementer Subagent — `delegate_task` Dispatch

Dispatch one fresh Hermes child per task. Fill every `[PLACEHOLDER]`, pass the plan text as a **file
path**, and always include the status `output_schema` so the return is machine-readable.

```python
delegate_task(tasks=[{
  "goal": "Implement Task [N]: [task name] of the approved plan, in [PROJECT_DIR]; commit the work.",

  "context": """
You are implementing Task [N]: [task name].

## Read first
- Your task brief (single source of requirements): [BRIEF_FILE]
- The plan's Global Constraints (copied verbatim): [GLOBAL_CONSTRAINTS]
- Working directory: [PROJECT_DIR]  (base commit [BASE_SHA])

## What earlier tasks already built
[DECISIONS_AND_INTERFACES — exact file paths, exported names, signatures, tokens]

## You cannot ask questions
You have no channel to the user or the controller mid-run. If something is missing, ambiguous or blocking,
do NOT guess: stop and return status NEEDS_CONTEXT (naming the exact missing piece) or BLOCKED (what you
tried, what you need).

## Your job
1. Implement exactly what the brief specifies — nothing more (no unrequested features, no refactors
   outside the task).
2. Where the brief says TDD applies, write the test first: run it, watch it fail (RED), then implement
   until it passes (GREEN), then clean up (REFACTOR).
3. Run the focused test while iterating; run the full suite once before committing.
4. Commit your work with a message naming the task.
5. Self-review with fresh eyes, then fix what you find.

## Code organisation
- Follow the file structure in the plan; one clear responsibility per file.
- If a file grows beyond the plan's intent, do not split it on your own — report it as a concern.
- In existing codebases, follow established patterns; improve only the code you touch.

## Escalate (status BLOCKED) when
- the task needs architectural decisions that were not made in the plan;
- you cannot find the clarity you need and the plan does not resolve it;
- your approach may be structurally wrong;
- you have read file after file without progress.
Bad work is worse than no work; escalating is not penalised.

## Report file: [REPORT_FILE]
Write the full report there: what you implemented, files changed, tests plus observable output, TDD evidence
(RED command and failing output, GREEN command and passing output) where TDD applied, self-review findings,
and any concerns. The report file is the durable record — write it even when blocked.

## Fix rounds
If a review finds issues, you will be re-dispatched as a NEW child with the findings in context. Read the
report file first, fix the findings, re-run the tests covering the amended code, and APPEND a fix report
(what changed, covering tests, command, output). Reviewers do not re-run tests for you — your appended
output is the evidence.
""",

  "output_schema": {
    "type": "object",
    "properties": {
      "status": {"type": "string", "enum": ["DONE", "DONE_WITH_CONCERNS", "NEEDS_CONTEXT", "BLOCKED"]},
      "summary": {"type": "string"},
      "commits": {"type": "array", "items": {"type": "string"}},
      "tests": {"type": "string"},
      "concerns": {"type": "array", "items": {"type": "string"}},
      "blocked_on": {"type": "string"},
      "report_file": {"type": "string"}
    },
    "required": ["status", "summary", "report_file"]
  }
}])
```

## Notes for the controller

- **Goal = one sentence, context = everything.** The child sees no conversation history, no plan file, no
  ledger, no skills from this session. If a decision matters, it must be in `context`.
- **A brief path beats pasted text.** `scripts/task-brief PLAN N` writes it; the child reads it in one call.
- **Verify the schema came back.** `schema_valid` false or a missing `status` → the child did not follow the
  contract; re-dispatch with the contract restated instead of interpreting prose.
- **Never pass `[GLOBAL_CONSTRAINTS]` as a summary.** Copy the exact values, formats and relationships.
- **One task per child.** Bundling tasks destroys the review granularity the loop depends on.
- **Children cannot delegate further.** Do not ask a child to spawn helpers; split the plan yourself.
- **The child inherits the parent model** (or the pinned `delegation.model`). There is no model argument.
