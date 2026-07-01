#!/usr/bin/env python3
"""
Static audit script for large global CSS files.
Produces candidate lists of duplicate selectors and possibly-unused classes.
Does NOT delete anything — output is for manual review.

Usage:
  python css-audit-script.py <path/to/globals.css> <path/to/src>
"""

import re
import sys
import os
from collections import Counter, defaultdict


def collect_classnames(project_dir):
    classnames = set()
    for root, _dirs, files in os.walk(project_dir):
        for file in files:
            if file.endswith(('.tsx', '.ts', '.jsx', '.js')):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    text = f.read()
                for pattern in (
                    r'className=["\']([^"\']+)["\']',
                    r'className=\{[`"]([^`"]+)[`"]\}',
                    r'className=\{[^}]*["\']([^"\']+)["\'][^}]*\}',
                ):
                    for m in re.findall(pattern, text):
                        classnames.update(m.split())
    return classnames


def find_media_blocks(css):
    """Return list of (start, end) for @media blocks."""
    blocks = []
    for m in re.finditer(r'@media[^{]*\{', css):
        depth = 1
        i = m.end()
        while i < len(css) and depth > 0:
            if css[i] == '{':
                depth += 1
            elif css[i] == '}':
                depth -= 1
            i += 1
        blocks.append((m.start(), i))
    return blocks


def is_inside_media(pos, media_blocks):
    for start, end in media_blocks:
        if start < pos < end:
            return True
    return False


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <globals.css> <src_dir>")
        sys.exit(1)

    css_path = sys.argv[1]
    src_dir = sys.argv[2]

    with open(css_path, 'r', encoding='utf-8') as f:
        css = f.read()

    classnames = collect_classnames(src_dir)
    media_blocks = find_media_blocks(css)

    # Basic metrics
    rules = list(re.finditer(r'([^{}]+)\{', css))
    selectors = []
    for m in rules:
        for sel in m.group(1).split(','):
            sel = sel.strip()
            if sel and not sel.startswith('@') and sel not in ('from', 'to'):
                selectors.append(sel)

    unique_selectors = set(selectors)
    duplicate_candidates = {sel: count for sel, count in Counter(selectors).items() if count > 1}

    # Duplicates outside @media are more likely accidental
    duplicate_outside_media = defaultdict(int)
    for m in rules:
        sel = m.group(1).strip()
        if sel in duplicate_candidates and not is_inside_media(m.start(), media_blocks):
            duplicate_outside_media[sel] += 1

    # Unused class candidates
    css_classes = set(re.findall(r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)', css))
    # Preserve common Bootstrap / JS state classes
    preserve = {
        'css', 'ru', 'navbar-collapse', 'page-item', 'page-link',
        'text-bg-primary', 'text-bg-success', 'is-valid', 'is-invalid',
        'is-expanded', 'is-rotated', 'show-mobile',
    }
    unused_candidates = css_classes - classnames - preserve

    print("=" * 60)
    print("CSS AUDIT REPORT")
    print("=" * 60)
    print(f"File: {css_path}")
    print(f"Size: {len(css)} bytes ({len(css)/1024:.1f} KB)")
    print(f"Lines: {len(css.splitlines())}")
    print(f"CSS blocks: {len(rules)}")
    print(f"Unique selectors: {len(unique_selectors)}")
    print(f"Duplicate selectors (all): {len(duplicate_candidates)}")
    print(f"Duplicate selectors outside @media: {len(duplicate_outside_media)}")
    print(f"!important count: {css.count('!important')}")
    print(f"Unused class candidates: {len(unused_candidates)}")
    print()

    if duplicate_outside_media:
        print("Duplicate selectors outside @media (likely accidental):")
        for sel, count in sorted(duplicate_outside_media.items(), key=lambda x: -x[1]):
            print(f"  {count}x: {sel}")
        print()

    if unused_candidates:
        print("Possibly-unused CSS classes (verify manually before deleting):")
        for cls in sorted(unused_candidates):
            print(f"  .{cls}")
        print()

    print("=" * 60)
    print("Next steps:")
    print("1. Review duplicate selectors; merge only obvious duplicates.")
    print("2. For unused classes, search the project for dynamic usage.")
    print("3. Apply one change at a time and run: npx tsc --noEmit && npm run build")
    print("=" * 60)


if __name__ == '__main__':
    main()
