# TTS project comparison — July 2026

Real evaluation for a CPU-only machine: Intel i5-9400F, 31 GB RAM, GeForce 210 (no usable GPU), Python 3.12.3.

## Candidates evaluated

| Project | Type | Languages | Parameters | CPU OK? | Verdict |
|---------|------|-----------|------------|---------|---------|
| **Kokoro** | Lightweight neural TTS | EN, ES, FR, IT, PT, HI, ZH, JA (RU via fallback) | 82 M | ✅ Yes | **Recommended** |
| **MARS5-TTS** | Flow-matching TTS | English only | ~1.2 B | ❌ No | Too large, needs GPU |
| **Rapida voice-ai** | Voice-agent orchestration platform | Depends on provider | N/A (cloud) | N/A | Not a TTS engine |
| **LiveKit agents** | Real-time voice agent framework | Depends on provider | N/A (cloud) | N/A | Not a TTS engine |

## Kokoro details

- `pip install kokoro soundfile`
- System dependency: `espeak-ng`
- PyTorch-based, but small enough for CPU.
- Download size modest (~330 MB).
- Apache 2.0 license.
- Russian not officially supported; `espeak-ng` fallback may work but quality uncertain.

## MARS5-TTS details

- Requires PyTorch, torchaudio, librosa, vocos, encodec.
- README explicitly states hardware requirement: GPU capable of holding ~750 M active parameters.
- 1.2 B total parameters (AR 750 M + NAR 450 M).
- English only.
- GNU AGPL 3.0.
- On the target CPU-only machine this would be impractical.

## Rapida / LiveKit

Both are platforms/frameworks for building voice AI applications. They route STT/LLM/TTS through external providers (OpenAI, Cartesia, ElevenLabs, Deepgram, etc.). They are overkill for a simple "generate an audio file from text" task and require API keys, Docker, and/or LiveKit server.

## Hardware check used

```bash
python3 --version
free -h
nvidia-smi  # failed — no NVIDIA driver
lspci | grep -iE "vga|3d|display"
```

## Recommendation for this machine

**Kokoro** is the only candidate that runs locally without GPU and fits in RAM. If Russian quality is insufficient, next step is **Piper** (small, Russian voices, CPU-fast) or **Silero** (better Russian, but non-commercial license for free use).

## Installation command summary

```bash
sudo apt-get install espeak-ng
python3 -m venv ~/.venvs/kokoro
source ~/.venvs/kokoro/bin/activate
pip install kokoro soundfile
```

## Smoke test

```python
from kokoro import KPipeline
import soundfile as sf

pipeline = KPipeline(lang_code='a')
generator = pipeline("Hello world", voice='af_heart')
for i, (gs, ps, audio) in enumerate(generator):
    sf.write(f'{i}.wav', audio, 24000)
```
