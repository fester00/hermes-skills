# OpenCode Execution (opt-in path)

OpenCode is **not** the default engine: Hermes subagents are (see `superpowers-workflow` Phase 4). Use this
recipe only when the user explicitly asks for OpenCode, or for a one-off prompt against a gateway model you
have no direct API key for.

Verified on `opencode v2.0.28`, 2026-10-13. Command forms differ from v1: `--attach` and `--dir` are gone.

## Prerequisites

1. Target directory is a git repository with a usable baseline. If not — ask the user before `git init`.
2. A profile that carries both the provider and the MCP servers: `~/.config/opencode/profiles/*.json`.
3. ⚠️ **Root configs can silently kill the profile's provider.** `OPENCODE_CONFIG` merges with
   `~/.config/opencode/opencode.json` and `opencode.jsonc`; the `providers` object behaves as
   last-document-wins, so a profile's `providers` disappears when a root config also defines `providers`
   (`Error: Model unavailable: opencode-go/<model>`). Verify before promising anything:
   ```bash
   OPENCODE_CONFIG=<profile> opencode models | grep opencode-go | head
   ```
   If the list is empty, either state the provider in the root `opencode.json`, remove the conflicting
   `providers` block from `opencode.jsonc`, or run in an isolated `HOME`.

## Smoke test

```bash
cd <project-root>
export OPENCODE_CONFIG=$HOME/.config/opencode/profiles/opencodeai.json
opencode run --auto -m <provider>/<model> 'Respond exactly: OPENCODE_SMOKE_OK'
```

`--standalone` is only needed when the background service is not listening (`ss -tlnp | grep 49374`).
A persistent server (needed for `opencode api`, web/TUI clients) is
`opencode serve --hostname 127.0.0.1 --port 4096`, then run with `--server http://127.0.0.1:4096`.

## Brief form (per task)

Markdown file, passed on stdin, executed from the project directory:

```markdown
Do not use todo or planning tools. Just execute the steps below.

## Goal
One sentence.

## Files to modify
- `src/components/X.tsx`

## Exact requirements
…

## External context sources
Read `~/obsidian-memory/Operations/Coding Principles.md` via the obsidian MCP server and follow it.
Use the configured MCP servers (obsidian, codebase-memory) for research outside this project.
Do not read or list files outside the project directory with direct shell commands.

## Verification
Run and require exit 0: `npx tsc --noEmit`, `npm run build`.

## Report
Write the short report to `<project>/.superpowers/opencode-<lane>-report.md` and print only
status, commits, one-line test summary, concerns.
```

```bash
opencode run --auto --title 'Task N: <title>' < brief.md > task-N.log 2>&1
grep -E 'DONE|DONE_WITH_CONCERNS|NEEDS_CONTEXT|BLOCKED' task-N.log
```

## Differences from the Hermes-subagent path

- OpenCode agents see the project, `AGENTS.md` and OpenCode's own skills — briefs can point at files
  instead of pasting context.
- Their model is chosen per run (`-m`), independent of the Hermes parent model.
- They cannot be steered mid-run; the whole brief must be self-contained, and recovery means re-running the
  brief, not steering.
- Keep at most 2 heavy OpenCode runs concurrent, and only when file sets are strictly disjoint.
