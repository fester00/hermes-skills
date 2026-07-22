# GL.iNet OpenWrt router as Xray/VLESS client — session notes

Real session: GL-MT6000, GL.iNet SDK 4 (OpenWrt 21.02-SNAPSHOT), VLESS/XRay subscription from okmulti.com.

## Router environment

```
DISTRIB_ID='OpenWrt'
DISTRIB_RELEASE='21.02-SNAPSHOT'
DISTRIB_TARGET='mediatek/mt7986'
DISTRIB_ARCH='aarch64_cortex-a53'
OPENWRT_DEVICE_PRODUCT='GL.iNet GL-MT6000'
```

- RAM: ~1 GB.
- Flash overlay: 7.2 GB usable (loop device).
- Stock GL.iNet web UI shows only OpenVPN Client/Server, WireGuard Client/Server, Tor.
- `xray-core` 1.5.9 available from GL.iNet repos (too old for VLESS Reality).

## Key finding: xray-core in repo is too old

`opkg install xray-core` gives `1.5.9-1`. Reality transport appeared in Xray ~1.8.x. The VLESS subscription requires Reality, so the stock package cannot be used directly.

## Updating xray-core manually on the router

Because the router's `wget`/`curl` to GitHub timed out, the easiest transfer path was to download the ARM64 binary on a local Ubuntu machine and serve it to the router over the LAN via a temporary Python HTTP server.

```bash
# On local machine (192.168.0.98)
cd /tmp
curl -L -O https://github.com/XTLS/Xray-core/releases/download/v25.3.6/Xray-linux-arm64-v8a.zip
unzip Xray-linux-arm64-v8a.zip
mkdir -p /tmp/xray-serve && cp xray /tmp/xray-serve/
cd /tmp/xray-serve && python3 -m http.server 8000
```

```bash
# On router (via SSH)
cd /tmp
wget -q -O xray.new http://192.168.0.98:8000/xray
chmod +x xray.new
mv /usr/bin/xray /usr/bin/xray.old
mv xray.new /usr/bin/xray
xray version
```

Result: `Xray 25.3.6 (Xray, Penetrates Everything.) 2cba2c4 (go1.24.1 linux/arm64)`.

## Configuration

`/etc/xray/config.json` was built from the Poland profile of the subscription:

- VLESS outbound with `xtls-rprx-vision` flow.
- Reality security with `serverName: nvidia.com`, public key, shortId, `fingerprint: firefox`.
- `dokodemo-door` inbound on `0.0.0.0:12345` with `tproxy`.
- SOCKS5 on `10808`, HTTP on `10809`.
- Routing: `geoip:private`, `geoip:ru`, `geosite:private`, `geosite:mailru`, and regex `\.(ru|su|xn--p1ai|by)$` direct; everything else to `proxy`.

Important: the bundled `geosite.dat` from `xray-geodata` package did not contain `category-ru`. We replaced both `geoip.dat` and `geosite.dat` with the versions bundled in the same Xray release zip so that current list names (`geosite:mailru`, etc.) resolve.

```bash
cd /usr/share/xray
wget -q -O geoip.dat http://192.168.0.98:8000/geoip.dat
wget -q -O geosite.dat http://192.168.0.98:8000/geosite.dat
```

## Service enable/disable

```bash
uci set xray.enabled.enabled=1   # or 0 to disable
uci commit xray
/etc/init.d/xray enable
/etc/init.d/xray start
/etc/init.d/xray stop
```

The init script reads `confdir` from UCI (`/etc/xray`) and loads all `*.json` there, including sample configs from `xray-example`. Rename/remove the sample files (`vpoint_socks_vmess.json`, `vpoint_vmess_freedom.json`) so only the intended config runs.

## TProxy attempt and failure mode

Manual iptables TPROXY rules were added:

```bash
ip rule add fwmark 1 table 100
ip route add local 0.0.0.0/0 dev lo table 100

iptables -t mangle -N XRAY
iptables -t mangle -A XRAY -d 192.168.0.0/16 -j RETURN
iptables -t mangle -A XRAY -d 130.255.9.0/24 -j RETURN   # WAN subnet
iptables -t mangle -A XRAY -p tcp -j TPROXY --on-port 12345 --tproxy-mark 1
iptables -t mangle -A XRAY -p udp -j TPROXY --on-port 12345 --tproxy-mark 1
iptables -t mangle -A PREROUTING -i br-lan -j XRAY

iptables -t mangle -N XRAY_MASK
iptables -t mangle -A XRAY_MASK -d 192.168.0.0/16 -j RETURN
iptables -t mangle -A XRAY_MASK -d 130.255.9.0/24 -j RETURN
iptables -t mangle -A XRAY_MASK -j MARK --set-mark 1
iptables -t mangle -A OUTPUT -j XRAY_MASK
```

This immediately broke internet access for all LAN clients. Likely causes:

1. DNS UDP traffic was captured by TPROXY but Xray could not establish its own Reality/TLS connection to the upstream server, so DNS and all outbound traffic stalled.
2. The WAN gateway/subnet used by Xray itself (130.255.9.x) was in the RETURN list, but the subscription's upstream server hostname resolved to other IPs that may also have needed exclusion, or the routing mark table was not applied correctly to locally-generated Xray packets.
3. GL.iNet SDK has its own firewall/DNS dispatcher (`dns_dispatcher` chain in `nat` table) that conflicts with raw TPROXY rules.

**Lesson:** On GL.iNet firmware, manual TPROXY is dangerous. Prefer Passwall2/OpenClash/Nikki, or keep Xray as a local SOCKS5 proxy only, not a transparent router proxy.

## Rollback commands

If TPROXY breaks connectivity, run via SSH or reboot the router:

```bash
/etc/init.d/xray stop
/etc/init.d/xray disable
uci set xray.enabled.enabled=0
uci commit xray

iptables -t mangle -D PREROUTING -j XRAY 2>/dev/null || true
iptables -t mangle -D OUTPUT -j XRAY_MASK 2>/dev/null || true
iptables -t mangle -F XRAY 2>/dev/null || true
iptables -t mangle -X XRAY 2>/dev/null || true
iptables -t mangle -F XRAY_MASK 2>/dev/null || true
iptables -t mangle -X XRAY_MASK 2>/dev/null || true

ip rule del fwmark 1 table 100 2>/dev/null || true
ip route del local 0.0.0.0/0 dev lo table 100 2>/dev/null || true

/etc/init.d/rpcd restart
/etc/init.d/uhttpd restart
/etc/init.d/nginx restart
```

## GL.iNet UI impact

The broken TProxy/Xray state caused the GL.iNet web UI to lose the WireGuard Client tab under VPN. The underlying packages (`gl-sdk4-wg-client`, `gl-sdk4-ui-vpn-client`, `wg-client.so`, `wg_client` RPC) remained installed and registered in `/usr/share/oui/menu.d/vpn-client.json`. The tab returned after:

1. Stopping and disabling xray.
2. Clearing all manual mangle/TPROXY rules.
3. Restarting `rpcd`, `uhttpd`, and `nginx`.

If the UI still does not show VPN Client after a service restart, a full router reboot is the most reliable way to re-initialize the GL.iNet Lua/nginx backend.

## Recommended path for this class of router

1. **Best:** get a WireGuard or OpenVPN config from the provider and use the native GL.iNet UI. No Xray needed.
2. **Next best:** install `v2rayA` from GL.iNet/opkg repos if available. `v2rayA` provides a web GUI on port `2017` for importing VLESS/Xray subscriptions and managing routing. Important limitation: v2rayA 2.2.7 on GL.iNet 21.02 failed to parse VLESS+Reality URLs with `LocateServerRaw: invalid TYPE`, even though it recognized the protocol name. It can still generate configs and TProxy rules; you may need to supply a full JSON config or use non-Reality nodes.
3. **Community firmware:** flash ImmortalWrt 23.05/24.10 or OpenWrt 23.05+ and install `luci-app-passwall2` or `luci-app-nikki`. This gives a maintained GUI for VLESS/Xray. Flashing carries brick risk; use U-Boot TFTP recovery if needed.
4. **Avoid:** manual TPROXY on stock GL.iNet 21.02.

## Additional transfer/tooling notes

### No SCP / sftp-server
`scp` to the router fails because GL.iNet build does not include `/usr/libexec/sftp-server`. Use LAN HTTP transfer instead.

### Old `wget`
Router `wget` does not support `--show-progress`. Use `wget -q -O <file> <url>` or `curl -L -o <file> <url>`.

### No Python 3
`python3` is not installed. Any helper scripts must run on the LAN machine, not the router.

### `xray convert` not available for geosite inspection
The CLI subcommand `xray geoip` / `xray geosite` / `xray convert geosite:...` did not exist in the deployed build. To find valid geosite list names, unpack `geosite.dat` from the same release zip on a PC and grep the binary for known names, or simply replace both `.dat` files with the release-bundled versions.

### Missing geosite list names
Old `xray-geodata` package (from `xray-core` 1.5.9 era) raised errors like:

```
Failed to load geosite: CATEGORY-RU
Failed to load geosite: RU
```

Fix: replace `/usr/share/xray/geosite.dat` and `/usr/share/xray/geoip.dat` with the versions bundled in the current Xray release zip.

## v2rayA on stock GL.iNet

v2rayA can be installed via opkg (`opkg install v2raya luci-app-v2raya`) on some GL.iNet/OpenWrt 21.02 builds. It listens on `0.0.0.0:2017` and provides a web GUI.

### What worked
- Creating a v2rayA admin account via `/api/account`.
- Importing a VLESS subscription URL via `/api/import`.
- Importing individual `vless://` URLs (the GUI showed them as `vless(tcp+reality)`).
- Updating GFWList via `/api/gfwList` with payload `{"version":"YYYY-MM-DD"}`.
- Enabling TProxy mode via `/api/setting` (`{"transparent":"tproxy", "pacMode":"gfwlist"}`).

### What did NOT work
- **Starting the selected Reality node.** v2rayA 2.2.7.4 returned `failed to start v2ray-core: LocateServerRaw: invalid TYPE` for VLESS+Reality profiles. The protocol was parsed enough to display, but not enough to build a valid outbound for xray-core.

### Practical fallback
If v2rayA fails on Reality, stop it and run `xray-core` directly with a hand-written config that includes only SOCKS5/HTTP inbounds (no transparent proxy). This keeps the router's normal routing intact while providing a LAN-accessible proxy on `192.168.0.1:10808`/`10809`.

```bash
# Router
/etc/init.d/v2raya stop
/usr/bin/xray run -config /etc/xray/config.json &
```

Then configure clients manually (browser proxy extension, SwitchyOmega, etc.).

## ImmortalWrt / community-firmware path

For a proper VLESS GUI on GL-MT6000, the standard path is:

- Download ImmortalWrt 23.05/24.10 for `mediatek/mt7986/glinet_gl-mt6000`:
  - https://firmware-selector.immortalwrt.org/?version=23.05.4&target=mediatek%2Fmt7986&id=glinet_gl-mt6000
  - https://downloads.immortalwrt.org/releases/23.05.4/targets/mediatek/mt7986/
- Flash either `factory.bin` via U-Boot TFTP or `sysupgrade.bin` from stock GL.iNet UI.
- Install `luci-app-passwall2` or `luci-app-nikki` from the ImmortalWrt feeds.
- Import the VLESS subscription URL in the GUI.

This is the recommended route for users who need router-level transparent proxy and do not have WireGuard/OpenVPN from the provider.

## Support scripts / templates

- `templates/xray-router-config.json` — minimal router VLESS+Reality config (SOCKS5/HTTP only, no TPROXY).
- `scripts/xray-router-rollback.sh` — firewall + xray stop/disable rollback.

See the main `selective-vpn-routing` SKILL.md for local-machine Xray setup.
