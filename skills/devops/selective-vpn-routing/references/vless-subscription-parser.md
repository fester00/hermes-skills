# Parsing a VLESS/Xray JSON subscription into individual vless:// links

## When this applies

Some VPN providers (e.g. okvpn-style `cdn.oksbrf.ru/new/<token>` endpoints) return a JSON array of full Xray configs instead of a single base64 subscription link. Each array item is a complete client config with inbounds (SOCKS/HTTP), routing, and one outbound. You may need to convert each outbound into a standalone `vless://` URL that can be imported into mobile/desktop clients one by one.

## Typical JSON shape

```json
[
  {
    "dns": { "servers": ["1.1.1.1", "1.0.0.1"] },
    "inbounds": [ { "tag": "socks", "port": 10808, ... } ],
    "outbounds": [
      {
        "tag": "proxy",
        "protocol": "vless",
        "settings": {
          "vnext": [{
            "address": "vless-addr.example.com",
            "port": 443,
            "users": [{ "id": "uuid", "encryption": "none" }]
          }]
        },
        "streamSettings": {
          "network": "tcp",
          "security": "reality",
          "realitySettings": {
            "serverName": "nvidia.com",
            "fingerprint": "firefox",
            "publicKey": "...",
            "shortId": "..."
          }
        }
      }
    ]
  }
]
```

There may also be `hysteria` or other non-VLESS outbounds mixed in; skip those.

## Deduplicate, and name links by server — not by profile

A single subscription often contains MANY profiles (one per region or routing group), and the same physical server reappears across them: one UUID/public-key pair shared by every node, the same `address:port` repeated under different `remarks` values. Naive iteration therefore emits the same server several times and labels each link with the profile name rather than the server.

- Deduplicate on the tuple `(address, port, users[0].id)` before writing the list.
- Derive the link remark from the SERVER, not the enclosing profile. If the array holds one region-named profile per server (e.g. `🇩🇪Германия`, `🇮🇹Италия`), build an `ip -> region` map from those profiles first and name each deduped link from it; otherwise fall back to `profile remarks + outbound tag`.
- Report the final unique count and print `name -> address` so the user can verify the set at a glance.

## Conversion rules

| Xray field | vless URL query param |
|---|---|
| `settings.vnext[0].users[0].id` | `uuid` after `vless://` |
| `settings.vnext[0].address` | host |
| `settings.vnext[0].port` | port |
| `streamSettings.network` | `type` |
| `streamSettings.security` | `security` |
| `tlsSettings.serverName` or `realitySettings.serverName` | `sni` |
| `tlsSettings.fingerprint` or `realitySettings.fingerprint` | `fp` |
| `realitySettings.publicKey` | `pbk` |
| `realitySettings.shortId` | `sid` |
| `wsSettings.path` / `grpcSettings.serviceName` / `httpSettings.path` | `path` |
| `wsSettings.headers.Host` / `tlsSettings.sni` | `host` |

Fragment (`#`) becomes the remark; URL-encode it if it contains spaces or non-ASCII.

## Python parser

```python
import json, urllib.parse

def parse_xray_subscription(json_text: str) -> list[str]:
    configs = json.loads(json_text)
    urls = []

    for cfg in configs:
        for ob in cfg.get("outbounds", []):
            if ob.get("protocol") != "vless":
                continue

            vnext = ob.get("settings", {}).get("vnext", [{}])[0]
            user = vnext.get("users", [{}])[0]
            stream = ob.get("streamSettings", {})
            sec = stream.get("security", "")

            address = vnext.get("address")
            port = vnext.get("port")
            uid = user.get("id")
            net = stream.get("network", "tcp")

            sni, fp, pbk, sid = "", "", "", ""
            if sec == "tls":
                tls = stream.get("tlsSettings", {})
                sni = tls.get("serverName", "")
                fp = tls.get("fingerprint", "")
            elif sec == "reality":
                reality = stream.get("realitySettings", {})
                sni = reality.get("serverName", "")
                fp = reality.get("fingerprint", "")
                pbk = reality.get("publicKey", "")
                sid = reality.get("shortId", "")

            path, host = "", ""
            if net == "ws":
                ws = stream.get("wsSettings", {})
                path = ws.get("path", "")
                host = ws.get("headers", {}).get("Host", "")
            elif net == "grpc":
                path = stream.get("grpcSettings", {}).get("serviceName", "")

            params = {"type": net, "security": sec}
            if sni: params["sni"] = sni
            if fp: params["fp"] = fp
            if path: params["path"] = path
            if host: params["host"] = host
            if pbk: params["pbk"] = pbk
            if sid: params["sid"] = sid

            remark = urllib.parse.quote(ob.get("tag", "proxy"))
            query = urllib.parse.urlencode(params)
            urls.append(f"vless://{uid}@{address}:{port}?{query}#{remark}")

    return urls
```

## Usage example

```python
import urllib.request

url = "https://cdn.example.com/new/<token>"
json_text = urllib.request.urlopen(url, timeout=20).read().decode()

for u in parse_xray_subscription(json_text):
    print(u)
```

If direct fetch fails, try through a local proxy:

```python
req = urllib.request.Request(url)
req.set_proxy("127.0.0.1:1081", "http")
json_text = urllib.request.urlopen(req, timeout=20).read().decode()
```

## Notes

- Some providers serve the array-of-Xray-configs format from a `/new/<token>` path on an `api.<provider>` host. Fetch with a client User-Agent (`-A "v2rayN/6.0"`) and confirm `Content-Type: application/json` before parsing.
- `type=raw` is the modern Xray name for plain TCP; many clients still expect `type=tcp`.
- Some clients require `encryption=none` as a query param even though it is the VLESS default.
- `spiderX` from Reality is rarely needed in import URLs; omit it unless the target client complains.
- For mixed subscriptions containing `hysteria` or `tuic`, those need separate `hysteria://`/`tuic://` URLs and are not covered here.
