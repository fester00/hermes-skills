#!/bin/bash
# Fix wg-easy Docker host forwarding on Ubuntu/Debian VPS.
# wg-easy NATs WG clients inside the container, but the host must forward
# from the Docker bridge to the public interface. This script adds and
# persists the required FORWARD rules.
#
# Usage: sudo /usr/local/bin/wg-easy-forward.sh
# Persistent: enabled as systemd service wg-easy-forward.service

set -e

PUB_IF=$(ip route show default | awk '{print $5}')
[ -z "$PUB_IF" ] && { echo "No default route found"; exit 1; }

NET_NAME=$(docker inspect wg-easy --format='{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}')
[ -z "$NET_NAME" ] && { echo "wg-easy container not found"; exit 1; }

NET_ID=$(docker network ls --filter name="^${NET_NAME}$" --format '{{.Id}}')
BR_IF="br-${NET_ID:0:12}"
[ -d "/sys/class/net/${BR_IF}" ] || {
    # fallback: find bridge interface by network id
    BR_IF=$(ip -o link show | grep -E "master br-|@${NET_ID:0:12}" | head -1 | awk -F': ' '{print $2}' | cut -d'@' -f1 | tr -d ' ')
}
[ -d "/sys/class/net/${BR_IF}" ] || { echo "Bridge interface not found"; exit 1; }

add_rule() {
    iptables -C FORWARD "$@" 2>/dev/null || iptables -A FORWARD "$@"
}

add_rule -i "$BR_IF" -o "$PUB_IF" -j ACCEPT
add_rule -i "$PUB_IF" -o "$BR_IF" -m state --state RELATED,ESTABLISHED -j ACCEPT

echo "FORWARD rules added: ${BR_IF} <-> ${PUB_IF}"
