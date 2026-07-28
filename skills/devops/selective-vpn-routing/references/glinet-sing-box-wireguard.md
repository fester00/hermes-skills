# GL.iNet Router with sing-box + WireGuard (domain-based routing)

## Context

Stock GL.iNet firmware (SDK 4.x / OpenWrt 21.02+) has a built-in WireGuard Client, but its policy engine can become unstable: `wgclient1` may flap up/down every 20-30 seconds, domain-based routing may stop working after a reset, and the UI may rewrite `AllowedIPs` or drop the domain list. When that happens, a clean alternative is to bypass the GL.iNet WG Client entirely and run **sing-box** directly on the router.

**sing-box** can:
- use WireGuard as an outbound,
- listen on a TPROXY port for transparent LAN proxying,
- route by domain set (`geosite:category-ru-blocked`) so only blocked resources go through the tunnel,
- manage DNS so that blocked domains are resolved through the tunnel.

This note covers installing sing-box from OpenWrt repos, configuring it for a personal VPS running WireGuard, enabling TPROXY, and integrating with dnsmasq so LAN clients need zero proxy configuration.

## When to use this path

- The GL.iNet WireGuard Client flaps and you have tried the fixes in `references/glinet-wireguard-policy-routing.md` without success.
- You want domain-based split tunneling on stock firmware without community packages like Passwall2/Nikki.
- You already have a VPS with a working WireGuard server and the keys.

## What you need

- SSH access to the router as root.
- Router architecture matching a published OpenWrt repo (GL-MT6000 = `aarch64_cortex-a53`).
- VPS endpoint, port, and WireGuard keys: private key, peer public key, preshared key (if used), and the client address inside the WG network (e.g. `192.168.101.2/24`).
- The VPS host must forward traffic from the WG subnet to its public interface and NAT it. For `wg-easy` in Docker see `references/wg-easy-docker-host-forwarding.md`.

## Install sing-box

```bash
opkg update
opkg install sing-box
```

If the package is not in the stock GL.iNet repo, add the matching OpenWrt packages feed:

```bash
cat >> /etc/opkg/customfeeds.conf <<'EOF'
src/gz openwrt_packages https://downloads.openwrt.org/releases/24.10.4/packages/aarch64_cortex-a53/packages/
EOF
opkg update
opkg install sing-box
```

Verify:

```bash
sing-box version
# must include with_wireguard in tags
```

## Config file

Create `/etc/sing-box/config.json` from `templates/sing-box-router-wg-domain-routing.json`.

Key sections:

- `outbounds[0]` is the WireGuard outbound:
  - `server` = VPS public IP
  - `server_port` = 51820
  - `local_address` = client WG address, e.g. `["192.168.168.101.2/24"]`
  - `private_key`, `peer_public_key`, `pre_shared_key`
  - `mtu` = 1420 (or 1380 if MTU issues)
  - `persistent_keepalive_interval` = 15

- `inbounds[0]` is TPROXY on `0.0.0.0:7893`.

- `route.rule_set` uses the remote `geosite-category-ru-blocked.srs` set.

- `route.rules` sends anything matching the blocked set through `wg-vps`; everything else uses `direct`.

- `dns` resolves blocked-domain queries through the `wg-vps` outbound; other queries go direct to the router/local DNS.

**Important:** because rule sets download from GitHub, set `download_detour` to `direct`. The router itself may not reach GitHub if the default WAN is blocked from it, so download the `.srs` file on another machine and copy it to `/etc/sing-box/geosite-category-ru-blocked.srs`, then change the rule set from `remote` to `local`:

```json
{
  "tag": "geosite-ru-blocked",
  "type": "local",
  "format": "binary",
  "path": "/etc/sing-box/geosite-category-ru-blocked.srs"
}
```

Then you do not need network access during sing-box startup.

## Validate and start

```bash
sing-box check -c /etc/sing-box/config.json
/etc/init.d/sing-box enable
/etc/init.d/sing-box start
/etc/init.d/sing-box status
```

The service file from the OpenWrt package reads `/etc/sing-box/config.json` by default.

## TPROXY and dnsmasq integration

TPROXY requires routing marks and iptables/nftables rules. The OpenWrt sing-box package may not create these automatically. Add them via `/etc/nftables.d/sing-box-tproxy.nft`:

```nft
#!/usr/sbin/nft -f

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
```

Also add a routing rule for the TPROXY mark:

```bash
ip rule add fwmark 0x1 lookup 100 2>/dev/null || true
ip route add local default dev lo table 100 2>/dev/null || true
```

Persist them in `/etc/rc.local` (before `exit 0`):

```bash
cat >> /etc/rc.local <<'EOF'
# sing-box TPROXY routing
ip rule add fwmark 0x1 lookup 100 2>/dev/null
ip route add local default dev lo table 100 2>/dev/null
EOF
```

Then reload nftables:

```bash
nft -f /etc/nftables.d/sing-box-tproxy.nft
```

**DNS:** Make sure LAN clients use the router as DNS. If sing-box handles DNS internally, you can leave dnsmasq as the DHCP DNS server. For better leak resistance, configure dnsmasq to forward blocked-domain queries to sing-box's DNS port, or let sing-box listen on 53 and replace dnsmasq (advanced).

The simplest reliable path on stock firmware is to let dnsmasq remain the LAN DNS server and have sing-box intercept and reroute blocked-domain queries via its own `dns` section.

## Verify

From the router:

```bash
# sing-box is running
pgrep -a sing-box

# interface exists
ip addr show singwg0

# WG handshake (sing-box creates the kernel interface)
wg show singwg0

# default gateway through the tunnel is in the sing-box route table, not the system table
ip route show table all | grep singwg0
```

From a LAN PC:

```powershell
ipconfig /flushdns
nslookup google.com
curl.exe -s https://2ip.ru
curl.exe -s https://api.github.com
```

If `2ip.ru` returns the VPS IP and GitHub is reachable, routing works.

## Coexistence with GL.iNet WG Client and v2rayA

Only one tunnel solution should be active at a time.

Disable GL.iNet WG Client in the web UI and stop any v2rayA:

```bash
uci set network.wgclient1.disabled='1' 2>/dev/null
uci commit network 2>/dev/null
ifdown wgclient1 2>/dev/null
/etc/init.d/v2raya stop 2>/dev/null
/etc/init.d/v2raya disable 2>/dev/null
```

## Pitfalls

- **Missing kernel TPROXY module.** Stock GL.iNet kernels usually have it. If `tproxy` fails, switch sing-box inbound to `redirect` (TCP only) plus `tun` for UDP, or use a `tun` inbound instead of TPROXY.
- **MTU too high.** If large HTTPS pages hang, lower WG MTU to 1380 and test.
- **DNS leaks.** A PC with browser DoH or hardcoded 8.8.8.8 will bypass router DNS and the domain-based routing. Force router DNS via DHCP option 6 or block outbound DNS to other servers in firewall.
- **VPS forwarding not configured.** See `references/wg-easy-docker-host-forwarding.md`. If the router can handshake but cannot reach the internet through the tunnel, the problem is almost always on the VPS host, not sing-box.
- **Geosite rule set out of date.** Blocked sites change; update the `.srs` file weekly or use a cron job.

## Rollback

If something breaks LAN internet:

```bash
/etc/init.d/sing-box stop
/etc/init.d/sing-box disable
nft delete table inet sing-box 2>/dev/null
ip rule del fwmark 0x1 lookup 100 2>/dev/null
ip route del local default dev lo table 100 2>/dev/null
```

Then restore GL.iNet WG Client or use Global Proxy.

## Bottom line

When the GL.iNet WireGuard Client UI/policy engine becomes unreliable, sing-box is a clean, self-contained replacement on stock firmware. It needs a correct WG server on the VPS side and one-time TPROXY setup, but it avoids the `tunnel-switch` flapping and domain-list rewrite issues of the GL.iNet UI.
