#!/usr/bin/env python3
"""LAN sweep with stdlib only: ICMP sweep + ARP + reverse DNS + port probe.

No nmap/arp-scan/fping required. Works on a consumer /24.

Usage:
    python3 lan_scan.py                 # auto-detect the local subnet
    python3 lan_scan.py 192.168.1.0/24  # explicit subnet

Output: alive hosts, ARP state, rDNS hostname (highest-value identifier —
consumer gear publishes its model there), and open ports from COMMON_PORTS.
Devices that do not answer ICMP still appear in the ARP/rDNS sections.
"""
import ipaddress
import json
import re
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

COMMON_PORTS = [22, 53, 80, 443, 554, 1961, 3000, 5000, 7000, 8008, 8009,
                8080, 8081, 8443, 9000, 10001, 18789, 32400]


def local_subnet():
    """Return the /24 of the interface that owns the default route."""
    try:
        route = subprocess.run(["ip", "route", "get", "1.1.1.1"],
                                capture_output=True, text=True).stdout
        m = re.search(r"src (\d+\.\d+\.\d+\.\d+)", route)
        if m:
            ip = ipaddress.ip_address(m.group(1))
            return str(ipaddress.ip_network(f"{ip}/24", strict=False))
    except Exception:
        pass

    out = subprocess.run(["ip", "-brief", "addr!"], capture_output=True, text=True).stdout
    for line in out.splitlines():
        m = re.search(r"inet (\d+\.\d+\.\d+\.\d+/\d+)", line)
        if m and not m.group(1).startswith("127."):
            return str(ipaddress.ip_interface(m.group(1)).network)
    raise SystemExit("could not determine local subnet — pass one explicitly")


def ping(ip):
    try:
        r = subprocess.run(["ping", "-c", "1", "-W", "1", "-n", ip],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=3)
        return ip, r.returncode == 0
    except Exception:
        return ip, False


def rdns(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return ""


def probe(ip, ports):
    openp = []
    for p in sorted(set(ports)):
        s = socket.socket()
        s.settimeout(0.6)
        try:
            if s.connect_ex((ip, p)) == 0:
                openp.append(p)
        except Exception:
            pass
        finally:
            s.close()
    return ip, openp


def arp_table():
    """Return {ip: {mac, state}} for every ARP entry, placeholders included."""
    out = subprocess.run(["ip", "neigh"], capture_output=True, text=True).stdout
    tbl = {}
    for line in out.splitlines():
        m = re.match(r"^(\S+)\s+dev\s+(\S+)\s+lladdr\s+(\S+)\s+(\S+)", line)
        if m:
            tbl[m.group(1)] = {"mac": m.group(3).lower(), "state": m.group(4),
                               "dev": m.group(2)}
            continue
        m2 = re.match(r"^(\S+)\s+dev\s+(\S+)\s+(FAILED|INCOMPLETE)", line)
        if m2:
            tbl[m2.group(1)] = {"mac": "", "state": m2.group(3), "dev": m2.group(2)}
    return tbl


def key(ip):
    return int(ip.split(".")[-1])


def main():
    net = ipaddress.ip_network(sys.argv[1] if len(sys.argv) > 1 else local_subnet(),
                                strict=False)
    hosts = [str(h) for h in net.hosts()]
    print(f"### SWEEP {net} ({len(hosts)} hosts)")

    alive = []
    with ThreadPoolExecutor(max_workers=128) as ex:
        for ip, ok in ex.map(ping, hosts):
            if ok:
                alive.append(ip)
    print(f"ICMP-alive: {len(alive)}")
    for ip in sorted(alive, key=key):
        print("  ", ip)

    time.sleep(1)
    tbl = arp_table()
    real = {ip: v for ip, v in tbl.items() if v["mac"]}
    print(f"\n### ARP: {len(tbl)} entries raw, {len(real)} with a MAC (the real inventory)")

    # union: ICMP-alive hosts plus everything ARP actually resolved
    candidates = sorted(set(alive) | set(real), key=key)
    detail = {}
    for ip in candidates:
        detail[ip] = {"ip": ip,
                      "mac": tbl.get(ip, {}).get("mac", ""),
                      "icmp": ip in alive,
                      "rdns": rdns(ip),
                      "ports": []}

    with ThreadPoolExecutor(max_workers=64) as ex:
        for ip, openp in ex.map(lambda i: probe(i, COMMON_PORTS), candidates):
            detail[ip]["ports"] = openp

    print("\n### HOSTS")
    for ip in candidates:
        d = detail[ip]
        print(f"  {ip:15} mac={d['mac'] or '-':18} icmp={'y' if d['icmp'] else 'n'} "
              f"rns={d['rdns'] or '-':32} ports={d['ports']}")

    out = "/tmp/lan_scan.json"
    with open(out, "w") as f:
        json.dump(detail, f, ensure_ascii=False, indent=2)
    print(f"\nsaved -> {out}")
    print("next: python3 mdns_probe.py   # mDNS finds devices that ignore ICMP and ARP")


if __name__ == "__main__":
    main()
