# v2rayA API commands for headless router tuning

Device context: GL.iNet GL-MT6000, v2rayA on `http://192.168.0.1:2017`, Xray-core backend.
Useful when browser access to the web UI is unavailable but SSH to the router works.

## Login and token

```bash
TOKEN=$(curl -s -m 5 -X POST http://127.0.0.1:2017/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"root","password":"<password>"}' | \
  sed -E 's/.*"token":"([^"]+)".*/\1/')
```

Set `Auth-Token` header (the field name returned by login) on subsequent calls:
```bash
curl -s -H "Authorization: $TOKEN" http://127.0.0.1:2017/api/touch
```

## Common API endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /api/login` | Obtain auth token. |
| `GET /api/touch` | List servers, subscriptions, connected server. |
| `POST /api/import` | Import a share URL (`vless://`, `vmess://`, `ss://`, subscription URL). |
| `POST /api/connection` | Connect a server by object `{id, _type, sub, outbound}`. |
| `GET /api/setting` | Read current settings. |
| `PUT /api/setting` | Update settings (JSON body with changed fields). |
| `GET /api/routingA` | Read custom routing-A rules. |
| `PUT /api/routingA` | Update custom routing-A rules. |

## Import a single VLESS node

```bash
curl -s -m 10 -H "Authorization: $TOKEN" \
  -X POST http://127.0.0.1:2017/api/import \
  -H "Content-Type: application/json" \
  -d '{"url":"vless://UUID@HOST:PORT?security=reality&flow=xtls-rprx-vision&sni=SNI&pbk=PBK&sid=SID&fp=firefox&type=tcp#NAME"}'
```

## Read current state

```bash
curl -s -m 5 -H "Authorization: $TOKEN" http://127.0.0.1:2017/api/touch | head -c 2000
```

Look for `connectedServer` to see which server is active.

## Switch to a different imported server

After importing, the server appears in `/api/touch` with an `id`. Connect it:

```bash
curl -s -m 10 -H "Authorization: $TOKEN" \
  -X POST http://127.0.0.1:2017/api/connection \
  -H "Content-Type: application/json" \
  -d '{"id":6,"_type":"server","sub":0,"outbound":"proxy"}'
```

## Bulk-import many nodes from a numbered list

When the nodes live in a file on the LAN host as `N|<vless url>` lines, copy the file to the router and loop over the import endpoint. BusyBox `sed` has no JSON library, so escape backslashes and quotes manually:

```bash
# from the host:
sshpass -e ssh root@ROUTER 'cat > /tmp/links.txt' < links.txt
# then on the router:
TOKEN=$(curl -s -m8 -X POST http://127.0.0.1:2017/api/login -H "Content-Type: application/json" \
  -d '{"username":"root","password":"<pw>"}' | sed -E 's/.*"token": *"([^"]+)".*/\1/')
for n in 7 8 9 10; do
  URL=$(sed -n "${n}p" /tmp/links.txt | sed -E 's/^[0-9]+\|//')
  BODY=$(printf '%s' "$URL" | sed 's/\\/\\\\/g; s/"/\\"/g')
  printf '{"url":"%s"}' "$BODY" > /tmp/imp.json
  curl -s -m15 -H "Authorization: $TOKEN" -X POST http://127.0.0.1:2017/api/import \
    -H "Content-Type: application/json" --data-binary @/tmp/imp.json | head -c 40; echo
  sleep 1
done
```

Notes:
- The import URL accepts the `vless://...#NAME` fragment as-is; v2rayA stores `name` from the decoded fragment, so pre-named links give readable entries.
- Import is **idempotent-ish but not de-duplicating**: importing the same node twice creates a second entry. Before importing, diff the current `/api/touch` `servers[]` against your list and import only the missing addresses.
- Importing while connected **restarts the Xray core** (the `xray run` PID changes) but preserves the active connection: verify afterwards that `config.json` `outbounds[tag=proxy]` still holds the same address and that `running:true`.
- `tr '{' '\n'` on the `/api/touch` body is a quick way to count/list servers without `jq` (usually absent on the router): `grep -c '"_type":"server"'`. The count is +1 because the active connection appears as a `_type:server` reference too — don't report the raw number as the server count.

## Checking whether xray/v2raya need an update (no web backend needed)

The router's own tunnel is the most reliable way to reach GitHub when the host's proxy is down. Run the query over the router's local SOCKS port:

```bash
curl -s --max-time 20 --socks5-hostname 127.0.0.1:20170 \
  https://api.github.com/repos/XTLS/Xray-core/releases/latest | grep -E '"tag_name"|"published_at"'
curl -s --max-time 20 --socks5-hostname 127.0.0.1:20170 \
  https://api.github.com/repos/v2rayA/v2rayA/releases/latest | grep -E '"tag_name"|"published_at"'
```

**On OpenWrt/GL.iNet 24.10.4, `opkg` will NOT offer an update.** Both the OpenWrt package feed and the GL.iNet feed pin `xray-core 25.1.30-r1` and `v2raya 2.2.7.3-r1`; `opkg list-upgradable` stays empty even though upstream is far ahead (Xray 26.x, v2rayA 2.5.x). Upgrading means manually replacing `/usr/bin/xray` with a current ARM64 release build (`aarch64_cortex-a53`), keeping `xray.old` for rollback — not an `opkg upgrade`. Do not tell the user to "just run opkg update".

Other checks worth reporting: `/usr/share/xray/{geoip,geosite}.dat` and any custom `LoyalsoldierSite.dat` carry file dates — a year-old geoip/geosite means new gfw/greatfire domains leak direct. Disk space is a non-issue on the GL-MT6000 (~6.6 GB free on /overlay). Upgrading v2rayA without a matching feed package is riskier than upgrading Xray alone: the older GUI may emit a config the newer core rejects (e.g. the removed `allowInsecure` field).

## Change transparent proxy mode to global + DoH

```bash
curl -s -m 10 -H "Authorization: $TOKEN" \
  -X PUT http://127.0.0.1:2017/api/setting \
  -H "Content-Type: application/json" \
  -d '{"transparent":"global","pacMode":"global","antipollution":"dns-over-https"}'
```

This makes all LAN traffic go through the active proxy and resolves DNS through the tunnel.

## Why use the API instead of editing files

`/etc/v2raya/config.json` is generated and overwritten by v2rayA. Persistent state lives in `/etc/v2raya/bolt.db` and `/etc/v2raya/boltv4.db`. Always change settings via the web UI or API; manual file edits are lost immediately.

## Verification

From the router itself:
```bash
curl -s -m 10 --connect-timeout 5 -o /dev/null -w "gemini: %{http_code}\n" https://gemini.google.com
```

From a LAN client:
```bash
curl -s https://2ip.ru
curl -s https://api.ipify.org
```

## Read-only config audit ("check my router, change nothing")

When the user asks to verify the live config without modifying anything, stay strictly read-only over SSH: no `PUT`/`POST` API calls, no file writes, no service restarts. State explicitly in the final reply that nothing was changed.

1. Confirm the stack is running:
   ```bash
   ps w | grep -i "[v]2ray"                 # expect: v2raya and "xray run --config=/etc/v2raya/config.json"
   opkg list-installed | grep -i v2ray      # package + version
   ```
2. Read the live config (safe — this is what Xray is actually running):
   ```bash
   cat /etc/v2raya/config.json              # outbounds[tag=proxy] = the active server
   cat /etc/v2raya/v2raya.nft               # transparent-proxy rules
   ```
3. Match the active outbound FIELD-BY-FIELD against the server the user says they use, and report the comparison rather than a bare "it works": `address`, `port`, `users[0].id` (UUID), `flow`, `security`, and `realitySettings.{serverName,publicKey,shortId,fingerprint}`.
4. Verify liveness with tunnel-ridden traffic. Do NOT test via a public-IP echo service — under split-tunnel the direct and proxied IPs are identical by design (see the pitfall in SKILL.md). Instead: fetch a blocked domain and require a real HTTP status, count ESTABLISHED flows to the proxy IP in `/proc/net/nf_conntrack`, and tail `/var/log/v2raya/v2raya.log` for `transparent -> proxy` lines.
5. Report any coverage gap you find — e.g. IPv4-only tproxy rules with no IPv6 chain (`grep nfproto /etc/v2raya/v2raya.nft`), noting it is harmless only while the router has no global IPv6.
