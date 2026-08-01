---
name: tts-selection
description: |
  Evaluate, select, and deploy local / self-hosted text-to-speech (TTS) engines
  under hardware constraints (CPU-only, low-GPU, no cloud). Covers lightweight
  models (Piper, Kokoro, Silero) and larger neural models (XTTS, CosyVoice, Fish
  Speech), with a unified decision framework and Hermes integration.
version: 1.0.0
author: Hermes Agent / Master Ugwai
license: MIT
metadata:
  hermes:
    tags: [tts, text-to-speech, local-inference, self-hosted, cpu, gpu, audio, piper, kokoro, xtts, cosyvoice]
    related_skills: [audiocraft-audio-generation, heartmula, songsee, hermes-agent]
---

# TTS Selection & Deployment

Class-level guide for choosing and running local or self-hosted text-to-speech engines.

## When to use this skill

- User wants local/offline TTS without cloud API keys.
- User asks "какую TTS поставить", "какой TTS движок выбрать", "что запустится на CPU".
- Need to evaluate a GitHub TTS project for feasibility on a specific machine.
- Integrating TTS into Hermes `text_to_speech` or another agent workflow.

## Core decision framework

Evaluate every TTS candidate against the same checklist:

| Criterion | Why it matters |
|-----------|----------------|
| **Language support** | The model must support the target language (e.g., Russian). |
| **Model size / parameters** | Larger models need more RAM and VRAM; CPU-only machines favor small models. |
| **Hardware requirements** | GPU may be required for real-time or high-quality inference. |
| **Inference speed on target hardware** | A slow model is impractical for interactive use. |
| **License / cost** | Some models are free for personal use but commercial-only. |
| **Integration complexity** | Python pip install vs Docker vs custom build. |

## Hardware assessment checklist

Before recommending any TTS, check:

1. `python3 --version` (many TTS want 3.10–3.12)
2. `which nvidia-smi && nvidia-smi` (GPU?)
3. `free -h` (RAM)
4. `df -h` (disk space for models)
5. `which uv || which pip` (packaging)

## Decision matrix

| Need | Recommended | Why |
|---|---|---|
| Quality Russian voice, local, low resource, CPU-only | **Piper-GPL** | Native Russian voices, RTF ~0.04 on CPU; see `references/piper-gpl-cpu-recipe.md` |
| Lightweight, fast, CPU-only, English + major languages | **Kokoro** | 82M params, pip install, runs on CPU |
| Voice cloning / prosody control, English only, has GPU | **MARS5-TTS / Matcha-TTS** | Research quality, needs VRAM |
| High-quality multilingual TTS, zero-shot voice cloning, production deployment, GPU available | **CosyVoice / Fish Speech / XTTS** | LLM-based neural TTS; see `references/neural-tts-cosyvoice-evaluation.md` |
| High-quality neural TTS, no GPU, patient batch use | **CosyVoice-300M** (CPU) | Works on CPU but RTF ~3.5; see `references/cosyvoice-cpu-install-recipe.md` |
| Real-time voice agent platform | **LiveKit Agents / Rapida** | Not a TTS engine; needs cloud providers |
| Music / sound effects generation | **AudioCraft / HeartMuLa** | Different domain; see related skills |

## Common candidates

### Piper / piper1-gpl (OHF-voice fork)

- **Size:** ~60 MB per `medium` voice; smaller sizes exist (x_low/low/medium).
- **Languages:** 40+ languages including **Russian (`ru_RU`)** with voices `denis`, `dmitri`, `irina`, `ruslan`.
- **Hardware:** Extremely fast on CPU; designed for Raspberry Pi and edge devices.
- **Install:** `pip install piper-tts` + system `espeak-ng`.
- **License:** GPL-3.0-or-later (OHF fork `piper1-gpl`, package `piper-tts` 1.6.0+).
- **Best for:** Minimal resource use, low-latency announcements, clear announcer-style voices, and especially Russian on CPU.
- **Hermes integration:** see `references/piper-hermes-integration.md` for configuring Piper as the default `tts.provider`.

### Kokoro / kokoro-onnx

- Repo: https://github.com/hexgrad/kokoro
- **Size:** 82 M parameters; `kokoro-v1_0.pth` ~312 MB.
- **Languages:** English, Spanish, French, Italian, Portuguese, Hindi, Chinese, Japanese. **Russian is not officially supported.** Cyrillic input will fall back to `espeak-ng`, which usually produces a heavily accented, low-quality result.
- **Hardware:** Runs comfortably on CPU; no GPU needed.
- **Install:** `pip install kokoro soundfile` + system package `espeak-ng`.
- **License:** Apache 2.0.
- **Best for:** High-quality, permissive, multi-language TTS when Russian is not required.

#### kokoro-onnx (yakhyo/kokoro-onnx)

A minimal ONNX Runtime wrapper for Kokoro-82M. Supports only `en-us` and `en-gb`.

| Model file | Size | Notes |
|---|---|---|
| `kokoro-quant.onnx` | ~169 MB | Mixed precision, faster inference |
| `kokoro-v0_19.onnx` | ~330 MB | Original model |

Use this when you want a lighter, PyTorch-free deployment for English only. It is not a separate model family — it is an inference packaging choice.

### Silero TTS

- **Size:** Medium.
- **Languages:** Russian, English, and others.
- **Hardware:** CPU OK, better on GPU.
- **Install:** PyTorch + Silero models via torch hub.
- **License:** CC BY-NC / commercial license for business use.
- **Best for:** Natural Russian if you accept the license terms.

### Coqui TTS / XTTS v2

- **Size:** Large (multiple GB).
- **Languages:** Multilingual, including Russian.
- **Hardware:** Ideally GPU; CPU is very slow.
- **License:** Coqui Public Model License (research/personal); commercial license available.
- **Best for:** Voice cloning and high-quality multilingual TTS when GPU is present.

### CosyVoice / Fish Speech

- **Size:** Large (LLM-based).
- **Languages:** Multilingual.
- **Hardware:** GPU for real-time; CPU possible but slow (RTF ~3.5).
- **Best for:** Zero-shot voice cloning, production multilingual TTS.
- See `references/neural-tts-cosyvoice-evaluation.md` and `references/cosyvoice-cpu-install-recipe.md`.

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

## Remember

- **Russian + CPU → Piper-GPL.**
- **English + CPU → Kokoro.**
- **Voice cloning / production → XTTS / CosyVoice / Fish Speech, but expect GPU.**
- Always benchmark RTF on the target machine before committing.

## References

- `references/piper-gpl-cpu-recipe.md`
- `references/piper-hermes-integration.md`
- `references/piper-russian-voice-comparison.md`
- `references/local-tts-project-evaluation.md`
- `references/neural-tts-cosyvoice-evaluation.md`
- `references/cosyvoice-cpu-install-recipe.md`
- `references/cpu-tts-piper-kokoro-evaluation.md`
- `references/tts-project-comparison-2026-07.md`
