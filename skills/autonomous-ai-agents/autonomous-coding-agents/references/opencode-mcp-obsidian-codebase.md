# MCP server setup for OpenCode: Obsidian + codebase-memory

Use this recipe when an OpenCode agent needs to read the user's Obsidian vault or query the codebase-memory graph.

## Profile config snippet

Add the `mcp` block to a profile or to `~/.config/opencode/opencode.json`:

```json
{
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

Adjust the Node path, the obsidian-mcp path, and the vault path to the actual host values.

## What the agent can do

| Server | Typical tools | Use in brief |
|---|---|---|
| `obsidian` | `search-vault`, `read-note` | "Find notes about X in the vault and summarize" |
| `codebase-memory` | graph queries, symbol search | "Search the codebase graph for usages of SYMBOL" |

## Verification

1. Start OpenCode and list MCP servers:
   ```bash
   opencode mcp list
   ```

2. Run a tiny task that reads from Obsidian:
   ```bash
   opencode run --auto /tmp/mcp-smoke \
     "Using the obsidian MCP server, search the vault for 'OpenCode' and write a one-line summary to obsidian-smoke.txt"
   ```

## Pitfalls

- Hard-code absolute paths in the profile. Relative paths or `~` expansion are not guaranteed inside the OpenCode server process.
- Verify the binary exists before launching a long agent task: `ls -la /home/natan/.local/bin/codebase-memory-mcp` and `ls -la .../obsidian-mcp/build/main.js`.
- If the Obsidian MCP times out, raise `timeout` or reduce the vault size scanned in the first request.
