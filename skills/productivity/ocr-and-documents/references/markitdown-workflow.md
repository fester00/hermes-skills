# markitdown workflow — Feed documents to LLM

## Installation

```bash
pip install 'markitdown[all]'
```

Without `[all]` only core formats; `[all]` adds PDF OCR, audio transcription, YouTube.

## Supported formats (summary)

- **Office**: PDF, DOCX, PPTX, XLSX, EPUB
- **Web/data**: HTML, CSV, JSON, XML
- **Media**: images (EXIF + OCR), audio (transcription), YouTube URLs
- **Archive**: ZIP (iterates contents)

## Quick commands

```bash
# Single file
markitdown report.xlsx > report.md
markitdown presentation.pptx > slides.md
markitdown contract.pdf > contract.md
markitdown https://youtube.com/watch?v=xxx > transcript.md

# Batch (directory)
for f in *.pdf *.xlsx *.docx; do
  [ -f "$f" ] && markitdown "$f" > "${f%.*}.md"
done
```

## Workflow with Hermes / LLM

### Option A: Copy-paste (small files)
```bash
markitdown data.xlsx | xclip -selection clipboard
# Paste into chat
```

### Option B: Yandex Disk (large files)
```bash
markitdown data.xlsx > data.md
# Upload data.md to Yandex Disk via `yandex-api` skill
# Share link with Hermes
```

### Option C: Direct pipe (if Hermes can read local files)
```bash
markitdown data.xlsx | cat
# Copy output and paste
```

## Pitfalls

- **GPU warning**: `onnxruntime` may warn about missing GPU. Ignore — CPU works fine for OCR.
- **Audio**: requires ffmpeg installed for transcription.
- **PDF scanned**: markitdown OCR is basic; for complex scanned docs use marker-pdf instead.
- **Math equations**: markitdown does NOT extract LaTeX — use marker-pdf for academic papers.
- **Tables**: Excel → clean Markdown tables; PDF tables may be plain text.

## When NOT to use markitdown

| Need | Use instead |
|------|-------------|
| High-fidelity human-readable conversion | pandoc, Acrobat |
| Scanned PDF with complex layout | marker-pdf |
| Equations / LaTeX extraction | marker-pdf |
| Image extraction from PDF | pymupdf |
| Word → styled HTML for website | mammoth.js, pandoc |

## One-liner for user

> "Drop your files here or tell me the path — I'll convert everything to Markdown so I can analyze it."
