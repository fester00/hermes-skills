# wg-easy Docker host forwarding

Quick reference for the common case where a VPS panel installs WireGuard as a `wg-easy` Docker container but traffic from WG clients does not reach the internet.

## Symptom

- WG handshake from the router works.
- `wg show wgclient1` shows `latest handshake` < 30s.
- `ping -I wgclient1 8.8.8.8` or `curl --interface wgclient1` mostly fails.
- LAN clients cannot load sites through the tunnel.

## Root cause

`wg-easy` runs inside Docker. The container NATs the WG client subnet (`192.168.101.0/24`) to its own container IP (`172.18.0.2`), but the **host** must then forward packets from the Docker bridge to the public interface. The default host `FORWARD` policy is `DROP`, and Docker only auto-adds rules for its own bridge subnets, not for the already-NATed WG traffic.

## One-liner diagnosis

```bash
# On the VPS host
PUB_IF=$(ip route show default | awk '{print $5}')
WG_NET=$(docker network inspect $(docker inspect wg-easy --format='{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}') -f '{{range .IPAM.Config}}{{.Subnet}}{{end}}')
echo "Public interface: $PUB_IF"
echo "wg-easy network: $WG_NET"
iptables -L FORWARD -v -n | head -10
docker exec wg-easy iptables -t nat -L POSTROUTING -v -n
```

If `MASQUERADE` exists inside the container but no `ACCEPT` rule routes `br-*` → `$PUB_IF`, this is the problem.

## Runtime fix

```bash
PUB_IF=$(ip route show default | awk '{print $5}')
NET_NAME=$(docker inspect wg-easy --format='{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}')
NET_ID=$(docker network ls --filter name="^${NET_NAME}$" --format '{{.Id}}')
BR_IF="br-${NET_ID:0:12}"
[ -d /sys/class/net/${BR_IF} ] || BR_IF=$(ip -o link show | grep -E "master br-|@${NET_ID:0:12}" | head -1 | awk -F': ' '{print $2}' | cut -d'@' -f1)

iptables -A FORWARD -i "$BR_IF" -o "$PUB_IF" -j ACCEPT
iptables -A FORWARD -i "$PUB_IF" -o "$BR_IF" -m state --state RELATED,ESTABLISHED -j ACCEPT
```

## Persistent fix (systemd)

```bash
cat > /usr/local/bin/wg-easy-forward.sh <<'EOF'
#!/bin/bash
set -e
PUB_IF=$(ip route show default | awk '{print $5}')
NET_NAME=$(docker inspect wg-easy --format='{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}')
NET_ID=$(docker network ls --filter name="^${NET_NAME}$" --format '{{.Id}}')
BR_IF="br-${NET_ID:0:12}"
[ -d /sys/class/net/${BR_IF} ] || BR_IF=$(ip -o link show | grep -E "master br-|@${NET_ID:0:12}" | head -1 | awk -F': ' '{print $2}' | cut -d'@' -f1)
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

## Verification

```bash
# From the router
ping -c 5 -I wgclient1 8.8.8.8
curl -s --interface wgclient1 https://api.ipify.org

# From a LAN PC
nslookup 2ip.ru
curl -s https://2ip.ru
```

## Note on ICMP loss

Ping may still drop packets even after forwarding works because some hosts/VPS filters filter ICMP or because of MTU. Trust `curl`/HTTP more than `ping` for tunnel connectivity.

## Note on MTU

If HTTP sites partially load or TLS hangs, try lowering MTU on the router WG client to 1380 and on the `wg-easy` peer config if possible.
