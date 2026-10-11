---
name: public-webhook-endpoint
description: Use when exposing a local service as a public webhook URL.
category: devops
metadata:
  hermes:
    tags: [webhook, tunnel, https, tailscale, nat, ops, deployment, hardening]
    related_skills: [yandex-dialogs-skill, webhook-subscriptions]
---

# Public Webhook Endpoint for a Local Service

## When to Use

- An external platform must POST callbacks to a service on this machine behind NAT
  (voice-assistant skill, Git host, payment provider, IoT cloud)
- A previously working webhook URL started failing while the service itself looks healthy
- Choosing how to publish one local port without opening the whole host

## Rule 1: a stable name, never a free anonymous tunnel

Free anonymous tunnels cannot serve as a webhook endpoint: `localhost.run` reassigns the subdomain
by itself — measured eight different names inside one ssh session — so the URL handed to the
platform dies within minutes while the ssh process still looks alive. Quick tunnels may not connect
at all from a filtered network. Use **Tailscale Funnel**: one permanent
`https://<host>.<tailnet>.ts.net` name, a Let's Encrypt certificate, and exactly one chosen local
port published. Comparison of what was measured, plus install/publish commands:
`references/tunnel-options-and-verification.md`.

## Rule 2: layer it so every layer self-heals

```
[platform] -> https://<host>.<tailnet>.ts.net   (Funnel :443)
            -> 127.0.0.1:8788  edge proxy (secret path, allowlist, request log)  <- cron @reboot + watchdog
            -> 127.0.0.1:8787  the app itself                                   <- systemd unit, enabled
```

Point the tunnel at the **edge proxy**, not the app: guards and edge behaviour then live outside the
app and keep working without editing or restarting it.

- app -> systemd unit, `systemctl enable --now`
- edge proxy -> crontab (no sudo required): an `@reboot` entry **plus** a `*/3 * * * *` watchdog that
  relaunches it only when `/health` is silent and the port is free
- tunnel -> `tailscaled` systemd service; funnel config persists

**Prove the watchdog, do not assume it:** kill the proxy process, run the watchdog once, confirm
`/health` returns and the log line was written. An untested cron entry is not persistence, and a
reboot nobody simulated is where a public endpoint dies silently.

## Rule 3: verify along the path the platform takes

From the same machine a `*.ts.net` name resolves to the **tailnet** address (100.64.0.0/10), so the
request lands on the local web server and appears broken while the public path is healthy. Get the
real edge IP from public DNS and test through it:

```bash
EDGE=$(curl -s -H 'accept: application/dns-json' "https://1.1.1.1/dns-query?name=$HOST&type=A" \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["Answer"][0]["data"])')
curl -s --resolve "$HOST:443:$EDGE" "https://$HOST/health"
```

An endpoint is not verified until the **reject** paths are shown to fire: missing secret path ->
404, foreign caller identity -> refusal. Then run the platform's real payload through the same
`--resolve` form.

## Rule 4: guard the public path

- Secret path segment (`/hook/<random-token>`) — the cheapest gate, shippable before any caller
  identity is known; keep the token in a git-ignored file, never in the repo.
- Caller allowlist taken from the **request body** (a user/account id) — fill it after the first real
  request; log the payload at the edge, since the app usually logs only rejections.
- **The same account presents different ids on different surfaces.** A developer console, a mobile
  app and the physical device each send their own caller id, so an allowlist learned from one client
  silently locks out the others — and the symptom is *your own* refusal text coming back, which reads
  like a platform problem rather than your guard firing. Gather the id from every client the owner
  will actually use, and log the rejected id together with its reason so the missing one is found by
  reading the log, not by guessing. Re-read the allowlist per request: adding the second id then needs
  no restart.
- Never authenticate on caller IP: the tunnel edge may present your own address or none at all.
- **Expect active scanning, and say as little as possible.** A freshly published host attracts
  automated probes for `/.env`, `/config.json`, `/graphql`, `/api`, `/.git/*`, `AGENTS.md` — measured
  in the hundreds of requests from a handful of addresses within minutes. They get 404 only because
  the guard path is unguessable, so keep `/health` to `{"status":"ok"}` and serve no directory,
  framework default page, or version banner.
- Ready-to-copy proxy implementing all of it: `templates/token_guarded_proxy.py`.

## Rule 4b: an upstream failure must never reach the platform as a 500

A platform shows the caller the raw error code, so a `500` from the edge is the difference between
"your service is broken" and "the assistant paused for a second". Wrap the upstream call at the edge:

- catch **every** exception, log `status=UPSTREAM_ERROR ms=<n> error=<Type>: <text>`, and answer with a
  **contract-valid** response (a filler such as «Секунду, я подумаю.») — never an empty body, never 500;
- set the upstream client timeout **just above the app's own internal budget** (≈5 s when the app
  promises ≈4 s), not a comfortable 12 s: a long timeout can only produce an answer that arrives after
  the platform has already given up;
- log the elapsed milliseconds per request, so the budget can be checked against real traffic instead
  of a one-off script measurement.

Prove the branch instead of trusting it: run the proxy in-process against a dead upstream
(`httpx.ASGITransport(app=app)` with `TARGET=http://127.0.0.1:9/...`) and assert the answer is the
filler with HTTP 200. **Check which branch the test actually entered** — a guarded proxy answers the
allowlist first, so a made-up caller id returns the refusal and silently skips the branch under test;
use a real allowed id or an empty allowlist file.

## Rule 5: privileged steps are run by the user, not by the agent

`sudo` is password-protected and the agent never handles a password — including one sent in chat,
which is already compromised and must be rotated. Never ask for it, echo it, or store it.
Deliver privileged work as ONE idempotent script the user runs in their own shell:

```bash
bash /path/to/scripts/<service>-setup.sh
```

Make re-runs harmless, print each step before doing it, and fail with a readable message rather
than a half-applied state. Pitfalls that break root-run installers — sticky `/tmp` writes, flaky
downloads, corrupting apt sources, `pkill` matching its own shell:
`references/root-run-installer-pitfalls.md`.

## Rule 6: keep hand-tuned text out of the restart path

Whatever the owner tunes by hand — persona prompt, greeting, refusal wording — must be read at
request time (a file read per call), never cached at import. Otherwise every wording change becomes
a privileged restart: the user has to stop what they are doing and run it, so tuning stalls after one
iteration and the owner ends up living with wording they dislike. Only **code** changes should need a
restart. Same rule for the edge proxy: because cron relaunches it unprivileged, its constants can be
edited and applied by the user's own watchdog cycle.

## Pitfalls

- **`curl` from the host to the public name is not a test** (see Rule 3) — use `--resolve` against
  the edge IP.
- **A tunnel process being alive does not mean the tunnel works.** Check the public URL, not
  `pgrep`. A rotating subdomain is the giveaway that the provider is unusable.
- **Local calls inside the service must not inherit proxy env vars.** An `httpx` client picks up
  `HTTP_PROXY`/`HTTPS_PROXY` from the environment and sends `127.0.0.1` calls through the proxy,
  failing with an empty error after a full timeout — build clients with `trust_env=False` and use
  `curl --noproxy '*'` for local checks.
- **Serialise JSON with `ensure_ascii=False`.** With escaping on, every non-ASCII log line is stored
  as `\u0417...`, so grepping the log for the platform's text silently finds nothing and a guard that
  works perfectly looks untested.
- **Opening a port publicly is a side effect.** Add the guard first, keep the exposure to one port,
  and record the disable command (`tailscale funnel --https=443 off`) next to the enable command.
- **Write the reachable URL into the project's runbook** together with the guard location, log path,
  and restore commands — the URL alone is useless six weeks later.

## Related material (absorbed 2026-10-11)

Two sibling skills covered the same ground; their content is kept here as references instead of
separate skills:

- `references/local-service-exposure-recipe.md` — the 5-step recipe: choose the path, gate it with a
proxy, publish one port, survive a reboot, verify the way the provider does (+ `templates/edge-watchdog.sh`)
- `references/publishing-lessons.md` — measure each exposure path before building on it, diagnose
layer by layer, honour the provider's webhook contract, privileged steps without handling passwords
