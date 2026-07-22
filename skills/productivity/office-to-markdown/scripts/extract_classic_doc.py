#!/usr/bin/env python3
"""Extract readable text from a legacy binary .doc (Word 97-2003) file.

This is a fallback when MarkItDown/libreoffice are unavailable. Output is plain
paragraph text; you will usually need to reformat headings/lists/tables by hand.
"""
import argparse
import olefile
import re
import sys


def extract_text(path: str) -> str:
    ole = olefile.OleFileIO(path)
    try:
        if not ole.exists('WordDocument'):
            raise ValueError("WordDocument stream not found — not a classic .doc file?")
        data = ole.openstream('WordDocument').read()
    finally:
        ole.close()

    text = data.decode('utf-16-le', errors='ignore')

    # Control chars
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', ' ', text)
    # Drawing / row-separator artifacts common in old .doc files
    text = re.sub(r'[ЀӿlBGHMxXZ\u0400-\u048f]{2,}', ' ', text)
    # Isolated 1-2 letter latin tokens (OLE field codes, etc.)
    text = re.sub(r'(?<=\s)[a-zA-Z]{1,2}(?=\s)', ' ', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text)
    # Fix space-before-punctuation
    text = re.sub(r' ([\.,;:!?])', r'\1', text)
    return text.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description='Extract text from a classic .doc file')
    parser.add_argument('doc', help='Path to .doc file')
    args = parser.parse_args()
    try:
        print(extract_text(args.doc))
        return 0
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
