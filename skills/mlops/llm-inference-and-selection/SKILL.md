---
name: llm-inference-and-selection
description: |
  Choose, compare, and run open-weight LLMs. Covers model discovery (Ollama Hub,
  Arena AI), benchmark-aware selection, hardware-fit sizing, local deployment
  (Ollama / llama.cpp / vLLM), storage management, and cloud-only provider
  caveats.
version: 2.0.0
tags: [mlops, llm, ollama, models, comparison, selection, local-inference, quantization, GGUF, vllm, llama.cpp, disk-space, RAM-planning]
---

# LLM Inference & Selection

End-to-end guide: from "which model should I use?" to "it's running on my machine."

## When to use

- User asks "compare models X and Y" or "which model for my task"
- Need to check if RAM / VRAM / disk space is sufficient for a chosen model
- Ollama models are eating the system disk
- Choosing between `ollama run`, `llama-server`, or `vllm serve`
- Evaluating a new open-weight model for adoption

---

# Part 1 — Model Selection & Comparison

## 1.1 Discovery (Ollama Hub)

```bash
# Quick variant discovery
curl -sL "https://ollama.com/library?q=<keyword>" | grep -o 'href="/library/[^"]*'
```

**Browser alternative (preferred when search engines require auth):**
Navigate directly to `https://ollama.com/search?q=<keyword>`. The filter textbox on `ollama.com/library` is JS-rendered and often does not react to accessibility input; the `/search?q=` URL pattern is reliable.

Then visit each model page (`https://ollama.com/library/<model-name>`) and record:
- **Parameter count** (e.g., 1.04T vs undisclosed)
- **Context window** (guaranteed vs max, e.g., 256K vs 512K guaranteed / 1M max)
- **Capability tags** (vision, tools, thinking, cloud)
- **Download count & last updated** — key risk signals
- **Declared strengths** (key features / highlights list)

## 1.2 Benchmark data & Arena AI cross-check

- Read Highlights / Benchmark / Architecture sections from the Ollama page.
- If benchmark images are visible, use `browser_vision` to read quantitative scores.
- **Arena AI (lmarena.ai) is mandatory** for models claiming frontier performance. Low Arena ELO despite excellent self-reported benchmarks suggests a real-world quality gap for interactive/chat use.

## 1.3 Task-fit analysis

Map model claims to the user's actual tasks:
- Does the model **explicitly mention** the target language / framework (e.g., Rust, Next.js)?
- Does it advertise **agentic/orchestration** capabilities (swarm, sub-agents, tool invocation)?
- Is **context length** the bottleneck for the user's use case?
- Does it prioritize **coding** vs **design** vs **browsing/research**?

## 1.4 Risk heuristics

| Signal | Meaning |
|--------|---------|
| Low downloads (< 10K) + updated < 48h ago | Bleeding edge. Flag as experimental. |
| Missing explicit language mention | ≠ incapable, but a model that declaratively lists it is safer. |
| Huge params (1T+) with modest context | May be slower/costlier per-token than a sparse-attention model with 4× context. |
| Self-reported benchmarks but low Arena ELO | Real-world quality gap for interactive use. |
| Multimodal claims are size-segmented | Check per-model benchmark table. A "-" in Audio/Video row means unsupported even if smaller sizes in the same family support it. |
| Cloud tag (`cloud` in Ollama) | NOT local. Requires Ollama Cloud API access. Verify the user's provider actually proxies Ollama Cloud endpoints. |

## 1.5 Deliverable format

Present comparison as:
1. Quick spec table (size, context, recency, downloads)
2. Per-scenario strengths (3–5 bullets per relevant user task)
3. Scenario-based verdicts (no single global "winner")
4. Practical test command (`ollama run <model>:cloud`)

---

# Part 2 — Local Deployment & Hardware Planning

## 2.1 Hardware assessment workflow (ALWAYS run first)

```bash
# One-liner snapshot: RAM, CPU, GPU, disk
free -h && echo "---CPU---" && nproc && lscpu | grep "Model name" | head -1 \
  && echo "---GPU---" && lspci | grep -i vga && nvidia-smi 2>/dev/null || echo "No working NVIDIA GPU" \
  && echo "---DISK---" && df -h && echo "---OS---" && lsb_release -a 2>/dev/null || cat /etc/os-release | head -5
```

Key thresholds to report back:
- **RAM free** — determines if CPU-only inference is viable
- **VRAM** — determines if GPU offload or vLLM is viable
- **Disk free on root** — Ollama defaults to `~/.ollama/models`, usually on root
- **Extra mounted disks** — `lsblk -f`, `df -h`, `/mnt`, `/media` — may hold terabytes

### Model-size rule of thumb for Ollama (Q4_K_M typical)

| Params | Download size | Load in RAM | Notes |
|--------|---------------|-------------|-------|
| ~2B (E2B) | ~1.5 GB | ~2 GB | Phones, edge |
| ~4B (E4B) | ~3 GB | ~4 GB | Entry laptops |
| 7–8B | ~4–5 GB | ~5–6 GB | Common laptop fit |
| 12B | ~7–9 GB | ~8–10 GB | Needs 16 GB RAM comfortably |
| 26B MoE | ~14–16 GB | ~16–20 GB | Needs 32 GB RAM |
| 31B dense | ~20+ GB | ~24+ GB | Needs 32–64 GB RAM or GPU |

For llama.cpp raw GGUF: same sizes. For vLLM / Transformers full precision: double or triple.

**Critical pitfall:** "16 GB" means nothing until you know if the user means RAM or VRAM. Always clarify.

## 2.2 Toolchain selection

| Situation | Tool | Command |
|-----------|------|---------|
| Quick local chat, CPU or modest GPU | Ollama | `ollama run <model>` |
| Programmatic Python, custom quant, embeddings | llama.cpp + Python | see `llama-cpp` skill |
| GPU server, high-throughput API | vLLM | `vllm serve <model>` |
| Apple Silicon, edge device | llama.cpp / Ollama | both work natively |

When in doubt, default to **Ollama** for interactive local use.

## 2.3 Ollama specifics

### Check / install
```bash
ollama --version
# Install if missing: curl -fsSL https://ollama.com/install.sh | sh
```

### Run a model
```bash
ollama run gemma4:12b
```

### List local models
```bash
ollama list
```

### Remove a model to reclaim space
```bash
ollama rm <model>
```

### Model storage: default vs custom path

Default: `~/.ollama/models/` (lives on root disk, often small).

To move models to a larger disk:
```bash
# 1. Create target dir
mkdir -p /mnt/bigdisk/ollama-models

# 2. Set env var BEFORE starting ollama
export OLLAMA_MODELS=/mnt/bigdisk/ollama-models
ollama serve

# 3. Or add to systemd override (requires sudo)
sudo systemctl edit ollama
# Add:
# [Service]
# Environment="OLLAMA_MODELS=/mnt/bigdisk/ollama-models"
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

**Important:** if Ollama is already running as a systemd service, you cannot change its env without sudo. Options:
- Ask user for sudo / password
- Kill the service and run `OLLAMA_MODELS=... ollama serve` manually
- Run a second Ollama on a different port: `OLLAMA_MODELS=... OLLAMA_HOST=127.0.0.1:11435 ollama serve`

### Ollama port / host
```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve   # listen on all interfaces
OLLAMA_HOST=127.0.0.1:11435 ollama serve # second instance
```

## 2.4 llama.cpp specifics

For direct GGUF control, custom quants, or Python integration, load the dedicated **`llama-cpp`** skill.

## 2.5 vLLM specifics

For GPU-backed production serving, load the dedicated **`serving-llms-vllm`** skill.

---

# Pitfalls (Selection + Deployment)

1. **RAM vs VRAM confusion** — users say "16 GB" and mean either. Always clarify.
2. **Root disk full** — Ollama defaults to `~/.ollama/models`. On a 60 GB root partition this fills fast. Check `df -h /` before pulling large models.
3. **Old / broken GPU drivers** — `nvidia-smi` may fail even if an NVIDIA card exists. Fall back to CPU inference; do not block on GPU setup.
4. **Systemd service locked env** — changing `OLLAMA_MODELS` for a running systemd service requires sudo or a restart strategy.
5. **Model names are aliases** — `gemma4:12b` is a convenience tag; the actual file is a quantized GGUF.
6. **No GPU = slower but functional** — CPU-only llama.cpp or Ollama runs 5–15 tok/s on modern CPUs. Set expectations.
7. **Never assume context size from memory of other variants.** A model family may have members with 2M, 256K, and 128K contexts. Always re-read the *current* Ollama page for the exact tag.
8. **When user provides links claiming a model exists, always check before contradicting.** Disregarding user-provided evidence damages trust.

---

# Related Skills

- `llama-cpp` — GGUF inference, quant selection, Hugging Face discovery
- `serving-llms-vllm` — GPU-backed high-throughput serving
- `huggingface-hub` — search/download/upload models and datasets

---

# References

- `references/model-comparison-example.md` — annotated example: Kimi K2.6 vs Minimax M3, benchmark images, Ollama metadata
- `references/ollama-cloud-model-comparison-2026-06-05.md` — three-model comparison (Kimi, Gemma 4, MiniMax) with Arena AI verification
- `references/ollama-model-paths.md` — OLLAMA_MODELS relocation recipes, systemd override patterns, multi-instance ports
