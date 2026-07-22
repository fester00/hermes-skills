# Конвертация технических PDF-учебников в Markdown

Сводный рецепт и типичные ловушки, отработанные на реальных сессиях с Python- и JavaScript-учебниками.

## Когда использовать что

| Тип PDF | Рекомендуемый инструмент | Почему |
|---|---|---|
| Простые текстовые документы / статьи | `markitdown` | Быстро, хорошая табличная структура |
| Программные учебники с главами, подзаголовками, листингами | `pymupdf4llm` | Сохраняет `#`/`##`/`###` и fenced code-блоки |
| Сканированные книги / формулы / сложные макеты | `marker-pdf` | OCR, LaTeX, чистая вёрстка |

## Workflow: по одному или batch

1. **Спроси пользователя о режиме**: «Всё сразу, по одному или несколько подряд?»
2. **Если по одному** — бери файлы строго по порядку, сообщай результат (размер, заголовки, code-блоки, путь), жди сигнала «давай следующий».
3. **Если batch** — группируй по 5 файлов. Сообщай, какие 5 книг взял, и жди окончания конвертации.
4. **Большие PDF (60+ МБ)** запускай в фоне через `terminal(background=true, notify_on_complete=true, timeout=3600)`, потому что `execute_code` обрывается ~300 сек. Без `notify_on_complete` легко потерять результат.
5. **Сразу после завершения** проверяй качество и показывай сводную таблицу: `lines`, `h1/h2/h3`, `code_blocks`. Если `code_blocks=0` при программной книге — предупреди пользователя, что код не выделен в блоки.

На хосте `natan` инструменты находятся в венве Hermes:

```bash
/home/natan/.hermes/hermes-agent/venv/bin/python -c "
import pymupdf4llm
md = pymupdf4llm.to_markdown('/path/to/book.pdf', show_progress=False)
with open('/path/to/book.md', 'w', encoding='utf-8') as f:
    f.write(md)
"
```

Почему важен именно венв: системный Python не содержит `markitdown`/`pymupdf4llm`.

## Большие файлы (60+ МБ)

`execute_code` падает по таймауту ~300 сек. Для тяжёлых книг используй фон:

```bash
/home/natan/.hermes/hermes-agent/venv/bin/python -c "
import pymupdf4llm
pdf = '/mnt/data/natan-storage/workspace/books/python/Mark_Lutts_tom_2_Python.pdf'
md = '/home/natan/obsidian-memory/Knowledge/Technical/Python/Books/Mark_Lutts_tom_2_Python.md'
text = pymupdf4llm.to_markdown(pdf, show_progress=False)
with open(md, 'w', encoding='utf-8') as f:
    f.write(text)
print('DONE', len(text))
"
```

После завершения фонового процесса проверяй качество.

### Уведомления о завершении

Запускай с `notify_on_complete=true`. Если по какой-то причине уведомление не пришло, **активно проверяй процесс через `process poll`** — не жди пассивно. Как только процесс завершён, сразу проверяй качество и сообщай пользователю результат.

Если пользователь спрашивает «готово?» — сначала проверь `process poll`, потом отвечай.

## Проверка качества

```python
from pathlib import Path
md = Path('book.md')
text = md.read_text(encoding='utf-8')
lines = text.splitlines()
print('h1', sum(1 for l in lines if l.startswith('# ')))
print('h2', sum(1 for l in lines if l.startswith('## ')))
print('h3', sum(1 for l in lines if l.startswith('### ')))
print('code_blocks', text.count('```') // 2)
```

Если заголовков и блоков кода почти нет — переконвертируй через `pymupdf4llm` или `marker-pdf`.

## Где сохранять в Obsidian

| Тема | Папка |
|---|---|
| Python | `Knowledge/Technical/Python/Books/` |
| JavaScript | `Knowledge/Technical/JavaScript/Books/` |
| Rust | `Knowledge/Technical/Rust/Books/` |
| Общее / не по языку | `Knowledge/Technical/Books/` или спроси пользователя |

## Примеры результатов

```
head_first_python_3_edition_.md: lines=18,678 h1=1 h2=2 h3=10 code_blocks=79
Mark_Lutts_tom_2_Python.md: lines=17,253 h1=11 h2=1 h3=31 code_blocks=254
Python_cheatsheet.md: lines=7,186 h1=33 h2=11 h3=70 code_blocks=875
```

Если `code_blocks=0` при программной книге — качество ограничено исходником, но текст всё равно читаем.

## Примечания

- `pymupdf4llm` выдаёт warnings про GPU (`onnxruntime device_discovery`) — это нормально, работает на CPU.
- MarkItDown остаётся полезным для Excel, Word, PowerPoint, HTML, аудио, ZIP, YouTube.
