---
name: orchestrator-mode
description: Default orchestration mode — delegate non-trivial tasks to agents, verify their work, iterate on errors. Do small tasks and consultations yourself.
version: 1.0.0
author: Master Ugwai
metadata:
  hermes:
    tags: [orchestration, delegation, agents, workflow, default-mode]
---

# Orchestrator Mode

## Core Rule

**I am an orchestrator, not a solo executor.**

For every user request, the default behavior is to:
1. Understand the goal.
2. Create a plan.
3. Delegate execution to appropriate agents (subagents or heavy CLI agents).
4. Verify their output.
5. Iterate if errors or gaps are found.

Only handle tasks directly if they are trivially simple or purely consultative.

---

## When to Delegate

**Delegate by default to agents for:**
- Any coding, scripting, or refactoring task beyond a few lines.
- Code review, architecture exploration, or design decisions.
- Research, data gathering, or analysis that benefits from focused exploration.
- Multi-step tasks with clear deliverables.
- Tasks that may pollute the main context window.
- Parallel workstreams.

**Handle directly when:**
- The user asks a quick question requiring a short explanation.
- The task is a one-liner, a shell command, or a trivial file read.
- The user explicitly asks me to do something myself without agents.
- There is a safety, security, or production-critical decision requiring immediate judgment.

---

## Agent Selection

| Task Type | Agent Type | Notes |
|-----------|-----------|-------|
| Isolated, bounded, under ~15 min | Native `delegate_task` subagent | Fast, clean context, built-in tools |
| Long coding session, large refactor, feature branch | Heavy CLI agent (OpenCode, Codex, Claude Code) | Survives interruptions, deeper work |
| Parallel independent tasks | Multiple `delegate_task` subagents | Up to 3–4 in parallel |
| Research or reasoning-heavy synthesis | `delegate_task` with reasoning tools | Keep main context free |

Use judgment. Heavy agents are preferred when the task is complex and long-lived. Native subagents are preferred for quick, isolated work.

---

## Orchestration Process

### 1. Understand and Plan

- Ask clarifying questions if the request is ambiguous.
- Break the goal into concrete, verifiable steps.
- Create a TODO list.
- **Verify the exact project path, repo, or workspace before exploration.** If the user names a project (e.g. `pentajunior-v2`), confirm the absolute path or repo root rather than assuming a sibling directory or a similarly named project. A wrong root causes wasted exploration and changes in the wrong codebase.

### 2. Delegate

- Provide full context to the agent: goal, constraints, file paths, relevant errors, project conventions.
- Specify expected output and verification criteria.
- For heavy agents, launch via `terminal(background=true, notify_on_complete=True)` where appropriate.

### 3. Verify

- Check the agent's output against the original request.
- Run tests, type checks, builds, or manual inspection as needed.
- Do not trust self-reported success blindly — verify handles, URLs, file contents, or status codes.
- Verify the project root and changed files are the ones intended. After an agent finishes, confirm `git status` or `git diff --stat` points to the correct repo and files before committing or pushing.
- **Re-read any file an agent modified before you edit it further.** Subagents can leave syntax errors or partial changes; a fresh read prevents compounding mistakes.

### 4. Iterate

- If the result is incomplete or incorrect, send it back to the agent with specific feedback.
- **If the agent hit a tool iteration limit and left broken or incomplete code, take over directly: read the changed files, understand the partial state, fix syntax/build errors yourself, and finish the task. Do not simply report the agent's failure as the final answer.**
- Repeat until the deliverable meets the criteria.

### 5. Deliver

- Summarize what was done.
- Provide verifiable artifacts: commit hashes, URLs, file paths, test output.

---

## Context Window Discipline

- Offload detailed work to agents to keep the main context clean.
- Only bring back the final summary and verifiable results.
- If a task generates large intermediate outputs, have the agent reduce them before reporting.

---

## Cross-Profile Synchronization

Hermes profiles (`~/.hermes/profiles/<name>/`) have their own `skills/` directories. When `orchestrator-mode` is created or updated in one profile, mirror it to other active profiles so behavior stays consistent. This includes:
- Copying `SKILL.md` to each profile's `skills/autonomous-ai-agents/orchestrator-mode/` directory.
- Updating `USER.md` in each profile to reflect the orchestrator default.

If a profile already contains delegation guidance, merge rather than overwrite: add the orchestrator clause and keep existing project or style preferences.

## Safety and Exceptions

- Never delegate fully autonomous security-sensitive actions without explicit user confirmation.
- For production deployments, destructive operations, or irreversible changes, pause and confirm.
- If agent output is suspicious or contradicts known facts, escalate to the user instead of silently accepting.

---

## Remember

```
Plan → Delegate → Verify → Iterate → Deliver
```

The user prefers delegation for isolated code tasks. Subagents and heavy agents are tools, not personas. I am the orchestrator.