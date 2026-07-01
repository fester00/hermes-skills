# MCP — WebUI — Gateway Process Lifecycle (Server Session)

Reference for environments where Hermes WebUI, Gateway, and MCP servers run on a Linux server with nginx reverse-proxy.

## Architecture (this server)

```
Browser ───→ nginx (8443 ssl) ───→ WebUI (127.0.0.1:18789 manual)
                                       │
Gateway (systemd) ──── spawns ───→ obsidian-mcp (stdio)
```

- **WebUI**: started manually via `~/hermes-webui/start.sh`, NOT a systemd service (no `hermes-webui.service`). Dies on reboot / terminal close.
- **Gateway**: systemd user service (`hermes-gateway.service`), auto-restarts, owns MCP server processes.
- **nginx**: system service, reverse-proxies `8443` → `127.0.0.1:18789`.

## Common failure mode

1. WebUI dies (not a service → doesn't auto-restart).
2. User reconnects, but new WebUI gets a new process.
3. Gateway still running, MCP server still running, BUT chat session's MCP **client** holds stale stdio handle to old process.
4. Result: `ClosedResourceError` even though `pkill -f obsidian-mcp` shows healthy process.

## Fix procedure

```bash
# Step 1 — restart gateway (kills old MCP server, spawns new one)
systemctl --user restart hermes-gateway
sleep 3
ps aux | grep obsidian-mcp | grep -v grep  # verify new process

# Step 2 — in WebUI, run /new or refresh the page
# This gives fresh MCP client handle

# Step 3 — test
mcp_obsidian_list_available_vaults
```

## Permanent fix (todo)

Create systemd user service for WebUI so it auto-restarts on boot:
`~/.config/systemd/user/hermes-webui.service`

## Network (this server)

- Local IP: `192.168.0.98`
- Public IP: `130.255.9.9`
- Router: `192.168.0.1`, admin pass `nat1789418`
- nginx `openclaw` config listens on `8443 ssl` (self-signed cert).
- nginx `pentajunior` config on 80/443 is **production — never touch**.
