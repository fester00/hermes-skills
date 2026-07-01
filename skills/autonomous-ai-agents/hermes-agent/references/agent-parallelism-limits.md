---
title: Agent Parallelism Limits — Confirmed Experiment
date: 2026-06-04
source: stress-test session with 4 subagent tasks
---

# Подтверждённые лимиты параллелизма агентов

## delegate_task (субагенты)

| Параметр | Значение |
|----------|----------|
| `max_concurrent_children` | **3** |
| Поведение при превышении | Batch из 4+ задач отклоняется с ошибкой `Too many tasks: 4 provided, but max_concurrent_children is 3` |
| 4-й+ субагент | Запускается **последовательно**, после освобождения пула |
| Процессы | Каждый субагент — отдельный PID (подтверждено: PID 618486, 618493, 618502, 618543) |

**Эксперимент:** 04.06.2026 — запущен batch из 4 задач (сумма чисел 1..5_000_000). Система отказала. Batch из 3 выполнился параллельно за 15.37 сек. 4-й выполнен отдельным вызовом за 22.1 сек.

## Standalone CLI-агенты (OpenCode, Codex, Claude Code)

| Параметр | Значение |
|----------|----------|
| Учёт в `max_concurrent_children` | **НЕТ** — это отдельные OS-процессы |
| Параллельность с subagents | **Да**, могут работать одновременно с 3 субагентами |
| Теоретический максимум | 3 subagents + 2-3 standalone CLI = **5-6 агентов** одновременно |

## Практическая схема максимального параллелизма

```
┌─────────────────────────────────────┐
│         Hermes (master)             │
│                                     │
│  delegate_task pool (max 3)         │
│  ├── Subagent A                     │
│  ├── Subagent B                     │
│  └── Subagent C                     │
│                                     │
│  Standalone CLI (вне пула)          │
│  ├── OpenCode process               │
│  ├── Codex process                  │
│  └── Claude Code process            │
└─────────────────────────────────────┘
```

## Как изменить лимит

```yaml
# ~/.hermes/config.yaml
delegation:
  max_concurrent_children: 6  # или другое значение
```
