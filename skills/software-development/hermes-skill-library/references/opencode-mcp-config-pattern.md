# OpenCode MCP Config Pattern

Reference note: how to wire local MCP servers (codebase-memory, obsidian) into OpenCode via `~/.config/opencode/opencode.json`.

## Schema

OpenCode expects `mcp.<name>` to be either `McpLocalConfig` or `McpRemoteConfig`.
Local config fields:

- `type`: must be `"local"`
- `enabled`: `true`
- `command`: array of strings (command + args)
- `timeout`: ms for tool discovery (default 5000)
- `environment`: optional env vars

## Example

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "ollama/kimi-k2.7-code:cloud",
  "provider": { ... },
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

## Verification

```bash
opencode mcp list
```

Should show `codebase-memory connected` and `obsidian connected`.

## Pitfalls

- Do not use string `command` — must be array.
- `type` and `enabled` are required; missing them causes a config validation error.
- `timeout` is for MCP tool discovery, not request timeout.
