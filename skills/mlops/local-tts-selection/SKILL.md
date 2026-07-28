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
| High-quality multilingual TTS, zero-shot voice cloning, production deployment, GPU available | **CosyVoice / Fish Speech / XTTS** | LLM-based neural TTS; see `references/neural-tts-cosyvoice-evaluation.md` |
| High-quality neural TTS, no GPU, patient batch use | **CosyVoice-300M** (CPU) | Works on CPU but RTF ~3.5; see `references/cosyvoice-cpu-install-recipe.md` |
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
- **VRAM estimate**: For LLM-based TTS (CosyVoice, XTTS, Fish Speech), use HuggingFace tree API to sum `*.pt` / `*.safetensors` / `*.onnx` sizes and add ~2–4 GB overhead for activations.
- **Dependencies**: PyTorch version, espeak-ng, special build steps?
- **License**: AGPL / Apache / GPL / commercial?
- **CPU support**: Does README mention CPU inference or require GPU?
- **Deployment modes**: local script, web UI, FastAPI/gRPC server, Docker?
- **Installation path**: pip install vs Docker vs build from source?

### Quick model-size probe

```bash
# HuggingFace model repo file sizes (no full clone needed)
curl -sL --max-time 30 "https://huggingface.co/api/models/<namespace>/<model>/tree/main" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); total=sum(n.get('size',0) for n in d if n.get('type')=='file'); [print(f'{n.get('size',0)/1024/1024:8.1f} MB  {n['path']}') for n in d if n.get('type')=='file']; print(f'TOTAL: {total/1024/1024:.1f} MB')"
```

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
3. **VRAM sizing**: Download size ≈ 30–50% of peak VRAM for fp32 inference. Add ~2–4 GB overhead. Example: CosyVoice3 weights are ~8.3 GB → comfortable at 16 GB VRAM, marginal at 12 GB.
4. **Mirror repos**: A GitHub org may host a fork/mirror of the original project (e.g. `QwenAudio/CosyVoice` vs `FunAudioLLM/CosyVoice`). Code is identical but issue tracker and clone URLs differ.
5. **espeak-ng dependency**: Many TTS tools need the system package, not just pip.
6. **Disk space**: PyTorch + model weights can take 2–5 GB for lightweight models, 5–10 GB+ for neural LLM-based TTS.
7. **Python 3.12 compatibility**: Research repos often pin 3.10; test before promising.
8. **Hermes Edge TTS Russian**: use `ru-RU-SvetlanaNeural` or `ru-RU-DmitryNeural`, not `en-US-AriaNeural`.
9. **CPU-only CosyVoice**: use CosyVoice-300M or 300M-SFT for smallest weights. Expect RTF ~3.5 (1 sec audio needs ~3.5 sec compute). CosyVoice2/3 are impractical on CPU. Always install `torch` CPU wheels and CPU ONNXRuntime to avoid pulling CUDA packages that fail to load.

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

For CosyVoice on CPU:

```bash
python - <<'PY'
import sys, time
sys.path.append('third_party/Matcha-TTS')
from cosyvoice.cli.cosyvoice import AutoModel
import torchaudio

model_dir = 'pretrained_models/CosyVoice-300M-SFT'
cosyvoice = AutoModel(model_dir=model_dir)
print('speakers:', cosyvoice.list_available_spks())
text = '你好，我是通义生成式语音大模型。'
start = time.time()
for i, output in enumerate(cosyvoice.inference_sft(text, '中文女', stream=False)):
    torchaudio.save(f'cosy_{i}.wav', output['tts_speech'], cosyvoice.sample_rate)
print(f'synthesis: {time.time()-start:.1f}s for {len(text)*0.3:.1f}s estimated audio')
PY
```

Listen with `ffplay`, `aplay`, or attach to Telegram response.

## References

- `references/neural-tts-cosyvoice-evaluation.md` — evaluation of CosyVoice as an example of a large LLM-based neural TTS: architecture, model sizes, VRAM requirements, deployment modes, and the fork-vs-original repo nuance.
- `references/local-tts-project-evaluation.md` — worked example comparing Kokoro, MARS5-TTS, Rapida, LiveKit Agents for a CPU-only Linux box with 31GB RAM and a non-functional GeForce 210.
- `references/cosyvoice-cpu-install-recipe.md` — exact CPU-only install steps for CosyVoice-300M-SFT on Ubuntu with `uv`, including PyTorch CPU wheels, dependency workarounds, and a smoke test.
