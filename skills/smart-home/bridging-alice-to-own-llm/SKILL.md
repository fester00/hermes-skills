---
name: bridging-alice-to-own-llm
description: Use when a Yandex Station must answer with your own LLM.
category: smart-home
---

# Bridging Alice to your own LLM

## Overview

Alice's brain is server-side; you cannot repoint the speaker itself. What works is a **private
Яндекс.Диалоги skill whose webhook is your own service**: the user launches the skill by voice,
every following utterance is POSTed to your server, your model answers, and Alice speaks the
reply in her own voice (voice is picked in the skill settings).

The speaker keeps all stock behaviour — this is an added channel, not a replacement.

## Architecture

```
[Station] -> [Yandex Dialogs cloud] -> https://<host>.ts.net/alice/<TOKEN>
   -> Tailscale Funnel :443 -> 127.0.0.1:8788 [edge proxy: token, allowlist, greeting, log]
   -> 127.0.0.1:8787 [FastAPI: answer flow + LLM client] -> Ollama / any OpenAI-compatible API
```

## When to Use

- «подключить колонке другие мозги» — make Alice answer with a self-hosted model
- A Диалоги skill webhook must be reachable over public HTTPS from a NAT'd home network
- Diagnosing a skill that times out, answers 500, or stops answering after a while
- User asks whether the speaker can be reflashed instead: it cannot (pinned TLS, locked bootloader)

When NOT to use: a fully local assistant with its own microphone — the speaker's mic stream is
closed, so that is a separate build with separate hardware.

## Hard limits (platform, not negotiable)

| Limit | Value | Consequence if broken |
|---|---|---|
| Answer budget | **4.5 s** total round-trip | Session dies, Alice says «навык не отвечает» |
| `response.text` / `response.tts` | ≤ 1024 chars each | Truncated |
| Response shape | `{"version":"1.0","response":{...}}` | The reply must contain **no** `session` object |
| Backend | HTTPS, publicly trusted cert | Self-signed rejected on save |

Set an internal budget of **4.0 s**: answer in time, else return a filler («Секунду, я подумаю.»)
and deliver the finished answer on the next turn.

## Recipe

1. **Service** on `127.0.0.1:PORT_APP`: `POST /alice`, `GET /health`, model client, session memory,
   4 s keep-alive flow. Every local HTTP client must use `trust_env=False`.
2. **Edge proxy** on `127.0.0.1:PORT_EDGE`: accepts only `POST /alice/<TOKEN>`, enforces a
   `user_id` allowlist, greets on session open, logs each request with elapsed ms, and returns a
   valid 200 Диалоги answer on **any** upstream failure.
3. **Public HTTPS**: `sudo tailscale funnel --bg --https=443 http://127.0.0.1:PORT_EDGE`.
   Publish the proxy port, not the app port — token and allowlist stay in front.
4. **Keep it alive**: systemd for the app, `cron @reboot` + a 3-minute watchdog for the proxy.
   A Funnel pointing at a dead port silently breaks the skill.
5. **Skill**: `dialogs.yandex.ru/developer` -> private access -> Webhook URL with the token ->
   Alice's voice -> test in the console before touching the speaker.

## Verification

`*.ts.net` resolves to a `100.x` tailnet address on the host itself, so a local curl hits your own
web server. Test the way Yandex does — against the public edge:

```bash
IP=$(dig +short <host>.ts.net @1.1.1.1 | head -1)
curl -s --resolve "<host>.ts.net:443:$IP" -X POST "https://<host>.ts.net/alice/<TOKEN>" \
  -H 'Content-Type: application/json' -d @payload.json
```

Expect HTTP 200 with a real model answer. Prove the guards too: wrong token -> 404, foreign
`user_id` -> polite refusal, dead upstream -> 200 with a spoken phrase.

## Common Mistakes

See `references/endpoint-and-pitfalls.md` for the full verified list. The four that cost the most:

- **Free tunnels are unusable for a webhook.** `localhost.run` rotates the subdomain on its own;
  `cloudflared` quick tunnels are blocked on some networks. Use Tailscale Funnel.
- **Never answer 500 or an empty body.** Yandex surfaces it as «HTTP ошибка 500» and the session
  dies. Catch upstream errors and return 200 with a spoken phrase.
- **`httpx` inherits `HTTP_PROXY`** and silently sends a localhost call to the system proxy.
- **The session-open request carries an empty utterance** — greet on `session.new` instead of
  replying «не расслышал».

## References

- `references/alice-protocol.md` — request/response JSON, fields, limits, activation, session flow
- `references/endpoint-and-pitfalls.md` — endpoint options and every pitfall hit in practice
