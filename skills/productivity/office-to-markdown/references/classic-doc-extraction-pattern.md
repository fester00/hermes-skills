# Classic `.doc` (Word 97–2003) text-extraction pattern

Use this recipe when MarkItDown refuses a `.doc` with `UnsupportedFormatException` and LibreOffice is not installed or cannot be installed.

## Core idea

Old `.doc` files are OLE compound documents. The readable text lives in the `WordDocument` stream as UTF-16-LE. Extract it, strip control characters and drawing artifacts, then manually reformat the result into clean Markdown.

## Standalone script

The skill provides `scripts/extract_classic_doc.py`:

```bash
python3 ~/.hermes/skills/productivity/office-to-markdown/scripts/extract_classic_doc.py input.doc > output.md
```

## Manual snippet

```python
import olefile, re, sys

path = sys.argv[1]
ole = olefile.OleFileIO(path)
data = ole.openstream('WordDocument').read()
ole.close()

# WordDocument stream text is mostly UTF-16-LE
text = data.decode('utf-16-le', errors='ignore')

# Remove control chars
text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', ' ', text)
# Remove drawing/row-separator artifacts (tune to the file if needed)
text = re.sub(r'[ЀӿlBGHMxXZ\u0400-\u048f]{2,}', ' ', text)
# Remove isolated one/two-letter latin tokens
text = re.sub(r'(?<=\s)[a-zA-Z]{1,2}(?=\s)', ' ', text)
# Collapse whitespace and fix punctuation spacing
text = re.sub(r'\s+', ' ', text)
text = re.sub(r' ([\.,;:!?])', r'\1', text)

print(text)
```

## Cleanup after extraction

The output is **plain paragraphs**, not structured Markdown. Expect to:

1. Split merged table rows into Markdown tables or lists.
2. Add `#`/`##` headings where the original used them.
3. Convert enumerations into real lists.
4. Verify numbers and units against the original — artifact removal can occasionally eat digits near drawing characters.

## When to prefer other routes

- If LibreOffice is available, use it (`libreoffice --headless --convert-to docx`) — it preserves tables and headings far better.
- If the `.doc` is a scan/raster with no text layer, use OCR (`ocr-and-documents` skill).
- For `.docx` (Open XML), use `markitdown` directly.

## Limitations

- This is a **fallback**, not a high-fidelity converter.
- Complex tables, nested lists, images, and precise formatting are lost.
- Always review the extracted text against the original before publishing.
