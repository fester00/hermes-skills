# Final Whole-Branch Reviewer — `delegate_task` Dispatch

Runs once, after all tasks are complete, over the cumulative diff. This file replaces a dangling pointer to
an external reviewer prompt that the previous version of this skill referenced but never shipped.

```python
delegate_task(tasks=[{
  "goal": "Final review of the whole branch: does the cumulative diff deliver the approved plan, coherently and safely?",

  "context": """
You are the final reviewer for a branch built task-by-task from an approved plan. Per-task reviews are done;
your job is the whole-branch view: coherence, integration, and what is only visible across tasks.

## The plan
Read the plan file: [PLAN_FILE]

## The change
Merge base: [MERGE_BASE]   Head: [HEAD_SHA]   Diff file: [DIFF_FILE]
(Produced by `scripts/review-package PLAN_FILE MERGE_BASE HEAD` — commit list, stat summary, full diff.)
Read the diff file once. Inspect code outside the diff only to evaluate a specific risk you name.
Read-only: do not mutate the working tree, index, HEAD or branch state.

## Ledger context
The controller parked these findings during the loop — decide whether any has become load-bearing:
[PARKED_FINDINGS]

## What to judge
1. **Plan delivered?** Every task's outcome present and integrated; nothing silently dropped.
2. **Cross-task coherence:** duplicated helpers, contradictory patterns, interfaces that drifted, dead code
   from superseded tasks, config/doc drift.
3. **Correctness and safety across seams:** data flow between modules, error handling at boundaries, security
   (secrets, injection, unsafe shell/eval), migration or deploy steps the plan implies.
4. **Verification reality:** do the existing tests actually cover the delivered behaviour? Name what matters
   that is untested.
5. **Leftovers:** TODOs, debug prints, placeholders, commented-out code, stray files, uncommitted artefacts.

## Calibration
Important = the branch cannot be trusted or shipped until fixed. Minor = polish. Cite file:line for every
finding. Note strengths before issues. Do not re-litigate per-task findings that were reviewed and closed
unless new evidence makes them load-bearing — say so if it does.

## Output (your final message is the report)
### Plan Delivery
- ✅ all tasks delivered | ❌ gaps: [list with file:line]
### Cross-Task Coherence
The seams that hold and the ones that don't.
### Issues — Critical / Important / Minor (each: file:line, what's wrong, why it matters, how to fix)
### Parked Findings Re-Assessment
For each parked finding: still acceptable | load-bearing (why).
### Verdict
Ship | Fix then ship (list the fixes) | Do not ship (why).
""",

  "output_schema": {
    "type": "object",
    "properties": {
      "plan_delivered": {"type": "boolean"},
      "critical": {"type": "array", "items": {"type": "string"}},
      "important": {"type": "array", "items": {"type": "string"}},
      "minor": {"type": "array", "items": {"type": "string"}},
      "load_bearing_parked": {"type": "array", "items": {"type": "string"}},
      "verdict": {"type": "string", "enum": ["ship", "fix_then_ship", "do_not_ship"]}
    },
    "required": ["plan_delivered", "verdict"]
  }
}])
```

## Controller notes

- Dispatch to a fresh child — never the controller with the plan in its head.
- Findings trigger **one** fix dispatch with the complete list, then one scoped re-review. Do not start a
  second loop here; residuals go to the user in the finish phase.
- `do_not_ship` is a stop condition: report it to the user with the evidence, do not merge.
