# Neural TTS / voice cloning evaluation — CosyVoice case

Session context: user linked `https://github.com/QwenAudio/CosyVoice` and asked what it does, how it works, whether it runs locally or remotely, and what GPU/VRAM it needs.

## What CosyVoice is

CosyVoice is an open-source multilingual neural text-to-speech (TTS) system from Alibaba / FunAudioLLM. It uses a large language model (LLM) to generate speech tokens, a flow-matching model to convert tokens to mel spectrogram, and a HiFT vocoder to produce the final waveform.

It supports:
- Text-to-speech in 9 languages (Chinese, English, Japanese, Korean, German, Spanish, French, Italian, Russian)
- Zero-shot voice cloning from a short prompt audio sample
- Cross-lingual voice cloning (speak in another language with the same voice)
- Instruct-driven control (emotion, dialect, speed, volume)
- Voice conversion
- Streaming inference with latency ~150 ms

## Architecture at a glance

```
Text  →  Frontend (normalization, tokenization, speaker embedding)
             ↓
      LLM generates speech tokens
             ↓
      Flow model → mel spectrogram
             ↓
      HiFT vocoder → PCM audio
```

Frontend also extracts:
- `speech_tokenizer_v*.onnx` — speech tokens from prompt audio
- `campplus.onnx` — speaker embedding
- `feat_extractor` — mel features for conditioning

## Model versions and disk size

| Version | Parameters | Download size | Notes |
|---|---|---|---|
| CosyVoice-300M | 300 M | ~2.5 GB | Entry model |
| CosyVoice2-0.5B | 0.5 B | ~3.7 GB | vLLM support, streaming |
| Fun-CosyVoice3-0.5B-2512 | 0.5 B | ~8.3 GB | Best quality; much larger flow + tokenizer |

Weights include: `llm.pt`, `flow.pt`, `hift.pt`, `campplus.onnx`, `speech_tokenizer_v*.onnx` (and optional ONNX/TRT engine files).

## Hardware requirements

| Version | Minimum VRAM | Comfortable VRAM | Notes |
|---|---|---|---|
| CosyVoice-300M | ~6–8 GB | 8 GB | Lightest |
| CosyVoice2-0.5B | ~8–10 GB | 12 GB | Recommended daily driver |
| Fun-CosyVoice3-0.5B | ~12–14 GB | 16 GB | Best quality, heaviest |

CPU inference is supported automatically (code disables JIT/TRT/fp16/vLLM when CUDA is absent), but it is impractically slow for interactive use.

## Deployment modes

| Mode | How | Best for |
|---|---|---|
| Local script | `python example.py` | Experimentation |
| Gradio WebUI | `python webui.py --port 50000` | Quick demos |
| FastAPI server | `runtime/python/fastapi/server.py` | HTTP API on a remote GPU box |
| gRPC server | `runtime/python/grpc/server.py` | Low-latency production RPC |
| Docker + TensorRT-LLM / vLLM | `runtime/python/docker build` + `runtime/triton_trtllm` | High-throughput deployment |

Conclusion: CosyVoice is a self-hosted local engine, but it is designed to be wrapped as a remote service via FastAPI/gRPC/Docker.

## Installation profile

- Python 3.10
- PyTorch 2.3.1 + CUDA 12.1
- ONNXRuntime GPU
- Gradio, FastAPI, gRPC, TensorRT optional
- Models downloaded via ModelScope or HuggingFace

## Important nuance: repo origin

The user linked `https://github.com/QwenAudio/CosyVoice`. This is a fork/mirror of the official `FunAudioLLM/CosyVoice`. The code and weights are identical; only the GitHub organization differs. README still references `FunAudioLLM/CosyVoice.git` for cloning.

## When to recommend CosyVoice vs lightweight TTS

| Need | Recommend |
|---|---|
| High-quality multilingual TTS, voice cloning, production API, GPU available | **CosyVoice** |
| CPU-only, low latency announcements, Raspberry Pi, simple Russian voice | **Kokoro / Piper / Silero** |
| Real-time voice agent platform | **LiveKit / Rapida** (not a TTS engine) |

## Key code entry points

- `cosyvoice/cli/cosyvoice.py` — `AutoModel()` dispatcher for v1/v2/v3
- `cosyvoice/cli/frontend.py` — text normalization, token extraction, speaker embedding
- `cosyvoice/cli/model.py` — LLM + Flow + HiFT inference loop
- `runtime/python/fastapi/server.py` — HTTP service wrapper
- `example.py` — usage examples for all modes

## Lessons learned

- For large model repos, remote inspection via GitHub API + raw files is enough to answer «what does it do» and «will it run on my hardware». Full clone is only needed for source audit or modification.
- HuggingFace API `https://huggingface.co/api/models/<namespace>/<model>/tree/main` gives precise per-file sizes — use it to estimate disk and VRAM.
- A 0.5 B parameter TTS is not a lightweight CPU model. Treat it like a small LLM: it needs GPU and several GB of VRAM.
- Always check whether the repo is the original or a mirror; it affects clone URLs and issue tracker locations.
