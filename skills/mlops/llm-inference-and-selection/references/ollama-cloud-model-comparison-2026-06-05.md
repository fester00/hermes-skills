# Reference: Ollama Cloud Model Comparison (Session 2026-06-05)

## Context
User requested comparison of three Ollama Cloud models for their stack:
- VIDVIS: Next.js 14 luxury gallery + textile store (GSAP, Lenis, Tailwind, framer-motion)
- Rust learning track (socratic courses)
- Multimodal agent pipelines (Whisper + vision + LLM)

## Data Sources
All data pulled from `ollama.com/search?q=<model>` via direct browser navigation.
Search engines (Google/Yandex) unavailable due to auth requirement on this host.

---

## Kimi K2.6 (kimi-k2.6:cloud)

**Specs:**
- Parameters: 1.04 trillion
- Context: 256K tokens
- Modalities: text, image (vision)
- Tags: vision, tools, thinking, cloud
- Pulls: 285.5K | Updated: 1 month ago
- Command: `ollama run kimi-k2.6:cloud`

**Key Features (from Ollama Readme):**
- Long-horizon coding (Rust, Go, Python, front-end, DevOps)
- Coding-driven design (prompts + visual inputs → production UI)
- Agent Swarm: up to 300 sub-agents, 4000 coordinated steps
- Proactive 24/7 background agents

**Verdict for user tasks:** Best fit for VIDVIS (coding-driven design explicitly matches luxury UI generation) and Rust learning (Rust explicitly listed in capabilities).

---

## Gemma 4 31B (gemma4:31b-cloud)

**Specs:**
- Parameters: 31B (dense)
- Context: 256K tokens
- Modalities: text, image, audio
- Tags: vision, tools, thinking, audio, cloud
- Pulls: 12.1M (entire Gemma 4 family) | Updated: 6 hours ago
- Size: ~20GB
- Command: `ollama run gemma4:31b-cloud`

**Family Variants:**
- `e2b` / `e4b`: edge models (128K context)
- `12b` / `26b` / `31b`: workstation models (256K context)
- `*-mlx`: Apple Silicon optimized

**Key Features:**
- Native `system` role support
- Configurable thinking modes
- Variable aspect ratio & resolution for vision
- Native function-calling
- NOTE: Audio/Video modality table on Ollama shows "-" for 26B/31B — only E2B/E4B/12B have audio support

**Verdict for user tasks:** Good all-rounder. Audio modality irrelevant for current tasks (no audio pipeline). Most frequently updated (6h ago).

---

## MiniMax M3 (minimax-m3:cloud)

**Specs:**
- Parameters: undisclosed
- Context: 512K guaranteed, up to 1M tokens
- Modalities: text, image (native multimodal from step zero)
- Architecture: MiniMax Sparse Attention (MSA)
- Tags: vision, tools, thinking, cloud
- Pulls: 24.8K | Updated: 4 days ago
- Command: `ollama run minimax-m3:cloud`

**Key Features:**
- First open-source with frontier coding + 1M context + multimodal simultaneously
- BrowseComp score: 83.5 (vs Opus 4.7: 79.3)
- 100T+ pretraining data
- Commercial license through Ollama Cloud partnership
- Zero data retention, US-based

**Verdict for user tasks:** Best for long-context pipelines (e.g., full video analysis). Too new (4 days old, 24.8K pulls) for production default.

---

## Cross-Model Observations

1. **All three are cloud-only** — `cloud` tag means Ollama Cloud API, not local download. User's `custom` provider in Hermes must proxy Ollama Cloud.

2. **Context sizes vary significantly** even within similar use cases:
   - Kimi K2.6: 256K
   - Gemma 4 31B: 256K
   - MiniMax M3: 512K guaranteed / 1M max

3. **Explicit language mention matters:** Kimi K2.6 explicitly lists Rust in its key features. Gemma 4 and MiniMax M3 do not mention Rust specifically.

4. **Recency vs. stability tradeoff:**
   - Most stable: Kimi K2.6 (1 month, 285K pulls)
   - Most bleeding edge: MiniMax M3 (4 days, 24.8K pulls)
   - Most actively maintained: Gemma 4 (6 hours ago)

## Ollama Navigation Notes
- Filter textbox on `ollama.com/library` does NOT work via accessibility APIs (`browser_type` fails silently)
- Use `https://ollama.com/search?q=<keyword>` for reliable discovery
- Model detail pages contain structured metadata (Size/Usage, Context, Input, Readme highlights)
- Always scroll to "Readme" section for benchmark images and architecture details
