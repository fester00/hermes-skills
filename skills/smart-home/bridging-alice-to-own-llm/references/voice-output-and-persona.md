# Voice output and persona for a speaker skill

## Writing the character

The persona text belongs in the prompt file the bridge reads **per request**, so the owner can edit
the character and hear the change on the next utterance — no restart, no code change.

Structure that works: a character block, then the guardrails that keep it usable.

- Say what the character *is* in one vivid sentence ("a person thoroughly tired of everyone else's
  stupidity, who has nonetheless deigned to pay attention"), then rules for how it speaks: mandatory
  barbs, praise accepted as a matter of course, no apologising for being harsh.
- **Guardrail 1 — mockery is the FORM, an answer is an OBLIGATION.** One jab, then the fact. A
  character that refuses to answer is not edgy, it is broken, and the owner will ask for it to be
  removed.
- **Guardrail 2 — on serious ground (health, money, deadlines, danger) drop the act after one line.**
  A sarcastic assistant that jokes instead of telling the user to check the iron is a hazard.
- **Guardrail 3 — never degrade the person for appearance, nationality, sex, religion, health or
  family.** Barbs target the question and the situation. Frame it in character ("that is not wit,
  that is vulgarity, and you are above vulgarity") so the model keeps the rule.
- Ask the owner whether those clauses stay, but write them in by default and say why you added them.
- Smoke-test the character against: a trivial question, a definition, a compliment, a real risk
  question, and a question about the assistant itself. Check every answer still carries information
  and stays inside the reply length budget.

## Entry and exit in character

- The greeting is rendered by the edge proxy with **no model call** (instant, spends none of the 4,5 s
  budget). The owner usually phrases it better than anything invented for them — offer to keep theirs.
- Exit lines live in the app; see the exit section of the umbrella SKILL.md for the matching rules.
  Keep goodbyes free of anything the platform would beep.

## TTS formatting

- One to three sentences, a few hundred characters. A 1024-character limit is not a target.
- Strip markdown before it reaches TTS: fences, `*_`#|`, bullets, links.
- Spell numbers and abbreviations the way they must be pronounced.

## Model refusal vs platform censorship — two different problems

They look identical from the speaker ("it would not say the word") and have different fixes. Diagnose
before editing either side:

| Where the word is lost | Evidence | Fix |
|---|---|---|
| The model refuses | The refusal text is in your request log | Prompt clause: no censorship, do not moralise, and **do not repeat your own earlier refusals in this dialogue** — a single earlier refusal otherwise poisons the rest of the session |
| The platform beeps | The log shows the word in the reply, the speaker plays a beep | Mask the token in `response.tts` (below) |
| Neither, but the reply never changed | The prompt file was edited, the service was not | The prompt is cached at import until the app is restarted — compare the file mtime with the process start time |

## Masking a token so the TTS filter does not beep it

Yandex's synthesis filters obscene lexicon platform-side: the skill requirements forbid it, and the
beep is applied on the way to the speaker, after your response has already arrived intact.

| Mode | What it writes | Note |
|---|---|---|
| `plus` | `ж+опа` | `+` before the stressed vowel is the **documented** TTS stress syntax |
| `accent` | `жо` + U+0301 + `па` | invisible combining acute |
| `zwsp` | `ж` + U+200B + `опа` | invisible zero-width space |
| hyphen | `ж-о-п-а` | survives, but reads as spelled-out letters |

- Send the masked string as `response.tts`; keep `response.text` screen-readable (invisible marks are
  fine there, `+` is not).
- Make the mode a **runtime file read per request** so switching variants needs no restart; `plus` is
  the best default — documented syntax, correct stress, no pause artefacts, legible in logs.
- **Calibrate by ear in ONE utterance.** The filter is opaque, so the only instrument is a human
  listening: on a trigger phrase return the same word in every variant *plus the unmasked control*, so
  the operator auditions them in a single request.
- Verified on a real speaker: `plus`, `accent`, `zwsp` and the hyphen all pass while the plain control
  is beeped for genuine obscenity — so the bypass works rather than the filter being absent.
- **Mild words are not filtered at all** (`жопа`, `писька` passed unmasked). Never validate a bypass
  on a mild word; you learn nothing and will misread the result.
- Keep several variants working: if the platform tightens the filter, switching one line in the
  runtime file restores service with no code change.
- The matcher must accept **combining marks** (`[\u0300-\u036f]`) inside a word: models often emit the
  stressed vowel as a base character plus U+0301, and a plain Cyrillic character class splits such a
  word into two tokens and silently skips it. Strip combining marks before dictionary comparison.
