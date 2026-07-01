# Selective SOCKS5 Proxy for Hermes Telegram Gateway

**Use when:** `api.telegram.org` and all Telegram fallback IPs time out from the host,
but the rest of the machine (nginx, Next.js, other outbound services) must stay on direct internet.

**Goal:** Run a local SOCKS5 proxy backed by a VLESS/Shadowsocks/Vmess subscription,
point **only** the Hermes Telegram adapter at it via `TELEGRAM_PROXY`,
and leave all other traffic untouched.

---

## Quick Diagnosis

```bash
# 1. Gateway status and logs
hermes gateway status
journalctl --user -u hermes-gateway -n 50 --no-pager

# 2. Direct Telegram reachability
for host in https://api.telegram.org \
            https://149.154.167.220/ \
            https://149.154.167.221/ \
            https://149.154.167.222/ ; do
    echo -n "$host: "
    curl -m 10 -sS -o /dev/null -w "%{http_code} %{time_total}s\n" "$host" || true
done
```

If every Telegram endpoint times out while other sites work, the network path to Telegram is blocked.

---

## Architecture

```
[Telegram Bot API]  <-- blocked directly --
                                          |
[ Hermes gateway ]  --socks5--> [ Xray inbound :10808 ] --VLESS/SS--> [ okmulti node ] --> Telegram
                                          |
[ nginx :80/:443 ]                          [ Next.js :3000 ]
          ^ unchanged, still direct internet
```

Default Xray SOCKS5 port used here: `10808`. It does not conflict with common Next.js/nginx ports.

---

## 1. Install Xray-core

### Preferred: official install script

```bash
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install
```

### Fallback if GitHub is unreachable from the host

Try the system package:

```bash
sudo apt-get update && sudo apt-get install -y xray
```

Or download from an alternative mirror and extract `xray` to `/usr/local/bin/xray`.

Verify:

```bash
xray version
```

---

## 2. Choose a node from the subscription

Subscription is a base64-encoded or plain-text list of URIs. Fetch it:

```bash
curl -L -s --max-time 30 'https://okmulti.com/v2/c2hhcmVkXzU2ZTMyZmFjLTliOWMtNGJiOC1iMzFmLWVjZDA1NmNmMDA5Yw' | head -c 5000
```

The output contains VLESS and Shadowsocks URIs. Pick a **VLESS+Reality TCP** node first
(reality tends to survive DPI blocks well). Example first node:

```text
vless://985af6eb-861a-4661-b9b3-2bdd20a0572d@144.31.131.38:8443
?type=tcp&security=reality
&pbk=ivSYLLXu-f4slJOLrlZxhnq0nAAaCW-ct6ptzVUJxUs
&fp=firefox
&sni=prod.pl-node-02.security-sbrf.ru
&sid=db04cebdb8900f1
&spx=%2F
```

Decode manually or with a URI parser to get:

| Field | Value |
|-------|-------|
| `address` | `144.31.131.38` |
| `port` | `8443` |
| `id` / UUID | `985af6eb-861a-4661-b9b3-2bdd20a0572d` |
| `security` | `reality` |
| `flow` | `xtls-rprx-vision` |
| `network` | `tcp` |
| `publicKey` | `ivSYLLXu-f4slJOLrlZxhnq0nAAaCW-ct6ptzVUJxUs` |
| `serverName` (SNI) | `prod.pl-node-02.security-sbrf.ru` |
| `shortId` | `db04cebdb8900f1` |
| `spiderX` | `/` |
| `fingerprint` | `firefox` |

---

## 3. Minimal Xray config for SOCKS5-only inbound

Path: `/usr/local/etc/xray/config.json`

```json
{
  "log": {
    "loglevel": "warning",
    "access": "/var/log/xray/access.log",
    "error": "/var/log/xray/error.log"
  },
  "inbounds": [
    {
      "tag": "socks-in",
      "port": 10808,
      "listen": "127.0.0.1",
      "protocol": "socks",
      "settings": {
        "udp": true,
        "ip": "127.0.0.1"
      }
    }
  ],
  "outbounds": [
    {
      "tag": "vless-out",
      "protocol": "vless",
      "settings": {
        "vnext": [
          {
            "address": "144.31.131.38",
            "port": 8443,
            "users": [
              {
                "id": "985af6eb-861a-4661-b9b3-2bdd20a0572d",
                "flow": "xtls-rprx-vision",
                "encryption": "none"
              }
            ]
          }
        ]
      },
      "streamSettings": {
        "network": "tcp",
        "security": "reality",
        "realitySettings": {
          "show": false,
          "fingerprint": "firefox",
          "serverName": "prod.pl-node-02.security-sbrf.ru",
          "publicKey": "ivSYLLXu-f4slJOLrlZxhnq0nAAaCW-ct6ptzVUJxUs",
          "shortId": "db04cebdb8900f1",
          "spiderX": "/"
        }
      }
    }
  ]
}
```

Create log directory and start:

```bash
sudo mkdir -p /var/log/xray
sudo systemctl restart xray
sudo systemctl enable xray
```

---

## 4. Verify the SOCKS5 tunnel

```bash
curl -x socks5h://127.0.0.1:10808 -m 10 -sS \
     -o /dev/null -w "%{http_code} %{time_total}s\n" \
     https://api.telegram.org/botFAKE/getMe
```

Expected: HTTP `401` or `404` (invalid bot token) — that means TLS + Telegram were reached.
If it returns `000` or times out, check Xray error log:

```bash
sudo tail -30 /var/log/xray/error.log
```

Try the next VLESS node from the subscription if the first one fails.

---

## 5. Point Hermes Telegram adapter at the proxy

Edit `~/.hermes/.env` (gateway reads **only** this file at startup):

```bash
TELEGRAM_PROXY=socks5://127.0.0.1:10808
```

Restart gateway:

```bash
hermes gateway restart
```

Verify:

```bash
hermes gateway status
journalctl --user -u hermes-gateway -n 30 --no-pager | grep -i telegram
```

---

## 6. Coexistence with co-hosted Next.js / nginx services

The user's pentajunior stack already exists on this host:

| Service | Port | Must stay direct |
|---------|------|------------------|
| nginx HTTPS (pentajunior.ru) | `443` | yes |
| nginx HTTP /cloud/ | `80` | yes |
| pentajunior (production, legacy) | `3000` | yes |
| pentajunior-v2 (dev) | `3001` or `3002` | yes |

Do **not** change default routes or default gateways.
The proxy lives only on `127.0.0.1:10808` and is used only by `TELEGRAM_PROXY`.

If you need to confirm the occupant of port 3000 before touching anything:

```bash
PID=$(ss -tlnp | grep ':3000' | sed 's/.*pid=\([0-9]*\).*/\1/')
echo "PID: $PID"
pwdx "$PID"
readlink -f /proc/$PID/exe
cat /proc/$PID/cmdline | tr '\0' ' '
```

---

## 7. Making the setup survive reboot

```bash
sudo systemctl enable xray
```

Optionally add a user-level systemd override for the gateway to make `TELEGRAM_PROXY`
explicit in the unit environment:

```bash
mkdir -p ~/.config/systemd/user/hermes-gateway.service.d
cat > ~/.config/systemd/user/hermes-gateway.service.d/telegram-proxy.conf <<'EOF'
[Service]
Environment="TELEGRAM_PROXY=socks5://127.0.0.1:10808"
EOF
systemctl --user daemon-reload
hermes gateway restart
```

---

## 8. Common failure patterns

| Symptom | Cause | Fix |
|---------|-------|-----|
| `curl` via proxy returns `000` | Xray outbound blocked; wrong Reality `shortId`/`publicKey`; SNI filtered | Try next node from subscription; verify `sni`, `sid`, `pbk` |
| Xray starts but gateway still can't connect | `TELEGRAM_PROXY` not in `~/.hermes/.env`; old gateway process cached env | Restart gateway after editing `.env`; check `systemctl --user show hermes-gateway --show-environment \| grep TELEGRAM` |
| Xray binds on all interfaces (`0.0.0.0:10808`) | Config missing `"listen": "127.0.0.1"` | Pin inbound to loopback to avoid exposing open proxy |
| nginx or pentajunior-v2 unreachable after changes | Accidentally changed default route / iptables / global proxy | Roll back routing changes; this guide intentionally avoids global proxying |
| Port 10808 already in use | Another proxy running | Pick another port, e.g. `10809`, and update both Xray inbound and `TELEGRAM_PROXY` |

---

## 9. One-shot curl test from the agent (when token is available)

If the bot token is readable from systemd environment or `.env`:

```bash
TOKEN=$(systemctl --user show hermes-gateway --show-environment | grep TELEGRAM_BOT_TOKEN | cut -d= -f2-)
CHAT_ID=$(systemctl --user show hermes-gateway --show-environment | grep TELEGRAM_HOME_CHANNEL | cut -d= -f2-)
curl -x socks5h://127.0.0.1:10808 -s -m 30 -X POST \
  "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\":\"${CHAT_ID}\",\"text\":\"SOCKS5 Telegram test OK\"}"
```

If the token is masked in output, ask the user to run this command directly.
