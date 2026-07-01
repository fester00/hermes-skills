# PDF → Markdown → Obsidian

Рецепт конвертации PDF-учебника (например, «Программирование на Rust») в набор Obsidian-заметок с оглавлением и главами.

## Когда использовать

- Пользователь дал PDF-учебник и хочет учиться по нему прямо из Obsidian.
- Нужно разбить книгу на главы/разделы с сохранением структуры.
- Исходник PDF — не скан, а текстовый (код и заголовки копируются).

## Что понадобится

- `pymupdf` + `pymupdf4llm` — быстрая конвертация в Markdown.
- Python 3.11+ и `uv` (или `pip` в venv).
- Путь к Obsidian-ваулу, например `~/obsidian-memory/Knowledge/Technical/<topic>/`.

## Подготовка окружения

```bash
uv venv pdf_extract_venv
source pdf_extract_venv/bin/activate
uv pip install pymupdf pymupdf4llm
```

## Алгоритм

1. Открыть PDF и получить TOC (`doc.get_toc()`).
2. Сгруппировать TOC по главам верхнего уровня (`level == 1`).
3. Для каждой главы определить диапазон страниц.
4. Вызвать `pymupdf4llm.to_markdown(pdf, pages=page_list)` для каждой главы.
5. Очистить артефакты: мягкие переносы (`по­ учиться`), номера страниц.
6. Записать главу как отдельный `.md`-файл.
7. Создать `README.md` и `SUMMARY.md` с оглавлением.

## Скрипт-шаблон

```python
import sys, re
sys.path.insert(0, '/tmp/pdf_extract_venv/lib/python3.11/site-packages')
import pymupdf, pymupdf4llm
from pathlib import Path

PDF = '/path/to/book.pdf'
OUT = Path('/home/USER/obsidian-memory/Knowledge/Technical/Topic/Book Name')
OUT.mkdir(parents=True, exist_ok=True)

doc = pymupdf.open(PDF)
total = len(doc)
toc = doc.get_toc()

# Группировка глав
chapters = []
current = None
for level, title, page in toc:
    title = title.replace('\xa0', ' ').strip()
    if level == 1:
        if current: chapters.append(current)
        current = {'title': title, 'start': page, 'sections': []}
    elif current:
        current['sections'].append({'level': level, 'title': title})
if current: chapters.append(current)

# Диапазоны страниц
for i, ch in enumerate(chapters):
    ch['end'] = chapters[i + 1]['start'] - 1 if i + 1 < len(chapters) else total

def slugify(title, idx):
    s = re.sub(r'[^\w\s-]', '', title.lower())
    s = re.sub(r'[\s]+', '-', s.strip())
    s = re.sub(r'-+', '-', s)[:60].strip('-')
    return f"{idx:02d}-{s}.md"

# Конвертация
for idx, ch in enumerate(chapters, 1):
    start = max(ch['start'] - 1, 0)
    end = min(ch['end'] - 1, total - 1)
    pages = list(range(start, end + 1))

    md = pymupdf4llm.to_markdown(PDF, pages=pages, show_progress=False)
    md = re.sub(r'\n\|?\s*\d+\s*\|?\s*\n', '\n\n', md)

    header = f"# {ch['title']}\n\n"
    if ch['sections']:
        header += "## Содержание\n\n"
        for sec in ch['sections']:
            indent = '  ' * (sec['level'] - 2)
            header += f"{indent}- {sec['title']}\n"
        header += "\n"

    (OUT / slugify(ch['title'], idx)).write_text(header + md, encoding='utf-8')

# README / SUMMARY
readme = [f'# Book Title\n', '## Оглавление\n']
summary = ['# Summary\n']
for idx, ch in enumerate(chapters, 1):
    fn = slugify(ch['title'], idx).replace('.md', '')
    readme.append(f'- [[{fn}|{ch["title"]}]]')
    summary.append(f'- {ch["title"]}: [[{fn}]]')

(OUT / 'README.md').write_text('\n'.join(readme), encoding='utf-8')
(OUT / 'SUMMARY.md').write_text('\n'.join(summary), encoding='utf-8')
```

## Ожидаемые артефакты и как их чистить

| Артефакт | Причина | Лечение |
|---|---|---|
| `по­ учиться`, `инстру­ мент` | Мягкие переносы из PDF | `re.sub(r'(?<=\S)\xad\s*', '', text)` |
| `Установка **29**` | Номер страницы в заголовке | `re.sub(r'\*\*\d+\s+.*?\*\*', '', md)` |
| Разорванные таблицы | PDF layout | проверить вручную; pymupdf4llm справляется лучше с простыми |

## Размер и производительность

- Книга ~600 страниц → ~30 глав → ~1–2 минуты на полную конвертацию.
- Итоговый объём Markdown: 1–3 МБ.

## Проверка перед сдачей

- Открыть одну главу и убедиться, что кодовые блоки и заголовки на месте.
- Проверить `README.md` — все wikilinks должны ссылаться на существующие файлы.
- Убедиться, что `.gitignore` не исключает папку в vault (если vault синхронизируется с Git).
