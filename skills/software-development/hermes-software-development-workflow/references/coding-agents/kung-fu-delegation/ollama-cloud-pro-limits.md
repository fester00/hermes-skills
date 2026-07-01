---
title: "Ollama Cloud Pricing & Limits — Extracted 2026-05-08"
source: https://ollama.com/pricing, https://docs.ollama.com/faq
---

# Ollama Cloud Plans

## Plans Overview

| Plan | Price | Concurrent Models | Usage Multiplier | Target Use |
|------|-------|-------------------|------------------|------------|
| Free | $0 | ? | 1x | Light usage, chat, small models |
| **Pro** | $20/mo or $200/yr | **3** | **50x** Free | Day-to-day work, larger models, coding, research |
| Max | $100/mo | **10** | **250x** Free | Heavy sustained usage, continuous agents, large models |

## Usage Model

- **Measured in GPU time** — not fixed token count or request count
- Depends on: model size, request duration, context caching
- "Shorter requests and prompts that share cached context use less"
- Limits reset: **every 5 hours** (session) + **every 7 days** (weekly)
- 90% usage warning via email (can disable in settings)

## Local vs Cloud Concurrency

**Local Ollama server** (`ollama serve`):
- `OLLAMA_MAX_LOADED_MODELS` — default 3 (or 3 × GPU count)
- `OLLAMA_NUM_PARALLEL` — default 1 per model
- `OLLAMA_MAX_QUEUE` — default 512

**Ollama Cloud** (Pro/Max via `ollama.com/v1`):
- Hard cap: **3 concurrent models** for Pro
- No `num_parallel` tuning — provider-managed
- Queuing happens on provider side

## Key FAQ Excerpts

> "How many cloud models can I run at once? Concurrency limits ensure dedicated capacity for workflows that need..."

> "Usage reflects actual utilization of Ollama's cloud infrastructure — primarily GPU time, which depends on model size and request duration."

> "Ollama doesn't cap you at a set number of tokens."

## Credential Pool Exhaustion

Under heavy concurrent load with ollama-cloud provider, `~/.hermes/auth.json` may mark key as `exhausted` with `last_error_code: 401`.

**Fix:** `hermes auth reset ollama-cloud`

**Prevention:** Keep concurrent cloud requests ≤ 3 for Pro, ≤ 2 for heavy/long tasks.
