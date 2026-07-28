---
name: orchestrator-mode
description: Default orchestration mode — delegate non-trivial tasks to agents, verify their work, iterate on errors. Do small tasks and consultations yourself.
version: 1.1.0
author: Master Ugwai
metadata:
  hermes:
    tags: [orchestration, delegation, agents, workflow, default-mode, opencode]
    related_skills: [opencode, subagent-driven-development, hermes-software-development-workflow, writing-plans]

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
| Quick question / one-liner | Do it directly | Fastest, no context setup |
| Isolated, 1–3 files, under ~15 min | Native `delegate_task` subagent | Fast, clean context, built-in tools |
| 3–5 files, well-defined, self-contained | Native `delegate_task` subagent | Up to 3 in parallel |
| > 5 files, refactoring, website or project from scratch | Heavy CLI agent (OpenCode) | No hard timeout, survives interruptions, deeper work |
| Parallel independent heavy streams | 2 OpenCode agents in background | True parallelism without delegate queue |
| Research / SEO / browser / web search | Do it yourself or native `delegate_task` | Never delegate web tasks to OpenCode |
| Code review of an entire branch | OpenCode or heavy CLI agent | Fresh context, deep review |

**Hard rule:** OpenCode is the default agent for any coding task that spans more than 5 files, requires refactoring, or builds a website/project from a written plan. Native `delegate_task` is reserved for smaller, isolated subtasks. Web search, browser navigation, and SEO analysis are always handled in the main Hermes session or by native subagents with explicit tool access.

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

Lightweight: do directly
Small/isolated: delegate_task
Heavy coding: OpenCode
Parallel heavy: 2 OpenCode agents max
Web/SEO/browser: main Hermes session
```

The user prefers delegation for isolated code tasks. Subagents and heavy agents are tools, not personas. I am the orchestrator.

## Template / References

- For heavy OpenCode tasks, use the brief template in `subagent-driven-development/templates/opencode-brief.md`.
- For MCP configuration patterns, see `native-mcp` skill and `opencode` skill references.