# Windows Nekobox / sing-box selective browser routing via SOCKS5

Date: 2026-06-21  
Goal: Route only browser traffic to blocked services (YouTube, Twitch, Discord, ChatGPT, Gemini) through a VLESS subscription proxy, leaving the rest of the system on the direct connection.

## Environment

- Client: Nekobox.exe on Windows (sing-box/Xray-based GUI)
- Subscription: `https://okmulti.com/v2/c2hhcmVkXzU2ZTMyZmFjLTliOWMtNGJiOC1iMzFmLWVjZDA1NmNmMDA5Yw`
- Target services: YouTube, Twitch, Discord, ChatGPT/OpenAI, Gemini/Google AI, Anthropic/Claude

## Subscription contents

The okmulti subscription returned 8 VLESS nodes:
- 7 Reality nodes (TCP/gRPC)
- 1 VLESS + WebSocket + TLS node at `194.152.44.1:443` with path `/stream` and SNI `fl-node.ok-sbrf.ru`

The VLESS+WS+TLS node is the safest first choice; it has already been confirmed working in other sessions with the same subscription.

## Recommended approach: System Proxy + browser extension

For Windows + Nekobox + "only browser" routing, the most reliable split-tunnel is:

1. **Nekobox provides a local SOCKS5 proxy** (`127.0.0.1:10808` by default).
2. **A browser extension decides per domain** whether to use the proxy.

This avoids TUN-adapter side effects (local services, DNS leaks, mobile-in-network edge cases) and does not change system-wide routing.

### Step 1: Import subscription

In Nekobox:
- Group → Subscription → Add
- URL: `https://okmulti.com/v2/c2hhcmVkXzU2ZTMyZmFjLTliOWMtNGJiOC1iMzFmLWVjZDA1NmNmMDA5Yw`
- Update
- Select the node `194.152.44.1:443` (VLESS/WS/TLS) and connect.

### Step 2: Enable local proxy without TUN

- Nekobox → toggle **System Proxy ON** (but keep **TUN Mode OFF**).
- Verify ports in Nekobox Settings → Inbound. Defaults:
  - SOCKS5: `127.0.0.1:10808`
  - HTTP: `127.0.0.1:2080`

### Step 3: Browser extension routing list

Install **Proxy SwitchyOmega 3** (or **SmartProxy**) in Chrome/Edge/Firefox.

Create a profile:
- Protocol: SOCKS5
- Server: `127.0.0.1`
- Port: `10808`
- DNS over SOCKS5 (SOCKS5h): enabled if available

Auto-switch rule list (wildcard domains sent through the proxy profile):

```
*.youtube.com
*.googlevideo.com
*.ytimg.com
*.youtu.be
*.twitch.tv
*.ttvnw.net
*.discord.com
*.discord.gg
*.discordapp.com
*.discord.media
*.cdn.discordapp.com
*.openai.com
*.chatgpt.com
*.anthropic.com
*.claude.ai
*.gemini.google.com
*.ai.google.dev
*.bard.google.com
*.twitter.com
*.x.com
```

Default profile: Direct.

### Step 4: Verification

Open three tabs:
1. `https://ipinfo.io` — should show your real IP.
2. `https://www.youtube.com` — should show the proxy IP.
3. `https://chatgpt.com` — should load without block page.

## Alternative: Nekobox built-in routing rules

If you prefer no browser extension, use Nekobox Route Settings:

- Default outbound: `direct` / `bypass`
- Add proxy rules BEFORE the final direct rule:
  - `geosite:youtube`
  - `geosite:google`
  - `geosite:discord`
  - `geosite:twitter`
  - `domain:chatgpt.com`
  - `domain:openai.com`
  - `domain:anthropic.com`
  - `domain:claude.ai`
  - `domain:gemini.google.com`
  - `domain:ai.google.dev`
  - `domain:twitch.tv`

Pitfall: Nekobox routing depends on bundled geosite data. If a domain is miscategorized or missing, it leaks out the direct connection. Manual domain rules are more reliable than geosite-only for a short target list.

## Alternative: TUN Mode (only if you need system-wide split-tunnel)

If you want *all* applications on the Windows machine (not just the browser) to use the same split-tunnel:
- Enable TUN Mode in Nekobox.
- Set routing default to `direct` and add domain/geosite rules pointing to the proxy outbound.
- Enable FakeDNS or set DNS to go through the proxy for blocked domains; otherwise DNS leaks will cause blocks even when TCP traffic is proxied.

Caveats:
- Localhost services (e.g., a dev WebUI on `127.0.0.1:18789`) usually stay reachable, but test after enabling.
- TUN adapters can conflict with other VPN clients, Hyper-V/WSL virtual switches, or company network policies.

## Diagnostic commands on Windows

PowerShell:
```powershell
# Check proxy port listening
netstat -ano | findstr "10808"

# Check current external IP (direct)
(Invoke-WebRequest -Uri "https://api.ipify.org" -TimeoutSec 10).Content

# Check external IP through SOCKS5 (requires curl.exe with SOCKS5 support)
curl.exe --socks5-hostname 127.0.0.1:10808 https://api.ipify.org --max-time 10
```

## When to use what

| Goal | Approach |
|---|---|
| Browser-only split-tunnel | Nekobox System Proxy + SwitchyOmega 3 |
| Multiple browsers / no extensions | Nekobox routing rules with manual domain list |
| All apps on Windows machine | Nekobox TUN Mode with FakeDNS |
| One specific CLI tool / bot | Point it directly at `socks5://127.0.0.1:10808` |

## Related

- `references/telegram-xray-session.md` — Linux Xray setup using the same okmulti subscription
- `references/gateway-telegram-selective-proxy.md` — Hermes Telegram gateway through selective SOCKS5 proxy
