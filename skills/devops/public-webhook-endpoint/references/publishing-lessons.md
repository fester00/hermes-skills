# Уроки публикации: измерение путей, диагностика по слоям, контракт провайдера

> Поглощено 2026-10-11 из навыка `public-endpoint-publishing` (навык удалён, содержимое сохранено здесь).

# Publishing a local service to the internet

Use for any task of the form "give this localhost service a public HTTPS address" — Yandex
Dialogs skill webhooks, Telegram bots, marketplace callbacks, tunnel-based demos.

## 1. Measure each exposure path before building on it

Never assume a tunnel works on the target network — probe first:

```bash
for h in tailscale.com pkgs.tailscale.com cloudflare.com ngrok.com localhost.run serveo.net; do
  printf '%-22s ' "$h"
  curl -s -o /dev/null -w "%{http_code} %{time_total}s\n" --noproxy '*' --max-time 8 "https://$h/"
done
```

Observed on the home LAN behind a transparent-proxy router (2026-10):

| Path | Verdict |
|---|---|
| **Cloudflare Tunnel (`cloudflared`)** | **Blocked.** QUIC: `failed to dial edge with quic: no recent network activity`. `--protocol http2`: `TLS handshake with edge error: EOF`. Every variant dies the same way — stop trying. |
| **localhost.run (free)** | Works over SSH/22 **but rotates the subdomain inside one SSH session** — 8 names observed in ~10 minutes, only the newest answered 200. **Unusable for a stored webhook URL.** |
| **serveo.net** | Works over SSH. Stable subdomain requires registering the SSH public key (browser login). |
| **Tailscale Funnel** | Permanent route: hostname never changes. Install needs `sudo` once. |
| **ngrok.com** | Unreachable directly. |

**Rule:** an ephemeral tunnel is fine for a one-off smoke test, never for a URL a third party
stores. If the provider can rotate the URL, the integration breaks silently — the caller sees
`500`/`502` while the app's own logs show healthy `200`s.

## 2. Publish the guarded edge proxy, not the raw app

If a small userspace proxy sits in front of the app (token path, allowlist, greeting shim),
point the tunnel at the **proxy port**. The guards survive, the proxied layers restart without
`sudo`, and the app's systemd unit never needs touching.

Corollary: when the app's allowlist lives in `.env` and restarting it needs `sudo`, enforce the
allowlist in the proxy instead — re-reading a plain file per request is enough.

## 3. Diagnose layer by layer before blaming the integration

```bash
curl -s --noproxy '*' http://127.0.0.1:8787/health            # app
curl -s --noproxy '*' http://127.0.0.1:8788/health            # edge proxy
curl -s --noproxy '*' "https://$PUBLIC/health"                # tunnel + edge
journalctl -u <service> --since "10 min ago" | grep POST       # did the request arrive?
```

If the app log shows **no** request, the caller never got through: the fault is the tunnel,
not the handler. `502 no tunnel` on the public URL means the tunnel session died.

## 4. Honour the provider's webhook contract exactly

Yandex Dialogs (the contract this skill was learned on):

- Backend must be **HTTPS with a fullchain certificate**; self-signed is rejected outright.
- **4.5 s** total round-trip budget (connect + delivery + handler + response). Slower models
  need a filler reply («Секунду, я подумаю.») plus delivery of the finished answer on the next turn.
- `response.text` and `response.tts` ≤ **1024** characters each.
- Body is **`version` + `response` only**: `end_session` lives *inside* `response`, and there is
  **no `session` object** in the response. Buttons are arrays of objects, not strings.
- Session-open requests arrive with an **empty utterance** — answer with a greeting, not
  «не расслышал», or the speaker's first words are a complaint.
- **Private** skill type keeps it out of the catalogue and limited to the author's account/devices.
- Skill name: 2–4 words, no «Алиса», «Яндекс», «Станция»; up to 3 activation names.
- Capture the caller's `user_id` from the first real request and pin it as an allowlist.

Verify the protocol against the vendor docs rather than trusting an earlier plan — a wrong
field placement (e.g. `end_session`) passes tests and fails in production.

## 5. Traps that cost real debugging time

| Symptom | Cause | Fix |
|---|---|---|
| `curl: (23) Failure writing output to destination` under `sudo` | `fs.protected_regular=2` + sticky `/tmp`: root may not write an **existing** file in `/tmp` owned by another user | Use a unique dir from `mktemp -d`, never `/tmp/fixed-name` |
| `curl` resolves every file in the directory as a hostname | `CURL="curl --noproxy *"` — the `*` is glob-expanded at use site | Quote at the call site: `curl --noproxy '*'` |
| Local call hangs ~25 s and errors with an *empty* message | `httpx`/`curl` honour `HTTP_PROXY`/`HTTPS_PROXY` and send `127.0.0.1` traffic to the proxy | `httpx.AsyncClient(trust_env=False)`; `curl --noproxy '*'` |
| Download fails intermittently (`SSL_ERROR_SYSCALL`, `EOF`) | Flaky network path to that host | Retry 3× with a pause **and validate the payload** before installing into `/etc` |
| apt dies with `Неизвестный тип «<!DOCTYPE»` | A failed download wrote an HTML error page into `/etc/apt/sources.list.d/*.list` | Repair step first: detect `<!DOCTYPE`/`<html`/missing `^deb`, delete, re-download, validate |

## 6. Privileged steps when the agent must not handle passwords

`sudo` may require a password the agent will never type or accept. Ship one idempotent script
the user runs themselves, which:

1. repairs state left broken by earlier attempts (bad apt source, empty keyring),
2. downloads with retries and validates content before writing to system paths,
3. prints the exact command to finish manually when a provider feature needs enabling in a web console,
4. prints the final public URL at the end,
5. tolerates already-done work on every re-run.

Never paste a secret into chat, and warn the user if they send one — the correct advice is to
rotate it.

## Related

- `hermes-ops-devops` — server operations, service debugging, systemd/nginx diagnostics
- `hermes-internal-operations` — class-level Hermes operations runbook
