---
name: piper-tts
description: Use when the user asks for local CPU text-to-speech with Piper, especially for Russian.
version: 1.0.0
author: Master Ugwai
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [piper, tts, audio, voice, local, russian]
    related_skills: [tts-selection]
---

# Piper local TTS

Use when the user asks for a voice/audio message or local text-to-speech on this host. Piper runs entirely on CPU, needs no cloud API, and produces Russian speech quickly.

## Default voice preference

This user prefers **fast local CPU TTS for Russian**. Default to the Russian Piper voice in the local cache; the current preferred voice is `ru_RU-dmitri-medium`. If it is missing, use another `ru_RU-*` voice from the cache (e.g. `ru_RU-denis-medium`).

## Where Piper lives on this host

| Path | Purpose |
|---|---|
| `/mnt/data/natan-storage/Piper-GPL/venv/bin/piper` | Piper executable |
| `/mnt/data/natan-storage/Piper-GPL/venv/bin/activate` | Virtualenv activation |
| `/mnt/data/natan-storage/.hermes/cache/piper-voices/` | Downloaded ONNX voices |
| `/mnt/data/natan-storage/.hermes/cache/piper-voices/ru_RU-dmitri-medium.onnx` | Preferred Russian voice (when present) |

## One-shot generation

```bash
source /mnt/data/natan-storage/Piper-GPL/venv/bin/activate
VOICE=/mnt/data/natan-storage/.hermes/cache/piper-voices/ru_RU-dmitri-medium.onnx

# Fallback if dmitri is missing
[ -f "$VOICE" ] || VOICE=/mnt/data/natan-storage/.hermes/cache/piper-voices/ru_RU-denis-medium.onnx

echo "Ваш текст здесь" | piper --model "$VOICE" --output_file /mnt/data/natan-storage/output.wav
```

Send the result as a Telegram voice message:

```
[[audio_as_voice]]
MEDIA:/mnt/data/natan-storage/output.wav
```

## Verify the file

```bash
file /mnt/data/natan-storage/output.wav
ls -lh /mnt/data/natan-storage/output.wav
```

Expected: `RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, mono 22050 Hz`.

## Voice discovery

```bash
ls -1 /mnt/data/natan-storage/.hermes/cache/piper-voices/*.onnx
```

Prefer `ru_RU-dmitri-medium` for this user; otherwise pick another `ru_RU-*` voice. Do not download voices unless the user explicitly asks — the cache is expected to contain the needed Russian model.

## Pitfalls

- **Do not run Piper from the bare system Python** — it is installed only in the Piper-GPL virtualenv. Activate it first or use the full path to the venv `piper` binary.
- **The ONNX file and its `.onnx.json` config must sit together** in the voices directory. Piper needs the JSON sidecar; do not move or rename the model without the matching JSON.
- **Piper logs a harmless GPU warning** (`Failed to detect devices under /sys/class/drm/card0`) when no GPU is present — it still runs on CPU and produces valid audio. Ignore the warning unless the output file is missing or zero bytes.
- **Use an absolute output path** in `/mnt/data/natan-storage/` (or another persistent location), not `/tmp/`, so the file survives for Telegram delivery.

## Related

- `tts-selection` skill for comparing TTS engines and choosing between local/cloud options.
- Telegram delivery: place `[[audio_as_voice]]` on its own line before the `MEDIA:/path` tag.
