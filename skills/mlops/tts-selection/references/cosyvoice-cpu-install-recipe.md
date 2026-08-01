# CosyVoice CPU-only install recipe

Session context: user asked to install the smallest CosyVoice model on a secondary disk and test it without GPU. Target machine: Ubuntu 24.04, Python 3.12 system, `uv` available, no CUDA.

## Target path

`/mnt/data/natan-storage/CosyVoice-CPU` (or any writable path on the second disk).

## 1. Clone source

```bash
cd /mnt/data/natan-storage
git clone --recursive https://github.com/FunAudioLLM/CosyVoice.git CosyVoice-CPU
cd CosyVoice-CPU
git submodule update --init --recursive
```

> A mirror/fork such as `QwenAudio/CosyVoice` contains identical code but README clone URLs still point to `FunAudioLLM/CosyVoice`. Use the official repo for consistency.

## 2. Create Python 3.10 venv

CosyVoice pins Python 3.10. Use `uv` to pull it:

```bash
uv venv venv --python 3.10
source venv/bin/activate
```

## 3. Install CPU-only PyTorch

Avoid CUDA wheels and the CUDA-only ONNXRuntime index that may time out.

```bash
uv pip install torch==2.3.1+cpu torchaudio==2.3.1+cpu --index-url https://download.pytorch.org/whl/cpu
```

## 4. Install remaining dependencies

Use the CPU ONNXRuntime and skip the GPU-only packages (`deepspeed`, `tensorrt-*`, `onnxruntime-gpu`).

```bash
uv pip install conformer==0.3.2 diffusers==0.29.0 fastapi==0.115.6 fastapi-cli==0.0.4 \
  gdown==5.1.0 gradio==5.4.0 grpcio==1.57.0 grpcio-tools==1.57.0 hydra-core==1.3.2 \
  HyperPyYAML==1.2.3 inflect==7.3.1 librosa==0.10.2 lightning==2.2.4 matplotlib==3.7.5 \
  modelscope==1.20.0 networkx==3.1 numpy==1.26.4 omegaconf==2.3.0 onnx==1.16.0 \
  onnxruntime==1.18.0 openai-whisper==20231117 protobuf==4.25 pyarrow==18.1.0 \
  pydantic==2.7.0 pyworld==0.3.4 rich==13.7.1 soundfile==0.12.1 tensorboard==2.14.0 \
  transformers==4.51.3 x-transformers==2.11.24 uvicorn==0.30.0 wetext==0.0.4 wget==3.2
```

`openai-whisper==20231117` needs `setuptools`/`pkg_resources` to build. If it fails with `No module named 'pkg_resources'`, install setuptools and build without isolation:

```bash
uv pip install setuptools wheel
python -m pip install openai-whisper==20231117 --no-deps --no-build-isolation
```

## 5. Download the smallest model

Use ModelScope (works without HuggingFace login inside Russia/China). The smallest usable SFT model is `CosyVoice-300M-SFT` (~2.5 GB); `CosyVoice-300M` has no built-in speakers.

```bash
python -c "from modelscope import snapshot_download; snapshot_download('iic/CosyVoice-300M-SFT', local_dir='pretrained_models/CosyVoice-300M-SFT')"
```

Model files:

```
pretrained_models/CosyVoice-300M-SFT/
  campplus.onnx
  cosyvoice.yaml
  flow.decoder.estimator.fp32.onnx
  flow.encoder.fp16.zip / fp32.zip
  flow.pt
  hift.pt
  llm.pt
  llm.text_encoder.fp32.zip
  llm.llm.fp16.zip / fp32.zip
  speech_tokenizer_v1.onnx
  spk2info.pt
```

## 6. CPU smoke test

Create `/mnt/data/natan-storage/CosyVoice-CPU/test_cpu.py`:

```python
import sys
sys.path.append('third_party/Matcha-TTS')
from cosyvoice.cli.cosyvoice import AutoModel
import torchaudio
import time

model_dir = 'pretrained_models/CosyVoice-300M-SFT'
print('Loading', model_dir)
start = time.time()
cosyvoice = AutoModel(model_dir=model_dir)
print(f'Loaded in {time.time()-start:.1f}s')
print('Speakers:', cosyvoice.list_available_spks())

text = '你好，我是通义生成式语音大模型，请问有什么可以帮您的吗？'
start = time.time()
for i, output in enumerate(cosyvoice.inference_sft(text, '中文女', stream=False)):
    torchaudio.save(f'sft_{i}.wav', output['tts_speech'], cosyvoice.sample_rate)
print(f'Synthesis: {time.time()-start:.1f}s')
```

Run:

```bash
source venv/bin/activate
python test_cpu.py
```

## 7. Expected result on CPU

With an Intel i5-9400F (6 cores) and 31 GB RAM:

| Metric | Value |
|---|---|
| Model load | ~10 s |
| Available speakers | 中文女, 中文男, 日语男, 粤语女, 英文女, 英文男, 韩语女 |
| Speech length | ~4.4 s |
| Synthesis time | ~15.5 s |
| RTF | ~3.5 |

CPU inference works but is impractical for real-time or interactive use. Use GPU for production.

## Pitfalls

- `CosyVoice-300M` (without `-SFT`) has no `spk2info.pt`, so `inference_sft(..., '中文女')` raises `KeyError`. Use `CosyVoice-300M-SFT` for built-in speakers or `CosyVoice-300M` with zero-shot/cross-lingual/instruct modes.
- The default `requirements.txt` pulls `onnxruntime-gpu` and `tensorrt-cu12`, which are unnecessary on CPU and may fail to install.
- Do not rely on the PyTorch CUDA extra index for CPU-only installs; it can time out resolving unrelated packages.
- First run downloads wetext resources from ModelScope (~10 MB); ensure network access to `modelscope.cn`.
