---
name: codebase-memory-audit
description: Use when exploring or modifying an existing project with more than a few files.
category: software-development
related_skills:
---

# codebase-memory-audit

Index and query a project knowledge graph using [codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp).

**Core principle:** Understand the codebase structure before changing it.

---

## When to use

Activate during the **Knowledge Discovery** phase when:

- The user asks to study, explore, refactor, or modify an **existing project**.
- The project has **more than 5 files**.
- The user asks architecture, dependency, structure, or "what calls X" questions.
- This is the first exploration of an unfamiliar codebase.

Do NOT run for:
- One-liner shell commands
- Pure explanations without codebase context
- Single scripts or throwaway prototypes
- Projects already audited in this session (cache is per-project in CBM)

---

## Trigger threshold

| Situation | Action |
|---|---|
| Single file / one-liner | Skip CBM; use `read_file` |
| 2–5 files, simple task | Optional — only if user asks structure questions |
| > 5 files | **Recommended:** index and query the graph |
| > 50 files | **Strongly recommended** — run architecture overview |
| > 200 files | Scope queries to relevant subfolder/package |

---

## Prerequisites

The MCP server must be configured in `~/.hermes/config.yaml`:

```yaml
mcp_servers:               # Hermes reads THIS key (see the native-mcp skill)
  codebase-memory:
    command: /home/natan/.local/bin/codebase-memory-mcp
```

> ⚠️ **Проверено 2026-10-11 (версия 0.11.0):** движок отдаёт **17 инструментов** (`hermes mcp test codebase-memory`).
> Ключ конфига — только `mcp_servers`; блок `mcp: servers:` — это формат **OpenClaw** (единственное место в коде Hermes, где он читается, — скрипт миграции `openclaw_to_hermes.py`), в Hermes он мёртв.
> В секции `mcp:` Hermes читает единственный под-ключ — `auto_reload_on_config_change`.
>
> **Что добавилось в 0.11.0** (после 0.9.0): `get_file_outline` (объявление символов одного файла), `compare_graphs` (сравнение двух индексов — что изменилось), `check_index_coverage` (реальное покрытие и свежесть). Итого 17 инструментов против 14.
>
> **Что движок умеет, а навык не описывал:** `.cbmignore` (исключения как в `.gitignore`),
> лимиты ресурсов индексации (`docs/INDEX_RESOURCE_LIMITS.md`), свежесть индекса и watch-режим,
> `detect_changes` (влияние правок), `index_status` (состояние и покрытие), пагинация графа.
>
> **`ingest_traces` — заглушка, подтверждено описанием самого инструмента в 0.11.0:**
> «Validate and count traces; **graph edge creation is not implemented**». Считать его рабочим нельзя.

When available, this skill uses the native MCP tools. Fallback to CLI is documented below.

---

## Updating the engine (0.9.0 → 0.11.0 и далее)

Встроенный апдейтер (проверено 2026-10-11, 0.9.0 → 0.11.0):

```bash
codebase-memory-mcp update -y --standard     # --standard ОБЯЗАТЕЛЕН: без tty апдейтер падает
                                             # с «variant selection requires a terminal»
```

Три вещи, которые он делает помимо замены бинаря — знать заранее:

1. **Удаляет все индексы** (формат меняется) и говорит «They will be rebuilt automatically». Пересобери вручную — быстрее и предсказуемее:
   `codebase-memory-mcp cli index_repository --repo-path <путь>` (pentajunior-v2 и vidvis — по ~5 с каждый).
2. **Переписывает конфиги агентов**: `~/.config/opencode/opencode.json`, `~/.config/opencode/AGENTS.md` (добавляет блок инструкций «предпочитай граф поиску grep»), а также `~/.claude.json` и `~/.claude/.mcp.json`. **Профили под `~/.config/opencode/profiles/` он НЕ трогает** — наши MCP-профили целы.
3. **Hermes продолжает работать со старым бинарём**, потому что MCP-потомок живёт с момента старта соединения (может — неделями) и держит удалённый inode. Новый бинарь подхватывается так:

```bash
ps -eo pid,ppid,etime,cmd | grep codebase-memory-mcp        # найти потомка с ppid = процесс gateway
readlink /proc/<pid>/exe | grep deleted                       # 'deleted' = старый бинарь
kill <pid>                                                    # Hermes пересоздаёт сервер при следующем вызове
```

Проверено: gateway пересоздаёт MCP-сервер сам, перезапуск gateway не нужен. Каталог инструментов в уже открытой сессии остаётся старым до следующей сессии — это косметика.

---

## Workflow

### Step 1: Confirm project root

Use the `[Workspace::v1: ...]` tag or explicit user path. Verify with:

```bash
pwd
ls -la
```

### Step 2: Index the project

If not already indexed, run:

```bash
codebase-memory-mcp cli index_repository --repo-path <project-root>
```

Or via MCP tool `index_repository` with `repo_path`.

Indexing is fast — реальные замеры 2026-10-11 на 0.11.0: `/home/natan/pentajunior-v2`
(1,9 ГБ, 66k файлов) → 910 узлов / 2433 связи за 5 с; `/mnt/data/natan-storage/vidvis` → 219 / 508 за 5 с.
Оба проекта были пересобраны после обновления движка. Собирается только исходный код — ассеты,
`.next`, `node_modules`, `.git` и всё из `.gitignore`/`.cbmignore` отсекаются by design.

**Project slug** is derived from the path (e.g. `/home/natan/pentajunior-v2` →
`home-natan-pentajunior-v2`). Confirm the slug with `list_projects` before using
it in queries. See `references/cbm-usage-notes.md` for real examples and output
field reference.

> **Правило: индекс ставится ДО разведки, а не после.** Проверено на себе 2026-10-16:
> `pentajunior-v2` был в индексе с прошлого раза, но редизайн и перенос 45 файлов прошли
> на `search_files`/`read_file`/`curl`/SQLite — графом не пользовался ни разу, а проиндексировал
> уже готовое. Порядок такой: `list_projects` → если проект есть, первый вопрос к нему
> через `search_code`/`trace_path` вместо серии поисков по файлам; если нет — `index_repository`
> в первые минуты (проект на 1,9 ГБ собирается за ~5 с, это дешевле одной разведки).
>
> **Работа в песочнице или в ветке — индексируется то дерево, где ты правишь.**
> Индекс основного репозитория про ветку не знает. Если правки идут в копии, песочнице
> или рабочем дереве другой ветки, собери отдельный проект с понятным именем
> (`index_repository(repo_path=<путь>, name='pjv2-redesign-a')`) — тогда новый слой
> ищется графом, а не глазами. Помни: песочница в `tmp/` живёт до чистки, и индекс
> придётся пересобрать заново.

### Step 3: Query the graph

Useful queries:

| Goal | Tool / CLI |
|---|---|
| Architecture overview | `get_architecture` — aspects: all |
| Who calls X? | `trace_path --function-name X --direction inbound` |
| What does X call? | `trace_path --function-name X --direction outbound` |
| Search symbols | `search_graph --label Function --name-pattern ".*Handler.*"` |
| Text search | `search_code --pattern "seo_text"` |
| Cypher-like query | `query_graph --query "MATCH (f:Function)-[:CALLS]->(g) WHERE f.name = 'main' RETURN g.name"` |
| Dead code | `query_graph` with zero in-degree filter |

For exact CLI flag syntax and expected JSON output, see
`references/cbm-usage-notes.md`.

For lessons learned about trying CBM on non-code corpora (e.g. Obsidian vaults),
see `references/non-code-corpora-limitations.md`.

### Step 4: Read and interpret

Key outputs to look for:

- **hotspots** — most referenced functions/modules
- **layers** — entry / internal / core / leaf
- **boundaries** — cross-module call counts
- **clusters** — functional communities
- **entry_points** — top-level routes, scripts, pages

### Step 5: Save summary to Obsidian

Create/update:

```
~/obsidian-memory/Projects/<project-name>/codebase-memory-audit.md
```

Include:
- Project path and CBM version
- Node/edge counts
- Top hotspots
- Layer breakdown
- Boundaries (key cross-module links)
- Notable clusters
- Actionable insights for design/planning

Use the template from `references/cbm-audit-template.md`.

---

## Integration with

This skill runs in **Phase 0: Knowledge Discovery**, before design.

After the audit:
1. Load project-specific skill if one exists (e.g. `pentajunior-v2-seo` for pentajunior-v2).
2. Ask clarifying questions informed by hotspots and boundaries.
3. Proceed to design.

---

## Common pitfalls

- **Wrong project root** — indexing a parent directory adds noise.
- **Indexing node_modules/.next/.git** — CBM excludes these by default.
- **Призрак проекта ≠ удалённый проект.** Если `index_status`/`list_projects` показывает проект без каталога (`root_exists: false`) или путь вида `/tmp/...`, **не считай его мусором и не удаляй молча** — индекс часто строился с копии в `/tmp`, которую ОС чистит, или с промежуточного пути. Прежде чем чистить: найди проект по имени по всему диску (`find /home /mnt/data /srv -maxdepth 5 -iname '*<имя>*'`), загляни в заметки хранилища и проверь git-remote. Так же проверь, нет ли рядом копий `_v2/_v3`: неверсионированная копия может быть **новее** репозитория, и тогда именно она — источник истины для пользователя.
- **Trusting outdated index** — re-index after large changes (в 0.11.0 формат индекса изменился: после апгрейда движка индексы надо пересобрать, иначе граф пуст).
- **Индекс построен, а им не пользуются** — самая частая потеря: проект в индексе, а разведка идёт перебором файлов. Если знаешь вопрос заранее («где используется этот компонент», «что вызывает эту функцию»), один `search_code` отвечает за 13 мс, тогда как серия поисков съедает и время, и контекст. Дисциплина: **открыл чужой проект — сначала граф, потом файлы**.
- **Over-querying** — one good `get_architecture` call replaces many greps.
- **Forgetting to save to Obsidian** — insights should persist across sessions.
- **Indexing non-code knowledge bases** — CBM is built for code, not for Markdown/Obsidian vaults. A vault full of notes yields many `Section`/`File` nodes but weak edges and poor `query_graph`/`search_graph` results. Use MCP Obsidian + `search_files`/`read_file` for vaults instead.

---

## CLI fallback

If the MCP tool is unavailable, use the CLI directly:

```bash
codebase-memory-mcp cli index_repository --repo-path <project-root>
codebase-memory-mcp cli get_architecture --project <project-slug> --aspects all
codebase-memory-mcp cli trace_path --project <project-slug> --function-name <name> --direction inbound
```

Project slug is derived from the path (e.g. `/home/natan/pentajunior-v2` → `home-natan-pentajunior-v2`).

## Using codebase-memory-mcp with OpenCode

OpenCode can consume the same `codebase-memory-mcp` server as an MCP tool, giving it access to the project knowledge graph during coding sessions. See `references/opencode-integration.md` for setup and prompt patterns.

---

## Detecting dead CSS

CBM indexes CSS files as `File` nodes but does **not** track which CSS classes are used by TSX/TS components. For dead-CSS analysis use PurgeCSS instead.

See `references/css-dead-code-detection.md` for the exact command and how to interpret false positives from dynamic `className` construction.

---

## Remember

```
Project root → index_repository → get_architecture/trace_path/search_code → Obsidian → design
```

codebase-memory-audit is a read-only map, not a code change.
