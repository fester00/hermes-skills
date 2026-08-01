# CPU-only lightweight TTS options: piper1-gpl and kokoro-onnx

Session: user already had a slow CPU-only CosyVoice deployment (RTF ~3.5 on Intel i5-9400F) and asked to evaluate two fast GPU-free alternatives.

## piper1-gpl (OHF-voice fork)

- Repo: https://github.com/OHF-voice/piper1-gpl
- PyPI package: `piper-tts` (v1.6.0+)
- License: GPL-3.0-or-later
- Dependencies: `onnxruntime>=1,<2`, `pathvalidate>=3,<4`
- Python support: 3.9–3.13
- Install: `pip install piper-tts`
- Languages: 40+ including Russian (`ru_RU`)
- Russian voices: `denis`, `dmitri`, `irina`, `ruslan`
- Voice size (medium): ~60 MB `.onnx` + `.onnx.json`
- Modes: CLI, Python API, HTTP server (`[http]` extra), C/C++ API

## kokoro / kokoro-onnx

### Original (hexgrad/kokoro)

- Repo: https://github.com/hexgrad/kokoro
- PyPI: `pip install kokoro soundfile`
- License: Apache 2.0
- Model: Kokoro-82M, 82 M parameters, ~312 MB `.pth`
- Languages: English, Spanish, French, Italian, Portuguese, Hindi, Japanese, Mandarin Chinese
- **Russian is not officially supported.** Cyrillic falls back to `espeak-ng` with poor results.
- Needs system package `espeak-ng`.

### ONNX wrapper (yakhyo/kokoro-onnx)

- Repo: https://github.com/yakhyo/kokoro-onnx
- Supports only `en-us` and `en-gb`.
- ONNX files:
  - `kokoro-quant.onnx` — ~169 MB, mixed precision, faster
  - `kokoro-v0_19.onnx` — ~330 MB, original
- Use case: PyTorch-free, English-only deployment.

## Measured results on Intel i5-9400F (6 cores), 31 GB RAM, no GPU

| Engine | Voice / model | Text language | Audio length | Synthesis time | RTF |
|---|---|---|---|---|---|
| piper1-gpl | `ru_RU-denis-medium` | Russian | 4.68 s | 0.19 s | **0.041** |
| kokoro-onnx | — | Russian | — | — | **Not supported (en-us/en-gb only)** |

Piper generated intelligible Russian audio in real time; 1 second of audio required ~0.04 seconds of CPU time.

## Decision notes

| Need | Choice |
|---|---|
| Russian language required | **Piper** (native `ru_RU` voices) |
| English only, best quality, permissive license | **Kokoro** |
| English only, smallest/fastest, no PyTorch | **kokoro-onnx** |
| Already have CosyVoice, need batch quality | Keep CosyVoice; accept RTF ~3.5 |

Next step for this session was to install both under `/mnt/data/natan-storage/` and measure RTF on the target CPU.
