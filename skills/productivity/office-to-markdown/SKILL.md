---
name: office-to-markdown
description: "Конвертация Office-документов (PDF, Excel, Word, PowerPoint, изображения, аудио, ZIP и др.) в Markdown через Microsoft MarkItDown."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Office, PDF, Excel, Word, Markdown, MarkItDown, Documents, Conversion]
    related_skills: [ocr-and-documents, powerpoint]
---

# Office → Markdown (MarkItDown)

При получении файлов из списка поддерживаемых форматов — всегда используй MarkItDown для конвертации в Markdown перед анализом или передачей в LLM.

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

## Сравнение: MarkItDown vs OCR-and-documents

| Сценарий | Рекомендация |
|----------|-------------|
| Обычный PDF с текстом | **MarkItDown** — быстрее, Markdown-структура |
| Сканированный PDF (растр) | **marker-pdf** (OCR-and-documents) — OCR + чистота |
| Научные статьи с формулами | **marker-pdf** — лучшее распознавание LaTeX |
| Excel-таблицы | **MarkItDown** — сохраняет табличную структуру |
| Word / PowerPoint | **MarkItDown** — родная структура в Markdown |
| Изображения с текстом | **MarkItDown** — OCR встроен |
| Аудио → текст | **MarkItDown** — транскрипция встроена |
| YouTube видео | **MarkItDown** — извлекает транскрипцию |

## Примеры использования

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
