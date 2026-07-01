# Session notes: Hermes Telegram via okmulti.com Xray SOCKS5

Date: 2026-06-20  
Goal: Route only Hermes Telegram adapter through VPN; keep pentajunior (Next.js :3000) and nginx (:80/:443) on direct connection.

## Environment

- Host: Ubuntu 22.04
- Gateway: `hermes-gateway.service` user systemd service
- Existing services: nginx `pentajunior.ru` → `localhost:3000`
- Subscription: `https://okmulti.com/v2/c2hhcmVkXzU2ZTMyZmFjLTliOWMtNGJiOC1iMzFmLWVjZDA1NmNmMDA5Yw`

## What worked

Xray VLESS + WebSocket + TLS outbound to `194.152.44.1:443` with SOCKS5 inbound on `127.0.0.1:10808`.

Working `~/.config/xray/config.json`:

```json
{
  "log": { "loglevel": "warning" },
  "inbounds": [{
    "tag": "socks-in",
    "port": 10808,
    "listen": "127.0.0.1",
    "protocol": "socks",
    "settings": { "udp": true, "ip": "127.0.0.1" }
  }],
  "outbounds": [{
    "tag": "vless-out",
    "protocol": "vless",
    "settings": {
      "vnext": [{
        "address": "194.152.44.1",
        "port": 443,
        "users": [{
          "id": "f670562c-6ea4-4f51-ad3f-f07abf5c62ca",
          "encryption": "none"
        }]
      }]
    },
    "streamSettings": {
      "network": "ws",
      "security": "tls",
      "tlsSettings": {
        "serverName": "fl-node.ok-sbrf.ru",
        "allowInsecure": false
      },
      "wsSettings": {
        "path": "/stream",
        "headers": { "Host": "fl-node.ok-sbrf.ru" }
      }
    }
  }]
}
```

Hermes `.env` addition:

```bash
TELEGRAM_PROXY=socks5://127.0.0.1:10808
```

## What did NOT work

1. **Reality shortId format**  
   Xray 26.3.27 rejected `"shortIds": ["..."]` array; wanted `"shortId": "..."` string.  
   Even with correct format, both Reality nodes from the subscription dropped TLS handshake with `SSL_ERROR_SYSCALL`. Switched to VLESS+WS+TLS node which succeeded immediately.

2. **GitHub/Xray download via curl install script**  
   Long-running curl commands were interrupted by the tool layer. Direct `curl -fsSL -m 90 -o /tmp/xray.zip https://github.com/XTLS/Xray-core/releases/download/v26.3.27/Xray-linux-64.zip` worked reliably.

3. **Installing to /usr/local/bin**  
   No sudo password available. Used `~/.local/bin` + systemd user service instead.

## Verification

```bash
# Proxy reachable and Telegram responds
curl -x socks5h://127.0.0.1:10808 https://api.telegram.org/bot123/test
# → HTTP 404 (expected for fake token)

# External IP changes through proxy
curl -x socks5h://127.0.0.1:10808 https://api.ipify.org
# → 95.216.114.245

# Gateway log confirms
tail ~/.hermes/logs/gateway.log
# [Telegram] Proxy detected; passing explicitly to HTTPXRequest: socks5://127.0.0.1:10808
# [Telegram] Connected to Telegram (polling mode)
# ✓ telegram connected
```

## Commands to manage

```bash
# Proxy
systemctl --user status xray
systemctl --user restart xray

# Gateway
hermes gateway status
hermes gateway restart
```
