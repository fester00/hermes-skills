#!/usr/bin/env python3
"""
Extract `application` (and optionally `description`) blocks for a single v1 category
from pentajunior/src/data/products.tsx, convert JSX to plain-ish HTML, split them
into v2 template fields, and print JSON for easy review before writing to v2.

Usage:
  python extract_v1_application.py --category-id 9 --output hand-care.json

The script is intentionally standalone and static: it does not read the v2 DB.
Review its output, then import the JSON into your migration script.
"""
import argparse
import json
import re
import sys
from pathlib import Path

V1_PRODUCTS_FILE = Path('/home/natan/workspace/pentajunior/src/data/products.tsx')


def extract_category_blocks(text: str, category_id: int) -> list[dict]:
    """Find product objects whose `categoryId` matches."""
    results = []
    # Find every object literal starting with `id:` and ending at the next top-level `},`
    for m in re.finditer(r'\{id:\s*([^,]+?),\s*categoryId:\s*(\d+)', text):
        raw_id = m.group(1).strip()
        cat = int(m.group(2))
        if cat != category_id:
            continue
        # boundaries: matching braces from the opening brace
        start = m.start()
        brace = 0
        i = start
        while i < len(text):
            if text[i] == '{':
                brace += 1
            elif text[i] == '}':
                brace -= 1
                if brace == 0:
                    break
            i += 1
        block = text[start:i + 1]
        # normalize id (remove quotes)
        pid = raw_id.strip("'\"")
        results.append({'id': pid, 'block': block})
    return results


def get_jsx_value(block: str, key: str) -> str | None:
    """Return the raw JSX/TSX value for `key: ...` (supports template literals)."""
    pattern = re.compile(rf'{re.escape(key)}:\s*((?:`[\s\S]*?`|\(\s*(?:<[\s\S]*?>|[\s\S]*?)\s*\)|"[^"]*"|\'[^\']*\'|\[[\s\S]*?\])),', re.VERBOSE)
    m = pattern.search(block)
    if not m:
        return None
    val = m.group(1).strip()
    if val.startswith('`') and val.endswith('`'):
        val = val[1:-1]
    elif val.startswith('(') and val.endswith(')'):
        val = val[1:-1].strip()
    elif (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        val = val[1:-1]
    return val


def jsx_to_html(value: str) -> str:
    """Minimal JSX → HTML for the pentajunior data file."""
    # Remove JSX comments and React fragments
    value = re.sub(r'\{/[\s\S]*?/\}', '', value)
    value = re.sub(r'<>|</>', '', value)
    # className -> class
    value = re.sub(r'className=\{?"([^"]+)"\}?', r'class="\1"', value)
    # style={{...}} -> remove for migration
    value = re.sub(r'style=\{\{[^}]+\}\}', '', value)
    # Replace self-closing JSX with nothing
    value = re.sub(r'<[^/][^>]*?/>', '', value)
    # Collapse multiple spaces/newlines
    value = re.sub(r'\n\s*\n+', '\n\n', value)
    return value.strip()


def html_to_items(html: str) -> list[str]:
    """Extract list items from a `<ul>`/`<ol>` block."""
    items = re.findall(r'<li[^>]*>(.*?)</li>', html, re.DOTALL)
    # Strip inline tags
    cleaned = []
    for item in items:
        item = re.sub(r'<[^>]+>', '', item)
        item = item.replace('  ', ' ').strip()
        if item:
            cleaned.append(item)
    return cleaned


def split_areas_and_instructions(items: list[str]) -> tuple[list[str], list[str]]:
    """Heuristic: action verbs indicate instructions, everything else is areas of use."""
    instruction_markers = [
        'нанесите', 'разотрите', 'смойте', 'удалите', 'распределите',
        'дайте', 'обновляйте', 'впитаться', 'вымойте', 'просушите',
        'наносите', 'втирайте', 'очистите', 'подождите', 'смешайте',
    ]
    applications = []
    recommendations = []
    for item in items:
        lowered = item.lower()
        if any(marker in lowered for marker in instruction_markers):
            recommendations.append(item)
        else:
            applications.append(item)
    return applications, recommendations


def split_by_headings(md: str) -> dict[str, list[str]]:
    """Split a Markdown-ish block by bold headings into v2 template fields."""
    out = {
        'applications': [],
        'application_industrial': [],
        'application_domestic': [],
        'method': [],
        'recommendations': [],
        'important_note': [],
        'surface_prep': [],
        'mixing_steps': [],
        'degassing': [],
        'safety': [],
        'other': [],
    }
    # Split on **Heading** or **Heading:**
    parts = re.split(r'\n\n\*\*([^*]+)\*\*[:：]?\s*', md)
    if not re.match(r'\n\n\*\*([^*]+)\*\*', md):
        # first chunk has no heading -> treat as intro/other
        current = 'other'
        first = parts.pop(0)
        if first:
            out[current].extend(html_to_items(first) or [first])
    else:
        current = 'other'

    for i, part in enumerate(parts):
        if i % 2 == 0:
            heading = part.strip().lower()
            if 'промышлен' in heading:
                current = 'application_industrial'
            elif 'бытов' in heading or 'домашн' in heading:
                current = 'application_domestic'
            elif 'область применения' in heading or 'применение' in heading and 'способ' not in heading:
                current = 'applications'
            elif 'способ' in heading or 'инструкция' in heading:
                current = 'recommendations'
            elif 'рекомендация' in heading:
                current = 'method'
            elif 'важно' in heading or 'внимание' in heading or 'предупреждение' in heading:
                current = 'important_note'
            elif 'подготовка' in heading or 'поверхност' in heading:
                current = 'surface_prep'
            elif 'приготовление' in heading or 'смеш' in heading:
                current = 'mixing_steps'
            elif 'дегаз' in heading or 'залив' in heading:
                current = 'degassing'
            elif 'безопас' in heading or 'меры' in heading:
                current = 'safety'
            else:
                current = 'other'
        else:
            items = html_to_items(part)
            out[current].extend(items)
    return out


def main():
    parser = argparse.ArgumentParser(description='Extract v1 product application blocks.')
    parser.add_argument('--category-id', type=int, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--include-description', action='store_true')
    args = parser.parse_args()

    text = V1_PRODUCTS_FILE.read_text(encoding='utf-8')
    blocks = extract_category_blocks(text, args.category_id)

    products = []
    for b in blocks:
        application = get_jsx_value(b['block'], 'application')
        record = {'id': b['id'], 'application_raw': application}
        if application:
            html = jsx_to_html(application)
            record['application_html'] = html
            split = split_by_headings(html)
            record['fields'] = {k: v for k, v in split.items() if v}
            # If only one unlabeled list, also provide the verb split
            if 'applications' not in record['fields'] and 'recommendations' not in record['fields']:
                items = html_to_items(html)
                apps, recs = split_areas_and_instructions(items)
                if apps:
                    record['fields']['applications'] = apps
                if recs:
                    record['fields']['recommendations'] = recs
        if args.include_description:
            desc = get_jsx_value(b['block'], 'description')
            record['description_raw'] = desc
            if desc:
                record['description_html'] = jsx_to_html(desc)
        products.append(record)

    result = {'category_id': args.category_id, 'products': products}
    json_text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(json_text, encoding='utf-8')
        print(f'Wrote {args.output} ({len(products)} products)')
    else:
        print(json_text)


if __name__ == '__main__':
    main()
