---
name: selective-vpn-routing
description: Route only specific services or applications through a VPN/proxy while keeping the rest of the system on a direct connection. Covers local SOCKS5/HTTP proxy setup with Xray/v2ray, subscription parsing, systemd user services, and Hermes Telegram gateway integration.
version: 1.0.0
author: Master Ugwai
metadata:
  hermes:
    tags: [vpn, proxy, xray, v2ray, sing-box, socks5, routing, telegram, hermes-gateway]
    related_skills: [hermes-agent]
---

# Selective VPN Routing

Use this skill when you need one service (e.g., Hermes Telegram gateway) to reach blocked destinations through a VPN/proxy, while the rest of the machine — nginx, Next.js, databases, cron, SSH — continues to use the direct connection.

## Core principle

Run a local proxy (usually SOCKS5) on `127.0.0.1:<port>`. Point only the target application at that proxy. Do not change system routing, default gateway, or global `*_PROXY` env vars. This keeps existing services untouched and makes debugging easier.

## When to use

- Telegram/Viber/WhatsApp gateway needs to bypass a regional block.
- A specific API or SaaS is unreachable from the host network.
- You want VPN for one bot/app but not for the public web server on the same machine.

## Common tools

| Tool | Use case |
|------|----------|
| Xray-core | VLESS/Vmess/Trojan/Shadowsocks → SOCKS5/HTTP |
| v2ray-core | Same ecosystem, older config format |
| sing-box | Modern universal proxy, good for complex routing |
| 3proxy/tinyproxy | Quick HTTP/SOCKS5 proxy |

Xray is usually the fastest path for VLESS/Shadowsocks subscription links.

Nekobox on Windows is a sing-box/Xray GUI. For browser-only selective routing, prefer **System Proxy + a browser extension** (e.g., Proxy SwitchyOmega 3) rather than TUN Mode, to avoid side effects on local services and system routing.

## Workflow

1. **Preserve existing services first.** Document what ports are in use (`ss -tlnp`) and what nginx/sites are active. Never touch them without explicit user direction.
2. **Install the proxy binary in user space.** Avoid `sudo`/`/usr/local/bin` if root is unavailable. Use `~/.local/bin` and a systemd **user** service.
3. **Pick a free local port.** Common defaults: 10808 (Xray), 1080, 8080. Verify with `ss -tlnp` first.
4. **Parse the subscription URL.** Usually base64/plaintext `vless://`, `vmess://`, `ss://` links. Extract one node and convert to JSON config.
5. **Test the proxy before relying on it.** `curl -x socks5h://127.0.0.1:10808 https://target-host`
6. **Wire the target application.** For Hermes Telegram gateway: set `TELEGRAM_PROXY=socks5://127.0.0.1:10808` in `~/.hermes/.env` and `hermes gateway restart`.
7. **Create a systemd user service** for the proxy so it survives reboots.
8. **Verify end-to-end.** Check application logs, not just proxy connectivity.

## Config pitfalls

### Reality `shortId`
Xray expects `shortId` as a single hex string, e.g. `"shortId": "db04ce8bdb8900f1"`. Do not wrap it in an array (`"shortIds": [...]`) unless the specific Xray version requires the newer format. If you see `invalid "shortId"`, check length and hex encoding.

### WebSocket headers
Old Xray configs put host inside `wsSettings.headers.Host`. Newer versions warn that `host` in `headers` is deprecated; use `wsSettings.host` directly when supported.

### `spiderX`
Reality `spiderX` may be empty (`""`) or a path. `/` is not always accepted. If Reality fails with TLS errors, try `"spiderX": ""` or switch protocols.

### Node reliability
Subscription lists are not guarantees. If one node fails with `SSL_ERROR_SYSCALL`, `Connection reset`, or timeouts, try the next node. Keep a fallback list when possible.

### Application proxy support
Hermes gateway supports `TELEGRAM_PROXY` for Telegram adapter. Other tools may need `HTTP_PROXY`/`ALL_PROXY` or native proxy settings. SOCKS5h (DNS over proxy) is safest for blocked domains.

## Hermes Telegram integration

Add to `~/.hermes/.env`:

```bash
TELEGRAM_PROXY=socks5://127.0.0.1:10808
```

Restart gateway:

```bash
hermes gateway restart
```

Watch for log line:

```
[Telegram] Proxy detected; passing explicitly to HTTPXRequest: socks5://127.0.0.1:10808
[Telegram] Connected to Telegram (polling mode)
```

## Example: Xray as systemd user service

Binary path: `~/.local/bin/xray`
Config path: `~/.config/xray/config.json`

Service file `~/.config/systemd/user/xray.service`:

```ini
[Unit]
Description=Xray SOCKS5 proxy for <service>
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=%h/.local/bin/xray -c %h/.config/xray/config.json
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

Enable and start:

```bash
systemctl --user daemon-reload
systemctl --user enable xray
systemctl --user start xray
systemctl --user status xray
```

## Verification commands

```bash
# Proxy is listening
ss -tlnp | grep 10808

# Test through proxy
curl -x socks5h://127.0.0.1:10808 -m 10 https://api.telegram.org

# Public IP through proxy (compare with curl without -x)
curl -x socks5h://127.0.0.1:10808 https://api.ipify.org

# Gateway status
hermes gateway status
journalctl --user -u hermes-gateway -n 30 --no-pager
```

## References

- `references/telegram-xray-session.md` — real session notes: okmulti.com VLESS/SS subscription, node selection, working Xray config, Hermes Telegram integration.
- `references/windows-nekobox-browser-split-tunnel.md` — Windows Nekobox setup for browser-only selective routing to YouTube, Twitch, Discord, ChatGPT, Gemini, etc.
