# Reference: LLM Model Comparison — Kimi K2.6 vs Minimax M3 vs Gemma 4 31B (June 2026)

## Session context
- **User profile**: learning Rust (web backend), Python/JS/TS background, Next.js projects, luxury web design
- **Goal**: compare three models for socratic course generation, agentic coding, and multimodal pipelines
- **Key lesson**: Kimi K2.6 context is 256K per Ollama page — NOT 2M. Agent initially misremembered from other Kimi variants.

## 1. Discovery (Ollama metadata extraction + Arena AI verification)

**Critical rule**: ALWAYS re-read the current Ollama page. Do not rely on memory of specs from other sessions.

```bash
# Quick discovery
curl -sL "https://ollama.com/library?q=kimi"   | grep -o 'href="/library/[^"]*'
curl -sL "https://ollama.com/library?q=minimax" | grep -o 'href="/library/[^"]*'
```

Navigate each page with browser and extract:
- `Context` line (exact tokens)
- `Size` / `Parameters` line
- `Tags` row (vision, tools, thinking, audio, cloud)
- `Input` row (Text, Image, Audio, Video)
- `Models` table (local weights vs cloud-only)
- Download count & last updated

**Arena AI leaderboard verification** (lmarena.ai → Text tab → View all):
- Search body.innerText for model slug to get ELO ranking
- Example results from this session:
  - `minimax-m3` — 1531 ±17 (~7th place)
  - `kimi-k2.6` — 1517 ±9 (~9th place)
  - `gemma-4-31b` — ~39th place

Key extracted data:
| Field | Kimi K2.6 | MiniMax M3 | Gemma 4 31B |
|---|---|---|---|
| Downloads | 284.5K | 23K | 12M (family) |
| Last updated | 1 month ago | 4 days ago | 16 hours ago |
| Parameters | 1.04T | undisclosed | 31B Dense |
| Guaranteed context | **256K** | **512K** | **256K** |
| Max context | 256K | 1M | 256K |
| Tags | vision, tools, thinking, cloud | vision, tools, thinking, cloud | vision, tools, thinking, audio, cloud |
| Input | Text, Image | Text, Image | Text, Image (31B); Audio only E2B/E4B/12B |
| Local weights | ❌ Cloud only | ❌ Cloud only | ✅ 20GB, Apache 2.0 |
| Arena ELO (Text) | 1517 ±9 | 1531 ±17 | ~39th |
| Agentic strengths | 300 sub-agents, swarm | Tool invocation, BrowseComp 83.5 | Function calling, system prompt |
| Coding benchmark | Long-horizon Rust/Go/Python | Frontier coding (claimed) | LiveCodeBench 80%, Codeforces 2150 |

## 2. Cross-checking multimodal claims

Gemma 4 is the trickiest: audio support varies by size.
- **E2B, E4B, 12B**: audio + image + text (CoVoST, FLEURS benchmarks on Ollama page)
- **26B, 31B**: **NO audio**, only text + image
- Always check the `Audio` section of the benchmark table on Ollama page — dashes ("-") mean unsupported.

## 3. Task-fit mapping

| User task | Best fit | Rationale |
|---|---|---|
| Socratic Rust course (proven) | Kimi K2.6 | Already validated with `socratic-course-architect` skill |
| Long course (10+ modules, no summaries) | MiniMax M3 | 512K-1M context holds multiple modules |
| Offline / privacy / Apache 2.0 | Gemma 4 31B | Only one with local weights + open license |
| CPU-only inference | Gemma 4 12B | 7.6GB, runs on 16GB RAM (Habr confirmed) |
| Audio transcription | None of these | Use Whisper — no 31B model has native audio |
| Video analysis | None natively | ffmpeg frames + any vision-capable model |

## 4. Risk assessment
- **MiniMax M3**: low downloads (23K), recent, Chinese company — possible API pricing opacity. US servers (zero data retention per Ollama).
- **Kimi K2.6**: mature (284K downloads), proven in our workflow.
- **Gemma 4 31B**: very high downloads, frequent updates, BUT Arena ranking ~39th suggests quality gap vs frontier cloud models for interactive use.

## 5. Output format
Present: spec table → per-scenario strengths → scenario-based verdict table → test command.
Never declare a single global winner. Always note when a model has been "proven in our workflow" vs "needs testing."

## 6. Key URLs
- https://ollama.com/library/kimi-k2.6
- https://ollama.com/library/minimax-m3
- https://ollama.com/library/gemma4
- https://arena.ai/leaderboard?arena=text&view=all
- https://huggingface.co/google/gemma-4-12B
- https://habr.com/ru/news/1043342/
