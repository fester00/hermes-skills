---
name: knowledge-first-protocol
description: Protocol for information retrieval — what to search and where. Compact checklist for every user request.
version: 1.2.0
author: Master Ugwai
metadata:
  hermes:
    tags: [workflow, protocol, memory, obsidian, search]
---
> **Version:** 1.3.0  
> **Date:** 2026-06-29

## При КАЖДОМ запросе пользователя

**Шаг 0 — Оценить и уточнить запрос (5-15 сек):**
- Если запрос неясен, амбициозен или требует материалов — задать 1-2 уточняющих вопроса.
- Не прыгать к execution, пока нет достаточного контекста.

**Шаг 1 — Быстрые внутренние источники (5-15 сек):**
1. `session_search(query="<тема запроса>")` — проверить прошлые разговоры
2. **Skills Discovery:**
   - Обязательно вызвать `skills_list()` (или `skills_list(category="...")`) для поиска наиболее специфичного навыка.
   - Системный prompt содержит только подсказку (hint); полный каталог живёт в `~/.hermes/skills/`.
   - Obsidian-реестр `Operations/MOC — Skills.md` может отставать, поэтому `skills_list()` — единственный авторитетный источник.
   - После обнаружения релевантного навыка загрузить его через `skill_view(name="<skill_name>")`.
   - Для задач по разработке ПО дополнительно загружать:
     - `superpowers-workflow` — полный lifecycle
     - `superpowers-writing-plans` — если задача требует создания/изменения 2+ файлов или имеет 2+ этапа
     - `code-quality-gates` — для verification gates
     - доменные навыки (например, `frontend-efficiency-audit`, `frontend-css-maintenance`)

**Шаг 2 — Обсидиан — основная база знаний и навыков (если шаг 1 недостаточно):**
3. `mcp_obsidian_search_vault(vault="obsidian-memory", query="<тема>")` — поиск по базе знаний
4. `mcp_obsidian_read_note(vault="obsidian-memory", filename="<MOC>.md", folder="<path>")` — читать MOC или заметку
5. Основные MOC:
   - `Knowledge/MOC — Index.md` — общая карта хранилища
   - `Projects/MOC — Projects.md` — активные проекты (Pentajunior, VIDVIS и т.д.)
   - `Operations/MOC — Skills.md` — индекс навыков Hermes
   - `Operations/MOC — Operations.md` — runbooks, баги, мониторинг
   - `Operations/Runbooks/Hermes — Knowledge Retrieval Protocol.md` — полная версия этого протокола
   - `Knowledge/Technical/MOC — Technical.md` — технический справочник
6. Если MCP Obsidian недоступен (timeout / ClosedResourceError) — немедленно переключиться на терминальный fallback: читать файлы напрямую из `~/obsidian-memory/` через `read_file` или `search_files`. Никогда не пропускать поиск в Обсидиане из-за сбоя MCP.

**Шаг 3 — Проекты (если запрос про активный проект):**
7. Читать файлы проекта напрямую — пути в `Projects/` Обсидиана или `~/projects/`

**Шаг 4 — Внешние источники (только если внутренних недостаточно):**
8. `web_search` или `browser_navigate` для документации, best practices, новых данных

## Ключевые MOC Обсидиана (чек-лист):

| Тема запроса | Где искать |
|---|---|
| Проект (VIDVIS, Pentajunior, htdata) | `Projects/MOC — Projects.md` |
| Навык / Skill Hermes | `Operations/MOC — Skills.md` |
| Операции / Runbook / Баг | `Operations/MOC — Operations.md` |
| Технический справочник | `Knowledge/Technical/MOC — Technical.md` |
| Rust обучение | `Knowledge/Technical/Rust/Чит-лист_Rust.md` |
| Общая навигация | `Knowledge/MOC — Index.md` |

## Правила:

- **Knowledge-First:** проверять session search, skills и Обсидиан перед веб-поиском.
- **Obsidian как база навыков:** MOC — Skills, MOC — Operations, Knowledge Retrieval Protocol — первые места для поиска процедур.
- **Никогда не дублировать** детали проектов в memory — они в Обсидиане.
- **Никогда не дублировать** runbook'и в memory — они в `Operations/Runbooks/`.
- **MCP fallback:** при timeout/ClosedResourceError сразу читать `~/obsidian-memory/` через `read_file`/`search_files`.
- **Если в Обсидиане нет** — добавить найденное туда после решения, обновив соответствующий MOC.
- **Не прыгать к execution** без уточнения неясных запросов.
- **Системный промпт:** если пользователь просит "внести в системный промпт" инструкцию/протокол, целевой файл — `~/.hermes/SOUL.md`. Добавлять туда рядом с персоной, чтобы каждая новая сессия видела его автоматически. См. `references/SOUL.md-knowledge-first-block.md` и `references/SOUL.md-edit-verification.md` для проверки результата.

## Obsidian как persistent agent memory

На основе исследования agentic workflow'ов (см. `references/obsidian-agentic-workflow-research.md`):

- Хорошо организованный vault = canonical memory для агента.
- Рекомендуемая структура:
  - `AGENTS.md` — durable agent-правила в корне vault (scope, folder map, safety rules).
  - `tasks.md` — active work, blockers, handoff notes между сессиями.
  - `Projects/` — canonical project pages.
  - `Operations/Skills/` — индексы и выжимки по Hermes skills.
  - `People/` — canonical people pages (если релевантно).
  - `Scripts/` — shared deterministic utilities.
- При появлении повторяющегося workflow более 2 раз — вынести в skill или script.
- Memory Hermes должна хранить только **координаты** (MOC entry points, критические правила), а **детали** жить в Obsidian.

## Rules for storing rules (anti-duplication)

Different rule layers have different durability and scope. Do NOT duplicate content across them.

| Layer | What belongs there | Examples |
|---|---|---|
| **System prompt / `~/.hermes/SOUL.md`** | Persona, tool availability, core philosophy only | "You are Master Ugwai", "Load skills before acting" |
| **Hermes memory (`MEMORY.md`)** | Coordinates and reminders: MOC paths, critical facts, short triggers | "For software work load `superpowers-workflow`", "Full workflow in Obsidian `workflows/knowledge-first-workflow.md`" |
| **`AGENTS.md` in vault root** | Durable agent constitution: scope, folder map, safety rules, task conventions | "Read this file first", "Check `tasks.md`", "Do not bulk-migrate without approval" |
| **`tasks.md` in vault root** | Active work, blockers, handoff notes | "Continue VIDVIS delivery page", "Blocker: waiting for real contacts" |
| **Skills (`~/.hermes/skills/`)** | Class-level how-to: procedures, pitfalls, execution patterns | `superpowers-workflow`, `superpowers-writing-plans` |
| **Obsidian runbooks / notes** | Detailed reference, project facts, research synthesis | `Hermes — Knowledge Retrieval Protocol`, project notes |

### Consequences

- If a rule is durable and vault-wide → put it in `AGENTS.md`.
- If a rule is a short trigger for this user → put it in Hermes memory.
- If a rule is detailed procedure for a class of task → put it in the relevant skill.
- If a rule is project- or environment-specific → put it in Obsidian, not memory or a skill.
- Never put a full checklist or runbook in memory — memory is ~2,200 chars and is read every turn. Details belong in Obsidian or skills.
- When the user says "this should not duplicate the system prompt", review the four layers above and move the rule to the correct layer.

## Updating the workflow stack

When the user asks to change how the agent works:

1. Clarify which layer the change targets: system prompt, memory, AGENTS.md, skills, or Obsidian workflow notes.
2. Make the change in **one canonical place**.
3. Update other layers only with short pointers, never with full copies.
4. Verify there is no duplication: search the vault and memory for the same rule.

## Vault structure standard

Maintain and use this structure inside the primary vault (`~/obsidian-memory`):

| Path | Purpose |
|---|---|
| `AGENTS.md` | Durable agent constitution; read at session start |
| `tasks.md` | Active work, blockers, handoff notes |
| `Knowledge/MOC — Index.md` | Top-level map |
| `Projects/MOC — Projects.md` | Active projects |
| `Operations/MOC — Skills.md` | Hermes skills index |
| `Operations/MOC — Operations.md` | Operations index |
| `Operations/Runbooks/` | Step-by-step procedures |
| `People/` | Canonical people pages (create as needed) |
| `Scripts/` | Deterministic utilities (create as needed) |

If `AGENTS.md` or `tasks.md` is missing, create it. If the user has not created `People/` or `Scripts/`, create them on first relevant need.

## Skill opportunity detection

When the same agent workflow or mechanical transformation appears **2 or more times**:
- Capture it as a new `references/<workflow>.md` under the relevant skill, or
- Capture it as a `scripts/<utility>.sh|py` if deterministic, or
- Propose a new class-level skill if it crosses domains.

## Web research under blocks

When external search engines or sites block automated access during research:
1. Prefer direct URLs of known authoritative sources over search engines.
2. Dispatch parallel subagents by source category (official, expert, technical, trends).
3. Do NOT solve CAPTCHA or Cloudflare challenges; switch to direct site URLs.
4. DuckDuckGo main site (`duckduckgo.com/?q=...&t=h_&ia=web`) works better than `html`/`lite` endpoints.
5. For 404 on direct article URLs, browse the site's analytics/blog section or use its internal search.
6. Record date, URL, and 2-4 key takeaways per source.

See `references/web-research-under-blocks-pattern.md` for full pattern and recommended Russian-language SEO research sources.

## Tool pitfall: `search_files` regex vs glob

`search_files` uses ripgrep and expects a **regex** pattern, not a shell glob.
Passing `pattern='*.md'` with `target='content'` fails with a regex parse error.

- Use `target='files'` + `pattern='*.md'` when finding files by name (glob mode).
- Use `pattern=r'\.md$'` with `target='content'` only when searching inside files.
- For directory inventories, prefer `terminal` (`ls /path` / `find ...`).
- For known file sets, read them directly with `read_file` instead of searching.

## References

- `references/SOUL.md-knowledge-first-block.md` — how to add this protocol to `~/.hermes/SOUL.md`
- `references/SOUL.md-edit-verification.md` — verify the edit landed
- `references/obsidian-agentic-workflow-research.md` — Obsidian + AI agent workflow best practices from external sources (AGENTS.md, tasks.md, skill grouping, vault structure)
- `references/anti-duplication-layer-map.md` — summary of which rule goes where
- `references/web-research-under-blocks-pattern.md` — practical pattern for research when search engines block automated access
