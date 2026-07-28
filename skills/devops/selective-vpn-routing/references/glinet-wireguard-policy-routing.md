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

### Symptom: policy list domains resolve, nft set is populated, but LAN traffic still leaves through WAN

**Likely cause:** GL.iNet policy engine has loaded both the primary VPN rule (`mark 0x1000`) and a failover rule (`mark 0x8000`) into `TUNNEL<tid>_ROUTE_POLICY`. nftables evaluates every matching rule, so the later `0x8000` rule overwrites the `0x1000` mark and traffic falls back to the WAN table. This happens when the default "last sort default policy" (`route_policy.@default[0]`) is enabled and the failover path gets appended after the primary VPN rule.

**Verification:**
```bash
tunnel_id=$(uci get route_policy.@rule[0].tunnel_id)
nft list chain inet vpn_table TUNNEL${tunnel_id}_ROUTE_POLICY
```
If you see both:
```text
ip daddr @dst_net<tid> meta mark set meta mark & 0xffff1fff | 0x00001000
ip daddr @dst_net<tid> meta mark set meta mark & 0xffff8fff | 0x00008000
```
then the second rule always wins and the domain is routed via WAN.

**Fix options (choose one):**

1. **Enable killswitch on the tunnel rule (preferred for leak protection).** When `killswitch='1'`, current GL.iNet builds skip the failover `0x8000` rules and keep only `0x1000` + drop rules, so domain routing works as intended:
   ```bash
   uci set route_policy.@rule[0].killswitch='1'
   uci commit route_policy
   /etc/init.d/vpn-client restart
   ```

2. **Disable the global default failover policy.** Only do this if you want listed domains to fall back to WAN when WG is down:
   ```bash
   uci set route_policy.@default[0].enabled='0'
   uci commit route_policy
   /etc/init.d/vpn-client restart
   ```

After either change, re-check the chain. It should contain only the `0x1000` rules followed by `drop` rules, with no `0x8000` rules for the same sets.

**Caution:** changing routing policy can briefly interrupt traffic. When connected remotely through the router, apply changes carefully; prefer the web UI or prepare an out-of-band management path.

### Symptom: `curl --interface wgclient1` works, but `ping -I wgclient1` loses packets

**Likely causes:**
- The VPS or the target host filters ICMP.
- MTU mismatch: WG uses `mtu 1420`; some networks drop fragments. Try lowering WG MTU to 1380 on both sides.
- The router's own ICMP packets are not marked by policy rules (policy applies to forwarded LAN traffic, not locally generated traffic).

**Fix/verify:**
1. Trust `curl`/`tcpdump` more than `ping` for WG connectivity. ICMP loss alone does not mean the tunnel is broken.
2. Lower MTU if TCP sites also fail:
   ```bash
   uci set network.wgclient1.mtu='1380'
   uci commit network
   ifdown wgclient1; ifup wgclient1
   ```

### Symptom: domain-based routing works briefly, then stops after some time

**Likely cause:** hardware/software flow offloading (`flags offload` in fw4) can bypass nftables policy chains or fail to copy conntrack marks correctly on some firmware builds. This manifests as nft sets being populated but LAN traffic no longer entering `wgclient1`.

**Fix:**
1. Check offloading state:
   ```bash
   uci show firewall | grep -i offload
   nft list ruleset | grep -i offload
   ```
2. Disable hardware and software flow offloading, then reload firewall:
   ```bash
   uci set firewall.@defaults[0].flow_offloading='0'
   uci set firewall.@defaults[0].flow_offloading_hw='0'
   uci commit firewall
   /etc/init.d/firewall reload
   ```
3. Re-test from a LAN client (not the router).

### Symptom: after a router reset / firmware restore, WireGuard policy routing no longer works even though the profile "looks the same"

**Likely cause:** GL.iNet renumbers tunnel and group identifiers after a reset. The UCI objects change:

| Before reset | After reset (example) |
|---|---|
| `wireguard.group_4491` | `wireguard.group_2676` |
| `wireguard.peer_2001` | still `peer_2001` (peer id is usually preserved) |
| `route_policy` tunnel_id `9192` | `328` |
| domain list `/etc/domain_mac_list/dst_net9192` | `/etc/domain_mac_list/dst_net328` |
| nftables chain `TUNNEL9192_ROUTE_POLICY` | `TUNNEL328_ROUTE_POLICY` |

The tunnel itself may come up with the same keys and endpoint, but the policy engine, domain list, and nftables sets are rebuilt with new IDs. The domain list is often reset to a single default entry (e.g. `2ip.ru`).

**Fix:**
1. Re-add the domain list through the web UI (VPN → WireGuard Client → Policy), or write it directly to the new path:
   ```bash
   tunnel_id=$(uci get route_policy.@rule[0].tunnel_id)
   cat > /etc/domain_mac_list/dst_net${tunnel_id} <<'EOF'
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
   /etc/init.d/dnsmasq restart
   /etc/init.d/vpn-client restart
   ```
2. Re-verify `AllowedIPs`:
   ```bash
   uci set wireguard.peer_2001.allowed_ips='0.0.0.0/0,::/0'
   uci commit wireguard
   ifdown wgclient1; ifup wgclient1
   ```
3. Re-enable killswitch if you want leak protection:
   ```bash
   uci set route_policy.@rule[0].killswitch='1'
   uci commit route_policy
   /etc/init.d/vpn-client restart
   ```
4. Verify the new chain and set:
   ```bash
   nft list chain inet vpn_table TUNNEL${tunnel_id}_ROUTE_POLICY
   nft list set inet vpn_table dst_net${tunnel_id}
   ```

### Symptom: `AllowedIPs` in `/etc/config/wireguard` is narrowed to the endpoint IP only

**Likely cause:** GL.iNet UI or import logic rewrote the peer's `allowed_ips` to the endpoint server's `/32` address instead of `0.0.0.0/0`. Handshake may still succeed, but the peer is not authorized to carry any destination, so table 1001 cannot forward anything through `wgclient1`.

**Fix:**
```bash
uci set wireguard.peer_2001.allowed_ips='0.0.0.0/0,::/0'
uci commit wireguard
ifdown wgclient1
ifup wgclient1
wg show wgclient1 | grep 'allowed ips'
```

**Tip:** after a router reset the peer id (`peer_2001`) is usually preserved, but group/tunnel IDs change. Verify `allowed_ips` after any reset or re-import.

### Safety note: apply routing changes carefully when connected through the router

If your SSH/web session to the router itself travels through the router (for example, you are on a LAN PC managing `192.168.0.1`), a broken routing or firewall change can cut your access. For policy/failover changes:

1. Prefer the GL.iNet web UI, which validates combinations.
2. If using SSH/UCI, change one setting at a time and verify `wg show wgclient1`, `ip route`, and basic internet before the next change.
3. Avoid disabling the global default failover policy and changing firewall offloading in the same command. If the policy engine reloads incorrectly, the router may briefly send all traffic to `blackhole` or lose the default gateway.
4. Keep an out-of-band path (mobile hotspot, direct cable to a different WAN port, or the router's physical reset button) when experimenting with routing.
5. `/etc/init.d/vpn-client restart` and `/etc/init.d/firewall reload` can both interrupt forwarding for a few seconds. Do not chain them blindly.

### Symptom: tunnel flaps up/down every 20-30 seconds

**Seen in logs as:**
```text
Interface 'wgclient1' is now down
vpn-failover-trigger: action=schedule iface=wgclient1 source=hotplug reason=ifdown
interface wgclient1 recovered after 6s, aborting tunnel-switch
```

**Likely cause:** GL.iNet's `vpn-failover` / `tunnel-switch.sh` watchdog decides the tunnel is down and restarts it. The tunnel reconnects quickly, but the cycle repeats. This can be triggered by:
- The watchdog itself misdetecting state.
- A firewall reload that indirectly bounces `wgclient1`.
- MTU/DNS issues that make health probes fail.

**Fixes (apply one at a time and verify):**
1. Check that the VPS/server side actually forwards traffic (see `references/wg-easy-docker-host-forwarding.md` if using wg-easy). If the tunnel has handshake but no forwarding, the router watchdog may treat it as down.
2. In the web UI, find the WG profile and disable **Kill Switch** / **Auto Reconnect** / **VPN Failover** if available.
3. Set `PersistentKeepalive = 15` (or lower) in the WG profile so NAT does not drop the UDP session.
4. Check MTU. Try `MTU = 1380` in the WG client config:
   ```bash
   uci set network.wgclient1.mtu='1380'
   uci commit network
   ifdown wgclient1; ifup wgclient1
   ```
5. Avoid chaining `/etc/init.d/vpn-client restart` and `/etc/init.d/firewall reload`. Each reload can briefly interrupt forwarding and may trigger the watchdog. Wait for `wgclient1` to settle before reloading firewall.
6. If nothing helps, switch to Global Proxy; some firmware builds handle Global Proxy more stably than Policy mode.

### Symptom: after disabling firewall flow offloading, `wgclient1` starts flapping

**Likely cause:** `/etc/init.d/firewall reload` re-applies all fw4 rules and can cause `netifd`/`tunnel-switch` to re-evaluate the WG interface. If the tunnel was already marginal, the extra reload pushes it into a restart loop.

**Fix/avoidance:**
1. Do not change flow offloading and VPN policy in the same command.
2. If you must disable offloading, stop tunnel monitoring first or use the web UI (which handles ordering better).
3. To recover from a flap loop:
   ```bash
   /etc/init.d/vpn-client restart
   sleep 10
   wg show wgclient1
   logread | grep -E 'wgclient1|vpn-failover|tunnel-switch' | tail -30
   ```
4. If the loop persists, disable failover monitoring in the web UI or set a longer health-check interval.

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

A GL.iNet WireGuard profile is only the **client**. Many VPS templates marketed as "with WireGuard" start a containerized server (e.g. `wg-easy`) but do not configure the **host** to forward traffic from that container to the public interface.

### Classic native server

Verify on the VPS before blaming the router:

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

### Docker / wg-easy server

Many one-click VPS panels install `wg-easy` as a Docker container. The container itself usually has NAT:
```text
MASQUERADE  all  --  *      eth0    192.168.101.0/24     0.0.0.0/0
```
But the **host** must still forward packets from the Docker bridge to the public interface. The default `FORWARD` policy is often `DROP`, and Docker only adds rules for its own bridge subnets (`172.17.0.0/16`, `172.18.0.0/16`), not for the WG client subnet (`192.168.101.0/24`) which is already NAT-ed inside the container.

**Symptom:** WG handshake works, `curl --interface wgclient1` or ping from the router succeeds for some packets but most traffic is lost, and LAN clients cannot load sites through the tunnel.

**Diagnosis on the VPS host:**
```bash
docker ps | grep wg-easy
docker exec wg-easy iptables -t nat -L POSTROUTING -v -n
docker network inspect <wg-easy-network> | grep -E '"Gateway"|"IPAddress"'
ip route show default
iptables -L FORWARD -v -n | head -10
```

**Fix on the VPS host (runtime):**
```bash
pub_if=$(ip route show default | awk '{print $5}')
br_if=$(docker network inspect <wg-easy-network> -f '{{range .IPAM.Config}}{{.Subnet}}{{end}}' | xargs -r ip route show | awk '{print $3}')
# Usually br_if is 'br-<network-id>' or 'br-fcbf081c5780'
iptables -A FORWARD -i "$br_if" -o "$pub_if" -j ACCEPT
iptables -A FORWARD -i "$pub_if" -o "$br_if" -m state --state RELATED,ESTABLISHED -j ACCEPT
```

Replace `<wg-easy-network>` with the actual network name (often `docker-app_default`). You can find it with:
```bash
docker network ls
docker inspect wg-easy --format='{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}'
```

**Make it persistent:**
Runtime iptables rules disappear after reboot. Add them to `iptables-persistent` or to a `PostUp`/`PostDown` wrapper. Since `wg-easy` is a container, the cleanest persistent path is a small host-side script started by systemd:

```bash
cat > /usr/local/bin/wg-easy-forward.sh <<'EOF'
#!/bin/bash
PUB_IF=$(ip route show default | awk '{print $5}')
BR_IF=$(docker inspect wg-easy --format='{{range $k,$v := .NetworkSettings.Networks}}{{printf "%s\n" $k}}{{end}}' | head -1)
BR_IF="br-$(docker network ls --filter name="${BR_IF}" --format '{{.ID}}')"
[ -d /sys/class/net/${BR_IF} ] || BR_IF=$(docker network inspect "${BR_IF#br-}" -f '{{.Id}}' | head -c 12 | sed 's/^/br-/')
iptables -C FORWARD -i "$BR_IF" -o "$PUB_IF" -j ACCEPT 2>/dev/null || iptables -A FORWARD -i "$BR_IF" -o "$PUB_IF" -j ACCEPT
iptables -C FORWARD -i "$PUB_IF" -o "$BR_IF" -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null || \
  iptables -A FORWARD -i "$PUB_IF" -o "$BR_IF" -m state --state RELATED,ESTABLISHED -j ACCEPT
EOF
chmod +x /usr/local/bin/wg-easy-forward.sh

cat > /etc/systemd/system/wg-easy-forward.service <<'EOF'
[Unit]
Description=Forward wg-easy container traffic to public interface
After=docker.service
Wants=docker.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/wg-easy-forward.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable wg-easy-forward.service
systemctl start wg-easy-forward.service
```

**Verify from the VPS host:**
```bash
# from the router / LAN side
ping -c 5 -I wgclient1 8.8.8.8
# or from the VPS container
docker exec wg-easy ping -c 3 8.8.8.8
```

If `docker exec wg-easy ping 8.8.8.8` works but the router's `ping -I wgclient1 8.8.8.8` does not, the problem is on the host forward path, not inside the container.

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
| `/etc/domain_mac_list/dst_net<tid>` | The domain list for a specific tunnel. `<tid>` is `route_policy.@rule[0].tunnel_id`. |
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
tunnel_id=$(uci get route_policy.@rule[0].tunnel_id)
nft list set inet fw4 dst_net${tunnel_id} 2>/dev/null || nft list set inet vpn_table dst_net${tunnel_id} 2>/dev/null
```

You should see resolved IPs of listed domains in the set. If the set is empty, dnsmasq did not pick up the domain list (restart dnsmasq, check `/tmp/dnsmasq.d/via_domain`).

### Check mark/routing rules exist

```bash
nft list ruleset | grep -A5 "TUNNEL${tunnel_id}_ROUTE_POLICY"
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

This is **normal**. The policy rules in `TUNNEL<tid>_ROUTE_POLICY` are placed in the forward/postrouting path for packets coming **from LAN clients**, not for locally-generated router traffic. To test, use a LAN device or run `tcpdump` on `wgclient1` while a PC accesses Gemini:

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

### Validate mark logic with `ip route get`

From the router, you can simulate the marked path that a LAN packet would take:

```bash
ip route get 8.47.69.0 mark 0x1000
# -> 8.47.69.0 dev wgclient1 table 1001 src 192.168.101.2 mark 0x1000

ip route get 8.47.69.0 from 192.168.0.176 iif br-lan mark 0x1000
# -> 8.47.69.0 from 192.168.0.176 dev wgclient1 table 1001 mark 0x1000
```

If this returns `wgclient1`, the routing tables are correct. Then the only remaining question is whether nftables is actually setting `0x1000` for LAN traffic (see `TUNNEL<tid>_ROUTE_POLICY` chain check above).

## Diagnostics checklist

Run from the router SSH:

```bash
tunnel_id=$(uci get route_policy.@rule[0].tunnel_id)

# WG state
wg show wgclient1

# AllowedIPs
uci show wireguard.peer_2001.allowed_ips

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
cat /etc/domain_mac_list/dst_net${tunnel_id}
grep dst_net${tunnel_id} /tmp/dnsmasq.d/via_domain 2>/dev/null
nft list set inet vpn_table dst_net${tunnel_id} 2>/dev/null | head -10
nft list chain inet vpn_table TUNNEL${tunnel_id}_ROUTE_POLICY 2>/dev/null

# Flow offloading (can break mark propagation)
uci show firewall | grep -i offload
nft list ruleset | grep -i offload | head -5

# Test marked routing path
ip route get 8.47.69.0 mark 0x1000
ip route get 8.47.69.0 from 192.168.0.176 iif br-lan mark 0x1000
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
- When the VPS runs `wg-easy` in Docker, the host must forward traffic from the Docker bridge to the public interface — see `references/wg-easy-docker-host-forwarding.md`.
