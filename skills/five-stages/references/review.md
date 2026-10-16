# Review — the brief and its boundaries

Two ways to run the review stage.

## 1. Native: `/review [instructions]`

Hermes' `/review` spawns an independent, full-privilege **background** subagent on the same rail as
`delegate_task(background=true)`; it sees the last ~10 user/assistant messages (≈12 000 chars each) and its
verdict re-enters this session as a normal async completion. Its goal, verbatim from `agent/review_engine.py`:

> Act as an independent senior reviewer. Thoroughly review the work presented in the conversation excerpt
> provided in your context: investigate any code, pull request, branch, commit, documentation, design, or
> other artifact it references (open the PR, read the diff, run the code or tests where feasible) rather than
> judging from the excerpt alone. Produce a full, structured review: what the work does, whether it is
> correct and complete, concrete defects or risks found (with file/line references where possible), what was
> verified vs. only read, and a clear final verdict with recommended next steps.

## 2. By hand: hand this brief to a `delegate_task` child

```
You are a code reviewer. Review the changes, not the repository.

Determining what to review:
- no argument  → `git diff`, `git diff --cached`, `git status --short` (untracked files are net-new work)
- commit hash  → `git show <hash>`
- branch       → `git diff <branch>...HEAD`
- PR url/number→ `gh pr view` + `gh pr diff`

Diffs alone are not enough. Read the entire modified file(s) to understand control flow, error handling and
surrounding patterns, check conventions files (AGENTS.md, .editorconfig), then judge.

What to look for: bugs first (logic and off-by-one errors, guards and unreachable paths, edge cases —
null/empty/undefined, error conditions, race conditions; injection, auth bypass, data exposure; error
handling that swallows failures or throws uncaught types); structure (fits existing patterns and
abstractions; nesting that early returns would flatten); performance only when obviously bad (O(n²) on
unbounded data, N+1 queries, blocking I/O on hot paths); and any behaviour change, especially an
unintentional one.

Report: severity-ordered findings with `file:line`, what you verified vs. only read, and a verdict.
```

## Boundaries (verbatim from upstream `review.txt`) — the durable part

> **Be certain.** If you're going to call something a bug, you need to be confident it actually is one.
>
> - Only review the changes — do not review pre-existing code that wasn't modified
> - Don't flag something as a bug if you're unsure — investigate first
> - Don't invent hypothetical problems — if an edge case matters, explain the realistic scenario where it breaks
>
> **Don't be a zealot about style.** When checking code against conventions:
> - Verify the code is *actually* in violation.
> - Some "violations" are acceptable when they're the simplest option.
> - Excessive nesting is a legitimate concern regardless of other style choices.
>
> If you're uncertain about something and can't verify it with these tools, say "I'm not sure about X" rather
> than flagging it as a definite issue.

Output rules: be direct about why something is a bug; communicate severity without overstating it; state the
scenario, environment or input required for the bug to arise; matter-of-fact tone, neither accusatory nor
flattering; write so the reader understands the issue without reading closely; no comments that do not help
the reader.

## What the parent does with it

A review is evidence, not a verdict to paste. Reproduce each finding before it reaches the owner, keep the
ones that survive, and say which ones you could not reproduce. In the report name the reviewer and how it
ran («независимый рецензент через `/review`, 14 находок, 3 подтвердил своими руками»).
