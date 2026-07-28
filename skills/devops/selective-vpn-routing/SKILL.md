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
- You want router-level transparent proxy: all LAN devices go through the tunnel for blocked resources, Russian/CIS/LAN traffic stays direct, and no per-device proxy configuration is required.

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

## Router-specific pitfalls (GL.iNet / OpenWrt 21.02)

### For router-level transparent proxy, prefer v2rayA on stock firmware
`v2raya` is the safest GUI path on stock GL.iNet SDK 4.x: it installs `xray-core`, exposes a web UI on port 2017, and manages its own transparent proxy + DNS rules. Do not attempt manual `iptables` TPROXY unless the user explicitly accepts the risk of breaking LAN internet and the web UI.

### Manual TPROXY breaks internet and the GL.iNet web UI backend
Manual `iptables -t mangle` TPROXY rules easily break internet for all LAN clients and can break the GL.iNet web UI backend (e.g. VPN tabs disappear). Prefer Passwall2/Nikki on community firmware, or use v2rayA on stock firmware, or keep Xray as SOCKS5/HTTP only.

### DNS must also go through the tunnel
TCP-only proxying is not enough: if DNS still resolves through the provider, blocked domains return fake/unreachable IPs. The solution must route DNS (UDP 53 or DNS-over-HTTPS/TLS) through the tunnel, or let v2rayA handle DNS transparently.

### Stock firmware does not support VLESS/XRay natively
GL.iNet SDK 4.x / OpenWrt 21.02 web UI only shows OpenVPN, WireGuard, Tor, and sometimes Shadowsocks. VLESS/VMess/Reality require community packages (`xray-core`, `luci-app-passwall2`, `luci-app-nikki`) that are not in stock GL.iNet repos. Do not promise the user a one-click GUI path on stock firmware.

### Modern OpenWrt feeds (24.10+) include current xray-core and v2rayA
On routers running newer OpenWrt/GL.iNet firmware based on 24.10, `opkg update && opkg install xray-core v2raya` installs current Xray >= 1.8 and v2rayA with a web UI on port 2017. This is the safest router-level GUI path on such firmware: v2rayA manages its own transparent proxy, DNS, and routing rules without hand-written iptables. However, v2rayA's built-in protocol list may not include WireGuard; use Xray/VLESS/Reality or VMess instead.

### Repo `xray-core` is too old for Reality
Vendor OpenWrt 21.02 repositories may ship `xray-core` 1.5.x. Reality transport requires Xray >= 1.8.x. You must replace the binary manually with a current release.

### Transfer binaries via LAN HTTP server, not SCP/GitHub
- The router may not have `sftp-server`, so `scp` fails.
- `wget`/`curl` from the router to GitHub often times out or uses an old `wget` without `--show-progress`.
- `python3` is usually missing on the router.
- **Working path:** download the ARM64 Xray zip on a LAN machine, unzip, then serve the files over the LAN with `python3 -m http.server 8000` and `wget` them from the router.

### Update `geoip.dat`/`geosite.dat` together with xray-core
The `xray-geodata` package bundled with old `xray-core` lacks list names used by current configs (e.g. `geosite:category-ru`). Copy `geoip.dat` and `geosite.dat` from the same Xray release zip that you install.

### Remove sample configs
`/etc/init.d/xray` loads all `*.json` in `/etc/xray`. Rename or remove `vpoint_socks_vmess.json` and `vpoint_vmess_freedom.json` from `xray-example` so they don't conflict.

### Use outbound server IP to avoid bootstrap DNS loops
When manually routing DNS through xray, configure the VLESS outbound with the VPN server IP instead of its domain. Otherwise xray must resolve the outbound domain before it can resolve anything, creating a bootstrap loop.

## Config pitfalls

### Router-side Reality through v2rayA (modern OpenWrt/GL.iNet)
On routers where `v2raya` and `xray-core` are available from OpenWrt 24.10+ repos:

1. `opkg install xray-core v2raya`
2. `/etc/init.d/v2raya enable; /etc/init.d/v2raya start`
3. Open `http://ROUTER_IP:2017`
4. Import the VLESS share URL from the server setup.
5. In **Settings → Transparent Proxy**, enable transparent proxy and choose a routing rule set that sends `geosite:category-ru-blocked` and common blocked domains to `proxy`, everything else `direct`.
6. Apply and verify from a LAN client with `curl https://2ip.ru`.

Caveats:
- v2rayA may not offer WireGuard in its UI; use VLESS/VMess/Xray protocols.
- If the router firmware is older (21.02-based), `opkg` may ship `xray-core` 1.5.x without Reality support; upgrade the binary manually or use a newer firmware.

### `luci-app-v2raya` is only the UI
`luci-app-v2raya` does not pull in `v2raya` or `xray-core`. Install both core packages explicitly.

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

# GitHub through proxy (when direct GitHub is blocked)
curl -x socks5h://127.0.0.1:10808 -sL https://api.github.com/user

# Gateway status
hermes gateway status
journalctl --user -u hermes-gateway -n 30 --no-pager
```

## Application-specific proxy tips

### git through a SOCKS5 proxy
When GitHub is only reachable via the local proxy, configure git to use it:

```bash
git config --global http.proxy socks5://127.0.0.1:10808
git config --global https.proxy socks5://127.0.0.1:10808
```

To scope it to one repo instead of global, run the same commands inside that repo without `--global`.

### Large git pushes through SOCKS5
HTTPS through a SOCKS proxy often hits GitHub's request/payload limits and fails with:

```
error: RPC failed; HTTP 408 curl 22 The requested URL returned error: 408
send-pack: unexpected disconnect while reading sideband packet
```

This is especially common when pushing big commits (converted book libraries, bulk media, large Obsidian vault syncs). **Switch the remote from HTTPS to SSH:**

```bash
cd /path/to/repo
OWNER_REPO=$(git remote get-url origin | sed -E 's|.*github\.com[:/]||; s|\.git$||')
git remote set-url origin "git@github.com:${OWNER_REPO}.git"
git push origin main
```

SSH tolerates large packs and long-running pushes far better than HTTPS tunneled through a SOCKS proxy. Ensure the host has a valid SSH key with GitHub (`ssh -T git@github.com`).

## WireGuard on GL.iNet

For users who rent their own VPS, WireGuard is often simpler and faster than Xray/VLESS. GL.iNet stock firmware has a built-in WireGuard Client, but split-tunnel policy routing has specific pitfalls. If the stock UI becomes unstable (constant `wgclient1` flap), replace it with **sing-box + WireGuard outbound** instead of fighting GL.iNet scripts: see `references/glinet-sing-box-wireguard.md` and `templates/sing-box-router-wg-domain-routing.json`.

- `AllowedIPs = 0.0.0.0/0` does **not** mean global proxy in Policy mode; it only authorizes the peer to receive traffic for any destination.
- The router uses DNS to learn the IP of each listed domain and injects host routes into routing table `1001`. If DNS is hidden (DoH/DoT on the client) or times out, policy routing breaks.
- `table 1001` usually contains `blackhole default` intentionally; only resolved IPs of listed domains get routed through `wgclient1`.
- The GL.iNet `vpn-failover` watchdog can cause `wgclient1` to flap up/down every 20-30 seconds if it misjudges the tunnel state. Disable failover monitoring or use Global Proxy for a stable baseline.
- Xray/v2rayA and WireGuard fight over firewall rules, routing table 1001, and DNS. Use one tunnel solution at a time.

### wg-easy quick fix from the session

If you just set up `wg-easy` on a fresh VPS and the router can handshake but cannot reach the internet:

1. On the VPS host, install `iptables-persistent` and save the forward rules:
   ```bash
   apt-get install -y iptables-persistent
   iptables -A FORWARD -i br-<docker-net-id> -o <public-if> -j ACCEPT
   iptables -A FORWARD -i <public-if> -o br-<docker-net-id> -m state --state RELATED,ESTABLISHED -j ACCEPT
   netfilter-persistent save
   ```
2. Do not blame MTU or the router until this forwarding works.
3. See `references/wg-easy-docker-host-forwarding.md` for the full script and `references/glinet-wireguard-policy-routing.md` for router-side policy routing.

## References

- `references/glinet-sing-box-wireguard.md` — GL-MT6000 stock firmware: setting up **sing-box** with a WireGuard outbound as a stable replacement for the flaky GL.iNet WG Client policy engine, including domain-based routing, nftables TPROXY, dnsmasq integration, and autostart.
- `templates/sing-box-router-wg-domain-routing.json` — known-good sing-box config template for a GL.iNet router with a WireGuard VPS, TPROXY inbound, and `geosite:category-ru-blocked` routing.
- `scripts/glinet-sing-box-install.sh` — installs sing-box from OpenWrt repos, creates `/etc/sing-box/config.json` from the template, enables the service, and configures dnsmasq/nftables/TPROXY on a GL-MT6000-class device.
- `references/wg-easy-docker-host-forwarding.md` — same problem as above, solved with `iptables-persistent` instead of a systemd service (simpler on Debian/Ubuntu hosts).
- `references/glinet-wireguard-policy-routing.md` — GL-MT6000 WireGuard Client: Policy vs Global Proxy, UCI file locations, DNS visibility, tunnel flapping, nftables set verification, Ubuntu 24.04 HWE kernel bug, and coexistence with v2rayA/Xray.
- `references/xray-vps-vless-reality.md` — installing a self-hosted Xray VLESS+Reality inbound on Ubuntu 24.04 alongside Docker/wg-easy, using port 8443 when nginx owns 443.
- `references/vless-subscription-parser.md` — parse JSON-style Xray/VLESS subscriptions into individual `vless://` URLs.
- `references/glinet-v2raya-transparent-session.md` — GL.iNet + v2rayA transparent proxy session: safe router-level path, DNS through tunnel, binary transfer recipe, rollback.
- `references/glinet-v2raya-autostart.md` — make v2rayA/xray start automatically after a router reboot on stock GL.iNet / OpenWrt, including the autoconnect caveat.
- `references/telegram-xray-session.md` — real session notes: okmulti.com VLESS/SS subscription, node selection, working Xray config, Hermes Telegram integration.
- `references/windows-nekobox-browser-split-tunnel.md` — Windows Nekobox setup for browser-only selective routing to YouTube, Twitch, Discord, ChatGPT, Gemini, etc.
- `templates/xray-router-socks5-only.json` — minimal router VLESS+Reality config (SOCKS5/HTTP only, no TPROXY).
- `templates/xray-router-socks5-ru-direct.json` — same with Russian/CIS domains routed direct.
- `scripts/wg-easy-forward.sh` — host-side script that adds/persists FORWARD rules for a Dockerized `wg-easy` server.
- `scripts/xray-router-rollback.sh` — one-click rollback for broken TPROXY/Xray state.
