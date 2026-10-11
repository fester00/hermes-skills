# Рецепт публикации локального сервиса: выбор пути, шлюз, один порт, автозапуск

> Поглощено 2026-10-11 из навыка `exposing-local-services-publicly` (навык удалён, содержимое сохранено здесь).

# Exposing local services publicly

## Overview

An external platform (voice assistant, webhook provider, SaaS callback) must reach a service running
inside a NAT'd home network. Publish the **gated edge**, never the app: one exposed port owned by a
small proxy that does the authentication, logging and failure handling, with the real service
listening on loopback behind it.

## When to Use

- A webhook must be reachable over public HTTPS from a NAT'd network, without a white IP
- Choosing between a tunnel service and a managed function
- A published endpoint works, then breaks on its own; or a provider reports 5xx while local checks pass
- Wiring reboot survival for a service that is not managed by a package

## Step 1 — choose the public path

| Option | Verdict | Why |
|---|---|---|
| **Tailscale Funnel** | default choice | Permanent hostname, publicly trusted cert issued automatically, exactly one port exposed, survives reboots once configured |
| SSH reverse tunnels (`localhost.run`, serveo, and similar) | not for webhook endpoints | The service **rotates the subdomain** on its own — several new names inside a single ssh session — so every rotation silently breaks the provider's stored URL |
| Quick tunnels from a large CDN provider | test first, do not assume | Edge handshake can fail on filtered networks: QUIC dies with `no recent activity`, and the TCP fallback reports `TLS handshake with edge error: EOF`. The log names the failing stage — read it before declaring the tool broken |
| Managed function (cloud FaaS) | good when the model/backend is already public | No domain or tunnel needed, free for many skill platforms — but it still has to reach a local backend, which brings the tunnel back |

Requirements to check before promising anything: the provider usually demands HTTPS with a
**publicly trusted full chain**; self-signed certificates are rejected when the URL is saved.

## Step 2 — put a gating proxy in front

The edge proxy is a separate small service on its own loopback port. It must:

1. Accept only a **token-bearing path** (`/<route>/<TOKEN>`), answer 404 to everything else. Tokens
   live in a gitignored file, never in code or logs.
2. Gate on the **caller identity** the platform supplies (account/user id) via an allowlist file;
   an empty file means "allow all" and is only acceptable while first proving the chain.
3. Treat the platform's **opening request** specially — an empty first message is normal, answer it
   with a greeting instead of an error, and do not spend a model call on it.
4. Log one line per request: timestamp, caller IP, caller id, session, status, elapsed ms, and the
   request/response text. This log is the entire debugging surface for "did the provider reach us".
5. **Never return 5xx or an empty body** — on upstream timeout, refusal or exception, return the
   provider's success shape with a spoken/apologetic phrase and log
   `status=UPSTREAM_ERROR ms=... error=<type>: <text>`. Providers surface a 500 as a hard failure and
   drop the session; a graceful phrase keeps the conversation alive.
6. Keep `/health` minimal — a public host is scanned continuously for `/.env`, `/config.json`,
   `/graphql`, `/api` and agent-config files. Answer 404 to all of it.

## Step 3 — publish exactly one port

```bash
sudo tailscale funnel --bg --https=443 http://127.0.0.1:PORT_EDGE
sudo tailscale funnel status
```

Enable Funnel once for the tailnet: the command prints a `login.tailscale.com/f/funnel?node=...`
link, and the tailnet also needs HTTPS certificates. Point Funnel at the **proxy** port, so token,
allowlist and logging stay in front of the real service.

## Step 4 — survive a reboot

| Layer | Supervised by |
|---|---|
| Real service | systemd unit, `enable --now`, `Restart=always` |
| Edge proxy | user `cron @reboot` **and** a watchdog every few minutes |
| Tunnel | its own daemon (`tailscaled`), config persisted |

A watchdog that checks the proxy `/health` and relaunches it is what makes the setup self-healing:
verify it by killing the proxy and watching it come back. A tunnel pointing at a dead port breaks
the provider silently — nothing in the tunnel log looks wrong.

**Check the public address as well, from outside.** A loopback probe cannot see a broken tunnel: the
proxy answers 200 locally while the provider's stored URL reaches nothing. Probe the public URL too,
with DNS resolved off-host (`*.ts.net`-style names resolve to a private/tailnet address on the
machine that owns the tailnet):

```bash
EDGE=$(curl -s --noproxy '*' --max-time 25 --doh-url https://1.1.1.1/dns-query \
        -o /dev/null -w '%{http_code} %{time_total}' "https://$HOST/health" 2>/dev/null || echo '000 -')
case "$EDGE" in 200*) : ;; *) echo "$(date -Is) edge: $EDGE" >>"$EDGE_LOG" ;; esac
```

Log failures only, so the file stays readable, and prove the failing branch once by pointing the
check at a guaranteed-dead hostname. A ready-to-adapt watchdog lives in `templates/edge-watchdog.sh`.

**Rotate those logs in place.** Every watchdog run appends lines to the service's own access log, so
an unrotated log grows forever. Rewrite the file's tail by opening it for writing — never replace the
file (`mv`, `sed -i`), which swaps the inode and leaves the running process appending into an
unlinked file nobody reads.

## Step 5 — verify the way the provider does

The host itself resolves its own tunnel hostname to a private/tailnet address, so a local curl can
hit the wrong server (a co-hosted web server may answer, with an unrelated certificate). Resolve
publicly and pin the edge IP:

```bash
IP=$(dig +short <host> @1.1.1.1 | head -1)
curl -s --resolve "<host>:443:$IP" https://<host>/health
curl -s --resolve "<host>:443:$IP" -X POST https://<host>/<route>/<TOKEN> \
  -H 'Content-Type: application/json' -d @payload.json
```

Prove every guard, not just the happy path: wrong token → 404, unknown caller id → refusal,
upstream down → success shape with the fallback phrase.

## Diagnosing "it's slow" without touching working code

Separate the hops with curl's timing variables before changing anything:

```bash
curl -s -o /dev/null -w 'connect=%{time_connect}s tls=%{time_appconnect}s total=%{time_total}s\n' \
  --noproxy '*' --max-time 30 --resolve "$HOST:443:$IP" "https://$HOST/health"
```

- Fast `time_connect` with slow `time_appconnect` means the stall is the **TLS handshake on the
  path**, not your handler — rewriting the service cannot help.
- **Attribute by comparison:** probe a few unrelated hosts the same way. When the same ~5 s stall
  shows up on other remote endpoints (a public model API, another tunnel) while domestic hosts answer
  in tens of ms, the stall is your own uplink route, not the endpoint you are debugging.
- **An occasional probe failure is not a fault:** if the identical request succeeds moments later and
  your request log recorded no error, the loss was outside the service. Do not "fix" it.
- **Trust the provider-side journal over local probes.** Aggregate the elapsed times your service
  actually logged for provider-originated requests (median, max, how many exceeded the contract
  budget). The path from a home network is not the path from the provider's data centres — a stall
  measured locally may never touch real traffic.
- A public hostname may answer from **several ingress IPs of differing quality**; one slow sample is
  not evidence the endpoint is broken. Resolve, sample each IP, keep the healthy one for probes.

## Restarting a published service

Kill by **port**, never by command-line pattern:

```bash
PID=$(ss -tlnp | grep ':PORT' | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] && kill "$PID"
```

`pgrep -f`/`pkill -f "<pattern>"` also matches the shell running your command, because that shell's
own command line contains the pattern — the call returns SIGTERM with no output. When a pattern is
unavoidable, exclude the caller: `for p in $(pgrep -f PATTERN); do [ "$p" != "$$" ] && kill "$p"; done`.

**A systemd unit running as your own user reloads without `sudo`.** If the unit has `User=<you>` and
`Restart=always`, `kill <MainPID>` makes systemd start it again within seconds, already on the new
code — no `sudo systemctl restart`, no password, no privileged step to ask the user for. Check
`systemctl show <unit> -p ActiveEnterTimestamp` moved before trusting the new behaviour: a service
that never restarted is the usual reason an edited prompt or config "has no effect".

Operator-tunable files — persona prompts, greylists, masking modes — are best read **per request**
rather than once at startup: the operator then edits a text file and the very next request uses it,
with no restart and no `sudo`. A value cached at import silently keeps the old behaviour, so when a
text edit "does not work", compare the file's mtime against the process start time before rewriting
anything. Values that genuinely need a restart are best batched with the next privileged step you are
already asking the user for.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Loopback calls fail with an **empty** error after ~25 s; the service looks broken | `httpx`/`requests` honour `HTTP_PROXY`/`HTTPS_PROXY`, so a `127.0.0.1` call is routed to the exported proxy | `httpx.AsyncClient(..., trust_env=False)` in every service that talks to a local port; `curl --noproxy '*'` for local checks — **quote the `*`**, unquoted it glob-expands to the cwd listing and curl reports `Could not resolve host: <filename>` per file |
| `curl: (23) Failure writing output to destination`, only under `sudo` | `fs.protected_regular=2` forbids root from creating a file in a sticky world-writable dir (`/tmp`) that another user owns | `WORK=$(mktemp -d)` + `trap 'rm -rf "$WORK"' EXIT`; validate the payload (`file -b`, `grep -q '^deb'`) before installing it over a system path |
| A retry loop keyed on grepping the body never matches, so a working feature looks broken | `json.dumps` escapes non-ASCII by default (`\u0417...`), so raw greps fail on non-Latin text | Assert on parsed JSON (`json.load`), not raw bytes; serve responses with `ensure_ascii=False` so logs stay greppable |
| Provider reports an HTTP error while the local service log shows only 200s | The named request never reached the service — the edge was down, or the tunnel's subdomain changed | Compare the provider's timestamp against the proxy request log; a missing line means the failure is upstream of the service |
| A single opening request in the log with no follow-up | The platform's session window closed before the user's next message, which then went to the platform's own default handler | Confirm from the log, and tell the user to speak immediately after the opening prompt |
| A verification loop burns its full timeout on a feature that actually works | The loop's predicate is wrong (wrong escaping, wrong field, wrong casing) | Grep for a predicate you can see in a captured sample body first; then loop on it |

## Privileged steps

Installing the tunnel package, enabling Funnel and restarting system services need `sudo` with a
password. Hand the user **one idempotent script** to run themselves and keep the agent out of the
credential path: never ask for, accept, store or transmit a password, even when the user offers it,
and say so plainly instead of quietly working around it. Make the script safe to re-run: repair
preconditions (a corrupted apt source or keyring) before writing new ones, retry flaky downloads two
or three times, and abort with a readable message rather than leaving the system in a worse state.
