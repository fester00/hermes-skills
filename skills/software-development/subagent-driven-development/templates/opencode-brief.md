# OpenCode Agent Brief Template

Starter template for a markdown brief passed to OpenCode. Prefer piping the brief via stdin (`opencode run < /tmp/brief.md`) because the `-f file.md 'prompt'` form is fragile and may be interpreted as a missing file argument in some OpenCode versions.

## Usage

1. Copy this file to `/tmp/brief.md` (or `/tmp/brief-<part>.md` for parallel agents).
2. Fill every placeholder.
3. Launch from the target project directory.

## Template

```markdown
# OpenCode Brief

## Goal

One sentence describing what to build or refactor.

## Project context

- **Tech stack:** [e.g. React 19 + Vite + Tailwind v4 + better-sqlite3]
- **Project root:** [absolute path]
- **Test command:** [e.g. `npm test`, `pytest tests/ -q`]
- **Lint command:** [e.g. `npx eslint .`, `ruff check .`]
- **Build command:** [e.g. `npm run build`]
- **Conventions:** [naming, file layout, style, state management, link to AGENTS.md if present]

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

## Files NOT to touch

- [List protected files or directories]

## Output format

After each task, report:
- Status: DONE / DONE_WITH_CONCERNS / BLOCKED
- Files changed
- Verification result (command + output)
- Concerns / next steps

At the end, run and report:
- `git status --short`
- `git diff --stat`
- [Full test/lint/build command]
```

## Launch command

**Recommended:** pipe the brief via stdin to avoid the fragile `-f file.md 'prompt'` interpretation:

```python
terminal(
    command="opencode run < /tmp/brief.md",
    workdir="/absolute/path/to/project",
    background=True,
    notify_on_complete=True
)
```

**Alternative** (only if your OpenCode version supports it):

```python
terminal(
    command="opencode run -f /tmp/brief.md 'Implement the attached plan task-by-task. Report status after each task.'",
    workdir="/absolute/path/to/project",
    background=True,
    notify_on_complete=True
)
```

## See also

- Skill `opencode` — full OpenCode orchestration guide
- Skill `subagent-driven-development` — when to use OpenCode vs delegate_task
- Skill `writing-plans` — how to write the plan this brief is based on
