# Яндекс.Диалоги skill protocol — essentials

## Request body (what the platform POSTs to the webhook)

```json
{
  "meta":    {"locale": "ru-RU", "timezone": "Europe/Moscow", "client_id": "..."},
  "session": {"message_id": 0, "session_id": "<uuid>", "skill_id": "...",
              "user_id": "<account hash>", "new": true},
  "request": {"type": "SimpleUtterance", "command": "привет",
              "original_utterance": "Привет, что такое энтропия?",
              "nlu": {"tokens": [...], "entities": []}},
  "version": "1.0"
}
```

Facts that matter:

- `session.user_id` — stable per account+skill. This is the value to put in an allowlist.
  It is identical for console tests and for the physical speaker.
- `session.new: true` opens the session, and that request usually has an **empty**
  `original_utterance` (often an empty `command` too). Greet on this turn; do not answer
  «не расслышал».
- Text to answer = `original_utterance` if non-empty, else `command`.
- Later turns arrive with `new: false` and the same `session_id`; keep history per `session_id`.
- Real payloads carry extra unknown fields — parse leniently (ignore unknown keys).
- Requests arrive from Yandex infrastructure (e.g. `5.45.207.x`), not from the speaker's LAN IP.

## Response body

```json
{"version": "1.0",
 "response": {"text": "...", "tts": "...", "end_session": false}}
```

- `response` and `version` are required. There is **no `session` object** in the answer.
- `end_session` lives inside `response`.
- `text` and `tts` are each capped at 1024 chars. For speech keep answers under ~600 chars.
- `tts` supports `<speaker ...>` markup: effects, whisper, library sounds, uploaded audio and
  different SpeechKit voices. Tags do not count towards the 1024 limit.
- Buttons, if used, are arrays of objects (`title`/`payload`/`url`/`hide`), not strings.

## Timing

- Hard timeout **4.5 s** end to end: connection + transit + skill execution + return.
- Exceeded -> the skill session terminates and Alice says the skill is not responding.
- Keep a 4.0 s internal budget plus a filler / deferred-delivery pattern for slow models.
- Measure real latency against the chosen model before promising a setup works.

## Publishing a skill

- Console: `dialogs.yandex.ru/developer`. Backend is a Webhook URL (HTTPS, full chain) or a
  Yandex Cloud Function (free for skills).
- **Private access** restricts the skill to its author on every surface, including the author's
  own speaker — exactly right for personal use, and no catalogue moderation needed.
- Name: 2–4 words, must not contain «Алиса», «Яндекс» or «Станция»; up to 3 activation names.
- Voice is chosen in the skill settings; Alice's voice gives the most native feel.
- Activate by voice: «Запусти навык <имя>». The skill stays in session for a limited time, then
  further questions go back to Alice's own brain — the service never sees those.

## What is NOT possible

- Replacing Alice's model on stock firmware: the assistant runs in the cloud and the device is a
  thin client over pinned TLS. No user-facing model choice exists.
- Intercepting arbitrary utterances: the platform forwards only what is said inside a skill session.
- Reading the microphone stream: speaker audio is not exposed, so a custom wake word or ASR on the
  device is out of reach.
- Reflashing: bootloader consoles are protected (RSA challenge) and newer boards ship locked.
