# Platform-side output post-processing

The case where your service returns the right thing and the user still hears or sees something else.

## Diagnose before changing your code

1. **Check the platform's own rules.** Public integration requirements frequently forbid content
   classes (profanity, low-register lexicon, brand references) and the platform enforces them at
   runtime, separately from moderation. If a rule covers your output, assume an automatic filter.
2. **Locate the gap.** Log and diff what you returned against what the caller received. If your
   response is intact (`200`, full text, every field), the transformation happened **after** you — in
   the platform's synthesis, rendering or delivery layer. Re-prompting the model or adding retries
   cannot fix a filter you do not control.
3. **Confirm with a control.** Send the same content twice: once verbatim and once masked. If only the
   verbatim copy is altered, the platform is matching the token, not rejecting the intent.

## Masking a token so the filter misses it but the synthesiser still reads it

Mask the **token**, not the meaning: the platform matches strings, while the audio engine reads
phonetics. It works because the masked form is a different string but a recognisable word.

| Technique | Example marker | Notes |
|---|---|---|
| Documented stress syntax | `+` before the stressed vowel (`ж+опа`) | Best when the platform documents stress marks for speech — official syntax, so it survives validation |
| Combining diacritic | U+0301 after a vowel | Invisible; safe to also use in display text |
| Zero-width space | U+200B inside the word | Invisible; occasionally changes synthesis timing |
| Hyphenated letters | `ж-о-п-а` | Always audible and readable, but the audio spells the word out |

Put the masked form in the field the platform **speaks**, and a screen-friendly form in the field it
**displays** — a screen client showing `+` marks looks broken, an invisible diacritic does not.

## Calibrate by ear, in one round

Whether a given mask survives is decided by an opaque filter; the only instrument is a human
listening. Do not spend five round-trips on five variants:

- serve **all variants of the same word in a single answer**, numbered, triggered by one short phrase
  the user can say — plus **one unmasked control** proving the filter is still firing;
- keep the whole set short enough to be spoken inside one answer budget;
- make the mask mode a per-request runtime setting (`<topic>.conf`: `tts=<mode>`, `text=<mode>`) so
  switching the winner into production needs no restart;
- keep the trigger in place after choosing the winner — the filter will change under you, and
  re-calibration should cost one utterance.

## Traps

- **A tokeniser regex must include combining marks** (`[\u0300-\u036f]`). Models often emit a
  stressed vowel as base char + U+0301; a plain Cyrillic/Latin class splits such a word into two
  tokens and the masking silently misses exactly the cases it exists for. Strip combining marks
  before dictionary comparison.
- **Do not promise that masking removes all refusals.** A model can refuse on its own alignment for
  reasons no mask or prompt reaches — say so instead of iterating forever.
- **Re-check after any platform change.** These masks are a workaround against an undocumented
  filter: expect to re-run the calibration after the platform updates synthesis or rules.
