# VPS-side Xray VLESS + Reality — August 2026 session notes

Real-world setup on a fresh Ubuntu 20.04 VPS (my-ihor.ru, ~713 MB RAM), producing a single `vless://` URL for import into a router running v2ray.

## What worked

- Xray installed via official install script: `bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install`
- Inbound on `8443/tcp` because the host had no other TLS listener on 443.
- VLESS + Reality, client flow `xtls-rprx-vision`, fingerprint `firefox`.
- SNI used successfully: `www.youtube.com`.
- Port opened with `ufw allow 8443/tcp` plus `iptables -I INPUT ...` fallback.

## Critical fix: SNI must be reachable FROM the VPS

The first attempt used `prod.de-node-01.security-sbrf.ru` as the Reality SNI. The client repeatedly got `EOF` during VLESS handshake and pages did not load.

Root cause: the VPS itself could not reach `prod.de-node-01.security-sbrf.ru:443`. Reality needs the server to open a TLS connection to the SNI destination so it can mimic the handshake. If that outbound TLS connection fails, the inbound Reality connection breaks immediately.

### Test the SNI from the VPS before committing

```bash
for host in www.youtube.com www.google.com www.microsoft.com; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 -m 10 "https://$host" 2>/dev/null || true)
  echo "$host -> HTTPS $code"
done
```

Pick an SNI that returns `200`, `301`, `302`, etc. Do not use an SNI that times out or returns no TLS from the VPS.

### Good Reality SNI candidates tested from this host

| Host | Result |
|------|--------|
| `www.youtube.com` | ✅ working |
| `www.google.com` | ✅ reachable |
| `www.microsoft.com` | ✅ reachable |
| `prod.de-node-01.security-sbrf.ru` | ❌ not reachable from VPS |

## Critical fix: parsing x25519 public key

`xray x25519` returns:

```
PrivateKey: <priv>
Password (PublicKey): <pub>
Hash32: <hash>
```

Do not parse the public key by looking for a line that starts with `PublicKey:` — it does not exist. The correct extraction is from `Password (PublicKey):`.

### Broken parser (returns empty public key)

```bash
KEYS=$(xray x25519)
PRIVATE_KEY=$(echo "$KEYS" | grep "Private" | awk '{print $3}')   # OK
PUBLIC_KEY=$(echo "$KEYS" | grep "Public" | awk '{print $3}')   # EMPTY — wrong label
```

### Working parser

```bash
KEYS=$(xray x25519)
PRIVATE_KEY=$(echo "$KEYS" | sed -n '1s/PrivateKey: //p')
PUBLIC_KEY=$(echo "$KEYS" | sed -n '2s/Password (PublicKey): //p')

# sanity check
[ -z "$PRIVATE_KEY" ] || [ -z "$PUBLIC_KEY" ] && { echo "key extraction failed"; exit 1; }
```

If the public key is empty, the client share URL imports but cannot complete Reality handshake.

## Minimal working server config

```json
{
  "log": { "loglevel": "warning" },
  "inbounds": [
    {
      "port": 8443,
      "protocol": "vless",
      "settings": {
        "clients": [
          { "id": "YOUR_UUID", "flow": "xtls-rprx-vision" }
        ],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "tcp",
        "security": "reality",
        "realitySettings": {
          "show": false,
          "dest": "www.youtube.com:443",
          "xver": 0,
          "serverNames": ["www.youtube.com"],
          "privateKey": "YOUR_PRIVATE_KEY",
          "shortIds": ["YOUR_SHORT_ID"]
        }
      },
      "sniffing": {
        "enabled": true,
        "destOverride": ["http", "tls", "quic"]
      }
    }
  ],
  "outbounds": [
    { "protocol": "freedom", "tag": "direct" }
  ]
}
```

## Verification from a test client

Use a separate Xray instance as SOCKS5 and confirm traffic leaves through the VPS IP:

```bash
curl -x socks5://127.0.0.1:10808 -s -m 15 https://ipinfo.io/ip
# should print the VPS public IP
```

## Client share URL

```
vless://UUID@VPS_IP:8443?type=tcp&security=reality&pbk=PUBLIC_KEY&fp=firefox&sni=www.youtube.com&sid=SHORT_ID&spx=%2F#🇪🇺Europe
```

Make sure the router-side client sets **Flow = `xtls-rprx-vision`**. Some router v2ray UIs do not import `flow` automatically from the URL.

## Session artifact: ready-to-run server setup script

See `scripts/xray-vps-vless-reality-setup.sh` in this skill for an idempotent install + config generator.
