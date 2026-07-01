# Subagent Delegation Pattern

A `delegate_task` delegation framework for splitting work across subagents while respecting concurrency limits.

## When to Delegate

| Task Type | Delegate To | Never Handle Yourself |
|-----------|-------------|----------------------|
| Code review, refactoring, debugging | Subagent (coder toolset) | Writing/refactoring code |
| Architecture analysis, tech design | Subagent (coder toolset) | Deep code analysis |
| Write interactive course | Subagent (writing focus) | Course creation |
| Documentation, articles | Subagent (writing focus) | Long-form writing |
| Simple question, wisdom, advice | Handle directly | — |
| Mixed tasks | Decide per piece | — |

## Ollama Pool Limits: Self vs Delegate

**⚠️ Critical constraint for ollama-cloud users (e.g. kimi-k2.6 via local proxy):**

The ollama pool has a hard concurrency ceiling. Exceeding it causes `exhausted` state (`401 unauthorized` in `~/.hermes/auth.json`), which blocks ALL agents until manual reset (`hermes auth reset ollama-cloud`).

**Concurrency math:**
```
1 main agent + N subagents = N+1 concurrent requests
N=2 subagents -> 3 total (SAFE with pool of 3)
N=3 subagents -> 4 total (POOL EXHAUSTED -- DO NOT DO THIS)
```

**Decision tree:**
```
IF task is SMALL (1-2 files, <10 min) -> Do it directly (faster than context setup)
IF task is MEDIUM (3-5 files, 10-20 min) -> 1 subagent + wait (safe)
IF task is LARGE (5+ files, 20+ min) -> Split into 2 sequential subagent batches (max 2 at a time)
IF tasks are MANY INDEPENDENT small ones -> Batch 2 at a time, sequential waves
```

**Recovery from exhausted pool:**
```bash
hermes auth reset ollama-cloud
# Or manually: remove last_status fields from ~/.hermes/auth.json
```

**Rule of thumb for this setup:**
- **Maximum 3 parallel subagents** at any time (config cap)
- **Recommended: 2 parallel subagents** for heavy/long tasks to avoid ollama-cloud pool exhaustion AND stay within Ollama Pro's 3-concurrent-model limit
- For static sites, use 2-page batches max (field-tested)
- Reserve the main session for heavy/urgent work (no timeout, no pool contention)
- **Never run a second Hermes/OpenCode process alongside 2-3 subagents** -- Ollama Pro counts each as a separate concurrent model, exceeding the 3-model limit

## Syntax

```python
delegate_task(
    goal="TASK DESCRIPTION",
    context="BACKGROUND INFO",
    toolsets=["terminal", "file", "browser"]  # for coder
)
# For content:
delegate_task(
    goal="TASK DESCRIPTION",
    context="BACKGROUND INFO",
    toolsets=["file", "web"]  # for writing
)
```

## Response Pattern After Delegation

1. **Announce delegation** -- brief routing statement
2. After result returned -- **Summarize** in your own voice
3. Add **commentary** -- your own insight on the result

---

*Delegation is a tool. Wisdom is in knowing when to use it.*
