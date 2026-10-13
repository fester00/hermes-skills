# Scoped Re-Review Subagent — `delegate_task` Dispatch

Dispatch after every fix round. The re-reviewer verifies the previous findings were addressed and checks the
fix diff for new breakage. It is not a fresh review.

```python
delegate_task(tasks=[{
  "goal": "Re-review Task [N] fix round [R]: verdict each finding and check the fix diff for new breakage.",

  "context": """
You are re-reviewing one task's fix round. A previous review produced findings; an implementer has attempted
to fix them. Verdict every finding and inspect the fix diff — nothing else.

## The task
Read the task brief: [BRIEF_FILE]

## Findings under verification (verbatim from the previous review)
[FINDINGS]

## The fix
Read the implementer's report (fix reports are appended at the end): [REPORT_FILE]
Fix base: [FIX_BASE_SHA]   Head: [HEAD_SHA]   Diff file: [DIFF_FILE]

Read the diff file once: it holds the fix commits, a stat summary and the fix diff with context. If it is
missing, fetch it yourself with `git diff --stat [FIX_BASE_SHA]..[HEAD_SHA]` and
`git diff [FIX_BASE_SHA]..[HEAD_SHA]`. Your review is read-only: do not mutate the working tree, the index,
HEAD or branch state.

## Scope
Your scope is the findings list plus the fix diff. Verdict every finding. Look for problems the fix itself
introduced. Do NOT re-review code the fix did not touch — if you spot something entirely outside the fix
diff, put it under Out-of-Scope Observations; it does not block this task and does not extend the loop.

## Tests
The implementer re-ran the tests covering the amended code and appended the results to the report. Treat that
as unverified claims: confirm the appended section names the covering tests and shows their output, and check
the claims against the diff. Do not re-run the suite; run one focused test only if the code raises a specific
doubt.

## Output (your final message is the report)
### Finding Verdicts
For each finding, in order: [one-liner] — ADDRESSED | NOT ADDRESSED, with file:line evidence.
"Attempted" is not addressed: the specific defect must no longer exist.
### New Breakage in the Fix Diff
Anything the fix broke or introduced, with severity and file:line. "None" if clean.
### Out-of-Scope Observations
Non-blocking; the controller ledgers these for the final review. "None" if none.
### Verdict
Fix round: all findings addressed, no new Critical/Important breakage | findings remain open (list them).
""",

  "output_schema": {
    "type": "object",
    "properties": {
      "addressed": {"type": "array", "items": {"type": "string"}},
      "not_addressed": {"type": "array", "items": {"type": "string"}},
      "new_breakage": {"type": "array", "items": {"type": "string"}},
      "out_of_scope": {"type": "array", "items": {"type": "string"}},
      "round_verdict": {"type": "string", "enum": ["clean", "findings_open"]}
    },
    "required": ["addressed", "round_verdict"]
  }
}])
```

## Placeholders

- `[FINDINGS]` — the Critical/Important findings and spec gaps from the previous review, copied verbatim,
  one per bullet
- `[FIX_BASE_SHA]` — the head the previous review saw (this is what keeps the fix diff scoped)
- `[HEAD_SHA]`, `[DIFF_FILE]` — as in `task-reviewer-prompt.md`, with
  `scripts/review-package PLAN_FILE FIX_BASE HEAD`

## Controller notes

- Every round ends with a scoped re-review; "the fix was small" is not an exemption.
- New findings that appear outside the fix diff go to the ledger, not into this loop.
- After round 5, adjudicate: load-bearing → stop and report BLOCKED; otherwise park with a ruling.
