# OpenCode Pitfalls and Workarounds

## Problem: MCP access inside OpenCode is unreliable

OpenCode CLI may list MCP servers in the smoke test (`opencode run 'List MCP servers...'`) but still fail during real execution with:

- `obsidian_list-available-vaults Unknown`
- `codebase-memory_list_projects Unknown`
- repeated MCP timeouts or empty responses

**Rule:** do not keep retrying or leave OpenCode stalled. Stop the agents, report the MCP failure to the user, and fall back to **inline execution** via `superpowers-executing-plans` or to **Hermes `delegate_task` subagents**.

## Problem: OpenCode sandbox auto-rejects external-directory writes

Even when the user explicitly authorizes OpenCode to write outside its working directory, the OpenCode environment may auto-reject with:

```
! permission requested: external_directory (/mnt/data/natan-storage/silicone-lending-v3/src/*, ...); auto-rejecting
```

or fail with an internal tool error such as:

```
✗ Todos failed
Error: The todowrite tool was called with invalid arguments: SchemaError(...)
```

**Rule:** when the target project lives outside OpenCode's default cwd, prefer **Hermes `delegate_task` subagents** instead. They share the host filesystem and can write to `/mnt/data/natan-storage` without sandbox permission dance. Use OpenCode only when the entire workspace can be created inside OpenCode's cwd and then moved by Hermes afterward. See `references/opencode-sandbox-external-directory.md` for the full decision tree and reproduction recipe, and `references/opencode-headless-limitations.md` for the `todowrite` schema bug and the prompt-level workaround.

## Mitigation: disable MCP servers in headless config

If you choose to run OpenCode headless despite the limitations, disable MCP
servers in `~/.config/opencode/opencode.json` (`enabled: false`) and pass all
external context directly in the brief. This avoids `obsidian_list-available-vaults
Unknown` and `codebase-memory_list_projects Unknown` errors that abort execution
before any files are created.

Example snippet:

```json
"mcp": {
  "codebase-memory": { "type": "local", "enabled": false, ... },
  "obsidian": { "type": "local", "enabled": false, ... }
}
```

When MCP is disabled, do NOT include the "External context sources" block in
the brief; the agent has no MCP to call. Put the needed context inline instead.

## Workaround: scaffold inside OpenCode cwd and move

If you still want to use OpenCode for a project outside its cwd:

1. Let OpenCode create the project under its own cwd (e.g. `/tmp/silicone-lending-v3`).
2. After OpenCode finishes, move the result to the real target directory with Hermes terminal.
3. Verify at the real target path.

This avoids the `external_directory` auto-reject.

## Canonical External context sources block

When OpenCode *can* reach MCPs, paste this block into every brief:

```markdown
## External context sources

Use the configured MCP servers for all research outside this project directory:
- **obsidian** — query the `obsidian-memory` vault for design references, project notes, templates, runbooks.
- **codebase-memory** — index and query relevant repositories for architecture, file structure, data paths, and reusable code.

Do NOT read, copy, or list files outside the current project directory via direct terminal commands. If MCP servers are unavailable, stop and report.
```

## Smoke test

Before any OpenCode-driven execution, run:

```bash
opencode --version
opencode auth list
opencode run 'List MCP servers you can access, then respond exactly: OPENCODE_SMOKE_OK'
```

If MCP servers are not listed, do not dispatch OpenCode for tasks requiring external context. Also verify the latest CLI version (`npm install -g opencode-ai@latest`) and plugin version (`cd ~/.config/opencode && npm install @opencode-ai/plugin@latest`) before relying on headless execution; stale plugin/CLI combinations can produce schema errors.

## Headless smoke task

Before a large headless run, test with a focused single-file prompt:

```bash
opencode run --auto --dir /path/to/project --title 'smoke' <<'EOF'
Do not use todo or planning tools. Write "ok" to /path/to/project/.opencode-smoke.
EOF
```

If this single-file task fails, do not dispatch a large brief headlessly.

## Decision tree

```
Can the project be created entirely inside OpenCode cwd?
  Yes  → Use OpenCode with MCP context block.
  No   → Use Hermes delegate_task subagents instead.
         (OpenCode will likely hit external_directory auto-reject.)

Did OpenCode fail with MCP Unknown / auto-reject / todowrite error?
  Yes  → Stop, report, fall back to delegate_task or inline execution.
  No   → Continue verification as planned.
```

## Session references

- 2026-07-31: silicone-landing-v2 — OpenCode blocked on direct filesystem access outside cwd; fixed by copying assets into project directory.
- 2026-08-01: silicone-lending-v3 — OpenCode failed with `external_directory` auto-reject and `todowrite` schema errors despite explicit user authorization; succeeded with Hermes `delegate_task` subagents. Later testing showed that adding `"Do not use todo or planning tools"` and updating CLI/plugin to 1.18.10 allowed simple headless tasks to work, but large multi-file briefs still truncated. MCP servers were disabled in `~/.config/opencode/opencode.json` to prevent `Unknown` errors.
