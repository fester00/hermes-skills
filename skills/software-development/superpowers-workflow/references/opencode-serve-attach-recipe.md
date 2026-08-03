# OpenCode Serve + Attach Recipe

> Session-verified recipe for running OpenCode agents with MCP access in headless mode.

## Problem

Headless `opencode run --auto --dir <project> < brief.md` launches and can edit files, but it cannot call MCP servers. Attempts yield `obsidian_list-available-vaults Unknown` / `codebase-memory_list_projects Unknown` because the headless runner does not expose MCP tools.

## Solution

Run a persistent OpenCode server in the project directory and attach headless runners to it.

## Recipe

### 1. Ensure git exists (init only if needed)

```bash
cd <project-root>
if [ ! -d .git ]; then
  git init
  git add .
  git commit -m "initial: baseline"
fi
```

Never re-initialize an existing repository.

### 2. Start the OpenCode server

```bash
cd <project-root>
opencode serve --port 4096 --hostname 127.0.0.1
```

Keep it running for all attached executions.

### 3. Smoke-test attach + MCP

```bash
opencode run --auto --attach http://127.0.0.1:4096 \
  --dir <project-root> \
  'Use obsidian MCP to read ~/obsidian-memory/Operations/Coding Principles.md and summarize it in one sentence. Then respond exactly: OPENCODE_MCP_OK.'
```

Expected output contains `OPENCODE_MCP_OK`.

### 4. Run a task brief

```bash
opencode run --auto --attach http://127.0.0.1:4096 \
  --dir <project-root> \
  --title 'Task N: <title>' \
  < task-N-brief.md > task-N.log 2>&1
```

Always capture stdout/stderr to a log file for post-run review.

### 5. Stop the server when done

Kill the background `opencode serve` process.

## Common Pitfalls

- **Port conflicts:** if 4096 is in use, pick another port consistently for the session.
- **Server without `--hostname 127.0.0.1`:** may bind to localhost only or expose to LAN unintentionally.
- **Attached runs without `--dir`:** use the server's CWD, not the target project.
- **MCP servers in `~/.config/opencode/opencode.json` must be `enabled: true`.**

## Verification Checklist

- [ ] `opencode --version` works.
- [ ] `opencode mcp list` shows obsidian + codebase-memory as connected.
- [ ] Smoke test with MCP read returns `OPENCODE_MCP_OK`.
- [ ] Task log shows `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`.
