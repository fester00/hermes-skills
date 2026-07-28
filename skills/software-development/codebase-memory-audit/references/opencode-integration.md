# codebase-memory-mcp with OpenCode

Session: 2026-07-28
OpenCode version: 1.18.8

## Overview

The same `codebase-memory-mcp` server used by Hermes `codebase-memory-audit` can be exposed to OpenCode as an MCP server. This lets OpenCode query the project knowledge graph during coding sessions.

## Setup

### 1. Index the project

From the project root:

```bash
codebase-memory-mcp cli index_repository --repo-path .
```

Project slug is derived from the path, e.g. `/home/natan/pentajunior-v2` → `home-natan-pentajunior-v2`.

### 2. Add to OpenCode

Edit `~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "codebase-memory": {
      "command": "/home/natan/.local/bin/codebase-memory-mcp"
    }
  }
}
```

Or via CLI:

```bash
opencode mcp add codebase-memory
```

### 3. Verify

```bash
opencode mcp list
opencode run "Show me the architecture overview of this project"
```

## Useful prompts for OpenCode

- "Show me the architecture overview of this project"
- "What functions call `authMiddleware`?"
- "What does `handleSubmit` call outbound?"
- "Find symbols matching `.*Controller.*`"
- "List entry points and hotspots"

## Limitations

- OpenCode decides when to call the tool; explicit prompts work best.
- The project must be indexed first; re-index after large refactors.
- CSS class usage is not tracked (use PurgeCSS for dead CSS).
- Not suitable for non-code corpora like Obsidian vaults.

## See also

- `SKILL.md` in this skill for full `codebase-memory-audit` workflow.
- `references/cbm-usage-notes.md` for exact CLI flags and query examples.
