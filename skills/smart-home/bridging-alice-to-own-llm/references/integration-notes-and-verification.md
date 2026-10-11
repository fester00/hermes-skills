# Широкий контекст интеграции: маршрут B, поиск устройства, выход, чек-лист проверки

> Поглощено 2026-10-11 из навыка `yandex-alice-integration` (навык удалён, содержимое сохранено здесь).

# Yandex Alice Integration

Wiring third-party backends into speakers with Alice: a Yandex Dialogs skill that
routes the user's speech to your own model, local control of the device, and an
honest account of what is impossible.

## When to use

- The user wants their speaker (Станция / Миди / Мини / Макс) to answer with a
  self-hosted or third-party LLM instead of the cloud assistant.
- Building or deploying a **Yandex Dialogs skill** (навык Алисы) with a webhook backend.
- Controlling a Yandex speaker locally from scripts or Home Assistant, or reading its state.
- Deciding whether a speaker can be reflashed or repointed to another backend.

## Hard limits — state these before proposing anything

- The assistant runs in Yandex's cloud; the device is a thin client on a
  TLS-pinned channel. There is **no supported way to repoint the assistant to another model**.
- The microphone stream is **not exposed**. You cannot run your own wake word or
  ASR on the device, and you cannot intercept arbitrary utterances.
- **Reflashing is off the table.** Amlogic-based stations guard the U-Boot console
  with a custom RSA-2048 challenge (Yandex "Rabbit Hole"): one wrong answer reboots
  the device, brute force is pointless, and public research covers only part of the
  line. No custom firmwares exist, newer boards ship or remotely receive a bootloader
  password, and the failure mode is a bricked speaker. Do not offer it as a path.
- What *is* possible: keep Alice as the mouth, and make a **Dialogs skill** the brain.

## Route A — your own model behind a Dialogs skill

The user says "Алиса, запусти навык <name>"; from then on every utterance reaches
your webhook as `original_utterance`, your code calls your model, and Alice speaks
the returned text in the voice chosen in the skill settings.

Protocol contract — take it from the official docs, never improvise it:

- Response body is exactly `{"version":"1.0","response":{...}}`. There is **no
  `session` object in the response**; `end_session` lives *inside* `response`.
  Buttons are objects, not strings. Inventing a `session` key in the reply is a real
  failure mode — pin it with a test asserting the top-level keys are exactly
  `{version, response}`.
- Hard timeout **4,5 s** for the whole round trip: connection + delivery to the skill
  + the skill's own work + delivery back. `response.text` and `response.tts` are capped
  at **1024** characters.
- Backend must be **HTTPS with a fullchain certificate**; self-signed is rejected.
  A Yandex Cloud Function is a free alternative backend.
- Skill name: 2–4 words, must not contain «Алиса»/«Яндекс»/«Станция»; up to 3
  activation names for pronunciation variants.
- **Тип доступа = Приватный** — the skill then works only for its author on every
  surface where they are logged in. This is the right setting for personal use.
- **The platform opens a session with an empty utterance** (`new: true`, `command` and
  `original_utterance` both empty). Answering that with the "ask again" hint means the first thing
  the user hears when launching the skill by voice sounds like a failure. Return a short greeting
  for a NEW empty session; keep the ask-again hint for empty turns inside an ongoing session.
  A greeting that runs before the model call also answers instantly, which keeps the launch snappy.
- **Let the bridged model answer honestly about what it is.** The owner's acceptance test is
  "did *my* model answer, or the platform assistant?" — so the persona must be free to name its model
  and say whose server it runs on when asked. Instructing it to deny being a language model makes a
  working bridge impossible to verify from the speaker. Keep the separate rule that it must not
  impersonate Алиса/Яндекс (that is not the same thing as naming its own model), and write the
  expected answer into the runbook so the check is repeatable.
- **Fact-check every self-description before it goes into a persona.** A strong character states the
  prompt's claims about itself louder and more confidently than a neutral assistant would: a prompt
  saying "runs on the owner's home server" produced the flat assertion "никаких тебе облаков, всё
  домашнее" — while the weights were served from the provider's cloud through a local gateway.
  Establish what is actually local (a gateway process is not a model) before writing hosting into a
  character, because the persona will defend it.

## Keep-alive inside the 4,5 s budget

Set an internal budget (~4,0 s). When the model misses it, answer with a filler
("Секунду, я подумаю."), keep the generation running, and deliver the finished
answer on the next turn.

- Store the in-flight task per session and **put it back into the store when it is not
  finished yet**. Taking it out and dropping it loses an almost-ready answer and starts
  a duplicate generation on the user's next words.
- Bound the HTTP client separately from the model timeout, so a dead provider cannot
  consume the whole window.
- A model that "thinks" can burn hundreds of tokens on a one-word answer and return an
  empty `content` with `finish_reason=length`. Give such models a large `max_tokens` or
  keep them out of the fast lane.

## Exit: never trap the user inside the skill

While a skill is open, the platform's own assistant and every other skill are unreachable — the
platform documents this outright. A skill that always answers `end_session: false` therefore feels
like a locked room, and the user has no way back to Alice.

- The platform handles «Алиса, хватит», «Алиса, вернись», «Стоп», «Закончить», «Выйти» itself.
- Handle the same words in the skill too and return `end_session: true` with a short goodbye, so the
  session is released at once instead of lingering to the platform's timeout. Answer the exit without
  a model call — it must be instant.
- Match on **whole tokens** and allow polite inserts («выйди, пожалуйста», «выйти из навыка»), but
  require at least one real exit word: otherwise «расскажи про слово хватит» closes the skill.
- Keep a handful of goodbye variants and pick one at random — a fixed sentence becomes a catchphrase
  by the third exit.

## Gate the public endpoint before it is useful

- Fill `ALLOWED_USER_IDS` from the `user_id` in the incoming request (log it once, then
  restrict). Until it is known, serve the route under a **secret path token**
  (`/alice/<random-token>`) rather than plain `/alice`.
- **Put edge POLICY in a layer you can restart without root.** The service under systemd needs
  sudo to restart, so the userspace proxy in front of it carries everything you will still want to
  change after launch: per-request logging (caller, `user_id`, session id, status, question,
  answer), the secret path token, the `user_id` allowlist, and the launch greeting. That makes
  `ALLOWED_USER_IDS` fillable and behaviour tunable from a live session without ever touching the
  unit — later it also separates platform traffic from your own test curls. Rebuild the app-side
  copy of these rules the next time a restart is available anyway.
- Bind the app to `127.0.0.1` and publish it only through the tunnel or reverse proxy.
- Publishing options, best first: an existing domain with a valid certificate (add a
  `location` vhost), a tunnel that terminates HTTPS for you (no white IP needed), or a
  cloud function. Whichever you choose, **verify the URL from outside the LAN** before
  typing it into the skill settings — a LAN-side check proves nothing.
- If the chosen tunnel is not installed yet, its setup needs root: hand the user one
  idempotent script (see the reference), never a password prompt you cannot answer.

## Route B — Home Assistant + local speaker control

The community integration for Yandex speakers (AlexxIT/YandexStation) uses the
device's local Glagol channel:

- TTS in Alice's voice (effects, whisper, alternate SpeechKit voices), arbitrary
  commands, playback and volume state, alarms, shopping list. Local mode has no
  100-character limit and the speaker keeps listening after the phrase.
- Local and cloud control coexist — nothing is lost by enabling it. Enabling the
  integration creates a service scenario named `ХА UUID` in the Yandex app; leave it alone.
- **Interception is the weak spot.** Catching the user's own phrases works only for a
  handful of fixed phrases set up as Yandex scenarios, and reading the speaker's answers
  is limited to a small phrase list. Never promise "replace Alice for any question".

## Device discovery on the LAN

- Speakers announce `_yandexio._tcp.local` over mDNS (multicast `224.0.0.251:5353`). The
  TXT record carries `deviceId`, `platform=cucumber`, `cluster=yes`; the PTR name looks
  like `YandexIOReceiver-<deviceId>`.
- **ICMP often does not answer**, so a ping sweep alone misses the speaker. Query mDNS or
  read the ARP table instead.
- Local protocol: TCP **1961**, wrapped in **TLS**. An empty reply to plaintext JSON means
  the channel is encrypted and expects a key — that is expected, not a fault.
- Reverse DNS usually reveals the model, e.g. `Yandex-Station-Midi-<id>.lan`.
- Yandex hardware registers under OUI `3C:0B:4F` (originally Yandex Services AG, now
  Intertech Services AG, Lucerne) — a vendor lookup confirms it is a Yandex device.

## A tunnel is not an endpoint: lifecycle and blame

A free tunnel gets the skill tested today; it is not what a working skill runs on.

- **Idle tunnels are dropped** by the provider (`tunnel activity timeout`), after which the public
  URL answers `no tunnel` / 502 and the skill platform reports a webhook error. Keep a keepalive
  hitting the **public** health URL every 1–2 minutes.
- **The URL changes when the tunnel is re-established**, so the user has to paste it into the skill
  settings again. Something that must survive the day needs a tunnel with a stable hostname (see the
  reference) rather than a throwaway one.
- **Blame the layer in order.** A platform message like "HTTP ошибка в ответе webhook: 500" says the
  call failed, not where. Put the platform's error next to your own service journal: no matching
  request at that timestamp ⇒ the call never arrived (edge/tunnel, or a stale URL in the settings);
  a request with a non-200 ⇒ the app is at fault. Never start editing application code on the
  strength of a platform error message alone.
- A logged request with **no** following model call is normal — an empty utterance is answered by
  the "ask again" hint without touching the model. Do not chase it as a bug.

## Verification checklist — all four, in order

1. Unit tests green, including one that pins the response shape (no `session` key).
2. Local smoke test with a real Dialogs payload: `curl --noproxy '*' -X POST .../alice`.
3. One **live** call through the real model, with the latency compared to the budget.
   Mocked tests pass happily while the real provider call is broken.
4. After the skill exists: a real voice test on the device, then lock the endpoint with
   `ALLOWED_USER_IDS`.

## Pitfalls

- **Localhost calls must not inherit proxies.** httpx and curl honour `HTTP(S)_PROXY`, so a
  call to the local model endpoint silently leaves the machine and dies at the timeout with
  an empty error. Use `trust_env=False` (httpx) and `--noproxy '*'` (curl). Mechanism,
  diagnostics and the regression test: `references/public-endpoint-and-root-script-hygiene.md`.
- **The platform censors the audio, not your text.** An obscene word the model willingly produced is
  beeped at synthesis time; nothing in your logs shows it. Masking the token in `response.tts`
  restores the word. Verified mask variants, the one-utterance calibration and the persona-writing
  recipe: `references/voice-output-and-persona.md`.
- Do not let model markdown reach TTS: strip code fences, `*_`#|`, list bullets and links
  before returning the text.
- Keep the reply short (a few hundred characters). A 1024-character answer is a wall of
  speech in a room, not an answer.

## References

- `references/public-endpoint-and-root-script-hygiene.md` — publishing the webhook safely, the
  localhost-proxy trap with its regression test, and the checklist for authoring the root-run
  setup script the user executes.
- `references/voice-output-and-persona.md` — writing the speaker's character with guardrails,
  in-character greeting and exit, and stopping the platform from beeping obscene words in TTS.
