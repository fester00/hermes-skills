# OpenCode MCP Config Pattern

Session-derived recipe for wiring local MCP servers into OpenCode so the heavy agent can use `codebase-memory` and `obsidian` tools.

## Required JSON shape in `~/.config/opencode/opencode.json`

```json
{
  "$schema": "https://opencode.ai/config.json",
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

## Rules

- `type` must be `"local"`.
- `enabled` must be `true`.
- `command` must be an **array** of strings, even for a single binary.
- Arguments go inside `command`; a separate `args` field is not used.

## Verification

```bash
opencode mcp list
```

Expected:

```
●  ✓ codebase-memory connected
●  ✓ obsidian connected
```

## Why this matters for orchestration

OpenCode with MCP can query the project knowledge graph and read the Obsidian vault, but it still does not see Hermes skills or memory. Project conventions and coding principles must be quoted in the brief.
