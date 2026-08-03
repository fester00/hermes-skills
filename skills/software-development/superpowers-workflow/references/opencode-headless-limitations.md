# OpenCode headless execution limitations

## Symptom

When invoking `opencode run < brief.md` from a pipe, OpenCode may fail before
creating files, even with `--auto --dir <project>`:

```
✗ Todos failed
Error: The todowrite tool was called with invalid arguments: SchemaError(
  Missing key at ["todos"][0]["content"])
```

The same error appears with `--pure`, which disables external plugins, so it is
an internal OpenCode tool issue rather than a plugin bug.

## Update: the error depends on prompt-triggered planning

Recent tests show the `todowrite` SchemaError is triggered when the prompt
encourages OpenCode to "plan your work" or when the task is large enough that
OpenCode decides to create a todo list. Adding an explicit instruction
`"Do not use todo or planning tools"` to the brief allows headless execution
with `--auto --dir` to create multiple files successfully. However, OpenCode
still truncated execution on large multi-file briefs and omitted files.

## Configuration recipe for headless use

If you choose to use OpenCode headlessly, prepare the environment once:

1. Update the global CLI and plugin:
   ```bash
   npm install -g opencode-ai@latest
   cd ~/.config/opencode && npm install @opencode-ai/plugin@latest
   ```
2. Disable MCP servers in `~/.config/opencode/opencode.json` for headless runs
   where context is passed via the brief:
   ```json
   {
     "mcp": {
       "obsidian": { "type": "local", "enabled": false, ... },
       "codebase-memory": { "type": "local", "enabled": false, ... }
     }
   }
   ```
3. **Always prepend the brief with the anti-todo instruction. This is the only reliable way to avoid the `todowrite` SchemaError in headless mode:**
   ```markdown
   Do not use todo, planning, or task-tracking tools. Do not call todowrite or similar tools. Execute the work directly.
   ```
4. Launch with `--auto --dir /path/to/project`:
   ```bash
   opencode run --auto --dir /mnt/data/natan-storage/project --title 'Task' < brief.md
   ```
5. Verify immediately after it exits; do not assume it completed every file.
   - For 1–3 file tasks, OpenCode usually succeeds.
   - For 10+ file greenfield builds, OpenCode frequently truncates or omits files.
   - For any task that involves planning, the anti-todo instruction is mandatory.

- `opencode run --auto --dir /path/to/project` successfully passes permission
decisions (no more `external_directory` auto-reject).
- OpenCode can execute simple one-off tasks via piped stdin (write a single file).
- Adding `"Do not use todo or planning tools"` to the prompt avoids the `todowrite`
  error on multi-step tasks.
- Updating `opencode-ai` to the latest version (1.18.10 at the time of writing)
  removed the stale `todowrite` schema mismatch in simple tests.

## What does NOT work reliably

- Large greenfield briefs with 10+ files via headless stdin. OpenCode may
  create only a subset of files or stop without error.
- Headless execution that triggers OpenCode's own planning/todo workflow.
- Passing complex multi-page implementation work through a single stdin brief.

## Recommended pattern

For greenfield or multi-file builds where you want an autonomous agent:

1. Write a detailed markdown brief.
2. Launch via `delegate_task` with `toolsets=['terminal', 'file']`.
3. The subagent writes files directly in the project directory.
4. Hermes retains planning, verification, and final review.

If you still want to use OpenCode for small, isolated tasks:

- Add `"Do not use todo, planning, or task-tracking tools. Execute directly."`
  at the top of the brief.
- Keep each brief to one focused deliverable (1–3 files).
- Use `--auto --dir /path/to/project`.
- Verify the result immediately; do not assume OpenCode completed all files.

Only fall back to OpenCode for large work if you can run it interactively
(`pty=true`) and the smoke test in the TUI succeeds.

## Session provenance

- 2026-08-01: `silicone-lending-v3` at `/mnt/data/natan-storage/silicone-lending-v3`.
  `opencode run --auto --dir /mnt/data/natan-storage/silicone-lending-v3 < brief.md`
  failed repeatedly on `todowrite` SchemaError when the brief included planning
  language. Adding `"Do not use todo or planning tools"` allowed simple multi-file
  tests to pass, but large briefs still truncated. Hermes `delegate_task`
  completed the same work without issues. OpenCode was updated from 1.18.8 to
  1.18.10; MCP servers were disabled in `~/.config/opencode/opencode.json` to
  avoid `Unknown` errors during headless execution.
- 2026-08-01 (continued): For the final design pass, Hermes `delegate_task` was
  used with `framer-motion` while OpenCode remained limited to small tasks.
  The resulting landing page used glassmorphism, animated gradient mesh, and
  scroll-triggered animations. A key lesson: `initial={{ opacity: 0 }}` with
  `whileInView` makes SSR/SSG previews blank until scroll; set
  `initial={{ opacity: 1, y: 20 }}` for visible first paint.
- 2026-08-01 (final): Confirmed on `silicone-lending-v3` that even with
  `--auto --dir` and `--pure`, large redesign briefs (Drift-style adaptation)
  truncated. Hermes `delegate_task` subagents (Groups A/B/C) completed tokens,
  navbar/hero, about/sticky-products, stats/contact/footer/modal/form in parallel,
  followed by controller integration, tsc, build, and screenshots. This validated
  the rule: OpenCode headless is for 1–3 file tasks; multi-file design/dev work
  flows through `delegate_task`.
