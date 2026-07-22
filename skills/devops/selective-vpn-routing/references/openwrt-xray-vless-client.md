# OpenWrt router as Xray/VLESS client

When the user wants to run VPN on an OpenWrt router instead of a local machine, the same Xray/VLESS subscription can be used, but the setup moves from `systemd --user` to the router's package manager (`opkg`) and config files.

## Preconditions

- Router is already running OpenWrt (not stock firmware).
- Router has SSH access (root password or key).
- User has a VLESS/Xray subscription URL returning an array of Xray JSON profiles.

## Check router environment

```bash
ssh root@192.168.0.1

cat /etc/openwrt_release
opkg update
opkg list | grep -iE "xray|v2ray|passwall|sing-box"
```

## Installation options

| Approach | Pros | Cons |
|----------|------|------|
| `xray-core` + manual `/etc/xray/config.json` | Minimal, no GUI dependencies | Edit JSON by hand or from a PC |
| `luci-app-passwall2` | Web GUI, import VLESS links/JSON | Larger flash/RAM footprint |
| `luci-app-openclash` | Good if config is Clash-format | Requires converting VLESS JSON |
| `sing-box` + `luci-app-nikki` | Lightweight universal proxy | Less common on low-end routers |

## Minimal `xray-core` setup

Install:
```bash
opkg update
opkg install xray-core
```

> Note: on some vendor OpenWrt 21.02 repos the package is `xray-core` 1.5.x, which is too old for VLESS Reality. Check `xray version` and, if needed, replace the binary with a current release from GitHub. See `references/glinet-openwrt-xray-vless-session.md` for a working manual replacement path using a LAN HTTP transfer.

Create config from one subscription profile. Strip the outer subscription routing/balancers if you only need a simple router-level proxy; otherwise keep them but ensure the router can resolve the outbound addresses.

```bash
mkdir -p /etc/xray
cat > /etc/xray/config.json <<'EOF'
{
  "log": { "loglevel": "warning" },
  "dns": { "servers": ["1.1.1.1", "1.0.0.1"] },
  "inbounds": [
    {
      "tag": "transparent",
      "port": 12345,
      "listen": "0.0.0.0",
      "protocol": "dokodemo-door",
      "settings": { "network": "tcp,udp", "followRedirect": true },
      "streamSettings": { "sockopt": { "tproxy": "tproxy" } },
      "sniffing": { "enabled": true, "destOverride": ["http", "tls", "quic"] }
    }
  ],
  "outbounds": [
    {
      "tag": "proxy",
      "protocol": "vless",
      "settings": {
        "vnext": [{
          "address": "vless-addr.example.com",
          "port": 443,
          "users": [{
            "id": "UUID-FROM-SUBSCRIPTION",
            "encryption": "none",
            "flow": "xtls-rprx-vision"
          }]
        }]
      },
      "streamSettings": {
        "network": "tcp",
        "security": "reality",
        "realitySettings": {
          "serverName": "nvidia.com",
          "publicKey": "PUBLIC-KEY-FROM-SUBSCRIPTION",
          "shortId": "SHORT-ID-FROM-SUBSCRIPTION",
          "fingerprint": "firefox"
        }
      }
    },
    { "tag": "direct", "protocol": "freedom" },
    { "tag": "block", "protocol": "blackhole" }
  ],
  "routing": {
    "rules": [
      { "ip": ["geoip:private"], "outboundTag": "direct" },
      { "domain": ["geosite:private"], "outboundTag": "direct" },
      { "type": "field", "network": "tcp,udp", "outboundTag": "proxy" }
    ]
  }
}
EOF
```

> Note: copy exact values (`address`, `UUID`, `publicKey`, `shortId`, `serverName`, `flow`) from the subscription profile. Do not guess them.

Enable service:
```bash
/etc/init.d/xray enable
/etc/init.d/xray start
/etc/init.d/xray status
logread -e xray | tail -30
```

### v2rayA as a middle ground
Some GL.iNet/opkg builds ship `v2raya` and `luci-app-v2raya`. v2rayA provides a web GUI on `http://router-ip:2017` and can import VLESS subscriptions. Caveat: v2rayA 2.2.7 on GL.iNet 21.02 parsed VLESS+Reality URLs as `vless(tcp+reality)` but failed to start them with `LocateServerRaw: invalid TYPE`. It may still be useful for non-Reality nodes or for generating TProxy firewall rules. If it fails, fall back to running `xray-core` directly with a hand-written config.

### Router-level transparent proxy
After Xray is running, redirect marked traffic to the `dokodemo-door` port. A common approach on OpenWrt:

1. Install `iptables-mod-tproxy` / `kmod-ipt-tproxy` (or `nftables` equivalents for newer OpenWrt).
2. Mark packets from selected clients or for selected destinations.
3. Route marked packets to Xray's TProxy port.

This is advanced and varies by OpenWrt version. For most users, `passwall2` is safer because it handles firewall rules automatically.

> **Warning for GL.iNet / OpenWrt 21.02:** manual TPROXY on stock GL.iNet firmware easily breaks internet for all LAN clients and can make the web UI misbehave (e.g. VPN tabs disappear while the network is broken). See `references/glinet-openwrt-xray-vless-session.md` for a real failure case and rollback commands. Prefer Passwall2/Nikki or provider-native protocols (WireGuard/OpenVPN) on these devices. If you must use Xray on stock firmware, keep it as a SOCKS5/HTTP proxy only (template `xray-router-socks5-ru-direct.json`) and configure clients manually.

## Passwall2 quick path

```bash
# Add passwall2 feed if not present (example for OpenWrt 23.05; URL may differ)
echo "src/gz passwall2_packages https://github.com/xiaorouji/openwrt-passwall-packages/releases/download/2024.02.07/packages-23.05_<arch>" >> /etc/opkg/customfeeds.conf
opkg update
opkg install luci-app-passwall2
```

Then in LuCI:
- Services → PassWall2 → Node Subscribe
- Add the subscription URL.
- Select a node and set it as default.
- Configure "Main Switch" and routing rules (china/ru direct, foreign proxy).
- Save & Apply.

## Verification from a LAN client

```bash
# Check public IP through the router
curl https://api.ipify.org

# Check via proxy from the router itself
curl -x socks5h://127.0.0.1:10808 https://api.ipify.org
```

## Pitfalls

- **Flash space:** `xray-core` is ~15–25 MB. Low-end routers with 8 MB flash will not fit it.
- **RAM:** running Xray on a router with <128 MB RAM is unstable.
- **DNS leaks:** make sure LAN clients use the router's DNS or a trusted DNS over the proxy.
- **Subscription credentials:** subscription URLs contain real credentials. Do not paste them into public chats or logs.
- **Stock firmware:** if the router menu only shows OpenVPN/WireGuard/Tor, it is likely not OpenWrt or OpenWrt without proxy packages.
- **Package age:** vendor OpenWrt 21.02 repos may ship `xray-core` 1.5.x, which is too old for VLESS Reality. You may need to replace the binary manually; use the LAN HTTP transfer trick if internet download from the router fails. See `references/glinet-openwrt-xray-vless-session.md`.

## Converting a subscription profile for manual use

Subscription URLs often return an array of full Xray configs with balancers, loopback inbounds, and SOCKS5 inbounds for local use. On a router you typically only need:
- one outbound (`proxy`) from one profile,
- `direct` and `block` outbounds,
- minimal routing rules,
- a `dokodemo-door` inbound for transparent proxy or rely on Passwall2.

Discard the `inbounds` section (ports 10808/10809) unless you want LAN clients to use the router as a SOCKS5 proxy explicitly.

## Related local-machine path

For running Xray on the Ubuntu server `192.168.0.98` instead of the router, see the main `selective-vpn-routing` SKILL.md section "Xray as systemd user service".

## Support files for this session

- `references/glinet-openwrt-xray-vless-session.md` — real GL-MT6000 session notes, v2rayA attempt, TProxy failure, rollback, and community-firmware options.
- `templates/xray-router-socks5-only.json` — minimal safe config (SOCKS5/HTTP only, no TPROXY).
- `templates/xray-router-socks5-ru-direct.json` — same with Russian/CIS domains routed direct.
- `scripts/xray-router-rollback.sh` — one-click rollback for broken TPROXY/Xray state.
