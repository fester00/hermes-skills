# Importing mdBook sources into Obsidian

Use this when the user wants a freely available technical book or tutorial in the Obsidian vault for later study.

## Principle

Prefer the **source Markdown** from the book's GitHub repository over PDF or scraped HTML. Most mdBook-based books (e.g. `rust-lang/book`) store one `.md` file per chapter under `src/`. Cloning the source avoids OCR errors, keeps code listings intact, and preserves the table of contents in `src/SUMMARY.md`.

## Workflow

1. Clone the book repository to a temp directory.
2. Inspect `src/SUMMARY.md` to confirm structure.
3. Convert each `src/*.md` file to Obsidian-ready Markdown:
   - Inline `{{#include path[:anchor]}}` directives as literal code blocks.
   - Remove Markdown image lines (`![...](...)`).
   - Convert internal links to Obsidian wikilinks.
   - Strip mdBook HTML helpers (`<Listing ...>`, `<a id="...">`, etc.).
4. Copy converted files into the relevant technology folder in the vault.
5. Ensure the destination folder contains `SUMMARY.md` as the navigation entry point.

## Reference script

```python
#!/usr/bin/env python3
"""Convert mdBook sources into clean Obsidian-ready Markdown."""
import re
import shutil
from pathlib import Path

# Configure before run
SRC = Path('/tmp/rust-book-src/src')      # cloned book src/
DST = Path('~/obsidian-memory/Knowledge/Technical/Rust/The Rust Programming Language').expanduser()

if DST.exists():
    shutil.rmtree(DST)
DST.mkdir(parents=True)

include_re = re.compile(r'\{\{#include\s+([^\s}]+)(?:\s*:\s*([^}]+))?\}\}')
link_re = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
image_re = re.compile(r'^!\[([^\]]*)\]\(([^)]+)\)\s*$', re.MULTILINE)
listing_open = re.compile(r'<Listing\s+[^>]+>')
listing_close = re.compile(r'</Listing>')
a_id = re.compile(r'<a\s+id="[^"]+"></a>')


def resolve_include(rel_path: str, anchor: str | None) -> str:
    full = SRC / rel_path
    if not full.exists():
        return f'```rust\n[Missing include: {rel_path}]\n```'
    txt = full.read_text(encoding='utf-8')
    ext = full.suffix.lstrip('.')
    if anchor:
        start = f'ANCHOR: {anchor}'
        end = f'ANCHOR_END: {anchor}'
        s, e = txt.find(start), txt.find(end)
        if s != -1 and e != -1:
            txt = txt[s + len(start):e]
        txt = re.sub(r'\n?\s*//\s*(ANCHOR|ANCHOR_END):?\s*.*', '', txt)
    txt = re.sub(r'^\s*//\s*(ANCHOR|ANCHOR_END):.*$', '', txt, flags=re.MULTILINE)
    return f'```{ext}\n{txt.rstrip()}\n```'


def fix_link(m: re.Match) -> str:
    text, href = m.group(1), m.group(2)
    if href.startswith(('http://', 'https://', 'mailto:')):
        return m.group(0)
    base = href.split('#')[0]
    anchor = href.split('#', 1)[1] if '#' in href else ''
    target = Path(base).stem
    if anchor:
        return f'[[{target}#{anchor}|{text}]]'
    return f'[[{target}|{text}]]'


def convert_file(md_path: Path) -> str:
    txt = md_path.read_text(encoding='utf-8')
    txt = image_re.sub('', txt)
    txt = listing_open.sub('', txt)
    txt = listing_close.sub('', txt)
    txt = a_id.sub('', txt)
    txt = re.sub(r'<!--\s*Old headings\.[^>]+-->', '', txt)
    txt = re.sub(r'<!--\s*ignore\s*-->', '', txt)
    txt = include_re.sub(lambda m: resolve_include(m.group(1), m.group(2)), txt)
    txt = link_re.sub(fix_link, txt)
    txt = re.sub(r'\n{3,}', '\n\n', txt)
    return txt


for f in sorted(SRC.glob('*.md')):
    (DST / f.name).write_text(convert_file(f), encoding='utf-8')

print(f'Converted {len(list(SRC.glob("*.md")))} files to {DST}')
```

## Pitfalls

- mdBook uses `{{#include}}` for code listings; Obsidian will show the literal directive unless you inline the referenced file contents.
- `SUMMARY.md` link syntax `[title](file.md)` must be converted to `[[file|title]]` so Obsidian navigation works.
- Image-only lines break the "no pictures" request; remove them with a line-level regex rather than a substring replace, to avoid stripping legitimate table cells that happen to contain `!`.
- Vault MCP tools may time out on bulk writes; use `write_file` or direct filesystem writes for the final copy.
- Always check the destination technology folder exists first (`Knowledge/Technical/<Topic>/` in this vault).
