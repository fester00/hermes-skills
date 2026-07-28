# wg-easy host forwarding via iptables-persistent

When `wg-easy` runs in Docker on a fresh Ubuntu VPS, the container itself usually has NAT:

```text
MASQUERADE  all  --  *      eth0    192.168.101.0/24     0.0.0.0/0
```

But the **host** default `FORWARD` policy is `DROP`, and Docker only installs rules for its own bridge subnets (`172.17.0.0/16`, `172.18.0.0/0`). The WG client subnet (`192.168.101.0/24`) is already NAT-ed inside the container, but the host must still forward packets from the Docker bridge to the public interface.

Symptom: WG handshake works, `wg show` shows `latest handshake`, but clients can barely reach the internet through the tunnel (ICMP loss, TCP timeouts, sites do not load).

## Quick persistent fix

1. SSH to the VPS as root.
2. Discover the public interface and the Docker bridge for the `wg-easy` container:

```bash
PUB_IF=$(ip route show default | awk '{print $5}')
DOCKER_NET=$(docker inspect wg-easy --format='{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}')
BR_IF="br-$(docker network ls --filter name="${DOCKER_NET}" --format '{{.ID}}')"
echo "PUB_IF=${PUB_IF}  BR_IF=${BR_IF}"
```

3. Install `iptables-persistent` and add the forward rules:

```bash
DEBIAN_FRONTEND=noninteractive apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y iptables-persistent
iptables -A FORWARD -i "${BR_IF}" -o "${PUB_IF}" -j ACCEPT
iptables -A FORWARD -i "${PUB_IF}" -o "${BR_IF}" -m state --state RELATED,ESTABLISHED -j ACCEPT
netfilter-persistent save
```

4. Verify from the router:

```bash
ping -c 5 -I wgclient1 8.8.8.8
curl -s --interface wgclient1 https://api.ipify.org
```

Both should work. ICMP may still be filtered by some targets, so trust TCP/HTTP more than ping.

## Why not just a systemd script?

The systemd approach in the main skill works too, but `iptables-persistent` is simpler because:
- It saves/restores the full IPv4/IPv6 ruleset at boot.
- It integrates with standard Debian/Ubuntu firewall management.
- It survives Docker restarts as long as the bridge name stays the same.

If the `wg-easy` Docker network is ever recreated and the bridge ID changes, update `BR_IF` and re-run the three `iptables`/`netfilter-persistent save` commands.

## Verify rules after reboot

```bash
iptables -L FORWARD -v -n | grep -E "br-.*ens"
```

You should see counters increasing when WG clients send traffic.

## One-liner script

For reuse, save this as `/usr/local/bin/wg-easy-forward.sh`:

```bash
#!/bin/bash
set -e
PUB_IF=$(ip route show default | awk '{print $5}')
DOCKER_NET=$(docker inspect wg-easy --format='{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}')
BR_IF="br-$(docker network ls --filter name="${DOCKER_NET}" --format '{{.ID}}')"
iptables -C FORWARD -i "$BR_IF" -o "$PUB_IF" -j ACCEPT 2>/dev/null || \
  iptables -A FORWARD -i "$BR_IF" -o "$PUB_IF" -j ACCEPT
iptables -C FORWARD -i "$PUB_IF" -o "$BR_IF" -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null || \
  iptables -A FORWARD -i "$PUB_IF" -o "$BR_IF" -m state --state RELATED,ESTABLISHED -j ACCEPT
netfilter-persistent save
```

Then run it after any Docker network change.
