# Workflow: Bulk CSV → Obsidian Catalog

Convert large structured CSV datasets into a searchable, navigable Obsidian vault catalog.

## Trigger
User says: "полный каталог в Obsidian", "перенеси данные скилла в Obsidian", "зеркало CSV в волт", or wants all rows of a skill's `.csv` data accessible as individual notes.

## Pattern: Summary Tables + Detail Pages
Best for 50+ rows. Creates two layers:
1. **Summary tables** — root-level `.md` with full markdown table (all rows, key columns)
2. **Detail pages** — one `.md` per row in a subfolder, linked from index

## Python Generator Script Template

```python
#!/usr/bin/env python3
import csv
from pathlib import Path

DATA_DIR = Path.home() / ".hermes/skills/.../data"
OUTPUT_DIR = Path.home() / "obsidian-memory/Design/Category Name"

def escape_md(text):
    if text is None:
        return ""
    text = str(text).replace("|", "\\|").replace("\n", " ")
    if len(text) > 200:
        text = text[:197] + "..."
    return text

def csv_to_md_table(filepath, title, key_cols):
    """Generate a root-level summary table."""
    with open(filepath, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    cols = [c for c in key_cols if c in rows[0].keys()]
    lines = [f"# {title}\n", f"**Total entries:** {len(rows)}\n"]
    lines.append("| " + " | ".join(cols) + " |")
    lines.append("|" + "|".join("---" for _ in cols) + "|")
    for row in rows:
        lines.append("| " + " | ".join(escape_md(row.get(c, "")) for c in cols) + " |")
    return "\n".join(lines) + "\n"

def csv_to_detail_pages(filepath, title, subdir_name, id_col='No'):
    """Generate one detail page per row + index note."""
    subdir = OUTPUT_DIR / subdir_name
    subdir.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    
    index = [f"# {title} — Detail Pages\n", f"**Total:** {len(rows)}\n"]
    
    for row in rows:
        item_id = row.get(id_col, '0')
        name = row.get('Product Type') or row.get('Name') or f"Entry {item_id}"
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()[:60]
        filename = f"{item_id} — {safe_name}.md"
        
        detail = [f"# {name}\n", f"**ID:** {item_id}\n"]
        for col, val in row.items():
            if col == id_col:
                continue
            val_str = str(val) if val is not None else ""
            if val_str.strip():
                detail.append(f"## {col}\n{val_str}\n")
        
        (subdir / filename).write_text("\n".join(detail), encoding='utf-8')
        index.append(f"- [[{subdir_name}/{filename[:-3]}|{name}]]")
    
    (OUTPUT_DIR / f"{subdir_name} — Index.md").write_text("\n".join(index) + "\n", encoding='utf-8')
    return len(rows)
```

## Naming Convention
- Summary tables: `01 — Domain Name.md` (sorted first)
- Stack/config files: `02 — Stack — Name.md`
- Detail subdirs: `Domain/` (e.g. `Products/`, `Styles/`)
- Detail index: `Domain — Index.md`
- Vault entry point: `Index.md` with links to all tables and detail indices

## Sizing Guidance
| Rows | Approach |
|------|----------|
| < 50 | Single table note is enough |
| 50–200 | Summary table + detail pages for key domains |
| 200–500 | Summary tables only; detail pages only for most-queried domains |
| 500+ | Summary tables only; use Python `search.py` for lookup, not Obsidian |

## Pitfalls

- **MCP timeout on large operations**: `mcp_obsidian_create_note` with >100 KB content may timeout (120s). Use `write_file` to filesystem directly when creating bulk notes.
- **Filename characters**: `shadcn/ui` contains `/` — sanitize to `shadcn-ui.md`.
- **Unicode in filenames**: Russian filenames work in ext4 but show as byte sequences in `git status`. Always quote paths in shell.
- **CSV cells with newlines**: `escape_md()` must flatten `\n` → space before table insertion.
- **Obsidian graph view**: Wikilinks `[[Subdir/Page Name]]` work for graph navigation; markdown links do not.
