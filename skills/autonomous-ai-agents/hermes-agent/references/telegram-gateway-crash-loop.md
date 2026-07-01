# Telegram Gateway Crash Loop + MCP Zombie Pattern

## Pattern

When `api.telegram.org` is unreachable (e.g., blocked by ISP in Russia), the gateway `telegram` platform adapter crashes with `telegram.error.TimedOut` on startup. Systemd restarts the gateway (`Restart=always`), but the child `obsidian-mcp` stdio process survives the SIGKILL because systemd `KillMode=mixed` does not reliably clean up the Node.js MCP server. The orphaned MCP server keeps stale stdio pipes, and the existing CLI session still holds a dead MCP client handle, yielding `ClosedResourceError` on every MCP call.

## Reproduction

1. Gateway starts with Telegram configured
2. `api.telegram.org` is unreachable
3. Gateway throws `TimedOut` during platform initialization
4. systemd SIGKILLs the gateway
5. Node.js obsidian-mcp child survives (PID remains)
6. systemd restarts gateway → spawns a *second* obsidian-mcp
7. CLI session's MCP handle is stale → `ClosedResourceError`
8. All MCP calls fail in a loop (looks like an "MCP broken" symptom, but root cause is Telegram network block)

## Network Block Diagnosis

Gateway auto-discovers Telegram API IPs via DNS-over-HTTPS (Google + Cloudflare). In blocked networks, DoH may return an IP that is **also blocked** (e.g., `149.154.166.110` on Rostelecom), while a hardcoded seed IP (`149.154.167.220`) may remain reachable.

Quick check from the server:
```bash
# Test direct HTTPS to seed fallback IP (skip cert verification because SNI mismatch)
curl -k --connect-timeout 5 -H "Host: api.telegram.org" \
  "https://149.154.167.220/bot<YOUR_TOKEN>/getMe"
# 401 = API alive, token accepted; 000/timeout = blocked

# Compare with DoH-returned IP
curl -k --connect-timeout 5 -H "Host: api.telegram.org" \
  "https://149.154.166.110/bot<YOUR_TOKEN>/getMe"
```

If the seed IP works but DoH IP does not, override fallback list via **systemd user environment** (survives service restarts without editing `.env`):
```bash
systemctl --user set-environment TELEGRAM_FALLBACK_IPS=149.154.167.220
systemctl --user restart hermes-gateway
```

Or add to `~/.hermes/.env`:
```bash
TELEGRAM_FALLBACK_IPS=149.154.167.220
```

Gateway reads this via `parse_fallback_ip_env()` in `gateway/platforms/telegram_network.py`.

**Relevant env vars**
| Env var | Effect |
|---------|--------|
| `TELEGRAM_FALLBACK_IPS` | Comma-separated list of fallback IPv4s used instead of auto-discovered IPs |
| `HERMES_TELEGRAM_DISABLE_FALLBACK_IPS` | Set to `1`/`true` to disable fallback transport entirely |
| `TELEGRAM_PROXY` | HTTP or SOCKS5 proxy URL for Bot API requests (e.g. `socks5://127.0.0.1:1080`) |
| `HERMES_TELEGRAM_MEDIA_BATCH_DELAY_SECONDS` | Float, default 0.8 |
| `HERMES_TELEGRAM_TEXT_BATCH_DELAY_SECONDS` | Float, default 0.6 |
| `HERMES_TELEGRAM_TEXT_BATCH_SPLIT_DELAY_SECONDS` | Float, default 2.0 |

**Important: MTProto proxies are incompatible.**
User-provided MTProto proxy links (`tg://proxy?server=...&port=...&secret=...`) use the MTProto protocol, which is **not** an HTTP or SOCKS5 proxy. Gateway (via `httpx`/`HTTPXRequest`) only supports HTTP/SOCKS5 proxies. MTProto proxies require a separate local bridge (e.g., `mtproto-proxy` daemon) or a VPN.

**Shadowsocks proxy setup for Telegram (Russia workaround)**
If you have a Shadowsocks subscription (e.g., `ss://...` links), you can run a local SOCKS5 proxy and point Telegram at it:

```bash
# Install shadowsocks-libev (C client — Python shadowsocks is broken on 3.11+)
sudo apt-get install shadowsocks-libev

# Create config JSON
mkdir -p ~/.shadowsocks
cat > ~/.shadowsocks/ru.json << 'EOF'
{
    "server": "YOUR_SS_SERVER_IP",
    "server_port": 443,
    "local_address": "127.0.0.1",
    "local_port": 1080,
    "password": "YOUR_SS_PASSWORD",
    "method": "aes-256-gcm",
    "timeout": 300
}
EOF

# Start local SOCKS5 proxy
ss-local -c ~/.shadowsocks/ru.json -f /tmp/ss-local.pid

# Verify SOCKS5 works
curl --socks5-hostname 127.0.0.1:1080 -sL https://api.telegram.org/bot<TOKEN>/getMe

# Point gateway at it
systemctl --user set-environment TELEGRAM_PROXY=socks5://127.0.0.1:1080
systemctl --user restart hermes-gateway
```

**Note:** `pip install shadowsocks` installs version 2.8.2 which is incompatible with Python 3.11+ (uses `collections.MutableMapping` which moved to `collections.abc` in 3.10). Always use `shadowsocks-libev` system package instead.

**Fallback IP vs Proxy behavior:**
- `TELEGRAM_FALLBACK_IPS` works at the transport layer — gateway rewrites TCP destination to the given IP while keeping TLS SNI as `api.telegram.org`. Only viable if the IP itself is not blocked.
- `TELEGRAM_PROXY` works at the HTTP/SOCKS layer — all Telegram traffic is tunneled through the proxy. Required when even fallback IPs are blocked.
- Both can be combined: `TELEGRAM_FALLBACK_IPS` for the primary path + `TELEGRAM_PROXY` as ultimate fallback.

## Recovery

```bash
# 1. Kill all surviving obsidian-mcp children
pkill -9 -f 'obsidian-mcp'
pgrep -f 'obsidian-mcp' || echo "clean"

# 2. Restart gateway (or wait for systemd auto-restart)
systemctl --user restart hermes-gateway

# 3. Start a brand-new CLI session so MCP gets a fresh handle
hermes  # or type /new inside CLI
```

**Troubleshooting persistent `ClosedResourceError` after gateway recovery**
If MCP still fails with `ClosedResourceError` after gateway is running:
1. Check that only ONE obsidian-mcp child exists: `ps aux | grep obsidian-mcp | grep -v grep`
2. If systemd shows `Unit process ... remains running after unit stopped`, it failed to kill the child. Manually `kill -9` the surviving PIDs.
3. **Start a fresh CLI session** — the MCP client handle lives in the CLI process (via `GatewayClient`/`StdioTransport`), not the gateway. A stale handle cannot be refreshed without `/new` or a new `hermes` invocation.

## Prevention

- In blocked networks, comment out `TELEGRAM_BOT_TOKEN` in `~/.hermes/.env` to skip the Telegram platform.
- Alternatively, configure a proxy:
  ```bash
  TELEGRAM_PROXY=socks5://127.0.0.1:1080
  # or
  TELEGRAM_PROXY=http://proxy.example.com:8080
  ```
- Or set a known-working fallback IP:
  ```bash
  TELEGRAM_FALLBACK_IPS=149.154.167.220
  ```
- For Russian/Roskomnadzor-blocked servers, combine fallback IP + local Shadowsocks SOCKS5 proxy for reliability.

## Affected versions

Hermes Agent v0.12.0+, python-telegram-bot with HTTPXRequest, systemd user service with `Restart=always`.

## Related

- `telegram-polling-bridge.md` — lightweight DIY Telegram fallback when native gateway is not possible
- `webui-profile-switch-mechanics.md` — profile + session isolation notes
