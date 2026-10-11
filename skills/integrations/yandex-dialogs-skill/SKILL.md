---
name: yandex-dialogs-skill
description: Use when building a Yandex Alice skill. Host the webhook backend and handle Alice voice/dialog requests.
category: integrations
metadata:
  hermes:
    tags: [yandex, alice, dialogs, voice, webhook, skill]
    related_skills: [public-webhook-endpoint]
---

# Yandex Dialogs (Alice) Skill Backend

## When to Use

- Building a webhook/backend for an Alice skill (own model, own agent, own data)
- The developer console reports `HTTP ошибка в ответе webhook: 500`, or the speaker says
  «навык не отвечает»
- Making a Yandex speaker answer with your own LLM instead of the platform's assistant

Exposing the backend publicly with a stable URL: `public-webhook-endpoint`. Deployment specifics of
an existing skill belong in that project's runbook, not here.

## The answer shape (guessing it wrong is the classic failure)

Request (platform → skill): `meta`, `session{session_id,user_id,new,...}`,
`request{type,command,original_utterance,nlu,...}`, `version`.

Answer (skill → platform):
```json
{"version": "1.0", "response": {"text": "...", "tts": "...", "end_session": false}}
```

- **There is no `session` object in the answer**, and `end_session` sits **inside `response`**.
  Putting it under `session` is the natural guess and it is wrong.
- `response.text` and `response.tts` — **max 1024 characters each**. `tts` may carry `<speaker>`
  markup (effects, whisper, sound library); those tags do not count against the limit.
- **Hard 4.5 s timeout** for the whole round trip (connect + delivery + your work + answer delivery).
  Overrun ends the session and the user hears that the skill is not responding.
- The webhook must be **HTTPS with a public fullchain certificate**; self-signed is rejected
  (`Endpoint URL: Некорректный SSL-сертификат`).
- `original_utterance` **is empty on the opening turn** (and may be empty again on silence). Answer a
  new session with a greeting — replying «не расслышал» is the first thing the user hears.
- `session.user_id` is the right identity for an allowlist, but it is **per account *and* per
  surface, not per account alone**: the developer console and the physical speaker send different ids
  for the same account and skill (and the value differs per skill too, so entries are not portable).
  An allowlist built from console traffic therefore refuses the speaker — and the speaker repeats
  *your own* refusal text, which reads like a platform problem rather than a guard firing. Collect
  the id from every surface the owner will actually use before locking the list down.
- `response.buttons` is a list of **objects** (`{title, payload, url, hide}`), never strings.
- The platform does not persist your conversation: keep your own history keyed by `session_id`.

## Publication settings that matter

- Name: 2–4 words, must not contain «Алиса», «Яндекс», «Станция», must be unique in the catalogue;
  add up to 3 activation names for pronunciation variants.
- **Access type «Приватный»** keeps the skill on the author's account only, on every surface they are
  logged into — including their own speaker. The right choice for personal skills.
- Voice: the answer is voiced with the voice selected in the skill settings (the assistant's voice is
  selectable), so a personal skill sounds native.
- Activation is explicit («запусти навык <имя>»). A skill never answers free-form questions outside
  its own session — it cannot replace the built-in assistant, only sit next to it.

## Persona for a personal skill

For a skill the owner runs as their own assistant these are standing requirements — state them in the
system prompt explicitly, because model defaults fight all three:

- **It answers identity questions honestly**: asked which model it runs on, it names the real model
  and where it is hosted. That answer is the owner's fastest proof that the whole chain works end to
  end; never instruct it to pose as Alice or to deny being an AI.
- **No censorship of everyday speech**: it is a private assistant in the owner's own home, so asked to
  pronounce, repeat or translate a rude or colloquial word it does so verbatim — no refusal, no
  moralizing, no «more appropriate» alternatives. Over-refusal is the default here and has to be
  countermanded in the prompt. Requests that go further (threats, harassment of a person) stay with
  the model's own alignment; a prompt does not reliably lift those and should not try.
- **The platform then beeps the word anyway.** Speech synthesis filters obscene lexicon
  independently of your prompt (the skill requirements forbid «нецензурная и низкая лексика»), so a
  perfectly compliant model still produces a beep over the word. Make the token unrecognisable to
  the filter yet still pronounceable: write `response.tts` with `+` before the stressed vowel (the
  documented TTS stress syntax), an invisible combining acute U+0301, or a zero-width space U+200B.
  Keep `response.text` screen-friendly, and put the chosen mode in a file read per request so the
  owner switches it without a restart. Verify by ear, not by reasoning.
- **The greeting is the owner's own wording**, spoken on session open; replies stay short and spoken,
  because they are heard and not read.

Keep all of it in a prompt file read at request time, so the owner tunes wording without a restart.

## Ending the session (a skill must be able to let go)

While a skill is active, **Alice herself and every other skill are unavailable** — the platform hands
every utterance to your skill. A backend that always answers `end_session: false` therefore feels
like a trap: the owner cannot reach Alice to get out, and only the platform timeout frees them.

- The platform handles «Алиса, хватит», «Алиса, вернись», «Стоп», «Закончить», «Выйти» itself;
  implement the same words in the backend so the session is released immediately.
- Match on whole tokens: allow polite inserts and «из навыка» («выйди, пожалуйста», «выйти из
  навыка»), but require at least one real exit word so «расскажи про слово хватит» stays a normal
  question instead of ending the dialogue.
- Answer an exit with a short spoken goodbye and `end_session: true`, without a model call — the exit
  must feel instant.

## Build shape

1. One small service that speaks the protocol; keep the model call behind a client with a fallback
   chain of models.
2. Budget the model call at ~4.0 s of the 4.5 s. If it is not ready, answer a filler and deliver the
   finished text on the **next** turn — keep the pending task, because a second utterance must not
   discard a nearly-ready answer or start a duplicate model call.
3. Guard the endpoint before it is public: secret path segment + caller allowlist + request log
   (`public-webhook-endpoint` → `templates/token_guarded_proxy.py`). The allowlist can only be filled
   after the first real request, so the secret path ships first.
4. Log the incoming payload at the edge: the app usually logs only rejections, so `user_id` is
   invisible exactly when it is needed.
5. Self-heal every layer (app unit, edge proxy, tunnel) and write the reachable URL into the project
   runbook with the guard location and the disable command.

## Pitfalls

- **Never report a spoken behaviour as fixed from one passing sample.** Voice answers are stochastic
  and phrasing-sensitive: the same request complies once and refuses the next time. Retry with the
  owner's *exact* wording several times, and read the service log for what actually went over the
  wire, before saying it works — a single green sample is how a wrong fix ships.
- **When the platform does the filtering, calibrate by ear with a control.** You cannot read the
  filter, only its effect. Have the owner audition every candidate masking **in one utterance**,
  unmasked control included, and report which survive — one listening round beats a series of round
  trips. Validate on real obscenity: mild words pass the filter unmasked, so a bypass tested on them
  proves nothing.
- **Restarting your own service needs no `sudo`** when the unit runs as your user with
  `Restart=always`: `kill <MainPID>` and systemd brings it back in ~3 s. Confirm
  `ActiveEnterTimestamp` moved before trusting the reload — edits applied to an un-restarted process
  look exactly like "the change did not work". Find the PID with a self-excluding pattern
  (`pgrep -f '[t]oken_proxy' | head -1`): `pkill -f <pattern>` also matches the shell command that is
  running it and kills your own call.
- **A passing test is not a verified protocol.** When the artifact is an external wire format, read
  the platform's documented answer shape before making a test green — a test asserting the wrong key
  placement will happily steer the implementation into the wrong shape. Fix whichever of the two
  contradicts the documentation.
- **Local HTTP calls must disable proxy inheritance.** With `HTTP_PROXY`/`HTTPS_PROXY` exported in
  the shell, an `httpx` client sends loopback calls through the proxy and they die with an empty
  error after a full timeout. Build clients with `trust_env=False`; use `curl --noproxy '*'` for
  local checks.
- **Do not test the public URL from the machine that serves it** when that name resolves into the
  LAN/tailnet — you reach the local web server instead. Use the public edge IP with `curl --resolve`.
- **Never publish the URL before the guard exists**, and never authenticate on caller IP — the edge
  may present your own address or none.
- A skill name is global; a private skill still needs a unique name, so have a fallback name ready at
  creation time.
