---
name: local-network-device-discovery
description: Use when scanning the local network. Find, identify, and inventory LAN devices by IP, MAC, and fingerprint.
version: 1.0.0
tags: [network, lan, discovery, mdns, arp, iot, inventory, smart-home, yandex, alice]
---

# Local Network Device Discovery & Inventory

Answer "is device X on our network?" and "what is on our network?" with evidence, not guesses.

## When to use

- "Find the <device> in our local network" (smart speaker, TV, camera, printer, NAS)
- "What devices are on my network?" / router DHCP shows an unknown host
- An IP needs identifying before you touch it (static assignment, local control, firewall rule)
- You need a device inventory that survives this session

## Procedure

### 1. Establish your own position — never assume the subnet

```bash
ip -brief addr; ip route; ip neigh
```

Record: own IP, subnet mask, default gateway IP + MAC. The subnet is whatever the active
interface says, not what the router docs or memory say.

### 2. Check what scanners exist before promising a scan

```bash
for t in nmap arp-scan fping avahi-browse arping; do printf '%-12s ' "$t"; command -v $t >/dev/null && echo OK || echo '-'; done
```

If they are absent, do **not** try to `apt-get install` — use the stdlib scripts shipped with
this skill. A ping sweep + ARP + rDNS + pure-Python mDNS covers everything a consumer LAN needs.

### 3. Ping sweep the /24, then read ARP — they answer different questions

```bash
python3 scripts/lan_scan.py                 # auto-detects the local /24
python3 scripts/lan_scan.py 192.168.1.0/24  # explicit subnet
```

Prints alive hosts, the ARP table, reverse DNS, and open ports from a common-service list.

The ICMP sweep is a *starting point*, never the inventory: many devices are ICMP-silent
(see Pitfalls). The ARP table is the more complete list.

```bash
ip neigh | grep -v -E "FAILED|INCOMPLETE"   # drop sweep placeholders
```

### 4. Reverse DNS is the highest-value identifier

Consumer gear publishes its **model** in the DHCP hostname:
`Yandex-Station-Midi-NY6N.lan`, `Keenetic-b84a.lan`, `RE220.lan`, `console.gl-inet.com`.

```bash
python3 -c "import socket; print(socket.gethostbyaddr('192.168.0.164'))"
```

Run it on every candidate before falling back to harder identification.

### 5. Enumerate mDNS services — the only voice of otherwise-silent devices

```bash
python3 scripts/mdns_probe.py                              # what service types are advertised
python3 scripts/mdns_probe.py _yandexio._tcp.local        # broadcast query for one service
python3 scripts/mdns_probe.py _yandexio._tcp.local --target 192.168.0.164   # unicast: full TXT
```

Service-type signatures:

| mDNS service | Device class |
|---|---|
| `_yandexio._tcp` | Yandex Station / Alice speaker (TCP 1961) |
| `_googlecast._tcp` | Chromecast, Android TV, Google/Nest speakers |
| `_airplay._tcp`, `_raop._tcp` | Apple TV, AirPlay-capable TVs (TXT carries `model`, `manufacturer`) |
| `_androidtvremote2._tcp` | Android TV remote |
| `_matter._tcp`, `_hap._tcp` | Matter / HomeKit accessories |
| `_http._tcp` | Generic embedded web UI |

TXT records carry the device identity: Yandex Stations expose `deviceId=<id>`, `platform=cucumber`,
`cluster=yes` (multiroom group). More per-vendor detail in `references/smart-device-signatures.md`.

### 6. Identify the vendor from the MAC OUI

```bash
curl -s --max-time 15 https://api.macvendors.com/3C:0B:4F
```

If it answers `Too Many Requests` / `Please slow down`, do not retry in a loop — fall back to a
search (`"<OUI>" OUI vendor`) and read the IEEE-derived result. The limit is per-API, not
per-address, so a ~1 s spacing still trips it on a batch of 5+.

Known: Yandex hardware uses OUI `3C:0B:4F` (registered to *Yandex Services AG*, later renamed
*Intertech Services AG*, Lucerne). So a Yandex speaker resolves to a non-Yandex vendor name —
check the registration history before doubting the identification.

### 7. Confirm identity with at least two independent signals

A single heuristic is not identification. Converge rDNS hostname + mDNS TXT + OUI + a port that
actually accepts a TCP connection. Two or more agreeing signals is the bar before reporting a
device as found.

### 8. Persist the inventory

Write the result to the vault, not just into chat:

- Note: `~/obsidian-memory/Knowledge/Домашняя сеть — инвентарь устройств.md` (device table:
  IP, rDNS name, MAC, vendor, open ports; plus topology quirks).
- Link it from `[[MOC — Index]]` under **Инфраструктура**.
- Keep the scan scripts in `~/obsidian-memory/Scripts/` so the vault stays self-contained.

Report in Russian with the evidence chain (how each identifier was obtained), not just the answer.

## Pitfalls

1. **ICMP-silent devices are the norm.** Smart speakers, phones and IoT frequently do not answer
   ping — a Yandex Station was invisible to a full /24 sweep yet present in ARP and loud on mDNS.
   Never conclude "not on the network" from a failed ping; confirm with ARP + mDNS + rDNS.
2. **Never trust a ping sweep's host count as the device count.** One /24 reported 6 ICMP-alive
   hosts while the ARP table held 253 entries and 11 real devices.
3. **A repeater proxies ARP for everything behind it.** Several IPs answering with the *same* MAC
   is a range extender (e.g. TP-Link RE220), not a spoof and not one device. Report the bridged
   IPs as separate devices.
4. **Locally administered MACs cannot be looked up.** If the second hex digit is 2/6/A/E
   (`36:ce:4b`, `62:08:8a`, `3a:c2:b9`), the address is randomised/private — the OUI API returns
   `Not Found`. Expected, not an error; identify those hosts by rDNS/mDNS instead.
5. **Filter ARP placeholders.** A sweep leaves hundreds of `FAILED`/`INCOMPLETE` entries; an
   unfiltered dump is noise, not an inventory.
6. **Expect double-NAT segments.** A second router (Keenetic, mesh node) behind the main gateway
   creates its own subnet leg; devices behind it may be reachable only across that router.
7. **An open port proves the device exists; it does not prove you control it.** Yandex Station TCP
   1961 accepts the connection but ignores plaintext JSON commands — the channel is encrypted and
   needs the device key, so an empty reply is the *expected* answer and still confirms the host.
   Do not promise local control until you have seen a real reply. Working path: the Home Assistant
   custom integration (`yandex_station`, HACS) in local mode, or the cloud API — and note that local
   mode is *additive* (it runs alongside the vendor assistant instead of replacing it). For the
   "can we reflash it / swap its AI model?" follow-up, see `references/smart-device-signatures.md`.
8. **Read the TXT record, not just the PTR name.** The mDNS instance name (`YandexIOReceiver-…`)
   is not the model name; the model comes from rDNS, and the identity from TXT.

## Files

- `scripts/lan_scan.py` — stdlib /24 sweep: ping, ARP, reverse DNS, common-port probe.
- `scripts/mdns_probe.py` — stdlib mDNS query (service-type enumeration, broadcast, unicast)
  with PTR/A/TXT parsing; no avahi needed.
- `references/smart-device-signatures.md` — mDNS service map, OUI notes, per-vendor quirks, and
  the local-control / reflash / "other AI model" verdicts worth knowing.
