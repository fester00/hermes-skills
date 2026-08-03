---
name: dispatching-parallel-agents
description: Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies
---

# Dispatching Parallel OpenCode Agents

## Overview

You run multiple OpenCode agents concurrently when you have independent failures or tasks with strictly disjoint file sets. Each agent gets a focused brief and an isolated context. This preserves your Hermes context for coordination.

**Core principle:** One OpenCode agent per independent problem domain, launched against a single `opencode serve` instance with `opencode run --attach`.

## Prerequisites

1. The project directory must be a git repository. If not, initialize it (only if `.git` is absent):
   ```bash
   if [ ! -d .git ]; then git init && git add . && git commit -m "initial"; fi
   ```
2. Start one OpenCode server in the project root: `opencode serve --port 4096 --hostname 127.0.0.1`.
3. Prepare one brief file per lane. Each brief must start with `Do not use todo or planning tools.` and must explicitly name the files the lane owns.

## When to Use

- 3+ test files failing with different root causes
- Multiple subsystems broken independently
- Each problem can be understood without context from others
- No shared files between lanes

**Don't use when:**
- Failures are related (fixing one might fix others)
- Need full system state
- Lanes would edit the same files

## The Pattern

### 1. Identify Independent Domains

Group failures or tasks by file ownership. Example:
- Lane A: `src/components/ProductCard.tsx`, `src/components/ProductModal.tsx`
- Lane B: `src/sections/Hero.tsx`, `src/sections/Contact.tsx`

### 2. Create Focused Lane Briefs

Each brief contains:
- **Specific scope:** exact files this lane owns
- **Clear goal:** what the agent must achieve
- **Constraints:** do not touch files outside the lane
- **Expected output:** `DONE` status, changed files, test/build exit codes

### 3. Dispatch in Parallel

Run multiple `opencode run --attach` invocations concurrently from the same server, each with its own brief and log file:

```bash
opencode run --auto --attach http://127.0.0.1:4096 --dir <project> --title 'Lane A: cards' < lane-a.md > lane-a.log 2>&1 &
opencode run --auto --attach http://127.0.0.1:4096 --dir <project> --title 'Lane B: hero'  < lane-b.md  > lane-b.log  2>&1 &
wait
```

### 4. Reconcile

When lanes finish:
- Read each log and report file.
- Check `git status --short` for conflicts.
- Run `npx tsc --noEmit` and `npm run build`.
- Run full test suite / smoke tests.
- Capture after-screenshots for visual changes.
- Resolve conflicts manually if lanes touched the same files.

## Common Mistakes

- **Too broad brief:** "Fix all the tests" — agent gets lost.
- **No context:** "Fix the race condition" — agent doesn't know where.
- **No constraints:** agent might refactor everything.
- **Vague output:** "Fix it" — you don't know what changed.
- **Shared files:** parallel lanes editing the same file cause last-write-wins races.

## When NOT to Use

- Related failures — investigate together first.
- Need full system context.
- Exploratory debugging.
- Shared state between lanes.

## Verification

After all agents return:
1. Read each log.
2. Check for conflicting file modifications.
3. Run full build/test/lint.
4. Spot-check screenshots.

Hermes `delegate_task` subagents are reserved for browser/profile research only. For code execution, use OpenCode.
