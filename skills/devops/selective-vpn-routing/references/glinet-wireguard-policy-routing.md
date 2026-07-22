# GL.iNet WireGuard Client with Policy-Based Routing

## Context

GL.iNet routers (tested on GL-MT6000 with stock SDK 4.x / OpenWrt 21.02) support WireGuard Client through the web UI. The UI offers routing policies that determine which traffic goes through the tunnel and which stays on the direct WAN connection.

Two common modes:

| Mode | Behavior | Use case |
|------|----------|----------|
| **Global Proxy** | All traffic (including DNS) goes through `wgclient1`. | Simplest; bypasses blocks for every site. |
| **Policy / VPN Dashboard** | Only domains/IPs from a user list go through `wgclient1`; everything else uses WAN. | Split tunneling; saves VPS traffic. |

This note focuses on the **Policy** mode, which is the most common choice for a personal VPS.

## How to enable policy routing

1. **VPN → WireGuard Client** in the web UI.
2. Add or select your WG profile.
3. Open profile settings / routing policy.
4. Choose **Policy** (not *Global Proxy*, not *Auto Detect*).
5. In the "Use VPN" list, add domains that must go through the tunnel.
6. Save and apply.

## Recommended domain list for Russia (minimal)

```
gemini.google.com
google.com
googleapis.com
gstatic.com
googleusercontent.com
github.com
api.github.com
raw.githubusercontent.com
fonts.googleapis.com
fonts.gstatic.com
```

For a larger list, see the session note `references/glinet-wireguard-blocked-domains-list.md`.

## Important: `AllowedIPs = 0.0.0.0/0` does **not** mean Global Proxy

When the router creates `wgclient1`, the peer section often contains:

```
allowed ips: 0.0.0.0/0, ::/0
```

On a phone or laptop this would send everything through WG. On GL.iNet in Policy mode it only means the peer is allowed to receive traffic for any destination; the router's policy engine decides what actually enters the tunnel.

## Routing tables on the router

Typical state in Policy mode:

```text
# ip route show table all | grep wgclient1
default dev wgclient1 table 1001 proto static scope link
192.168.101.0/24  dev wgclient1 table 1001 proto static scope link
```

```text
# ip route show table 1001
blackhole default proto static metric 254
```

`table 1001` intentionally has a `blackhole default`. It is used as the target routing table for marked VPN traffic, but the router injects host routes for resolved IPs of the listed domains into that table. If a domain's IP is not in the table, traffic falls back to the WAN.

## DNS and Policy mode

In Policy mode the router uses DNS to learn the IP address of a listed domain and then installs a route for that IP through `wgclient1`. Therefore:

- Client devices must use the router as DNS server (default DHCP setting).
- Do **not** use DNS-over-HTTPS / DNS-over-TLS on the client, or the router cannot see the domain name.
- If DNS resolution of a VPN-only domain times out (`nslookup gemini.google.com` → timeout), the tunnel or the DNS forwarding through the tunnel is broken. In that case switch to **Global Proxy** temporarily to confirm basic WG connectivity, then debug DNS.

## Common symptoms and fixes

### Symptom: `nslookup gemini.google.com` times out

**Likely cause:** DNS request is being routed through `wgclient1` but the DNS server (8.8.8.8) is not reachable through the tunnel, or the tunnel itself is flapping.

**Fix steps:**
1. Check WG handshake: `wg show wgclient1`. `latest handshake` should be < 30s.
2. Check if the tunnel is flapping in logs: `logread | grep wgclient1 | tail -50`.
3. If it flaps every ~25s, the router watchdog is restarting it. Disable VPN failover monitoring for this WG profile in the web UI, or increase the watchdog timeout.
4. Try **Global Proxy** mode. If DNS works there, the problem is specifically DNS forwarding in Policy mode.

### Symptom: `curl -I https://gemini.google.com` from the router returns 200, but browser on a PC shows an error

**Likely causes:**
- Browser cached an old failed response.
- PC uses a different DNS server (e.g. 8.8.8.8 directly, or DoH in browser).
- Gemini loads resources from domains not in the policy list (`ogs.google.com`, `*.googleusercontent.com`, etc.).

**Fix:**
1. Clear browser cache / cookies for `.google.com`.
2. Flush DNS on the PC:
   - Windows: `ipconfig /flushdns`
   - macOS: `sudo dscacheutil -flushcache`
   - Linux: `sudo systemd-resolve --flush-caches`
3. Add related Google domains to the policy list.
4. Verify the PC receives DNS from the router:
   ```powershell
   ipconfig /all   # Windows
   ```
   DNS server should be `192.168.0.1` (the router LAN IP).

### Symptom: tunnel flaps up/down every 20-30 seconds

**Seen in logs as:**
```text
Interface 'wgclient1' is now down
vpn-failover-trigger: action=schedule iface=wgclient1 source=hotplug reason=ifdown
interface wgclient1 recovered after 6s, aborting tunnel-switch
```

**Likely cause:** GL.iNet's `vpn-failover` / `tunnel-switch.sh` watchdog decides the tunnel is down and restarts it. The tunnel reconnects quickly, but the cycle repeats.

**Fixes:**
1. In the web UI, find the WG profile and disable **Kill Switch** / **Auto Reconnect** / **VPN Failover** if available.
2. Set `PersistentKeepalive = 15` (or lower) in the WG profile so NAT does not drop the UDP session.
3. Check MTU. Try `MTU = 1380` in the WG client config.
4. If nothing helps, switch to Global Proxy; some firmware builds handle Global Proxy more stably than Policy mode.

## Coexistence with Xray / v2rayA

GL.iNet can run WireGuard Client and v2rayA/Xray at the same time, but they fight over:
- firewall rules,
- routing table 1001,
- DNS forwarding,
- `0x8000`/`0xf000` fwmark rules.

**Recommendation:** use only one tunneling solution at a time on the router.

- If you want **domain-based split tunneling** with minimal setup → use **v2rayA** with a VLESS/VMess subscription.
- If you want **your own VPS and simple global VPN** → use **WireGuard Global Proxy**.
- If you want **your own VPS + domain split tunneling** → WireGuard Policy mode is possible, but less mature than v2rayA; be ready to debug flapping and DNS.

To disable v2rayA/Xray temporarily:
```bash
/etc/init.d/v2raya stop
/etc/init.d/v2raya disable
killall xray 2>/dev/null
killall v2ray 2>/dev/null
```

Configs remain in `/etc/v2raya/` and `/etc/xray/`. To re-enable:
```bash
/etc/init.d/v2raya enable
/etc/init.d/v2raya start
```

## WireGuard server setup on the VPS

A GL.iNet WireGuard profile is only the **client**. Many VPS templates marketed as "with WireGuard" do not actually start the server. Verify on the VPS before blaming the router:

```bash
wg show
ls -la /etc/wireguard/
systemctl status wg-quick@wg0
```

If nothing is running, create `/etc/wireguard/wg0.conf`:

```ini
[Interface]
Address = 10.99.99.1/24
ListenPort = 51820
PrivateKey = <server-private-key>
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o <main-interface> -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o <main-interface> -j MASQUERADE

[Peer]
PublicKey = <router-public-key>
PresharedKey = <preshared-key>
AllowedIPs = 10.99.99.2/32
PersistentKeepalive = 15
```

Then enable and start:
```bash
sysctl -w net.ipv4.ip_forward=1
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0
wg show
```

### Pitfall: Linux 7.x HWE kernel breaks WireGuard socket creation

On Ubuntu 24.04 with HWE kernel `7.0.0-28-generic`, `wg-quick up` may fail with:

```text
wireguard: wg0: Could not create IPv4 socket
RTNETLINK answers: Address already in use
```

Symptoms:
- `wg-quick up wg0` exits after `ip link set mtu 1420 up dev wg0`.
- `dmesg` shows `wireguard: wg0: Could not create IPv4 socket`.
- The error repeats with any interface name (`wg1`, `wg2`) and any subnet.

This is a kernel-level regression, not a config conflict. The stable kernel `6.8.0-124-generic` works correctly. Switch the default kernel and reboot:

```bash
GRUB_DEFAULT="Advanced options for Ubuntu>Ubuntu, with Linux 6.8.0-124-generic"
sed -i "s|^GRUB_DEFAULT=.*|GRUB_DEFAULT=\"$GRUB_DEFAULT\"|" /etc/default/grub
update-grub
reboot
```

After reboot confirm with `uname -r` and then start WireGuard:

```bash
systemctl start wg-quick@wg0
```

Note: the VPS may keep booting into `7.0.0-28` until `GRUB_DEFAULT` is changed; simply installing `linux-image-6.8.0-124-generic` is not enough if it is not the default.

## Where the GL.iNet config actually lives

The web UI writes into UCI files. Knowing them lets you fix things from SSH when the UI is slow or confusing.

| File / UCI path | What it controls |
|---|---|
| `/etc/config/wireguard` | WireGuard peer list. Each `config peers 'peer_<N>'` contains name, endpoint, keys, allowed IPs, DNS, persistent keepalive. |
| `/etc/config/network` | `config interface 'wgclient1'` — the WireGuard interface, routing table (`1001`), and policy rules. |
| `/etc/config/route_policy` | The high-level policy engine: which tunnel, which ipset, killswitch, mark value (`0x1000`). |
| `/etc/domain_mac_list/dst_net<tid>` | The domain list for a specific tunnel. One domain per line. |
| `/tmp/dnsmasq.d/via_domain` | dnsmasq rules that tell dnsmasq to add resolved IPs of listed domains into the nftables set. |

To update the domain list from SSH:

```bash
mkdir -p /etc/domain_mac_list
cat > /etc/domain_mac_list/dst_net4803 <<'EOF'
gemini.google.com
google.com
googleapis.com
gstatic.com
googleusercontent.com
github.com
api.github.com
raw.githubusercontent.com
fonts.googleapis.com
fonts.gstatic.com
EOF

/etc/init.d/network reload
/etc/init.d/firewall reload
/etc/init.d/dnsmasq restart
```

Then trigger DNS resolution so dnsmasq populates the nftables set:

```bash
nslookup gemini.google.com 127.0.0.1
nslookup github.com 127.0.0.1
sleep 2
nft list set inet fw4 dst_net4803   # or inet vpn_table dst_net4803, depending on firmware build
```

## Verifying policy routing is actually working

### Check the nftables set has IPs

```bash
nft list set inet fw4 dst_net4803 2>/dev/null || nft list set inet vpn_table dst_net4803 2>/dev/null
```

You should see Google/GitHub IPs in the set. If the set is empty, dnsmasq did not pick up the domain list (restart dnsmasq, check `/tmp/dnsmasq.d/via_domain`).

### Check mark/routing rules exist

```bash
nft list ruleset | grep -A5 "TUNNEL4803_ROUTE_POLICY"
```

You should see rules like:

```text
ip daddr @dst_net4803 meta mark set meta mark & 0xffff1fff | 0x00001000
```

### Important: `ip route get` from the router itself may still show WAN

```bash
ip route get 142.251.150.2
# -> 142.251.150.2 via 130.255.9.1 dev eth1
```

This is **normal**. The policy rules in `TUNNEL4803_ROUTE_POLICY` are placed in the forward/postrouting path for packets coming **from LAN clients**, not for locally-generated router traffic. To test, use a LAN device or run `tcpdump` on `wgclient1` while a PC accesses Gemini:

```bash
tcpdump -i wgclient1 -n host 142.251.150.2
```

If you see packets, the tunnel is being used.

### Check a LAN PC actually routes Gemini through the tunnel

From a Windows PC:

```powershell
# Must use curl.exe, not PowerShell alias
ipconfig /flushdns
nslookup gemini.google.com
curl.exe -s https://ipinfo.io/ip
curl.exe -sI https://gemini.google.com/?hl=ru
```

If `ipinfo.io/ip` returns your WAN IP but Gemini works, policy routing is functioning.

## Diagnostics checklist

Run from the router SSH:

```bash
# WG state
wg show wgclient1

# Routing tables
ip route show table all | grep wgclient1
ip route show table 1001
ip rule show

# DNS resolution
nslookup gemini.google.com 127.0.0.1
nslookup gemini.google.com 192.168.0.1

# Interface and MTU
ip link show wgclient1

# Recent WG / failover logs
logread | grep -E 'wgclient1|vpn-failover|tunnel-switch' | tail -60

# Policy engine files
cat /etc/domain_mac_list/dst_net4803
grep dst_net4803 /tmp/dnsmasq.d/via_domain 2>/dev/null
nft list set inet fw4 dst_net4803 2>/dev/null | head -10
```

From a LAN PC:

```powershell
# Windows example
nslookup gemini.google.com
ipconfig /all | findstr DNS
ping 8.8.8.8
curl.exe -sI https://gemini.google.com/?hl=ru
```

## Bottom line

- Policy mode on GL.iNet is convenient but relies on DNS-based routing injection.
- DNS must be visible to the router; disable DoH/DoT on clients.
- The router config lives in `/etc/config/wireguard`, `/etc/config/network`, `/etc/config/route_policy`, and `/etc/domain_mac_list/`.
- Verify policy with nftables sets and `tcpdump` on `wgclient1`, not with `ip route get` from the router.
- If DNS or tunnel flapping makes Policy mode unusable, switch to **Global Proxy**.
- Keep v2rayA/Xray stopped while testing WireGuard to avoid rule conflicts.
