#!/bin/sh
# Roll back Xray + manual TPROXY on a GL.iNet / OpenWrt router.
# Run via SSH as root. Reboot if SSH is unavailable.

set -e

/etc/init.d/xray stop 2>/dev/null || true
/etc/init.d/xray disable 2>/dev/null || true
/etc/init.d/v2raya stop 2>/dev/null || true
/etc/init.d/v2raya disable 2>/dev/null || true

uci set xray.enabled.enabled=0 2>/dev/null || true
uci commit xray 2>/dev/null || true
uci set v2raya.config.enabled=0 2>/dev/null || true
uci commit v2raya 2>/dev/null || true

# nat
iptables -t nat -D PREROUTING -j XRAY_TCP 2>/dev/null || true
iptables -t nat -D OUTPUT -j XRAY_TCP_OUTPUT 2>/dev/null || true
iptables -t nat -F XRAY_TCP 2>/dev/null || true
iptables -t nat -F XRAY_TCP_OUTPUT 2>/dev/null || true
iptables -t nat -X XRAY_TCP 2>/dev/null || true
iptables -t nat -X XRAY_TCP_OUTPUT 2>/dev/null || true

# mangle
iptables -t mangle -D PREROUTING -j XRAY 2>/dev/null || true
iptables -t mangle -D OUTPUT -j XRAY_MASK 2>/dev/null || true
iptables -t mangle -F XRAY 2>/dev/null || true
iptables -t mangle -F XRAY_MASK 2>/dev/null || true
iptables -t mangle -X XRAY 2>/dev/null || true
iptables -t mangle -X XRAY_MASK 2>/dev/null || true

# shadowsocks leftover
iptables -t mangle -D PREROUTING -j ss_rules_pre_src 2>/dev/null || true
iptables -t mangle -F ss_rules_pre_src 2>/dev/null || true
iptables -t mangle -F ss_rules_src 2>/dev/null || true
iptables -t mangle -F ss_rules_dst 2>/dev/null || true
iptables -t mangle -F ss_rules_forward 2>/dev/null || true
iptables -t mangle -X ss_rules_pre_src 2>/dev/null || true
iptables -t mangle -X ss_rules_src 2>/dev/null || true
iptables -t mangle -X ss_rules_dst 2>/dev/null || true
iptables -t mangle -X ss_rules_forward 2>/dev/null || true

ip rule del fwmark 1 table 100 2>/dev/null || true
ip route del local 0.0.0.0/0 dev lo table 100 2>/dev/null || true

# restore dnsmasq upstream
uci -q delete dhcp.@dnsmasq[0].server 2>/dev/null || true
uci -q delete dhcp.@dnsmasq[0].noresolv 2>/dev/null || true
uci -q delete dhcp.lan.dhcp_option 2>/dev/null || true
uci commit dhcp 2>/dev/null || true
/etc/init.d/dnsmasq restart 2>/dev/null || true

/etc/init.d/rpcd restart 2>/dev/null || true
/etc/init.d/uhttpd restart 2>/dev/null || true
/etc/init.d/nginx restart 2>/dev/null || true

echo "Xray/TPROXY/v2rayA rollback complete."
