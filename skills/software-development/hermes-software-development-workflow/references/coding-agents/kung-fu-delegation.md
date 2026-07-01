---
name: kung-fu-delegation
description: Kung Fu Panda themed multi-agent delegation. Master Ugwai (Hermes) orchestrates + 2 OpenCode background agents for true parallelism. No credential pool exhaustion, no session interruption.
version: 2.0.0
author: Master Ugwai
updated: 2026-05-08
tags: [delegation, subagent, opencode, kung-fu-panda, multi-agent]
metadata:
  hermes:
    delegate_task_hard_cap: 2 (runtime limit, always 2 regardless of config.yaml)
    delegate_task_timeout: 1500 seconds (25 minutes) — confirmed by stress test 2026-05-08
    opencode_agents: 2 (background processes, independent of Hermes session)
    max_true_simultaneous: 2 (2 OpenCode as primary; delegate_task as auxiliary for short tasks only)
    total_orchestrated: "3 peak: 1 Hermes + 2 OpenCode; delegate_task only when OpenCode idle"
    opencode_path: "/home/natan/.nvm/versions/node/v24.13.1/bin/opencode"
    opencode_version: "1.3.15"
    related_skills: [hermes-agent, subagent-driven-development]
    stress_test_verified: "2026-05-08: 2 delegate=OK(40s), 2 OpenCode=OK(35s), MIXED 2OC+2del=delegates queue(99s)"
---

# Kung Fu Delegation v2.0 ⚡🐼

## Updated Architecture: 2 OpenCode + 1 Hermes

| Slot | Agent | Тип | Задачи | Параллельность |
|------|-------|-----|--------|----------------|
| **A** | **Master Ugwai** (Hermes, Telegram) | Интерактивный | Планирование, роутинг, ответы пользователю, synthesize | ✅ Не прерывается при новых сообщениях |
### Auxiliary slot (short tasks only)
| Slot | Agent | Тип | Задачи | When to use |
|------|-------|-----|--------|-------------|
| **B** | **delegate_task 1** (Hermes subagent) | Internal | Короткие задачи: read/write ≤3 файлов, точечные патчи, быстрые проверки | Only when OpenCode idle AND task < 5 min |
| **C** | **delegate_task 2** (Hermes subagent) | Internal | Короткие задачи, тесты, проверки | Only when OpenCode idle AND task < 5 min |

**delegate_task** — **максимум 2** одновременно, **hard timeout 1500 секунд** (25 min). Runtime cap.

**НО**: delegate_task прерывается при новом сообщении Telegram ❌. Не используй для длинных задач.

**Эффективный максимум одновременности:**
- **2 OpenCode** = 2 агента реально параллельно ✅ (основной режим)
- **2 OpenCode + 1 delegate_task** = 3 агента, но delegate в очереди ❌
- **2 delegate_task + 0 OpenCode** = 2 агента, только для быстрых задач ✅
- **2 OpenCode + 2 delegate_task** = delegates ждут в очереди ❌ (работают, но медленно)

### Command to activate nvm before running opencode

```bash
- Делегирование теперь чистое: toolsets + context, без ролевых персон
- Единственная persona: Master Ugwai (главный ассистент)
- **См. также** [[hermes-ops-devops]] — диагностика и восстановление инфраструктуры (зомби-процессы, Telegram fallback IP)

## Запуск OpenCode агентов

```bash
# Agent B: тяжёлый кодинг (backend, architecture)
nohup opencode run "Полная задача с context" > /tmp/oc-$(date +%s).log 2>&1 &

# Agent C: тяжёлый кодинг (frontend, tests)
nohup opencode run "Полная задача с context" > /tmp/oc-$(date +%s).log 2>&1 &
```

### Requirements для OpenCode задачи
- **Полный context**: пути файлов, архитектура, требования
- **Absolute paths**: `/home/natan/projects/...` вместо относительных
- **Язык**: "Respond in Russian"
- **Output**: сохранить в файл, не в stdout (чтобы лог не раздулся)

### OpenCode `run` Mode — Unreliable for Multi-File Code Gen (Verified 2026-05-31)

**Discovery:** `opencode run --model <provider/model> --dir <path> "<prompt>"` streams `message.part.delta` for 4+ minutes but **creates zero files**. Two independent attempts confirmed: qwen3 (model not found, immediate fail) and kimi-k2.6:cloud (4+ min deltas, exit 143, zero files). `git status --short` showed only files created by Hermes before dispatch.

**Why:** `run` mode treats the prompt as a chat Q&A to respond to, not as a directive to modify the filesystem. No file-write MCP tools are activated.

**Alternatives for multi-file code generation:**

| Approach | Command | Reliability |
|----------|---------|-------------|
| Claude Code | `claude -p "<detailed prompt>"` | ✅ High |
| Hermes direct | Do it yourself | ✅ Highest (often fastest for 6-12 files) |
| Hermes delegate_task | `delegate_task(tasks=[...])` | ✅ High (up to 2 parallel, Telegram-interruptible) |
| OpenCode interactive | `opencode <dir>` (TUI) | ⚠️ Needs human to start |

**Rule:** For admin panels, CRUD, any 6+ file task with full context → **Hermes direct is faster than debugging agent setup**. Reserve agents for truly independent parallel workstreams.

**Verification rule:** Check `git status --short` within 60 seconds of dispatch. Zero new files → kill process, switch approach immediately.

## Routing Matrix (Updated)

| Задача | Hermes direct | delegate_task | OpenCode run | Claude Code | Notes |
|--------|---------------|---------------|--------------|-------------|-------|
| Простой поиск/чтение (1-2 файла) | ✅ Direct | ❌ | ❌ | ❌ | Hermes fastest |
| Точечные патчи (≤3 файла, ≤10 min) | ✅ | ✅ OK | ❌ | ❌ | delegate OK for short |
| Рефакторинг 5+ файлов | ✅ Plan | ❌ Timeout | ❌ Unreliable | ✅ Claude | Hermes plan → Claude or direct |
| Написать полный API (300+ строк) | ✅ Direct | ❌ | ❌ Unreliable | ✅ Claude | Hermes direct often wins |
| Написать admin panel (6-12 файлов) | ✅ Direct | ❌ | ❌ **Zero files** | ✅ Claude | Verified: Hermes 20 min vs OC 4+ min wasted |
| Debug production (logs + поиск) | ✅ | ❌ | ❌ | ❌ | Hermes only (needs web/search) |
| Сложный анализ архитектуры | ✅ | ❌ | ❌ | ❌ | Hermes reads files + synthesizes |

### Critical rule: NO delegate_task for long tasks

**delegate_task hard timeout = 1500 секунд (25 min)**. Задачи, которые гарантированно падают:
- Чтение 5+ файлов + анализ
- Поиск по кодовой базе + ревью
- Миграция API (v1 → v2)
- Написание 300+ строк кода
- Любая задача с web-поиском + файловым анализом

**Решение**: Ugwai делает рекогносцировку сам (2-5 `read_file`/`search_files`/`terminal`), формирует сжатый контекст, и отдаёт **OpenCode** (для кодинга) или делает сам (для анализа).

## Example: Full-stack feature

1. **Ugwai** (Hermes): Создаёт план, todo, задаёт архитектуру
2. **OpenCode B**: `nohup opencode run "Напиши Express API на TypeScript..." &`
3. **OpenCode C**: `nohup opencode run "Напиши React-компониты..." &`
4. **Ugwai** ждёт, собирает `/tmp/oc-*.ts`, проверяет, даёт фидбек

## Pitfalls

### Always verify tool availability with nvm paths
On servers with nvm, `which` from the default shell may NOT see Node tools. They live under `~/.nvm/versions/node/v*/bin/` and are only in PATH after `source ~/.nvm/nvm.sh`. If you report a tool as "not found" — you are likely WRONG. Use this pattern:

```bash
# find across filesystem (slow but exhaustive)
find / -name "opencode" -type f 2>/dev/null

# or try nvm path explicitly
env -i PATH="/home/natan/.nvm/versions/node/v24.13.1/bin:$PATH" which opencode
```

⚠️ **Never modify a skill based on a negative `which` result alone.** Verify with `find` or nvm PATH first.

- OpenCode **не имеет** web search, browser, todo, memory — если нужна исследовательская часть, делай её в Hermes, потом отдавай OpenCode
- OpenCode **не умеет** `delegate_task` — он одиночный кодер
- **Никогда** не запускай >2 OpenCode одновременно при интерактивной работе — 4 запроса (2 OC + я + субагент?) может перегрузить kimi-k2.6
- OpenCode **не обрабатывает** длинные stdout — всегда сохраняй результат в файл
- `delegate_task` таймаутит на **1500 секунд** (25 минут) — если задача требует чтения 10+ файлов (поиск v2, ревью архитектуры, миграция API) плюс web-поиск, субагент гарантированно упадёт. **Решение**: Ugwai делает рекогносцировку сам (2-5 `read_file`/`search_files`/`terminal`), формирует сжатый контекст, и отдаёт **OpenCode** (для кодинга) или делает сам (для анализа). Не давай агенту открытый доступ к `web` если он уже загружает файловый анализ — это комбинация = смерть по таймауту.

## Session Interruption Safety

| Что прерывается | Когда | Как защититься |
|-----------------|-------|----------------|
| `delegate_task` | Новое сообщение в Telegram | ❌ Не защитить |
| OpenCode | Новое сообщение в Telegram | ✅ **Не прерывается** (отдельный процесс) |
| Hermes (я) | Никогда — я главный | ✅ Я всегда отвечаю |

## Recovery from Long Tasks

```bash
# Проверить жив ли OpenCode
ps aux | grep opencode | grep -v grep

# Прочитать результат
cat /tmp/oc-*.log
cat /tmp/opencode-*.ts

# Если нужно — убить
pkill -f "opencode run"
```

## Reference: Ollama Pro Stress-Test Data

Удостоверили лимиты empirically — см. `references/ollama-cloud-stress-test-results.md` для полных данных.
