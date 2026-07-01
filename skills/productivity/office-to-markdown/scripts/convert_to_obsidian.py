#!/usr/bin/env python3
"""Конвертация файла в Markdown и сохранение как заметки в Obsidian."""

import sys
import os
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

def convert_and_save(source_path, vault, note_name=None, folder=""):
    source = Path(source_path)
    if not source.exists():
        print(f"❌ Файл не найден: {source}", file=sys.stderr)
        sys.exit(1)

    # Конвертация через MarkItDown
    result = subprocess.run(
        ["markitdown", str(source)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ Ошибка конвертации: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    md_content = result.stdout

    # Формируем имя заметки
    name = note_name or source.stem
    if not name.endswith(".md"):
        name += ".md"

    # Frontmatter
    frontmatter = f"""---
source: {source.name}
converted_with: markitdown
date: {datetime.now().isoformat()}
tags: [office-document, converted]
---

"""

    # Используем Obsidian MCP для создания заметки
    # Если MCP недоступен — пишем в папку vault напрямую
    from hermes_tools import mcp_obsidian_create_note
    
    try:
        mcp_obsidian_create_note(
            vault=vault,
            filename=name,
            folder=folder,
            content=frontmatter + md_content
        )
        print(f"✅ Создана заметка: {folder}/{name} в хранилище {vault}")
    except Exception as e:
        # Fallback: пишем напрямую
        vault_path = Path.home() / vault
        target_dir = vault_path / folder
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / name
        target_file.write_text(frontmatter + md_content, encoding="utf-8")
        print(f"✅ Создана заметка: {target_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert file to Obsidian note")
    parser.add_argument("source", help="Source file path")
    parser.add_argument("--vault", required=True, help="Obsidian vault name")
    parser.add_argument("--name", help="Note name (default: source filename)")
    parser.add_argument("--folder", default="office-documents", help="Folder in vault")
    args = parser.parse_args()
    convert_and_save(args.source, args.vault, args.name, args.folder)
