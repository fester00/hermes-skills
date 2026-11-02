---
name: docx-template-filling
description: Use when filling a .docx template with data from scans.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [DOCX, Word, Contracts, Templates, python-docx, Fonts]
    related_skills: [ocr-and-documents, powerpoint]
---

# Filling a Word (.docx) template with real data

Contract forms, acts, invoices, requisites blocks. The deliverable is a valid `.docx` that opens in Word, carries the source data in the right fields, keeps the template's formatting, and is honest about which values are invented.

## When to Use

- A `.docx` contract/form must be filled from a scan, passport, or a data set the user supplied.
- An already-filled `.docx` must be re-issued for another party (substitution, not blank fill).
- The rendered font of a Word file must be changed or preserved while its content is edited.
- Skip only when the task is pure text reading — that is `ocr-and-documents` / `office-to-markdown`.

## Step 0 — get the data out of the scan

`pypdf`/`pdfplumber` returning `chars=0` on every page means a pure image scan: no text layer, and `pdftotext`/`tesseract`/LibreOffice are often absent on a minimal host. Do not ask the user to retype the document. Render pages and read them yourself:

```bash
pip install pymupdf   # no external binaries needed
python3 -c "import pymupdf; d=pymupdf.open('p.pdf'); [p.get_pixmap(dpi=200).save(f'page{i+1:02d}.png') for i,p in enumerate(d)]"
```

Then load each PNG with `vision_analyze` (page spread 2 = ФИО/дата рождения/серия-номер/кем выдан/код подразделения, page 3 = штамп регистрации, later pages often blank). 200 dpi is enough for the small print; transcribe MRZ as a cross-check on the number and birth date.

## Step 1 — read the template's ACTUAL structure

Unzip and look before writing anything:

```bash
unzip -o -q template.docx -d x && ls x/word
```

- `word/document.xml` — the body, tables, and content controls
- `word/styles.xml` — `docDefaults` (what unstyled text renders as)
- `word/theme/theme1.xml` — theme fonts (`majorFont` / `minorFont` `a:latin`)
- `word/header*.xml`, `word/footer*.xml` — often carry the contract number

Then dump a flattened, run-level view of every paragraph. **`paragraph.text` in python-docx omits text inside content controls (`w:sdt`)** — a field that looks empty there is frequently filled. A template that reads "Индивидуальный предприниматель , ОГРНИП…" usually has the name sitting in an `sdtContent` run; before calling any field blank, iterate `w:t` under the paragraph:

```python
tx = ''.join(t.text or '' for t in p.iter(W + 't'))   # W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
```

Also decide which job you have: a **blank fill** or a **re-issue for a different party**. A template already carrying another person's values is a substitution — every one of their identifiers must leave the file.

## Step 2 — confirm each old value sits inside ONE `w:t`

Word splits text across runs arbitrarily (`'Д'` + `'ОГОВОР № '`, `'16.07.2024'` vs `'от 16.07.2024'`). A per-`w:t` replace is the only formatting-safe edit, and it silently misses a token that spans a run boundary. Scan first:

```python
for t in p.iter(W + 't'):
    if token in (t.text or ''): print('contiguous:', token)
```

If a token spans runs, join the paragraph text, redistribute characters into the first run and blank the rest — never rebuild the paragraph as one run (that flattens bold, underline, tabs and page layout).

Set `xml:space="preserve"` on every `w:t` you write (including values with leading/trailing spaces).

Scope the rules by paragraph where a token is ambiguous: an index fragment like `'143'`, `'ул. '`, `', д. 30, кв. 186'` must only be replaced in the paragraphs that hold that address, never document-wide.

## Step 3 — replace every occurrence, then prove none are left

One party's data lives in more than the visible preamble: requisites table, every signature block, act/appendix headers, and the short `/И.О. Фамилия/` signature form. Build the map, apply it, then re-scan the saved file and assert **zero** leftovers of every old identifier (name parts, ОГРНИП, ИНН, passport series/number, address streets, phone, e-mail, account).

Fill blank date placeholders too (`«___» ___________ 2026г.`) and keep the contract number/date already present in the template rather than inventing a new one.

## Step 4 — fonts: three layers decide what renders

Effective font = run `rPr/rFonts` → style `rPr` → `docDefaults` → theme. Runs with no `rPr` inherit the theme, so an audit that only looks at explicit runs will lie.

To force one font everywhere:

1. every `w:r`: create `rPr` if missing, set `rFonts` `ascii`/`hAnsi`/`cs`/`eastAsia`, delete the `asciiTheme`/`hAnsiTheme`/`cstheme`/`eastAsiaTheme` attributes (a theme attribute beats an explicit name);
2. every `w:rPr`, including `pPr/rPr` paragraph marks;
3. `<w:rPrDefault>` in `styles.xml` → one `rFonts` element;
4. `<a:latin typeface="…">` both occurrences in `theme1.xml`.

Audit after: count runs whose `ascii` is not the target (must be 0), and count the old font name in `document.xml` + `styles.xml` (must be 0).

**Ambiguous font instructions.** When a template carries a display font on headings only, that split IS the design; "font X must be" can mean *everything in X* or *keep X where it was*. Decide by looking at where the font already appears, then deliver both variants in one pass — one fully in X, one preserving the template's mix — with distinct file names and a line saying which is which. Two files from one script run cost less than a wrong guess or a blocking question. Warn when the font has no Cyrillic coverage: Word substitutes per glyph, headings land, body can drift.

## Step 5 — invented values must look valid or be clearly fake

Only what the source document states is real; ОГРНИП, ИНН, bank account, phone, e-mail, postal index, service start date are usually absent and must be invented. Make them internally consistent:

- compute real check digits — see `references/russian-requisites-checksums.md` (ОГРНИП, 12-digit ИНН, 20-digit account control key);
- make the tax-office code agree with the address (a Moscow street with a Подмосковье ИНН is an obvious tell);
- use reserved domains for invented e-mail (`example.ru`), obviously patterned phone numbers;
- keep bank name/БИК/к/с of the real counterparty when the template provides them and change only the subscriber's account.

List every invented value in the reply. The user must be able to tell at a glance what to replace before signing.

## Step 6 — verify, then deliver

- Re-open the output with `python-docx` (proves the package is intact) and parse every `*.xml` / `*.rels` with `lxml` (proves the zip edits did not corrupt parts).
- Grep the saved file for old tokens → must be empty; count each new value against expectation (a name appearing 7 times, a signature 4 times).
- Render to PDF/screenshot only if Word or LibreOffice exists; when it does not, **say plainly that layout was not visually verified** — do not imply it was.
- Copy finished files out of the scratch dir (it is pruned) to a durable path, keep file names space-free, and deliver with `MEDIA:/absolute/path`.
- Reply with a short passport: real data and its source, invented data as a list, what was replaced and where, what was verified and with which check.

## Pitfalls

- `python3 -c "import docx"` failing right after a successful `pip3 install` means two interpreters: `pip3 --version` prints the interpreter that received the package — run that one, or make a dedicated venv. Never re-install in a loop.
- Never hand-edit `document.xml` with stream editors: attributes and namespaces break Word silently. Use python-docx + lxml, or a string map applied through the XML tree, and the `patch` tool for source-level edits.
- `w:sdtContent` runs are edited like any other run; deleting the `sdt` wrapper loses the template's field metadata but not its text — prefer editing the content.
- Saving the zip by rewriting only some parts (styles/theme) requires copying every other entry unchanged, or relationships and media vanish.
