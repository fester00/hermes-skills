#!/usr/bin/env python3
"""Пакетная конвертация Office-документов в Markdown через MarkItDown."""

import sys
import os
import glob
from pathlib import Path

SUPPORTED = {".pdf", ".docx", ".pptx", ".xlsx", ".xls", ".csv", ".html", ".htm",
             ".json", ".xml", ".epub", ".zip", ".mp3", ".wav", ".jpg", ".jpeg", ".png"}

def main(directory=".", output_dir=None, dry_run=False):
    directory = Path(directory)
    out = Path(output_dir) if output_dir else directory
    out.mkdir(parents=True, exist_ok=True)

    files = []
    for ext in SUPPORTED:
        files.extend(directory.glob(f"*{ext}"))

    if not files:
        print(f"Нет поддерживаемых файлов в {directory}")
        return

    print(f"Найдено файлов: {len(files)}")
    for f in sorted(files):
        md_path = out / (f.stem + ".md")
        print(f"  {f.name} → {md_path.name}")
        if dry_run:
            continue
        os.system(f"markitdown {shlex.quote(str(f))} > {shlex.quote(str(md_path))}")

    print(f"\nГотово! Markdown файлы в: {out}")

if __name__ == "__main__":
    import argparse, shlex
    parser = argparse.ArgumentParser(description="Batch convert office files to Markdown")
    parser.add_argument("directory", nargs="?", default=".", help="Source directory")
    parser.add_argument("-o", "--output", help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be converted")
    args = parser.parse_args()
    main(args.directory, args.output, args.dry_run)
