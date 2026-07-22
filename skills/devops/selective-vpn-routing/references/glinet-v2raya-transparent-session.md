# GL.iNet + v2rayA transparent proxy session notes

Device: GL.iNet GL-MT6000
Firmware: OpenWrt 21.02-SNAPSHOT / GL.iNet SDK 4.x
Goal: router-level transparent VPN for blocked resources; Russian/CIS/LAN direct.
Provider: okmulti.com VLESS+Reality subscription.

## What finally worked

1. Install `v2raya` and `xray-core` from GL.iNet / community repos.
2. v2rayA web UI on `http://192.168.0.1:2017`.
3. v2rayA generates `xray` config and manages its own iptables/nftables transparent proxy.
4. DNS also routed through tunnel so blocked domains resolve to real IPs.

## Manual xray TPROXY path (do NOT recommend on stock GL.iNet)

- Manual `iptables -t mangle` TPROXY broke internet for all LAN clients.
- Also broke GL.iNet web UI backend (VPN tabs disappeared from menu).
- Rollback required: stop xray, flush mangle/nat chains, remove ip rule/route table 100.

## Binary transfer recipe

Router lacks `sftp-server` and `python3`. GitHub download from router times out.
Working path:

```bash
# On a LAN Ubuntu machine
mkdir -p /tmp/xray-serve
cd /tmp/xray-serve
curl -LO https://github.com/XTLS/Xray-core/releases/download/v25.10.15/Xray-linux-arm64-v8a.zip
unzip -o Xray-linux-arm64-v8a.zip
python3 -m http.server 8000

# On the router
wget -O /usr/bin/xray.new http://<lan-machine>:8000/xray
chmod +x /usr/bin/xray.new
mv /usr/bin/xray /usr/bin/xray.old
mv /usr/bin/xray.new /usr/bin/xray
```

Also copy `geoip.dat` and `geosite.dat` from the same zip to `/usr/share/xray/`.

## DNS is mandatory

Without DNS through tunnel, blocked sites stay blocked because provider DNS returns fake/unreachable IPs.

Options:
- Let v2rayA handle DNS + transparent proxy together.
- Manual: set dnsmasq upstream to `1.1.1.1` and route UDP 53 through xray; use outbound server IP in xray config to avoid bootstrap loop.

## Rollback script

See `scripts/xray-router-rollback.sh`.
