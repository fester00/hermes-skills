# Tunnels: What Works, and How to Verify It

## Measured comparison (filtered network, behind NAT)

| Option | Result |
|---|---|
| `localhost.run` (free, `ssh -R`) | **Unusable.** The service reassigns the subdomain by itself — 8 different names in one ssh session. All but the newest returned `502 no tunnel`; a periodic `/health` ping did not prevent it. |
| `cloudflared` quick tunnel | **Did not connect.** QUIC: `failed to dial a connection: no recent network activity`. `--protocol http2` fallback: `TLS handshake with edge error: EOF`. Nothing to fix locally. |
| Serveo | Connects over ssh, but a stable subdomain needs a registered SSH key (browser login) and the free tier injects a browser warning page. |
| **Tailscale Funnel** | **Works.** Permanent name, Let's Encrypt certificate, one published port, survives reboots. |

General rule: anything handing out a random subdomain per session is a dead end for a webhook
endpoint — the platform stores that URL and keeps calling it.

## Install Tailscale from the official apt repo

The package host is intermittently flaky (`SSL_ERROR_SYSCALL`), so retry and validate BEFORE
installing into `/etc` (a failed download written into sources.list breaks apt itself):

```bash
WORK=$(mktemp -d "${TMPDIR:-/tmp}/ts.XXXXXX"); trap 'rm -rf "$WORK"' EXIT
fetch() { local url="$1" dest="$2" i
  for i in 1 2 3; do curl -fsSL --noproxy '*' --max-time 60 -o "$dest" "$url" && return 0
    echo "retry $i/3"; sleep 3; done; return 1; }

fetch https://pkgs.tailscale.com/stable/ubuntu/noble.noarmor.gpg "$WORK/keyring.gpg"
file -b "$WORK/keyring.gpg" | grep -qi OpenPGP || { head -c 160 "$WORK/keyring.gpg"; exit 1; }
sudo install -m 644 "$WORK/keyring.gpg" /usr/share/keyrings/tailscale-archive-keyring.gpg

fetch https://pkgs.tailscale.com/stable/ubuntu/noble.tailscale-keyring.list "$WORK/ts.list"
grep -q '^deb' "$WORK/ts.list" || { head -c 160 "$WORK/ts.list"; exit 1; }
sudo install -m 644 "$WORK/ts.list" /etc/apt/sources.list.d/tailscale.list

sudo apt-get update && sudo apt-get install -y tailscale
```

Only the distro codename (`noble`) changes on another release; the `.list` variant already contains
the `signed-by=` pointer.

## Connect the node

```bash
sudo tailscale up --hostname=<hostname>     # prints https://login.tailscale.com/a/<id>
```

The user opens that link and presses **Connect**. Until they do, every other tailscale command
answers `Logged out. Log in at: ...` — expected, not a bug, and worth warning the user about so they
do not read it as a failure.

## Publish exactly one port

```bash
sudo tailscale funnel --bg --https=443 http://127.0.0.1:<port>
```

First run may answer `Funnel is not enabled on your tailnet` and print
`https://login.tailscale.com/f/funnel?node=<node>` — the user enables Funnel (and HTTPS
certificates) there once, then re-runs the same command. Success prints the public base URL plus a
`|-- / proxy http://127.0.0.1:<port>` line.

```bash
tailscale funnel status                 # what is published
tailscale funnel --https=443 off        # disable
```

Point it at the edge proxy port, not the app port.

## Verification, in order

1. Public DNS must return public edge IPs (not a tailnet 100.x address):
```bash
curl -s -H 'accept: application/dns-json' "https://1.1.1.1/dns-query?name=$HOST&type=A"
```
2. TLS must be a public CA for exactly this name:
```bash
EDGE=<first answer from step 1>
echo | openssl s_client -connect "$EDGE:443" -servername "$HOST" 2>/dev/null \
  | openssl x509 -noout -issuer -dates -ext subjectAltName
```
Expect `Let's Encrypt` and `DNS:<host>` among the SANs.
3. Reachability and payload, through the edge:
```bash
curl -s --resolve "$HOST:443:$EDGE" "https://$HOST/health"
curl -s --resolve "$HOST:443:$EDGE" -X POST "https://$HOST/<path>/<token>" \
  -H 'Content-Type: application/json' -d @payload.json
```
4. Reject paths: no token -> 404; foreign caller id -> refusal plus a `REFUSED` log line.

Skipping `--resolve` sends the request to the local web server (the `*.ts.net` name resolves to the
tailnet address from inside the tailnet) and produces a false negative — or a TLS certificate from
an unrelated local vhost.

## Persistence check list

- app: systemd unit `enabled` + `active`
- edge proxy: crontab `@reboot` + 3-minute watchdog; verified by killing the proxy once
- tunnel: `tailscaled` active and `tailscale funnel status` shows the mapping
- after any reboot: re-run verification step 3 and keep the raw output as evidence
