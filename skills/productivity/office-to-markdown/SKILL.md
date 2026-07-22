---
name: office-to-markdown
description: "Конвертация Office-документов (PDF, Excel, Word, PowerPoint, изображения, аудио, ZIP и др.) в Markdown через Microsoft MarkItDown."
version: 1.0.1
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Office, PDF, Excel, Word, Markdown, MarkItDown, Documents, Conversion]
    related_skills: [ocr-and-documents, powerpoint]
---

# Office → Markdown (MarkItDown)

При получении файлов из списка поддерживаемых форматов — используй MarkItDown для конвертации в Markdown перед анализом или передачей в LLM.

> **Важное исключение:** программные/технические учебники (особенно русскоязычные PDF с листингами кода) часто превращаются в MarkItDown в плоский текст без `##`/`###` и без fenced code-блоков. Для таких книг используй **PyMuPDF4LLM** — см. раздел ниже и `references/technical-book-conversion.md`.

## Поддерживаемые форматы

- **PDF** — учебники, отчёты, документация, научные статьи
- **Excel (.xlsx, .xls)** — таблицы, отчёты, данные для анализа
- **Word (.docx)** — документы, статьи, инструкции
- **PowerPoint (.pptx)** — презентации, слайды
- **Изображения (.jpg, .png)** — OCR (распознавание текста) + EXIF
- **Аудио (.mp3, .wav)** — транскрипция речи + EXIF
- **HTML** — веб-страницы
- **CSV, JSON, XML** — текстовые структурированные форматы
- **ZIP** — рекурсивная обработка содержимого
- **YouTube URL** — извлечение транскрипции
- **EPUB** — электронные книги

## Workflow: получил файл → MarkItDown → Markdown

### 1. Один файл

```bash
markitdown документ.pdf > документ.md
markitdown отчет.xlsx -o отчет.md
markitdown презентация.pptx -o презентация.md
```

### 2. Пакетная конвертация (все файлы в папке)

```bash
python3 ~/.hermes/skills/productivity/office-to-markdown/scripts/batch_convert.py папка_с_файлами/
```

Результат: рядом с каждым файлом создаётся `.md` версия.

### 3. Конвертация с сохранением в Obsidian

```bash
python3 ~/.hermes/skills/productivity/office-to-markdown/scripts/convert_to_obsidian.py файл.pdf "Название заметки" --vault МоёХранилище
```

### 4. Пайп (pipe) — для скриптов

```bash
cat файл.pdf | markitdown > вывод.md
echo "https://youtube.com/watch?v=..." | markitdown
```

## Python API

Если нужно встроить в скрипт:

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("документ.pdf")
print(result.text_content)
```

## Workflow: конвертация библиотеки PDF-учебников

Когда пользователь просит «перевести учебники в Markdown» или «закинуть PDF в Obsidian»:

1. **Спроси о режиме**: «Всё сразу, по одному или несколько подряд?»
2. **Если «по одному»** — бери файлы строго по порядку, сообщай результат (размер, заголовки, code-блоки, путь), жди сигнала «давай следующий».
3. **Если batch (5, 10 и т.д.)** — сгруппируй и запускай. Для группы с тяжёлыми PDF (>50 МБ) используй фоновый процесс, иначе `execute_code` оборвётся по таймауту ~300 сек.
4. **Для программных/технических книг используй `pymupdf4llm`**, а не `markitdown`. MarkItDown на таких PDF часто выдаёт плоский текст без Markdown-заголовков и без fenced code-блоков.
5. **Проверяй качество** после конвертации: должны быть `#`/`##`/`###` и, для книг с кодом, блоки `` ``` ``. Если их нет — переконвертируй через `pymupdf4llm`.
6. Клади `.md` в Obsidian в соответствующую языковую папку: `Knowledge/Technical/<Язык>/Books/`.

Подробный рецепт, примеры output'ов и ловушки с большими PDF — в `references/technical-book-conversion.md`.

## Сравнение: MarkItDown vs OCR-and-documents vs PyMuPDF4LLM

| Сценарий | Рекомендация |
|----------|-------------|
| Обычный PDF с текстом | **MarkItDown** — быстрее, Markdown-структура |
| Технические учебники / книги с главами, подзаголовками и листингами | **pymupdf4llm** — сохраняет заголовки и fenced code-блоки лучше |
| Сканированный PDF (растр) | **marker-pdf** (OCR-and-documents) — OCR + чистота |
| Научные статьи с формулами | **marker-pdf** — лучшее распознавание LaTeX |
| Excel-таблицы | **MarkItDown** — сохраняет табличную структуру |
| Word / PowerPoint | **MarkItDown** — родная структура в Markdown |
| Legacy Word 97–2003 `.doc` | **LibreOffice headless** → `.docx` → `markitdown`; or `olefile` fallback — see § Legacy `.doc` below |
| Изображения с текстом | **MarkItDown** — OCR встроен |
| Аудио → текст | **MarkItDown** — транскрипция встроена |
| YouTube видео | **MarkItDown** — извлекает транскрипцию |

### PyMuPDF4LLM для PDF-учебников

MarkItDown на программных книгах часто выдаёт почти плоский текст: нет `##`/`###` и нет блоков кода `` ``` ``. PyMuPDF4LLM сохраняет структуру лучше.

**Установка и один файл:**
```bash
pip install pymupdf4llm
python3 -c "
import pymupdf4llm
md = pymupdf4llm.to_markdown('учебник.pdf')
with open('учебник.md', 'w', encoding='utf-8') as f:
    f.write(md)
"
```

**Если `markitdown`/`pymupdf4llm` не найдены в системном Python:** проверь венв Hermes: `/home/natan/.hermes/hermes-agent/venv/bin/`. Запускай через этот интерпретатор:

```bash
/home/natan/.hermes/hermes-agent/venv/bin/python -c "
import pymupdf4llm
md = pymupdf4llm.to_markdown('учебник.pdf')
with open('учебник.md', 'w', encoding='utf-8') as f:
    f.write(md)
"
```

### Проверка качества конвертации

После конвертации проверь, что контент не превратился в плоский текст:

```bash
python3 -c "
from pathlib import Path
text = Path('учебник.md').read_text(encoding='utf-8')
lines = text.splitlines()
print('h1=', sum(1 for l in lines if l.startswith('# ')))
print('h2=', sum(1 for l in lines if l.startswith('## ')))
print('h3=', sum(1 for l in lines if l.startswith('### ')))
print('code_blocks=', text.count('\`\`\`') // 2)
"
```

Если заголовков мало и нет блоков кода — попробуй `marker-pdf` или сообщи пользователю, что качество ограничено исходником.

**Excel-отчёт по продажам:**
```bash
markitdown продажи_2026.xlsx | grep "Москва" | head -20
```

**PDF-учебник по Rust:**
```bash
markitdown rust_book.pdf > rust_book.md
# Затем передать мне содержимое rust_book.md для анализа
```

**Презентация → markdown для summary:**
```bash
markitdown презентация_инвесторов.pptx > pitch.md
```

**Пакетно все PDF в папке:**
```bash
for f in *.pdf; do markitdown "$f" > "${f%.pdf}.md"; done
```

## Legacy `.doc` (Word 97–2003) fallback

MarkItDown and most modern converters only support `.docx`/`.xlsx`/`.pptx` (Open XML). Old binary `.doc` files (Word 97–2003) are not supported by MarkItDown and often are not present in `.docx` form.

1. **Best-effort conversion:** if LibreOffice is available, use it headlessly:
   ```bash
   libreoffice --headless --convert-to docx старый_файл.doc
   markitdown старый_файл.docx > старый_файл.md
   ```
2. **Fallback without LibreOffice:** extract readable text directly from the OLE `WordDocument` stream with the bundled script:
   ```bash
   python3 ~/.hermes/skills/productivity/office-to-markdown/scripts/extract_classic_doc.py старый_файл.doc > старый_файл.md
   ```
   The script decodes UTF-16-LE text and removes control/drawing artifacts. Output is plain paragraph text, not perfect Markdown, so reformat headings, lists and tables by hand before use.
3. **Manual recipe:** see `references/classic-doc-extraction-pattern.md` for the cleanup heuristics and a copy-paste Python snippet.

## Зависимости

```bash
pip install 'markitdown[all]'
```

Уже установлено на сервере. При необходимости обновить:
```bash
pip install --upgrade 'markitdown[all]'
```

## Примечания

- MarkItDown оптимизирован для **LLM-friendly** Markdown — структура (заголовки, списки, таблицы, код) сохраняется
- Вывод — Markdown, не визуальный HTML. Для человеческого чтения PDF лучше открывать оригинал
- При работе с изображениями требуется ONNX runtime — может выдавать warnings про GPU, но работает на CPU
- Для сканированных документов (растр без OCR-слоя) лучше использовать `ocr-and-documents` skill с marker-pdf
