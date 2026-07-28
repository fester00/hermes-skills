#!/bin/sh
# Install and configure sing-box for WireGuard domain-based routing on GL.iNet stock firmware.
# Run as root on the router. Edit KEYS before running.

set -e

# --- configuration ---
VPS_IP="189.74.120.227"
VPS_PORT="51820"
WG_CLIENT_ADDR="192.168.101.2/24"
PRIVATE_KEY="YOUR_PRIVATE_KEY"
PEER_PUBLIC_KEY="YOUR_PEER_PUBLIC_KEY"
PRE_SHARED_KEY="YOUR_PRESHARED_KEY"

# --- install sing-box ---
opkg update || true
if ! command -v sing-box >/dev/null 2>&1; then
    if ! grep -q "downloads.openwrt.org/releases" /etc/opkg/customfeeds.conf 2>/dev/null; then
        echo "Adding OpenWrt packages feed..."
        cat >> /etc/opkg/customfeeds.conf <<'EOF'
src/gz openwrt_packages https://downloads.openwrt.org/releases/24.10.4/packages/aarch64_cortex-a53/packages/
EOF
        opkg update
    fi
    opkg install sing-box
fi

# --- ensure geosite rule set exists ---
mkdir -p /etc/sing-box
if [ ! -f /etc/sing-box/geosite-category-ru-blocked.srs ]; then
    echo "Downloading geosite-category-ru-blocked.srs ..."
    # Try direct first; fall back to curl without proxy if router cannot reach GitHub.
    if ! wget -q -O /etc/sing-box/geosite-category-ru-blocked.srs.new \
        "https://github.com/SagerNet/sing-geosite/raw/rule-set/geosite-category-ru-blocked.srs" 2>/dev/null; then
        echo "ERROR: could not download geosite rule set. Download it on another machine and copy to /etc/sing-box/geosite-category-ru-blocked.srs"
        exit 1
    fi
    mv /etc/sing-box/geosite-category-ru-blocked.srs.new /etc/sing-box/geosite-category-ru-blocked.srs
fi

# --- write config ---
cat > /etc/sing-box/config.json <<EOF
{
  "log": {
    "level": "info",
    "timestamp": true
  },
  "dns": {
    "servers": [
      {
        "tag": "google",
        "address": "tcp://8.8.8.8",
        "detour": "wg-vps"
      },
      {
        "tag": "local",
        "address": "udp://192.168.0.1",
        "detour": "direct"
      }
    ],
    "rules": [
      {
        "rule_set": ["geosite-ru-blocked"],
        "server": "google"
      }
    ],
    "final": "local"
  },
  "inbounds": [
    {
      "type": "tproxy",
      "tag": "tproxy-in",
      "listen": "::",
      "listen_port": 7893,
      "sniff": true,
      "domain_strategy": "prefer_ipv4"
    }
  ],
  "outbounds": [
    {
      "type": "wireguard",
      "tag": "wg-vps",
      "server": "${VPS_IP}",
      "server_port": ${VPS_PORT},
      "system_interface": false,
      "interface_name": "singwg0",
      "local_address": ["${WG_CLIENT_ADDR}"],
      "private_key": "${PRIVATE_KEY}",
      "peer_public_key": "${PEER_PUBLIC_KEY}",
      "pre_shared_key": "${PRE_SHARED_KEY}",
      "reserved": [0, 0, 0],
      "mtu": 1420,
      "persistent_keepalive_interval": 15
    },
    {
      "type": "direct",
      "tag": "direct"
    },
    {
      "type": "block",
      "tag": "block"
    }
  ],
  "route": {
    "rule_set": [
      {
        "tag": "geosite-ru-blocked",
        "type": "local",
        "format": "binary",
        "path": "/etc/sing-box/geosite-category-ru-blocked.srs"
      }
    ],
    "rules": [
      {
        "rule_set": ["geosite-ru-blocked"],
        "outbound": "wg-vps"
      }
    ],
    "final": "direct",
    "auto_detect_interface": true,
    "default_mark": 0
  },
  "experimental": {
    "clash_api": {
      "external_controller": "0.0.0.0:9090"
    }
  }
}
EOF

# --- nftables TPROXY rules ---
mkdir -p /etc/nftables.d
cat > /etc/nftables.d/sing-box-tproxy.nft <<'EOF'
table inet sing-box {
    chain prerouting {
        type filter hook prerouting priority mangle; policy accept;
        iifname "br-lan" meta l4proto { tcp, udp } tproxy to :7893 meta mark set meta mark | 0x01
    }

    chain output {
        type route hook output priority mangle; policy accept;
        ip daddr != { 127.0.0.0/8, 192.168.0.0/16 } meta l4proto { tcp, udp } meta mark set meta mark | 0x01
    }
}
EOF

# --- TPROXY routing rule ---
cat > /etc/hotplug.d/iface/99-sing-box-tproxy <<'EOF'
#!/bin/sh
[ "$ACTION" = "ifup" ] || exit 0
ip rule add fwmark 0x1 lookup 100 2>/dev/null || true
ip route add local default dev lo table 100 2>/dev/null || true
EOF
chmod +x /etc/hotplug.d/iface/99-sing-box-tproxy

# --- apply now ---
nft -f /etc/nftables.d/sing-box-tproxy.nft 2>/dev/null || {
    nft delete table inet sing-box 2>/dev/null || true
    nft -f /etc/nftables.d/sing-box-tproxy.nft
}
ip rule add fwmark 0x1 lookup 100 2>/dev/null || true
ip route add local default dev lo table 100 2>/dev/null || true

# --- disable conflicting services ---
ifdown wgclient1 2>/dev/null || true
uci set network.wgclient1.disabled='1' 2>/dev/null && uci commit network 2>/dev/null || true
/etc/init.d/v2raya stop 2>/dev/null || true
/etc/init.d/v2raya disable 2>/dev/null || true

# --- enable and start sing-box ---
/etc/init.d/sing-box enable
sing-box check -c /etc/sing-box/config.json || {
    echo "sing-box config check failed"
    exit 1
}
/etc/init.d/sing-box restart
sleep 2
pgrep -a sing-box || {
    echo "sing-box did not start"
    exit 1
}

echo "sing-box configured. Check: curl https://2ip.ru from a LAN PC."
