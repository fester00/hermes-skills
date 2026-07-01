---
name: kanban
description: |
  Multi-agent Kanban board for Hermes: orchestrator decomposition playbook,
  worker lifecycle guidance, and specialist roster conventions. Covers task routing,
  workspace isolation, tenant memory, and anti-temptation rules.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [kanban, multi-agent, orchestration, workflow, routing, workers]
    related_skills: [hermes-software-development-workflow]
---

# Kanban Multi-Agent Workflows

Use the Hermes Kanban board to decompose work, route tasks to specialist agents,
and coordinate parallel execution with persistent state and audit trails.

---

## Part 1: When to Use the Board

Create Kanban tasks when any of these are true:

1. **Multiple specialists are needed.** Research + analysis + writing is three profiles.
2. **The work should survive a crash or restart.** Long-running, recurring, or important.
3. **The user might want to interject.** Human-in-the-loop at any step.
4. **Multiple subtasks can run in parallel.** Fan-out for speed.
5. **Review / iteration is expected.** A reviewer profile loops on drafter output.
6. **The audit trail matters.** Board rows persist in SQLite forever.

If *none* apply — it's a small one-shot reasoning task — use `delegate_task` directly
or answer the user directly.

---

## Part 2: Orchestrator Playbook

### Anti-Temptation Rules

Your job description says "route, don't execute."

- **Do not execute the work yourself.** Your restricted toolset usually doesn't include terminal/file/code/web for implementation. If you find yourself "just fixing this quickly" — stop and create a task for the right specialist.
- **For any concrete task, create a Kanban task and assign it.** Every single time.
- **If no specialist fits, ask the user which profile to create.** Do not default to doing it yourself under "close enough."
- **Decompose, route, and summarize — that's the whole job.**

### Standard Specialist Roster

| Profile | Does | Typical workspace |
|---------|------|-------------------|
| `researcher` | Reads sources, gathers facts, writes findings | `scratch` |
| `analyst` | Synthesizes, ranks, de-dupes. Consumes multiple `researcher` outputs | `scratch` |
| `writer` | Drafts prose in the user's voice | `scratch` or `dir:` into their Obsidian vault |
| `reviewer` | Reads output, leaves findings, gates approval | `scratch` |
| `backend-eng` | Writes server-side code | `worktree` |
| `frontend-eng` | Writes client-side code | `worktree` |
| `ops` | Runs scripts, manages services, handles deployments | `dir:` into ops scripts repo |
| `pm` | Writes specs, acceptance criteria | `scratch` |

### Decomposition Steps

1. **Understand the goal** — ask clarifying questions if ambiguous.
2. **Sketch the task graph** — draft the dependency graph out loud before creating tasks.
3. **Create tasks** — one per concrete deliverable with clear acceptance criteria.
4. **Route to specialists** — assign based on the roster above.
5. **Monitor and summarize** — check board state, report progress, handle blockers.

See `references/kanban-orchestrator.md` for full decomposition examples, task graph patterns, and specialist routing rules.

---

## Part 3: Worker Lifecycle

The Kanban worker lifecycle is auto-injected into every Kanban worker's system prompt
as `KANBAN_GUIDANCE`. This skill provides deeper detail on edge cases and pitfalls.

### Workspace Handling

Your workspace kind determines how you should behave inside `$HERMES_KANBAN_WORKSPACE`:

| Kind | What it is | How to work |
|------|------------|-------------|
| `scratch` | Fresh tmp dir, yours alone | Read/write freely; GC'd when task archived. |
| `dir:<path>` | Shared persistent directory | Other runs will read what you write. Treat as long-lived state. |
| `worktree` | Git worktree at resolved path | If `.git` doesn't exist, run `git worktree add <path> <branch>` first. |

### Tenant Isolation

If `$HERMES_TENANT` is set, prefix memory entries with the tenant to prevent cross-tenant leakage:

- Good: `business-a: Acme is our biggest customer`
- Bad: `Acme is our biggest customer`

### Good Handoff Shapes

**Coding task:**
```python
kanban_complete(
    summary="shipped rate limiter — token bucket, keys on user_id with IP fallback, 14 tests pass",
    metadata={
        "changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"],
        "tests_run": 14,
        "tests_passed": 14,
        "decisions": ["user_id primary, IP fallback for unauthenticated requests"],
    },
)
```

**Research task:**
```python
kanban_complete(
    summary="3 competing libraries reviewed; vLLM wins on throughput",
    metadata={
        "sources_read": 12,
        "recommendation": "vLLM",
        "benchmarks": {"vllm": 1.0, "sglang": 0.87, "trtllm": 0.72},
    },
)
```

See `references/kanban-worker.md` for retry diagnostics, heartbeat patterns, block/complete edge cases, and full handoff examples.