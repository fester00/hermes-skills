# OpenCode Execution Recipe

Validated pattern for running OpenCode agents against a project in this environment.

## When to use this recipe

Use this recipe whenever `superpowers-workflow` reaches Phase 4 and the task is multi-file or multi-step. Inline execution is only for tiny, single-verification changes.

## Prerequisites

1. The target directory must be a git repository. If it is not, initialize it:
   ```bash
   cd <project-root>
   git init
   git add .
   git commit -m "initial: baseline"
   ```
2. OpenCode CLI 1.18.10 or later must be installed and configured in `~/.config/opencode/opencode.json`.
3. MCP servers (obsidian, codebase-memory) must be configured in `~/.config/opencode/opencode.json` as `type: local` with `enabled: true`.

## Important limitation

Headless `opencode run --auto --dir <project> < brief.md` **cannot** call MCP servers. The `opencode mcp list` command shows them as connected, but headless invocations receive `Unknown` responses for MCP tool calls.

To use MCP servers, you must run a persistent OpenCode server and attach to it.

## Recipe

### 1. Start the OpenCode server

```bash
cd <project-root>
opencode serve --port 4096 --hostname 127.0.0.1
```

Leave it running in the background. It will print:
```
opencode server listening on http://127.0.0.1:4096
```

### 2. Smoke-test the connection

```bash
opencode run --auto --attach http://127.0.0.1:4096 \
  --dir <project-root> \
  'Do not use todo or planning tools. Run any lightweight MCP query via obsidian or codebase-memory to prove connectivity, then respond exactly: OPENCODE_SMOKE_OK.'
```

### 3. Write a brief file

Every brief must:
- Start with: `Do not use todo or planning tools.`
- Define exact files the agent may modify.
- Include an **External context sources** block with MCP servers to use (obsidian, codebase-memory).
- For UI changes, include a **Visual verification contract** with exact design tokens and required after-screenshots.
- Include verification commands (`npx tsc --noEmit`, `npm run build`) and require clean exit codes.
- Name a report file path and a log file path.

### 4. Execute

```bash
opencode run --auto --attach http://127.0.0.1:4096 \
  --dir <project-root> \
  --title 'Task N: <title>' \
  < workspace/task-N-brief.md > workspace/task-N.log 2>&1
```

### 5. Verify

After the run completes:
- Check the log for `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`.
- Run `git diff --stat`.
- Run verification commands from the brief.
- For UI changes, capture after-screenshots via Playwright.

### 6. Stop the server

When all tasks are complete:
```bash
kill <opencode-serve-pid>
```

## Parallel lanes

For independent tasks with strictly disjoint file sets, start one server and dispatch multiple `opencode run --attach` invocations concurrently, each with its own brief and log. After all lanes finish, reconcile: check `git status --short`, run full verification, capture after-screenshots.

## Fallback

If OpenCode cannot connect to MCP servers even after serve/attach, stop and report the failure to the user. Do not silently fall back to inline execution unless the user explicitly approves it.

## Security note

`opencode serve` without `OPENCODE_SERVER_PASSWORD` is unsecured on localhost. This is acceptable for local development, but do not expose the port beyond `127.0.0.1`.
