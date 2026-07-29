# OpenCode stdin launch recipe

Tested with `opencode` 1.18.8 on Linux (Node 24, local Ollama-compatible proxy).

## The trap

The obvious-looking launch fails:

```bash
opencode run -f /tmp/brief.md 'Implement the attached plan task-by-task.'
# Error: File not found: Implement the attached plan task-by-task.
```

OpenCode treats the quoted prompt argument as a file path, not as the task prompt. Put the instruction inside the brief instead.

## Correct one-shot launch

```bash
cd /path/to/project
opencode run < /tmp/brief.md
```

From Hermes:

```python
terminal(
    command="opencode run < /tmp/brief.md",
    workdir="/path/to/project",
    background=True,
    notify_on_complete=True
)
```

## With extra context files

```bash
opencode run -f /tmp/extra-context.md < /tmp/brief.md
```

## Minimal smoke-test brief

Use this to verify an OpenCode installation can follow a brief end-to-end.

```markdown
# OpenCode Brief

## Goal
Create a simple HTML5 test page and README in the working directory, verify the files, and report completion.

## Project context

- **Tech stack:** Plain HTML5 + Markdown
- **Project root:** `/tmp/opencode-smoke/`
- **Test command:** `ls -la /tmp/opencode-smoke/`
- **Conventions:** Create a fresh directory, write exactly the requested files, run verification commands.

## Plan

1. Create `/tmp/opencode-smoke/index.html` with valid HTML5, a heading, a timestamp paragraph, and a button.
2. Create `/tmp/opencode-smoke/README.md` with a heading, one-sentence description, and list of files.
3. Run `ls -la /tmp/opencode-smoke/` and end the report with `OPEN_CODE_SMOKE_OK`.

## Output format

Report status after each step, show verification command output, and finish with the exact marker `OPEN_CODE_SMOKE_OK`.
```

Save it as `/tmp/opencode-smoke-brief.md`, then:

```bash
mkdir -p /tmp/opencode-smoke
opencode run < /tmp/opencode-smoke-brief.md
```

Success = files created, marker present in output.

## When to use this pattern

- Heavy OpenCode tasks launched from Hermes.
- Any one-shot `opencode run` where the prompt plus file attachments would otherwise be misinterpreted.
- Smoke tests and orchestration validation.
