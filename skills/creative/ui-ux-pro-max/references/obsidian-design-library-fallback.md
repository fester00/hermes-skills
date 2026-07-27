# Obsidian design library as a fallback for ui-ux-pro-max

Сессионная заметка из silicone-landing (июль 2026).

Пользователь напомнил: при работе с дизайн-навыками у него в обсидиане есть библиотека примеров, и если в навыках нет ссылки на библиотеку — можно обращаться туда.

## Структура локальной библиотеки

Vault: `~/obsidian-memory/`
Раздел: `Design/UI-UX Pro Max/`

Ключевые заметки:
- `Design/UI-UX Pro Max/Product Types.md` — все 161 тип продукта
- `Design/UI-UX Pro Max/VIDVIS Reference.md` — референс для VIDVIS
- `Design/UI-UX Pro Max/Pentajunior Reference.md` — корпоративный референс
- `Design/UI-UX Pro Max/htdata Reference.md` — dashboard референс
- `Design/UI-UX Pro Max/Style Catalog.md` — 67 UI-стилей
- `Design/UI-UX Pro Max/Color Palettes.md` — ключевые палитры
- `Design/UI-UX Pro Max/Typography.md` — 57 пар шрифтов

## Когда MCP Obsidian недоступен

Если `mcp__obsidian__search_vault` возвращает `TimeoutError` или `unreachable`, не прерывать работу. Варианты:

1. **Прямое чтение файлов** через `read_file` / `search_files`:
   ```bash
   search_files --path ~/obsidian-memory/Design --pattern "contact card"
   read_file ~/obsidian-memory/Design/UI-UX\ Pro\ Max/Style\ Catalog.md
   ```
2. **Если искомой заметки нет** — работать по данным CSV-навыка ui-ux-pro-max и общим принципам `popular-web-designs` / `claude-design`.

## Практический паттерн

При запросе «сделай дизайн / редизайн»:
1. Загрузить `ui-ux-pro-max` и `popular-web-designs`.
2. Попытаться получить бриф из CSV-скриптов навыка.
3. Если пользователь ссылается на библиотеку в Obsidian — попробовать `mcp__obsidian__search_vault`.
4. При падении MCP сразу переключиться на `read_file` / `search_files` в `~/obsidian-memory/Design/`.
5. Не сообщать «Obsidian недоступен» как блокер — просто использовать альтернативный путь.

## Подчёркнутый для себя урок

- `ui-ux-pro-max` — это *интеллектуальная база* (CSV + скрипты).
- `~/obsidian-memory/Design/` — это *библиотека примеров пользователя*.
- Обе нужны, но Obsidian не должен быть единой точкой отказа.
