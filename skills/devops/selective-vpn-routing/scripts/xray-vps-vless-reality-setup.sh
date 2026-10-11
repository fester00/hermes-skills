#!/usr/bin/env bash
set -euo pipefail
# Idempotent setup of Xray VLESS + Reality inbound on a fresh Ubuntu/Debian VPS.
# Outputs a vless:// share URL and the raw config parameters.

export DEBIAN_FRONTEND=noninteractive
IP=${IP:-$(curl -s -4 ifconfig.me)}
PORT=${PORT:-8443}
SNI=${SNI:-"www.youtube.com"}
SPX="%2F"

apt-get update -qq
apt-get install -y -qq curl jq qrencode openssl iptables-persistent ufw || true

# Install Xray if missing
if ! command -v xray >/dev/null 2>&1; then
  bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install
fi

systemctl enable xray || true

# Generate credentials
KEYS=$(xray x25519)
PRIVATE_KEY=$(echo "$KEYS" | sed -n '1s/PrivateKey: //p')
PUBLIC_KEY=$(echo "$KEYS" | sed -n '2s/Password (PublicKey): //p')
UUID=$(xray uuid)
SHORT_ID=$(openssl rand -hex 8)

if [ -z "$PRIVATE_KEY" ] || [ -z "$PUBLIC_KEY" ]; then
  echo "ERROR: failed to extract x25519 keys" >&2
  exit 1
fi

# Validate chosen SNI from the VPS before writing config
echo "Testing SNI $SNI from VPS..."
if ! curl -s -o /dev/null -w "%{http_code}" --connect-timeout 8 -m 15 "https://$SNI" | grep -Eq '^(200|301|302|307|308)$'; then
  echo "WARNING: https://$SNI is not reachable from this VPS. Reality handshake may fail." >&2
fi

# Write config
jq -n \
  --arg uuid "$UUID" \
  --arg pk "$PRIVATE_KEY" \
  --arg sni "$SNI" \
  --arg sid "$SHORT_ID" \
  --argjson port "$PORT" \
  '{
    log: { loglevel: "warning" },
    inbounds: [
      {
        port: $port,
        protocol: "vless",
        settings: {
          clients: [{ id: $uuid, flow: "xtls-rprx-vision" }],
          decryption: "none"
        },
        streamSettings: {
          network: "tcp",
          security: "reality",
          realitySettings: {
            show: false,
            dest: "\($sni):443",
            xver: 0,
            serverNames: [$sni],
            privateKey: $pk,
            shortIds: [$sid]
          }
        },
        sniffing: { enabled: true, destOverride: ["http", "tls", "quic"] }
      }
    ],
    outbounds: [{ protocol: "freedom", tag: "direct" }]
  }' > /usr/local/etc/xray/config.json

# Open port
ufw allow "$PORT/tcp" >/dev/null 2>&1 || true
iptables -I INPUT -p tcp --dport "$PORT" -j ACCEPT 2>/dev/null || true

systemctl restart xray
sleep 1
if systemctl is-active xray --quiet; then
  echo "Xray active on port $PORT"
else
  echo "ERROR: xray failed to start" >&2
  exit 1
fi

# Output link
LINK="vless://${UUID}@${IP}:${PORT}?type=tcp&security=reality&pbk=${PUBLIC_KEY}&fp=firefox&sni=${SNI}&sid=${SHORT_ID}&spx=${SPX}#🇪🇺Europe"
echo ""
echo "VLESS_LINK=$LINK"
echo ""
echo "$LINK" | qrencode -t ANSI256 2>/dev/null || true
