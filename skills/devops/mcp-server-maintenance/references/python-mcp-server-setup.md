# Python MCP Server Setup Workflow

Class-level workflow for adding a third-party Python MCP server to Hermes. Based on installing `stealth-browser-mcp`; applies to any Python MCP server distributed as a repo with `requirements.txt` / `pyproject.toml`.

## 1. Isolate the install

Clone into a durable path and create a dedicated venv. Use `uv` when the system Python lacks `venv`.

```bash
cd /mnt/data/natan-storage
git clone https://github.com/<owner>/<python-mcp-server>.git
cd <python-mcp-server>
uv venv --clear .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## 2. Verify before registering

Run the server standalone to confirm startup arguments and tool sections. For FastMCP-based servers:

```bash
source .venv/bin/activate
python src/server.py --list-sections
```

Only add the server to `~/.hermes/config.yaml` after this succeeds. Fix dependency or argument errors now, not after registration.

## 3. Register in Hermes

Use the top-level `mcp_servers:` block (servers under `mcp.servers` are legacy and inactive).

```yaml
mcp_servers:
  <server-name>:
    command: "/mnt/data/natan-storage/<python-mcp-server>/.venv/bin/python"
    args:
      - "/mnt/data/natan-storage/<python-mcp-server>/src/server.py"
      - "--any-required-server-args"
    env:
      PATH: "/mnt/data/natan-storage/<python-mcp-server>/.venv/bin:/usr/local/bin:/usr/bin:/bin"
      HOME: "/home/natan"
    timeout: 300
    connect_timeout: 60
```

### Reduce attack surface for high-privilege servers

Browser MCP servers expose JS execution, CDP commands, network interception, etc. For an untrusted or broad-tool-surface server, disable risky sections via args:

```yaml
args:
  - "/mnt/data/natan-storage/stealth-browser-mcp/src/server.py"
  - "--disable-cdp-functions"
  - "--disable-dynamic-hooks"
```

## 4. Activate the server

MCP tools are discovered only at session start. After editing `config.yaml`:

- In CLI/WebUI: start a new session (`/new`).
- Do **not** attempt to restart the gateway from inside an active gateway process — the command is blocked.

## 5. Test with native MCP tools

Once the new session starts, verify with Hermes commands:

```bash
hermes mcp list
hermes mcp test <server-name>
```

You can also exercise the tools by asking the agent to use them, e.g. `mcp_stealth_browser_spawn_browser`.

## 6. Transport preference: stdio for local, HTTP with care

- **Local servers:** prefer stdio transport. HTTP/StreamableHTTP can be fragile with servers that raise exceptions during tool calls (observed `ConnectionClosedOK` / `RuntimeError` in both client and server logs).
- **Remote/shared servers:** use HTTP with auth headers. Set `connect_timeout` generously.

## 7. Browser-server-specific notes

Linux headless deployments commonly need these arguments/env:

- `sandbox: false` (or `--no-sandbox` via `browser_args`) — Chrome sandbox usually fails outside a normal user session.
- `headless: true` works without a display.
- `headless: false` with `DISPLAY: ":100"` requires a running Xvfb instance; check with `ps aux | grep Xvfb`.

## 8. Persistent profile tip

If the browser server supports `user_data_dir`, reuse the same directory across sessions so cookies/history reduce bot-detection friction. Create the directory outside the repo so it survives repo updates.

```yaml
args:
  - "/path/to/server.py"
env:
  BROWSER_IDLE_TIMEOUT: "300"
```
