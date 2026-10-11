# MCP Legacy Config Trap

## Symptom

A server is configured in `~/.hermes/config.yaml` under the `mcp.servers` block, e.g.:

```yaml
mcp:
  servers:
    codebase-memory:
      command: /home/natan/.local/bin/codebase-memory-mcp
```

But `hermes mcp list` does not show it, `hermes mcp test <name>` says "not found in config", and the MCP tools are unavailable.

## Cause

Hermes recognizes active MCP servers from the **top-level `mcp_servers:`** block, not from `mcp.servers`. The nested shape is a legacy or alternative config that Hermes does not load for active tool discovery.

## Fix

Register the server explicitly:

```bash
hermes mcp add <name> --command <path-to-binary>
```

Then verify:

```bash
hermes mcp list
hermes mcp test <name>
```

Start a new Hermes session after registering, because MCP tools are discovered at session start and prompt caching prevents mid-session toolset changes.

## Prevention

After any manual edit of `~/.hermes/config.yaml` for MCP servers, run `hermes mcp list` and `hermes mcp test <name>` before assuming the server is available.
