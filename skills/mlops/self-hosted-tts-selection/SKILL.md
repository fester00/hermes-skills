---
name: self-hosted-tts-selection
description: |
  Choose, install, and run a self-hosted text-to-speech (TTS) engine under hardware
  constraints (CPU-only, no GPU, limited RAM/disk). Covers model size, language support,
  inference speed, and integration into Hermes or other applications.
version: 1.0.0
author: Master Ugwai
license: MIT
metadata:
  hermes:
    tags: [tts, text-to-speech, kokoro, piper, silero, xtts, mars5, local-inference, cpu-inference]
    related_skills: [hermes-agent, selective-vpn-routing]
---

# Self-hosted TTS selection and deployment

Use this skill when the user wants local/offline text-to-speech synthesis — for example, to generate audio messages from Hermes without relying on cloud TTS providers.

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

## Common candidates

### Kokoro

- **Size:** 82 M parameters (~330 MB download).
- **Languages:** English, Spanish, French, Italian, Portuguese, Hindi, Chinese, Japanese. Russian is **not** officially listed, but `espeak-ng` fallback may produce intelligible output.
- **Hardware:** Runs comfortably on CPU with 31 GB RAM; no GPU needed.
- **Install:** `pip install kokoro soundfile` + system package `espeak-ng`.
- **License:** Apache 2.0.
- **Best for:** Lightweight, permissive, multi-language TTS on modest hardware.

### Piper

- **Size:** Very small (~20–100 MB per voice).
- **Languages:** Many, including Russian voices.
- **Hardware:** Extremely fast on CPU.
- **Install:** `pip install piper-tts` (or prebuilt binaries).
- **License:** MIT.
- **Best for:** Minimal resource use, Raspberry Pi, embedded, clear announcer-style voices.

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

### MARS5-TTS

- **Size:** 1.2 B parameters (AR 750 M + NAR 450 M).
- **Languages:** **English only**.
- **Hardware:** Requires GPU with ~4 GB+ VRAM. CPU is impractical.
- **License:** GNU AGPL 3.0.
- **Verdict for low-end hardware:** Not suitable.

## What not to choose

| Project | Why it is not a TTS engine for this use case |
|---------|-----------------------------------------------|
| **Rapida voice-ai** | Voice-agent orchestration platform; TTS comes from external providers. |
| **LiveKit agents** | Real-time conversational agent framework; uses cloud TTS by default. |

## Workflow

1. **Confirm target language and hardware.**
   - `python3 --version`
   - `free -h`
   - `nvidia-smi` or `lspci | grep -i vga`
2. **Shortlist candidates** by language + hardware fit.
3. **Install in a venv**, never system-wide:
   ```bash
   python3 -m venv ~/.venvs/tts
   source ~/.venvs/tts/bin/activate
   ```
4. **Run a hello-world synthesis** and measure time + listen to quality.
5. **Wrap the chosen engine** behind a CLI script or HTTP endpoint that Hermes can call.
6. **Document the final command/path** so future sessions can reuse it.

## Kokoro quickstart

```bash
# Debian/Ubuntu
sudo apt-get install espeak-ng

python3 -m venv ~/.venvs/kokoro
source ~/.venvs/kokoro/bin/activate
pip install kokoro soundfile
```

```python
from kokoro import KPipeline
import soundfile as sf

pipeline = KPipeline(lang_code='a')  # 'a' = American English
generator = pipeline("Hello, this is a test.", voice='af_heart')

for i, (gs, ps, audio) in enumerate(generator):
    sf.write(f'{i}.wav', audio, 24000)
```

For Russian, try `lang_code='a'` anyway and pass Cyrillic text; quality is not guaranteed. If Russian quality is critical, prefer Piper or Silero.

## Pitfalls

- **Voice/language mismatch.** English neural voices cannot pronounce Russian well; always check language support before installing a multi-GB model.
- **GPU assumptions.** READMEs often assume CUDA. On CPU-only machines, ignore GPU instructions but expect slower inference.
- **Disk space.** Models plus PyTorch can consume several gigabytes. Check `df -h` before installing.
- **Python version.** Some packages pin `python>=3.10,<3.13`; verify before creating the venv.
- **Provider fallback failures.** Hermes `text_to_speech` with `edge` provider may fail if the configured voice does not match the text language (e.g., `en-US-AriaNeural` for Russian). Switch to a matching voice (`ru-RU-SvetlanaNeural`) or a local engine.

## References

- `references/tts-project-comparison-2026-07.md` — side-by-side comparison of Kokoro, MARS5-TTS, Rapida, and LiveKit agents from a real evaluation session.
- `references/hermes-tts-integration.md` — wiring a local TTS script into Hermes `text_to_speech`.
