# Local TTS project evaluation — worked example

Session context: user wanted local TTS for Hermes audio messages on a CPU-only Linux machine (31GB RAM, GeForce 210 with no working NVIDIA driver, Python 3.12.3, `uv` available). Four GitHub repos were evaluated.

## Machines profile

| Resource | Value |
|---|---|
| CPU | Intel i5-9400F (6 cores) |
| RAM | 31 GB |
| GPU | NVIDIA GeForce 210, driver not loaded, `simple-framebuffer` in use |
| Python | 3.12.3 |
| Package manager | `uv` installed |
| Disk | 3.1 GB free on root at evaluation time |

## Evaluated projects

### 1. MARS5-TTS (Camb-ai)

- URL: https://github.com/Camb-ai/MARS5-TTS
- Languages: English only
- Params: AR 750M + NAR 450M (~1.2B)
- Dependencies: `torch`, `torchaudio`, `librosa`, `vocos`, `encodec`, `safetensors`, `regex`
- Verdict: ❌ Not suitable
- Reason: README explicitly requires GPU capable of holding 750M active parameters. CPU inference is impractical. Only English.

### 2. Kokoro (hexgrad)

- URL: https://github.com/hexgrad/kokoro
- Languages: en, es, fr, it, pt, hi, ja, zh (official); Russian possible via espeak-ng fallback
- Params: 82M
- Dependencies: `kokoro`, `soundfile`, system `espeak-ng`
- Verdict: ✅ Best fit
- Reason: Small, pip-installable, CPU-friendly, multiple languages, easy to wrap for Hermes.

### 3. Rapida voice-ai

- URL: https://github.com/rapidaai/voice-ai
- Languages: Depends on connected provider
- Stack: Go, Docker Compose, React UI, PostgreSQL, Redis, OpenSearch
- RAM requirement: 16GB+
- Verdict: ❌ Not suitable
- Reason: This is a voice-agent orchestration platform, not a TTS engine. Requires external TTS/STT providers and heavy infrastructure.

### 4. LiveKit Agents

- URL: https://github.com/livekit/agents
- Languages: Depends on plugin/provider
- Stack: Python, requires LiveKit server, API keys
- Default TTS: cloud providers (Cartesia, ElevenLabs, OpenAI)
- Local option: `livekit-plugins-silero` wrapper
- Verdict: ❌ Not suitable as direct TTS
- Reason: Framework for real-time agents, not a standalone local TTS. Needs cloud keys or Silero plugin.

## Recommendation

For this machine and goal (Hermes audio messages), **Kokoro** is the only viable choice. Install with:

```bash
sudo apt-get install -y espeak-ng
uv pip install kokoro soundfile
```

Quick test:

```python
from kokoro import KPipeline
import soundfile as sf

pipeline = KPipeline(lang_code='a')
for i, (gs, ps, audio) in enumerate(pipeline("Hello from local Kokoro TTS", voice='af_heart')):
    sf.write(f'test_{i}.wav', audio, 24000)
```

## Notes on Russian

Kokoro does not officially list Russian. It uses `misaki` for G2P with `espeak-ng` fallback. Russian may work with `lang_code='a'` and Cyrillic input, but quality is not guaranteed. For guaranteed Russian quality, evaluate Silero or Piper instead.

## Lessons learned

- Always check pretrained model languages first; many TTS repos are English-only.
- "GPU recommended" for 1B+ param models effectively means "unusable on CPU".
- Orchestration platforms (Rapida, LiveKit) are not TTS engines; they route to providers.
- `nvidia-smi` failure + `simple-framebuffer` means no CUDA acceleration is available.
