# OpenCode + MCP via `serve` + `run --attach`

## When to use this pattern

Use this pattern when you want OpenCode to access MCP servers (`obsidian`, `codebase-memory`, custom tools) while running headless/batch tasks. Plain `opencode run --auto --dir <project> < brief.md` does **not** expose MCP; calls return `Unknown`.

## Verified environment

- OpenCode CLI 1.18.10
- Local Ollama provider at `http://127.0.0.1:11434/v1`
- MCP servers declared in `~/.config/opencode/opencode.json` with `"enabled": true`
- Project is a git repository (OpenCode diffs/commits more reliably)

## Configuration

`~/.config/opencode/opencode.json` example (no `permissions` key — that key is rejected by the 1.18.10 schema):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "ollama/kimi-k2.7-code:cloud",
  "provider": {
    "ollama": {
      "models": {
        "kimi-k2.7-code:cloud": {
          "_launch": true,
          "limit": { "context": 256000, "output": 32768 },
          "name": "kimi-k2.7-code:cloud"
        }
      },
      "name": "Ollama",
      "npm": "@ai-sdk/openai-compatible",
      "options": { "baseURL": "http://127.0.0.1:11434/v1" }
    }
  },
  "mcp": {
    "codebase-memory": {
      "type": "local",
      "enabled": true,
      "command": ["/home/natan/.local/bin/codebase-memory-mcp"],
      "timeout": 30000
    },
    "obsidian": {
      "type": "local",
      "enabled": true,
      "command": [
        "/home/natan/.nvm/versions/node/v24.13.1/bin/node",
        "/home/natan/.nvm/versions/node/v24.13.1/lib/node_modules/obsidian-mcp/build/main.js",
        "/home/natan/obsidian-memory"
      ],
      "timeout": 30000
    }
  }
}
```

## Step-by-step recipe

### 1. Ensure the project is a git repo

**This is mandatory.** OpenCode is far more reliable with git. Before any OpenCode task:

```bash
cd <project-root>
git init
git add .
git commit -m "initial: baseline before opencode run"
```

### 2. Start the OpenCode server

Use a background terminal process:

```bash
cd <project-root>
opencode serve --port 4096 --hostname 127.0.0.1
```

Wait for:

```
opencode server listening on http://127.0.0.1:4096
```

### 3. Smoke test

```bash
opencode run --auto --attach http://127.0.0.1:4096 \
  --dir <project-root> \
  'List the MCP servers and tools you can access, then respond exactly: OPENCODE_MCP_SMOKE_OK'
```

Expected output contains `OPENCODE_MCP_SMOKE_OK` and lists `obsidian` and `codebase-memory` tools.

### 4. Run the brief via attach

```bash
opencode run \
  --auto \
  --attach http://127.0.0.1:4096 \
  --dir <project-root> \
  --title 'Task title' \
  < /path/to/brief.md > task.log 2>&1
```

Capture stdout/stderr to a log file for post-run review.

### 5. Stop the server

Kill the background `opencode serve` process when the run finishes.

## Brief requirements

Include these at the top of every brief used with this pattern:

```markdown
## CRITICAL INSTRUCTIONS

1. Do NOT use todo or planning tools.
2. Use git. Run `git status`, `git diff`, and commit changes with a clear message when done.
3. Do NOT change data files or structural types.
4. Run verification before finishing: `npx tsc --noEmit` and `npm run build` (or project-specific commands).

## External context sources

Before editing, read this note via the obsidian MCP server and follow its principles:
- `~/obsidian-memory/Operations/Coding Principles.md`

You have access to MCP servers:
- **obsidian** — read design references and project notes in vault `obsidian-memory`.
- **codebase-memory** — query project architecture; project slug is derived from the directory path.

If an MCP tool returns unknown/error, fall back to reading files directly.
```

## Verification

After OpenCode finishes, always run the project verification commands yourself:

```bash
cd <project-root>
npx tsc --noEmit
npm run lint
npm run build
```

For visual/UI changes, also capture screenshots via Playwright and compare before/after.

## Parallel lanes

Start one server. Then dispatch multiple attached runs concurrently, but **only when file sets are strictly disjoint**:

```bash
opencode run --auto --attach http://127.0.0.1:4096 --dir <project> --title 'Lane A' < lane-a.md > lane-a.log 2>&1 &
opencode run --auto --attach http://127.0.0.1:4096 --dir <project> --title 'Lane B' < lane-b.md  > lane-b.log  2>&1 &
wait
```

After lanes finish, reconcile: check `git status --short`, run build/lint/tests, capture screenshots.

## Common failures

| Symptom | Cause | Fix |
|---|---|---|
| `obsidian_list-available-vaults Unknown` | Running plain `opencode run`, not attached to `opencode serve` | Use `opencode serve` + `opencode run --attach` |
| `Configuration is invalid … Unrecognized key: permissions` | Added `permissions` block to `opencode.json` | Remove `permissions`; control behavior via brief only |
| OpenCode does not commit or diff cleanly | Project is not a git repo | `git init` + initial commit before dispatch |
| Server refuses to start | Port 4096 in use | Pick another port and update `--attach` URL |

## Fallback

If the server starts and smoke test passes but MCP calls still fail inside the task, stop OpenCode, report the failure to the user, and fall back to inline execution via `superpowers-executing-plans`. Do not leave OpenCode stalled.

## Session provenance

- 2026-08-01: silicone-landing-v2 — OpenCode successfully upgraded `ProductCard.tsx` using `opencode serve --port 4096` + `opencode run --auto --attach http://127.0.0.1:4096`, with `obsidian` and `codebase-memory` MCP servers enabled.
