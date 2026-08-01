# Headless `opencode run` todowrite / multi-step failure

## Symptom

OpenCode CLI `opencode run < prompt.md` crashes with:

```
✗ Todos failed
Error: The todowrite tool was called with invalid arguments:
SchemaError(Missing key at ["todos"][0]["content"])
```

or stops after creating only a partial set of files.

## Root cause

OpenCode's internal todo/planning tool is broken in headless `run` mode for
multi-step prompts. It can also fail with `permission requested: external_directory`
when not scoped to a project directory.

## Mitigation steps

1. Update OpenCode CLI and plugin:
   ```bash
   npm install -g opencode-ai@latest
   cd ~/.config/opencode && npm install @opencode-ai/plugin@latest
   ```

2. Disable MCP servers in `~/.config/opencode/opencode.json` when context is
   provided via the prompt:
   ```json
   {
     "mcp": {
       "obsidian": { "type": "local", "enabled": false, ... },
       "codebase-memory": { "type": "local", "enabled": false, ... }
     }
   }
   ```

3. Add an anti-todo instruction at the top of every brief:
   ```markdown
   Do not use todo, planning, or task-tracking tools. Do not call todowrite
   or similar tools. Execute the work directly.
   ```

4. Launch with `--auto --dir /absolute/path/to/project`:
   ```bash
   opencode run --auto --dir /path/to/project --title 'Brief title' < brief.md
   ```

## Known practical limits

Even with the workaround, headless `opencode run` is **unreliable for tasks
that create 10+ files in one shot**. It may:
- stop after a partial file set,
- only inspect files without writing,
- ignore later items in the brief.

For heavy multi-file implementation tasks, prefer **Hermes `delegate_task`**
leaf subagents.

## Fallback decision

If `opencode run` fails twice with the same error, stop retrying and switch to
`delegate_task`. Do not keep tuning OpenCode prompts for tasks it cannot
complete headlessly.
