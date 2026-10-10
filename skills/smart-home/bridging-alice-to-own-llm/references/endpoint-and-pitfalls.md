# Endpoint options and pitfalls hit in practice

## Choosing a public HTTPS endpoint

| Option | Verdict | Why |
|---|---|---|
| **Tailscale Funnel** | use this | Permanent hostname, valid Let's Encrypt cert, one exposed port, survives reboots |
| `localhost.run` (ssh -R) | avoid for webhooks | Rotates the subdomain on its own (several names inside one ssh session); old addresses return `502 no tunnel` |
| `cloudflared` quick tunnel | avoid on filtered networks | QUIC edge dies with `no recent network activity`; `--protocol http2` then fails `TLS handshake with edge error: EOF` |
| Yandex Cloud Function | good alternative | Free for skills and no domain needed — but it must reach your model, so a local LLM still needs a tunnel |

Symptom of a dead or rotated endpoint: the console shows «HTTP ошибка 500» or the browser shows
`no tunnel`, while the local service is healthy and its own log shows 200s.

## Pitfalls: symptom, cause, fix

### Local HTTP client goes through the system proxy
Symptom: model calls fail with an empty error after ~25 s; every request times out.
Cause: `httpx`/`requests` honour `HTTP_PROXY`/`HTTPS_PROXY`, so a call to `127.0.0.1` is sent to
whatever proxy the shell or unit has set.
Fix: `httpx.AsyncClient(..., trust_env=False)`, and `curl --noproxy '*'` for local checks.

### `--noproxy *` unquoted inside a script
Symptom: `curl: (6) Could not resolve host: config.yaml` for every file in the directory, and a
system file ends up containing an HTML page.
Cause: the shell glob-expands `*` into the directory listing.
Fix: always quote — `curl --noproxy '*' ...`.

### Root-run script cannot write its temp file
Symptom: `curl: (23) Failure writing output to destination` when the script runs under `sudo`,
while the same command works as a normal user.
Cause: `fs.protected_regular=2` — root may not open, with `O_CREAT`, a file in a sticky
world-writable directory (`/tmp`) that another user already owns.
Fix: write into a unique directory from `mktemp -d`, never a fixed path in `/tmp`.

### `UID` is a readonly bash variable
Symptom: a script or test sends a wrong `user_id` (e.g. `1000`) and gets refused by the allowlist.
Cause: `UID` is set by bash and cannot be assigned.
Fix: use another variable name (`MYID`).

### `*.ts.net` resolves to the tailnet address locally
Symptom: a local curl of the Funnel URL returns a certificate for an unrelated site, or connects
somewhere unexpected.
Cause: on a tailnet member the name resolves to `100.x`, so the request hits the local machine's
web server instead of the public edge.
Fix: resolve publicly (`dig +short <host> @1.1.1.1`) and test with `curl --resolve <host>:443:<ip>`.

### Funnel refuses to start
Symptom: `Funnel is not enabled on your tailnet.`
Fix: open the printed `login.tailscale.com/f/funnel?node=...` link and enable Funnel (and HTTPS
certificates) once for the tailnet.

### Empty first utterance
Symptom: on skill launch the speaker says «Я не расслышал, повтори, пожалуйста».
Fix: when `session.new` and the text is empty, return a greeting and do not call the model
(instant, spends none of the latency budget).

### 500 or empty body returned to the platform
Symptom: console reports «HTTP ошибка в ответе webhook: 500», and nothing appears in the service log.
Cause: the edge raised (upstream timeout/refused) before it could log or answer.
Fix: wrap the upstream call; on any exception return HTTP 200 with a spoken phrase and log
`status=UPSTREAM_ERROR ... error=<type>: <text>`.

### Cloud reasoning models return empty content
Symptom: `finish_reason: length` with empty `content`; the answer looks broken.
Cause: thinking models spend the whole `max_tokens` budget on reasoning.
Fix: raise `max_tokens` (≥1500) for such models, or keep them as fallback only.

### `user_id` differs per surface (console vs device)
Symptom: the physical speaker is answered with your own refusal text («доступен только владельцу»),
while the console test of the same skill works perfectly.
Cause: Yandex issues a **different `session.user_id` per surface** for the same account — the
developer console and the device send different IDs. An allowlist built from console traffic
rejects the device.
Fix: read the rejected ID from your own request log (refusals log the offending `user_id`) and add
it as a second line. Re-read the allowlist on every request so no restart is needed.

### Public endpoint gets scanned
Symptom: `/.env`, `/config.json`, `/graphql`, `/api`, `/AGENTS.md` requests from unrelated IPs.
Cause: normal background noise for any public host.
Fix: keep `/health` minimal, answer 404 to everything but the token path, and gate on `user_id`.

## Keeping the edge alive

- App: systemd unit with `Restart=always`, installed with `enable --now`.
- Edge proxy: `cron @reboot` plus a watchdog every few minutes that checks `/health` and restarts it.
- Verify the watchdog by killing the proxy and watching it come back.

## Privileged steps

Installing Tailscale, enabling Funnel and restarting a system service need `sudo` with a password.
Hand the user a single idempotent script to run themselves; never take, store or transmit a
password, and never accept one in chat.

**Reloading your own service needs no sudo.** If the unit runs as *your* user (`User=natan`) with
`Restart=always`, `kill <MainPID>` makes systemd restart it in ~3 s with the new code — confirm
`ActiveEnterTimestamp` moved before trusting the reload. Use this instead of asking the user for a
privileged restart after every code change.

## Making a setting take effect

Read the system prompt (and any operator-tunable text) **from disk on every request**, never once
in `__init__`. Then persona / tone / censorship edits apply to the very next utterance: the
operator edits a text file — no restart, no code change, no sudo. A prompt cached at process
start silently keeps the old behaviour, so when a prompt edit "doesn't work", first compare the
file's mtime against the service start time before rewriting the prompt.
