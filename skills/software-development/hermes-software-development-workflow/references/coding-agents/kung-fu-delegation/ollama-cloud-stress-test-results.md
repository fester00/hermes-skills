---
title: "Ollama Cloud Pro Stress-Test: Concurrent Request Limits"
date: 2026-05-08
model: kimi-k2.6:cloud
provider: ollama-launch (http://127.0.0.1:11434/v1 → ollama-cloud)
subscription: Ollama Pro ($20/mo)
---

# Stress-Test Results: Real-World Ollama Cloud Limits

## Setup

| Component | Value |
|-----------|-------|
| Model | `kimi-k2.6:cloud` |
| Provider | `ollama-launch` (local proxy) |
| Backend | `ollama-cloud` (https://ollama.com/v1) |
| Plan | Ollama Pro |
| max_concurrent_children (config) | 3 |
| delegate_task runtime cap | 2 (кеш сессии, требует `/new` для обновления) |
| OpenCode version | 1.3.15 |

## Test 1: 3 delegate_task Subagents (Easy Tasks)

**Result:** ❌ `Too many tasks: 3, but max_concurrent_children is 2`
- Config shows 3, runtime cached 2
- Не Ollama, а Hermes runtime cap

## Test 2: 2 delegate_task Subagents (Easy Tasks)

**Result:** ✅ Success — 6.88 sec, no exhaustion

## Test 3: 2 delegate_task Subagents (Heavy Tasks — 300+ LOC TypeScript)

**Result:** ✅ Success — 47.18 sec, no exhaustion

## Test 4: Full Stress — 2 delegate_task + OpenCode + Parent (2026-05-08 evening)

**Result:**
- ✅ OpenCode: жив 3+ min, CPU 59%
- ⚠️ Subagent 1: Прерван от нового сообщения
- ⚠️ Subagent 2: Прерван (166s elapsed)
- ✅ auth.json: ALL OK

## Test 5: Sequential 2 OpenCode → then 2 delegate (2026-05-08 evening)

**What happened**: Запустил 2 OpenCode → дождался завершения → затем запустил 2 delegate_task.

**Timeline:**
- OpenCode 1: `20:11:40 → 20:12:15` (35 сек)
- OpenCode 2: `20:11:39 → 20:11:59` (20 сек)
- delegate_task 3: `20:12:30 → 20:12:50` (38.79 сек)
- delegate_task 4: `20:12:30 → 20:12:50` (38.58 сек)

**Peak concurrency**: 2 одновременно — **не true parallel of 4**.

**What this proves**: delegate_task и OpenCode — **разные пулы**, не конкурируют за `max_concurrent_children`.

## Test 6: Goal — True 4-Agent Parallel

**Not yet proven** — требуется одновременный запуск:
1. `nohup opencode run ... &` (Agent E)
2. `nohup opencode run ... &` (Agent D)
3. **Немедленно**, не дожидаясь — `delegate_task([1, 2])` (Agents B, C)

**Лимитирующий фактор**: Ollama Cloud HTTP workers (не 429, а queue/wait).

## Critical Discoveries

**delegate_task ПРЕРЫВАЕТСЯ** при новом сообщении пользователя.

**OpenCode** — **не прерывается** (отдельный процесс).

**delegate_task runtime cap = 2**, независимо от config.yaml (требует `/new` или restart).

## Parity Analysis: Hermes delegate vs OpenCode (opencode run)

| Capability | delegate_task (Hermes) | OpenCode (nohup) |
|---|---|---|
| **max_concurrent_children** | 2 (runtime cap) | ❌ None — not tracked |
| **session interrupt safety** | ❌ **INTERRUPTED** by user message | ✅ **NOT interrupted** |
| **model access** | ✅ Same model as parent | ✅ Same model (reads config) |
| **tool access** | ✅ Full toolsets | ⚠️ No Hermes tools (terminal only) |
| **web search** | ✅ Yes | ❌ No |
| **tool invocation** | ✅ terminal, read_file, etc | ⚠️ Limited — terminal only |
| **timeout** | 1500s default | Unlimited (process) |
| **speed** | ~1 min setup overhead | ~5-10s startup via nohup |
| **price ($/token)** | ❌ Parent charge (2x if 2 subagents, but shared 1 context model) | ⚠️ Also charges via proxy (same token pricing) |
| **memory / persistence** | ✅ Has user's context, task description, tool output | ❌ **No** — fresh context |

--- (below unchanged)

## Recovery

```bash
hermes auth reset ollama-cloud
```

---
#last-verified: 2026-05-08