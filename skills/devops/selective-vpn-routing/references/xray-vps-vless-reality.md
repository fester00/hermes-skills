# VPS-side Xray VLESS + Reality server on Ubuntu 24.04

Session notes for setting up a self-hosted Xray inbound on a fresh Ubuntu VPS behind Docker/wg-easy, with a separate VLESS+Reality port.

## Context

- VPS: Ubuntu 24.04, public interface `ens3`, Docker `wg-easy` already on UDP 51820.
- Nginx already listens on 443 for the wg-easy web UI; do not kill it.
- Goal: add a second proxy path (Xray Reality) so the router can reach blocked sites.

## Server install

```bash
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install
```

This installs `/usr/local/bin/xray`, systemd service `xray.service`, and `/usr/local/etc/xray/config.json`.

## Credentials

```bash
UUID="$(xray uuid)"
KEYS="$(xray x25519)"
PRIVATE_KEY="$(grep "PrivateKey" <<< "$KEYS" | awk '{print $2}')"
PUBLIC_KEY="$(grep "Password (PublicKey)" <<< "$KEYS" | awk '{print $3}')"
SHORT_ID="$(openssl rand -hex 8)"
PORT=8443   # because 443 is taken by nginx
```

Record all four values; the client needs UUID, PUBLIC_KEY, SHORT_ID, PORT, and SNI.

## Sample config

`/usr/local/etc/xray/config.json`:

```json
{
  "log": { "loglevel": "warning" },
  "inbounds": [
    {
      "port": 8443,
      "protocol": "vless",
      "settings": {
        "clients": [{ "id": "YOUR_UUID", "flow": "xtls-rprx-vision" }],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "tcp",
        "security": "reality",
        "realitySettings": {
          "show": false,
          "dest": "www.google.com:443",
          "xver": 0,
          "serverNames": ["www.google.com", "google.com", "www.youtube.com"],
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
    { "protocol": "freedom", "tag": "direct" },
    { "protocol": "blackhole", "tag": "block" }
  ]
}
```

Validate and restart:

```bash
xray run -test -c /usr/local/etc/xray/config.json
systemctl restart xray
systemctl status xray --no-pager
ss -tlnp | grep 8443
```

## Client share URL

```
vless://UUID@VPS_IP:8443?security=reality&flow=xtls-rprx-vision&sni=www.google.com&sid=SHORT_ID&pbk=PUBLIC_KEY&fp=chrome&type=tcp#VPS-Reality
```

## Notes

- Port 8443 is fine; GFW warning from Xray about non-443 Reality is acceptable for a self-hosted VPS in a non-censoring region.
- Keep wg-easy running if you still want WireGuard access; Xray and WG can coexist on the same host as long as ports do not collide.
- Ensure `net.ipv4.ip_forward=1` is set and Docker FORWARD rules for wg-easy remain saved via `iptables-persistent` if WG clients still need internet.
