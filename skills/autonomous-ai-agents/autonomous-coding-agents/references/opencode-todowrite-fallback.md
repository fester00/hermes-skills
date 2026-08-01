# OpenCode `todowrite` failure and fallback

## Symptom

Running `opencode run --auto --dir /path/to/project < brief.md` exits early with:

```
✗ Todos failed
Error: The todowrite tool was called with invalid arguments: SchemaError(Missing key
  at ["todos"][0]["content"]).
```

or:

```
Error: The todowrite tool was called with invalid arguments: SchemaError(Missing key
  at ["todos"][0]["priority"]).
```

The project directory is left empty or only partially populated.

## Root cause

OpenCode has a built-in `todowrite` tool that it tries to use when the prompt looks like a multi-step task. In headless `opencode run` mode the tool schema is not satisfied, causing a fatal error. This happens regardless of:

- `--auto` / no `--auto`
- `--pure` (external plugins disabled)
- MCP server availability
- target directory (`/tmp` or `/mnt/data/...`)

The bug is in OpenCode's internal planning/todo mechanism, not in permissions or configuration.

## Reproduction

1. Write a complex multi-file brief with explicit file list and verification steps.
2. Run:
   ```bash
   opencode run --auto --dir /path/to/project < brief.md
   ```
3. Watch for `todowrite` errors in the log.

Simple one-line tasks ("write a single file") usually succeed.

## Verified workaround

**Switch to Hermes native `delegate_task` subagents.** They do not have the `todowrite` limitation and can write to the project directory directly.

Example:

```python
delegate_task(
    goal="Create Next.js project skeleton...",
    context="Project path: /path/to/project. Files to create: ...",
    role="leaf"
)
```

## Other options to try

- **Interactive TUI** (`opencode /path/to/project` or `opencode --mini`) may avoid the headless `todowrite` path.
- **Break the task into tiny single-file prompts** and feed them sequentially. This is slow and not recommended for multi-file work.
- **Update OpenCode** to the latest version — the bug may be fixed in a newer release.

## Decision rule

| Symptom | Action |
|---|---|
| Simple single-file task | Use `opencode run` |
| Multi-file / multi-step task with `todowrite` error | Switch to `delegate_task` immediately |
| Need OpenCode specifically | Try interactive TUI or update OpenCode |

## References

- Skill: `autonomous-coding-agents`
- Related: `opencode`, `superpowers-workflow`, `subagent-driven-development`, `dispatching-parallel-agents`
