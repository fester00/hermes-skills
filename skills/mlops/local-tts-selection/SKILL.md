---
name: local-tts-selection
description: |
  Evaluate, select, and deploy local text-to-speech (TTS) models on CPU-only or
  low-GPU Linux machines. Covers lightweight open-weight models (Kokoro, Piper,
  Silero), research models that need GPU (MARS5-TTS, Matcha-TTS), orchestration
  platforms, and provider-agnostic agent frameworks. Helps choose a TTS that fits
  the hardware, language, and integration constraints.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [tts, text-to-speech, local-inference, cpu, gpu, audio, kokoro, piper, silero, mars5, matcha-tts]
    related_skills: [audiocraft-audio-generation, heartmula, songsee]
---

# Local TTS Selection & Deployment

Class-level guide for choosing and running local text-to-speech models.

## When to use this skill

- User wants local/offline TTS without cloud API keys.
- User asks "какую TTS поставить", "какой TTS движок выбрать", "что запустится на CPU".
- Need to evaluate a GitHub TTS project for feasibility on a specific machine.
- Integrating TTS into Hermes `text_to_speech` or another agent workflow.

## Decision matrix

| Need | Recommended | Why |
|---|---|---|
| Lightweight, fast, CPU-only, English + major languages | **Kokoro** | 82M params, pip install, runs on CPU |
| Quality Russian voice, local, low resource | **Silero / Piper** | Russian voices out of the box |
| Voice cloning / prosody control, English only, has GPU | **MARS5-TTS / Matcha-TTS** | Research quality, needs VRAM |
| Real-time voice agent platform | **LiveKit Agents / Rapida** | Not a TTS engine; needs cloud providers |
| Music / sound effects generation | **AudioCraft / HeartMuLa** | Different domain; see related skills |

## Hardware assessment checklist

Before recommending any TTS, check:

1. `python3 --version` (many TTS want 3.10–3.12)
2. `which nvidia-smi && nvidia-smi` (GPU?)
3. `free -h` (RAM)
4. `df -h` (disk space for models)
5. `which uv || which pip` (packaging)

## Project evaluation template

When user links a TTS repo, answer these questions:

- **Languages**: What languages are pretrained models trained on?
- **Parameters / model size**: Can the model fit in RAM/VRAM?
- **Dependencies**: PyTorch version, espeak-ng, special build steps?
- **License**: AGPL / Apache / GPL / commercial?
- **CPU support**: Does README mention CPU inference or require GPU?
- **Installation path**: pip install vs Docker vs build from source?

## Models

### Kokoro

- Repo: https://github.com/hexgrad/kokoro
- Params: 82M
- Python: >=3.10, <3.14
- Install: `pip install kokoro soundfile` + system `espeak-ng`
- Languages: en, es, fr, it, pt, hi, ja, zh (via `misaki`); Russian via espeak-ng fallback is experimental
- CPU: ✅ Yes
- GPU: Optional
- Integration example:
  ```python
  from kokoro import KPipeline
  import soundfile as sf
  pipeline = KPipeline(lang_code='a')
  for i, (gs, ps, audio) in enumerate(pipeline("Hello world", voice='af_heart')):
      sf.write(f'{i}.wav', audio, 24000)
  ```
- Best for: quick local TTS, English/multilingual, low resource

### Piper

- Repo: https://github.com/rhasspy/piper
- Languages: many, including Russian voices
- CPU: ✅ Very fast
- Best for: Raspberry Pi / edge / low-latency announcements

### Silero

- Repo: https://github.com/snakers4/silero-models
- Languages: Russian, English, others
- CPU: ✅ Yes
- Best for: quality Russian local TTS

### MARS5-TTS

- Repo: https://github.com/Camb-ai/MARS5-TTS
- Params: AR 750M + NAR 450M (~1.2B total)
- Languages: English only
- GPU: Required for reasonable speed; needs ~4GB+ VRAM
- CPU: Too slow / impractical
- Best for: high-quality English voice cloning with reference audio
- Pitfall: README says "you must be able to store at least 750M+450M params on GPU"

### Matcha-TTS

- Repo: https://github.com/shivammehta25/Matcha-TTS
- Params: flow-matching TTS
- Languages: English only (LJ Speech / VCTK)
- GPU: Strongly preferred
- CPU: Possible but slow
- Best for: fast English TTS research demos

## Orchestration platforms vs TTS engines

| Project | What it really is | Why not a direct TTS solution |
|---|---|---|
| **Rapida voice-ai** | Voice AI orchestration platform in Go + Docker | TTS through external providers (OpenAI, Deepgram, etc.) |
| **LiveKit Agents** | Real-time voice agent framework | TTS through cloud plugins by default; local only via wrappers like Silero |

Use these when building a voice call center or real-time assistant, not when you just need `text → audio`.

## Integration into Hermes

Hermes `text_to_speech` tool uses providers configured in `~/.hermes/config.yaml`:
- `edge` (Microsoft Edge TTS, free, online)
- `openai` / `elevenlabs` / `xai` / `gemini` / `mistral` / `neutts` / `piper`

For a custom local TTS like Kokoro:
1. Deploy it as a small local HTTP service or CLI wrapper.
2. Point Hermes at a custom provider if supported, or call the wrapper from a script.
3. Save the wrapper path in `references/` of this skill.

## Common pitfalls

1. **Language mismatch**: A model trained only on English will not produce intelligible Russian.
2. **GPU requirement stated as "recommended" often means "unusable on CPU" for large models.**
3. **espeak-ng dependency**: Many TTS tools need the system package, not just pip.
4. **Disk space**: PyTorch + model weights can take 2–5 GB.
5. **Python 3.12 compatibility**: Research repos often pin 3.10; test before promising.
6. **Hermes Edge TTS Russian**: use `ru-RU-SvetlanaNeural` or `ru-RU-DmitryNeural`, not `en-US-AriaNeural`.

## Verification steps

After installing any local TTS:

```bash
# Kokoro
python - <<'PY'
from kokoro import KPipeline
import soundfile as sf
pipeline = KPipeline(lang_code='a')
for i, (_, _, audio) in enumerate(pipeline("Hello from local TTS", voice='af_heart')):
    sf.write(f'test_{i}.wav', audio, 24000)
print('OK')
PY
```

Listen with `ffplay`, `aplay`, or attach to Telegram response.

## References

- `references/local-tts-project-evaluation.md` — worked example comparing Kokoro, MARS5-TTS, Rapida, LiveKit Agents for a CPU-only Linux box with 31GB RAM and a non-functional GeForce 210.
