# OpenCode Agent Brief Template

Copy this template into `/tmp/brief.md` and fill every section before launching OpenCode for a heavy coding task.

## Goal

One sentence describing what the agent must build or refactor.

## Project context

- **Path:** `/absolute/path/to/project`
- **Tech stack:** e.g. Next.js 14 + React + TypeScript + Tailwind + better-sqlite3
- **Test command:** e.g. `npm run test` or `pytest tests/ -q`
- **Build/lint command:** e.g. `npm run build && npx eslint .`
- **Conventions:** existing file naming, import style, state-management patterns, where to place new components/utils/tests
- **Files NOT to touch:** list explicitly to prevent scope creep

## Plan

Copy-paste tasks from the written implementation plan. Each task must include:

- exact file paths
- what to create or modify
- expected behavior
- verification command and expected output

## Coding principles

Include verbatim:

```
CODE PRINCIPLES (follow strictly):
1. TDD: write the failing test first, watch it fail, write minimal code, watch it pass, refactor.
2. No production code without a failing test first.
3. One behavior per test; clear descriptive names; test real code, not mocks when possible.
4. Run the exact verification command after every task and report the result.
5. No hardcoded secrets, SQL injection, shell injection, eval/exec with user input, or path traversal.
6. Validate user inputs; handle errors for I/O, network, DB calls.
7. Keep changes surgical — only touch files required by the task.
8. DRY and YAGNI: reuse existing helpers, prefer stdlib, no speculative abstractions.
9. Commit after every task.
10. If a task is unclear, stop and state what is missing. Do not guess.
11. No web search or browser navigation. Use only project files and tools.
```

## Output format

After completing all tasks, report:

1. `git status --short`
2. `git diff --stat`
3. Test/lint/build output
4. Any blockers or concerns
5. Next steps you recommend

## Launch command

```python
terminal(
    command="opencode run -f /tmp/brief.md 'Implement the attached plan task-by-task. Report status after each task.'",
    workdir="/absolute/path/to/project",
    background=True,
    notify_on_complete=True
)
```
