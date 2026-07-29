# codebase-memory-mcp with OpenCode

Session: 2026-07-28
OpenCode version: 1.18.8

## Overview

The same `codebase-memory-mcp` server used by Hermes `codebase-memory-audit` can be exposed to OpenCode as an MCP server. This lets OpenCode query the project knowledge graph during coding sessions.

## Setup

### 1. Verify the binary

```bash
which codebase-memory-mcp
codebase-memory-mcp --version
```

### 2. Add to OpenCode config

Edit `~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "codebase-memory": {
      "type": "local",
      "enabled": true,
      "command": ["/home/natan/.local/bin/codebase-memory-mcp"],
      "timeout": 30000
    }
  }
}
```

### 3. Verify connection

```bash
opencode mcp list
```

Expected: `✓ codebase-memory connected`.

## Useful prompts for OpenCode

- "Show me the architecture overview of this project"
- "What functions call `authMiddleware`?"
- "What does `handleSubmit` call outbound?"
- "Find symbols matching `.*Controller.*`"
- "List entry points and hotspots"

## Limits

- OpenCode decides when to call the tool; explicit prompts work best.
- The project must be indexed first; re-index after large refactors.
- CSS class usage is not tracked (use PurgeCSS for dead CSS).
- Not suitable for non-code corpora like Obsidian vaults.

## See also

- `SKILL.md` in this skill for full `codebase-memory-audit` workflow.
- `references/cbm-usage-notes.md` for exact CLI flags and query examples.
- `hermes-skill-library/references/opencode-mcp-config-pattern.md` for the general MCP config schema.
