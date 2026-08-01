# Piper Russian voice comparison recipe

Session context: user already had Piper working as the Hermes TTS provider with `ru_RU-denis-medium`. They wanted short (~10 s) sample clips of all available Russian Piper voices to compare and pick the preferred one.

## Available Russian voices

```text
ru_RU-denis-medium
ru_RU-dmitri-medium
ru_RU-irina-medium
ru_RU-ruslan-medium
```

All are medium-quality voices, ~60 MB per `.onnx` model, mono 22050 Hz 16-bit WAV output.

## Suggested test text

A good comparison text should exercise vowels, consonants, intonation (statement/question/exclamation), and numbers:

```text
Здравствуйте! Это тестовый образец русского голоса. Меня зовут Пайпер, и я произношу слова с разной интонацией: вопросы, восклицания, а также цифры — семнадцать, двести тридцать шесть.
```

Length on the four voices (observed on one run):

| Voice | Duration |
|---|---|
| denis | ~12.4 s |
| dmitri | ~11.1 s |
| irina | ~14.7 s |
| ruslan | ~11.9 s |

## One-liner: generate all samples

```bash
VOICE_DIR=~/.hermes/cache/piper-voices
OUT_DIR=/tmp/piper-ru-voice-samples
TEXT="Здравствуйте! Это тестовый образец русского голоса. Меня зовут Пайпер, и я произношу слова с разной интонацией: вопросы, восклицания, а также цифры — семнадцать, двести тридцать шесть."
mkdir -p "$OUT_DIR"
printf '%s\n' "$TEXT" > "$OUT_DIR/test_text.txt"

for voice in ru_RU-denis-medium ru_RU-dmitri-medium ru_RU-irina-medium ru_RU-ruslan-medium; do
  piper -m "$VOICE_DIR/$voice.onnx" \
        -c "$VOICE_DIR/$voice.onnx.json" \
        -i "$OUT_DIR/test_text.txt" \
        -f "$OUT_DIR/$voice.wav"
done
```

The `piper` binary is in the same venv where `piper-tts` is installed (e.g. `~/.hermes/hermes-agent/venv/bin/piper`).

## Verify durations

```bash
python3 - <<'PY'
import wave, glob
for p in sorted(glob.glob('/tmp/piper-ru-voice-samples/*.wav')):
    with wave.open(p) as w:
        print(f'{p}: {w.getnchannels()}ch {w.getframerate()}Hz {w.getsampwidth()*8}bit {w.getnframes()/w.getframerate():.2f}s')
PY
```

## Pitfalls

- `ruslan-medium` may partially download and appear as ~33 MB; a truncated `.onnx` will fail with `INVALID_PROTOBUF` at inference. Re-download if the size is wrong.
- The `--download-dir` downloader may need a retry on slow networks; verify each `.onnx` is ~60 MB.
- GPU discovery warnings from `onnxruntime` on CPU-only machines are harmless; inference still runs on CPU.
