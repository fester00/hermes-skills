# Piper-GPL CPU install and Russian voice recipe

Session context: user wanted a fast, GPU-free TTS for Russian and asked to evaluate `https://github.com/OHF-voice/piper1-gpl` alongside `kokoro`/`kokoro-onnx`. This recipe captures the exact working install on an Intel i5-9400F (6 cores) / 31 GB RAM / no GPU / Ubuntu 24.04.

## What piper1-gpl is

- Official GPL-3.0 fork of Piper by the Open Home Foundation.
- PyPI package: `piper-tts` (v1.6.0 at the time of writing).
- Runtime dependencies: `onnxruntime>=1,<2`, `pathvalidate>=3,<4`.
- Python support: 3.9–3.13.
- No PyTorch needed — very small footprint.

## Install

```bash
cd /mnt/data/natan-storage
mkdir -p Piper-GPL && cd Piper-GPL
uv venv venv --python 3.12
source venv/bin/activate
uv pip install piper-tts
mkdir -p voices
```

## Download a Russian voice

Piper voices live at `https://huggingface.co/rhasspy/piper-voices`. A medium Russian voice is about 60 MB.

### Option A: use the built-in downloader (recommended)

`piper-tts` ships a `download_voices` module that lists available voices and downloads both `.onnx` + `.onnx.json`:

```bash
# List all voices
python -m piper.download_voices

# Filter Russian voices
python -m piper.download_voices | grep '^ru_RU'

# Download one voice
python -m piper.download_voices ru_RU-denis-medium --download-dir voices/
```

### Option B: direct curl

```bash
curl -sL --max-time 120 -o voices/ru_RU-denis-medium.onnx \
  "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/ru/ru_RU/denis/medium/ru_RU-denis-medium.onnx"
curl -sL --max-time 60 -o voices/ru_RU-denis-medium.onnx.json \
  "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/ru/ru_RU/denis/medium/ru_RU-denis-medium.onnx.json"
```

### Verify the download

A truncated `.onnx` fails at load time with `ONNXRuntimeError : 7 : INVALID_PROTOBUF`. After downloading, confirm the file loads:

```bash
python - <<'PY'
import onnxruntime as ort
m = ort.InferenceSession('voices/ru_RU-denis-medium.onnx')
print('OK', [i.name for i in m.get_inputs()])
PY
```

Medium voices are ~60 MB; `ruslan-medium` was observed at 33 MB when a partial download occurred. If the size looks wrong, delete and re-download.

Available Russian voices: `denis`, `dmitri`, `irina`, `ruslan`.

## CLI usage

The `piper` CLI binary is installed into the same venv as the Python package:

```bash
piper -m voices/ru_RU-denis-medium.onnx \
      -c voices/ru_RU-denis-medium.onnx.json \
      -i input.txt \
      -f output.wav
```

Output is a mono 22050 Hz 16-bit WAV. The CLI is the fastest way to generate one-off samples; use the Python API only when you need programmatic control.

## Correct Python API (v1.6.0)

The API changed from older Piper examples. `PiperVoice.synthesize()` now returns an iterable of `AudioChunk` objects. Write `chunk.audio_int16_bytes` to a WAV file.

```python
import time
import wave
from pathlib import Path
from piper import PiperVoice

model_path = Path('voices/ru_RU-denis-medium.onnx')
config_path = Path('voices/ru_RU-denis-medium.onnx.json')

text = 'Привет, это тест локального синтеза речи на русском языке с помощью Piper.'
print(f'Text: {text}')

# Load model
start = time.time()
voice = PiperVoice.load(str(model_path), str(config_path))
print(f'Model loaded in {time.time() - start:.2f}s')

# Synthesize
output_path = 'test_ru.wav'
start = time.time()
with wave.open(output_path, 'wb') as wav_file:
    for chunk in voice.synthesize(text):
        wav_file.setnchannels(chunk.sample_channels)
        wav_file.setsampwidth(chunk.sample_width)
        wav_file.setframerate(chunk.sample_rate)
        wav_file.writeframes(chunk.audio_int16_bytes)
synth_time = time.time() - start
print(f'Synthesis done in {synth_time:.2f}s')

# Measure audio duration and RTF
with wave.open(output_path, 'rb') as w:
    frames = w.getnframes()
    rate = w.getframerate()
    audio_duration = frames / rate
    print(f'Audio: {audio_duration:.2f}s @ {rate} Hz')
    print(f'RTF: {synth_time / audio_duration:.3f}')
```

## Measured performance

| Machine | Voice | Text length | Audio length | Synthesis time | RTF |
|---|---|---|---|---|---|
| Intel i5-9400F (6 cores), 31 GB RAM | `ru_RU-denis-medium` | 14 words | 4.68 s | 0.19 s | **0.041** |
| Intel i5-9400F (6 cores), 31 GB RAM | `ru_RU-denis-medium` | 18 words | 6.70 s | 0.24 s | **0.036** |

1 second of audio needs ~0.04 seconds of CPU time — fast enough for real-time or interactive use.

## Comparison with Kokoro on Russian

| Engine | Russian support | RTF on Russian | Quality | Notes |
|---|---|---|---|---|
| **Piper-GPL** | ✅ Native voices | ~0.04 | ✅ Good native Russian | Best choice for Russian CPU TTS |
| **Kokoro (kokoro 0.9.4)** | ❌ No official Russian; espeak-ng fallback | ~0.35 | ❌ Unintelligible | Reads Cyrillic as Latin phonemes; audio stretched to 12s |
| **kokoro-onnx** | ❌ `en-us`/`en-gb` only | — | — | Do not use for Russian |

## Pitfalls

- Older Piper code examples use `voice.synthesize(text, wav_file)`, which no longer works in v1.6.0. Iterate over `AudioChunk` instead.
- Piper can emit an `onnxruntime` GPU warning on CPU-only systems; it is harmless and inference still runs on CPU.
- A voice needs both the `.onnx` model and the matching `.onnx.json` config file.
- Kokoro looks attractive for English/multilingual, but do not recommend it for Russian — it has no Russian G2P or voice and falls back to broken espeak-ng behavior.

## Conclusion

For local Russian TTS on CPU, use **Piper-GPL** (`piper-tts`). It is ~8–10× faster than Kokoro on Russian and produces intelligible native Russian speech. Reserve Kokoro for supported languages (English, Spanish, French, Italian, Portuguese, Hindi, Japanese, Mandarin Chinese).
