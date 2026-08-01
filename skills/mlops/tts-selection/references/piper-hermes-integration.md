# Piper TTS integration with Hermes Agent

Session context: user had a working local CosyVoice CPU install but wanted a faster local TTS for Russian. We installed Piper-GPL (`piper-tts`) and configured it as the default Hermes TTS provider.

## Why Piper for Hermes

- **CPU-only**, no GPU needed.
- **Very fast**: RTF ~0.04 on a 6-core Intel CPU (1 second of audio needs ~0.04 seconds of compute).
- **Native Russian voices**: `ru_RU-denis`, `ru_RU-dmitri`, `ru_RU-irina`, `ru_RU-ruslan`.
- **Tiny per-voice footprint**: ~60 MB per medium voice.
- Works offline, no API keys.

## Installation

### 1. Install `piper-tts` into the Hermes Python environment

Hermes runs in its own venv (`~/.hermes/hermes-agent/venv`). Install Piper there, not just in a project venv:

```bash
/home/natan/.hermes/hermes-agent/venv/bin/python -m pip install piper-tts
```

### Option A: use the built-in downloader

```bash
~/.hermes/hermes-agent/venv/bin/python -m piper.download_voices ru_RU-denis-medium --download-dir ~/.hermes/cache/piper-voices
```

### Option B: direct curl

```bash
mkdir -p ~/.hermes/cache/piper-voices
cd ~/.hermes/cache/piper-voices
curl -sL -o ru_RU-denis-medium.onnx \
  "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/ru/ru_RU/denis/medium/ru_RU-denis-medium.onnx"
curl -sL -o ru_RU-denis-medium.onnx.json \
  "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/ru/ru_RU/denis/medium/ru_RU-denis-medium.onnx.json"
```

### Verify the download

A truncated `.onnx` fails at load time. After downloading, confirm size and loadability:

```bash
ls -lh ~/.hermes/cache/piper-voices/ru_RU-denis-medium.onnx   # should be ~60 MB
~/.hermes/hermes-agent/venv/bin/python - <<'PY'
import onnxruntime as ort
m = ort.InferenceSession('~/.hermes/cache/piper-voices/ru_RU-denis-medium.onnx')
print('OK')
PY
```

### 3. Configure Hermes to use Piper

```bash
hermes config set tts.provider piper
hermes config set tts.piper.voice ru_RU-denis-medium
hermes config set tts.piper.voices_dir /home/natan/.hermes/cache/piper-voices
```

Resulting config snippet:

```yaml
tts:
  provider: piper
  piper:
    voice: ru_RU-denis-medium
    voices_dir: /home/natan/.hermes/cache/piper-voices
```

### 4. Test

Use Hermes `text_to_speech` tool or the in-session `/voice tts` command.
Hermes will generate `~/.hermes/audio_cache/tts_*.ogg` using Piper.

## Voice cache

Hermes caches Piper voices in `~/.hermes/cache/piper-voices` by default. Keep the `.onnx` and `.onnx.json` files together with matching basenames.

## Available Russian voices

| Voice | Gender | Quality tier | Size |
|---|---|---|---|
| ru_RU-denis | male | medium | ~60 MB |
| ru_RU-dmitri | male | medium | ~60 MB |
| ru_RU-irina | female | medium | ~60 MB |
| ru_RU-ruslan | male | medium | ~60 MB |

Swap the `voice` value in config to try another.

## Pitfalls

- **Install in the right venv.** `piper-tts` must be importable from the Python interpreter that runs Hermes (`~/.hermes/hermes-agent/venv/bin/python`). Installing only in a project venv will give `ModuleNotFoundError` at synthesis time.
- **Both files required.** A missing `.onnx.json` next to the `.onnx` will cause Piper to fail loading the voice.
- **No Russian in Kokoro-onnx.** The `kokoro-onnx` wrapper only supports `en-us`/`en-gb`. For Russian, use Piper (or Silero) instead.
