#!/usr/bin/env python3
"""mDNS/DNS-SD probe with stdlib only — no avahi, no bonjour, no install.

Usage:
    python3 mdns_probe.py                              # list advertised service types
    python3 mdns_probe.py _yandexio._tcp.local        # broadcast query for one service type
    python3 mdns_probe.py _airplay._tcp.local --target 192.168.0.144   # unicast to one host
    python3 mdns_probe.py _http._tcp.local --timeout 6

Why: consumer devices (smart speakers especially) are often ICMP-silent and expose their
identity only via mDNS. A unicast query to a known IP returns that device's full record set.

Output is the union of two parsers: a structured walk (PTR / A / TXT) and a printable-run
fallback, so a reply is never silently swallowed by one parser's assumptions.
"""
import argparse
import re
import socket
import time

MDNS_ADDR = "224.0.0.251"
MDNS_PORT = 5353
SERVICE_ENUM = "_services._dns-sd._udp.local"


def encode_name(name):
    out = b""
    for part in name.split("."):
        if part:
            out += bytes([len(part)]) + part.encode()
    return out + b"\x00"


def make_query(name, qtype=12):
    """qtype 12 = PTR (service discovery), 16 = TXT."""
    return (b"\x12\x34\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00"
            + encode_name(name) + qtype.to_bytes(2, "big") + b"\x00\x01")


def query(name, target=None, timeout=4.0):
    """Broadcast (target=None) or unicast to one host. Returns [(src_ip, raw_bytes)]."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    s.settimeout(timeout)
    out = []
    try:
        s.sendto(make_query(name), (target or MDNS_ADDR, MDNS_PORT))
        t0 = time.time()
        while time.time() - t0 < timeout:
            try:
                data, addr = s.recvfrom(9000)
            except socket.timeout:
                break
            out.append((addr[0], data))
    finally:
        s.close()
    return out


def parse_structured(pkts):
    """Walk the answer section -> {ptr, a, txt}."""
    found = {"ptr": set(), "a": set(), "txt": set()}
    for _addr, data in pkts:
        i = 12
        try:
            qd = int.from_bytes(data[4:6], "big")
            for _ in range(qd):
                while i < len(data) and data[i] & 0xC0 != 0xC0 and data[i] != 0:
                    i += data[i] + 1
                i += 2 if (i < len(data) and data[i] & 0xC0 == 0xC0) else 1
                i += 4
            an = int.from_bytes(data[6:8], "big")
            for _ in range(an):
                if i >= len(data):
                    break
                while i < len(data) and data[i] & 0xC0 != 0xC0 and data[i] != 0:
                    i += data[i] + 1
                i += 2 if (i < len(data) and data[i] & 0xC0 == 0xC0) else 1
                rtype = int.from_bytes(data[i:i + 2], "big")
                rdlen = int.from_bytes(data[i + 8:i + 10], "big")
                i += 10
                rd = data[i:i + rdlen]
                if rtype == 12:
                    found["ptr"].update(x.decode("ascii", "ignore")
                                        for x in re.findall(rb"[ -~]{3,}", rd))
                elif rtype == 16:
                    j = 0
                    while j < len(rd):
                        ln = rd[j]
                        j += 1
                        seg = rd[j:j + ln]
                        j += ln
                        try:
                            found["txt"].add(seg.decode())
                        except Exception:
                            pass
                elif rtype == 1 and rdlen == 4:
                    found["a"].add(".".join(str(b) for b in rd))
                i += rdlen
        except Exception:
            pass
    return {k: sorted(v) for k, v in found.items()}


def parse_printable(pkts):
    """Fallback: every printable run >= 3 chars in the payload."""
    names = set()
    for _addr, data in pkts:
        names.update(x.decode("ascii", "ignore")
                     for x in re.findall(rb"[ -~]{3,}", data[12:]))
    return sorted(names)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("service", nargs="?", default=SERVICE_ENUM,
                    help="service type, e.g. _yandexio._tcp.local (default: enumerate types)")
    ap.add_argument("--target", help="unicast to this IP instead of multicast")
    ap.add_argument("--timeout", type=float, default=4.0)
    args = ap.parse_args()

    mode = f"unicast -> {args.target}" if args.target else "broadcast"
    pkts = query(args.service, args.target, args.timeout)
    print(f"[{args.service}] {mode}: {len(pkts)} reply packet(s)")
    if not pkts:
        print("  no replies — device may not advertise this service, or multicast is filtered")
        return

    print("  responders:", sorted({a for a, _ in pkts}))
    structured = parse_structured(pkts)
    for k, v in structured.items():
        if v:
            print(f"  {k}: {v}")

    if not any(structured.values()):
        print("  structured parse empty — raw printable runs:")
        for n in parse_printable(pkts)[:60]:
            print("   ", n)

    if args.service == SERVICE_ENUM:
        print("\n  next: query one of the listed types, e.g. "
              "python3 mdns_probe.py _yandexio._tcp.local")


if __name__ == "__main__":
    main()
