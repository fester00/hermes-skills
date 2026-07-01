#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Шаблон миграционного скрипта для согласования product-данных:
- удаляет из template_data дублирующие характеристики, уже покрытые spec-таблицей;
- создаёт персональные spec-таблицы для товаров без таблицы, но с секцией «Характеристики».

Копируется в проект и адаптируется под конкретный набор товаров.
"""

import json
import re
import shutil
import sqlite3
from datetime import datetime
from math import gcd
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / 'pentajunior.db'
BACKUP_PATH = DB_PATH.parent / f'pentajunior.db.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
LEGACY_PRODUCTS_JSON = Path('/tmp/legacy_products.json')
LEGACY_SPEC_JSON = Path('/tmp/legacy_spec_tables.json')


def react_to_markdown(node, depth=0):
    """Преобразует JSON-сериализованное React-дерево в markdown-подобный текст."""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return ''.join(react_to_markdown(c, depth) for c in node)
    if not isinstance(node, dict):
        return ''
    t = node.get('type')
    p = node.get('props', {})
    ch = p.get('children')
    if t in (None, 'React.Fragment'):
        return react_to_markdown(ch, depth)
    inner = react_to_markdown(ch, depth + 1)
    if t == 'p':
        return f"\n{inner}\n"
    if t in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
        return f"\n{'#' * int(t[1])} {inner}\n"
    if t == 'strong':
        return f"**{inner}**"
    if t == 'em':
        return f"*{inner}*"
    if t == 'ul':
        items = [item for item in react_to_markdown(ch, depth).strip().split('\n') if item]
        return '\n' + '\n'.join(f"- {item}" for item in items) + '\n'
    if t == 'ol':
        items = [item for item in react_to_markdown(ch, depth).strip().split('\n') if item]
        return '\n' + '\n'.join(f"{i + 1}. {item}" for i, item in enumerate(items)) + '\n'
    if t == 'li':
        return f"{inner}\n"
    if t == 'br':
        return '\n'
    if t == 'a':
        return f"[{inner}]({p.get('href', '')})"
    if t == 'span':
        return inner
    if t == 'div':
        return f"\n{inner}\n"
    return inner


def extract_sections(md):
    parts = re.split(r'\n###\s+', md)
    sections = {'_intro': parts[0].strip()} if parts else {}
    for part in parts[1:]:
        lines = part.split('\n', 1)
        title = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ''
        sections[title] = body
    return sections


def parse_bullets(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    items = []
    for line in lines:
        if line.startswith('- ') or line.startswith('* '):
            items.append(line[2:].strip())
        elif re.match(r'^\d+\.\s+', line):
            items.append(re.sub(r'^\d+\.\s+', '', line).strip())
        else:
            items.append(line)
    return items


def normalize_for_match(s):
    return (
        str(s).lower()
        .replace('\u00a0', '')
        .replace(' ', '')
        .replace('·', '')
        .replace('–', '-')
        .replace('—', '-')
    )


def normalize_mark(s):
    return (
        str(s).lower()
        .replace('\u00a0', '')
        .replace(' ', '')
        .replace('-', '')
        .replace('®', '')
        .replace('™', '')
        .replace('©', '')
        .translate(str.maketrans('abcdefgkmoprtvxy', 'абсдефгкмопртвху'))
    )


def simplify_ratio(s):
    if ':' not in s:
        return s
    parts = s.split(':')
    if len(parts) != 2:
        return s
    try:
        a = int(parts[0])
        b = int(parts[1])
        g = gcd(a, b)
        return f"{a // g}:{b // g}"
    except ValueError:
        return s


SPEC_ROW_NAME_HINTS = {
    'color': ['цвет'],
    'ratio': ['соотношение', 'весовое'],
    'viscosity': ['вязкость'],
    'pot_life': ['время жизни'],
    'cure_time': ['время отверждения', 'выдержки в форме', 'время'],
    'hardness': ['твердость'],
    'elongation': ['удлинение', 'эластичность'],
    'shrinkage': ['усадка'],
    'certificates': ['fda', 'bfr', 'сертификат'],
    'temp_range': ['температура', 'диапазон'],
    'method': ['способ', 'нанесение', 'применение'],
    'tu': ['ту'],
    'shelf_life': ['срок', 'годности'],
    'composition': ['состав'],
    'surfaces': ['поверхности'],
}


def find_matching_spec_row(table, product_mark, key, value):
    if not table or not product_mark:
        return None
    norm_mark = normalize_mark(product_mark)
    target_col = None

    # Prefer matching by numeric/ alphanumeric suffix, because column names like
    # '9110', '6В', 'TRANS' rarely contain the full product id.
    pid_digits = re.findall(r'\d+', product_mark)
    for col in table['columns'][1:]:
        if pid_digits and re.findall(r'\d+', col) == pid_digits:
            target_col = col
            break
    if not target_col:
        for col in table['columns'][1:]:
            col_suffix = col.split('-')[-1]
            if col_suffix.lower() == product_mark.lower() or col.lower() == product_mark.lower():
                target_col = col
                break
            if normalize_mark(col_suffix) == norm_mark or normalize_mark(col) == norm_mark:
                target_col = col
                break
    if not target_col:
        return None

    val_norm = normalize_for_match(value)
    for row in table['rows']:
        row_name = row['name'].lower()
        hints = SPEC_ROW_NAME_HINTS.get(key, [])
        if not any(h in row_name for h in hints):
            continue
        table_val = normalize_for_match(row['values'].get(target_col, ''))
        if key == 'certificates':
            return row['name']
        if not table_val or not val_norm:
            continue
        if key == 'ratio':
            if simplify_ratio(val_norm) == simplify_ratio(table_val):
                return row['name']
        if key in ('hardness', 'elongation', 'shrinkage', 'viscosity', 'pot_life', 'cure_time'):
            v_digits = re.sub(r'[^\d,\-.:]', '', val_norm)
            t_digits = re.sub(r'[^\d,\-.:]', '', table_val)
            if v_digits and t_digits and (v_digits in t_digits or t_digits in v_digits):
                return row['name']
        if val_norm in table_val or table_val in val_norm:
            return row['name']
    return None


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(DB_PATH)

    legacy = json.loads(LEGACY_PRODUCTS_JSON.read_text(encoding='utf-8'))
    legacy_map = {p['id']: p for p in legacy}
    legacy_spec = json.loads(LEGACY_SPEC_JSON.read_text(encoding='utf-8'))

    shutil.copy(DB_PATH, BACKUP_PATH)
    print(f'[backup] {BACKUP_PATH}')

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute('SELECT id, template_type, spec_table_id, template_data, features FROM products').fetchall()

    new_spec_tables = {}
    updates = []
    log_lines = []

    # Helper: remove duplicate features too, because ProductCard renders product.features
    def dedupe_features(pid, features, spec_id):
        if not spec_id or not features:
            return features
        spec = legacy_spec.get(spec_id)
        if not spec:
            return features
        product_mark = pid.split('-')[-1]
        target_col = None
        pid_digits = re.findall(r'\d+', pid)
        for col in spec['columns'][1:]:
            if pid_digits and re.findall(r'\d+', col) == pid_digits:
                target_col = col
                break
        if not target_col and len(spec['columns']) > 1:
            target_col = spec['columns'][1]
        spec_values = [
            normalize_for_match(row['values'].get(target_col, ''))
            for row in spec['rows']
        ]
        kept = []
        for f in features:
            f_norm = normalize_for_match(f)
            f_digits = set(re.findall(r'[0-9]+[,.]?[0-9]*', f_norm))
            dup = False
            for v_norm in spec_values:
                if v_norm and (v_norm in f_norm or f_norm in v_norm):
                    dup = True
                    break
                v_digits = set(re.findall(r'[0-9]+[,.]?[0-9]*', v_norm))
                if f_digits and f_digits == v_digits:
                    units = set(re.findall(r'[а-яa-z]+', f_norm)) & set(re.findall(r'[а-яa-z]+', v_norm))
                    if units:
                        dup = True
                        break
            if not dup:
                kept.append(f)
            else:
                log_lines.append(f"{pid}: removed feature '{f}' (duplicate of spec table)\n")
        return kept

    for r in rows:
        pid = r['id']
        spec_id = r['spec_table_id']
        td = json.loads(r['template_data'] or '{}')
        features = json.loads(r['features'] or '[]')
        legacy_p = legacy_map.get(pid)
        if not legacy_p:
            continue

        desc_md = react_to_markdown(legacy_p.get('description', {})).strip()
        desc_sections = extract_sections(desc_md)
        new_spec_id = spec_id
        modified = False

        # 1) Remove duplicate template_data keys when a spec table exists
        if spec_id and spec_id in legacy_spec:
            table = legacy_spec[spec_id]
            product_mark = pid.split('-')[-1]
            for key in list(td.keys()):
                if key not in SPEC_ROW_NAME_HINTS:
                    continue
                row_name = find_matching_spec_row(table, product_mark, key, td[key])
                if row_name:
                    log_lines.append(f"{pid}: removed template_data.{key} (matched spec row '{row_name}')\n")
                    del td[key]
                    modified = True

        # 2) Create personal spec table when no table but a clear characteristics section exists
        if not spec_id:
            allowed_titles = {'характеристики', 'технические характеристики'}
            char_sections = [
                (title, body)
                for title, body in desc_sections.items()
                if title != '_intro' and title.lower() in allowed_titles
            ]
            if char_sections:
                rows_for_table = []
                for title, body in char_sections:
                    for bullet in parse_bullets(body):
                        if ':' in bullet:
                            name, val = bullet.split(':', 1)
                            rows_for_table.append({'name': name.strip(), 'values': {'Значение': val.strip()}})
                        else:
                            rows_for_table.append({'name': title, 'values': {'Значение': bullet.strip()}})
                if rows_for_table:
                    new_spec_id = f"{pid}-specs"
                    new_spec_tables[new_spec_id] = {
                        'columns': ['Характеристика', 'Значение'],
                        'rows': rows_for_table,
                    }
                    log_lines.append(f"{pid}: created spec table {new_spec_id} ({len(rows_for_table)} rows)\n")
                    modified = True
                    for key in list(td.keys()):
                        if key in SPEC_ROW_NAME_HINTS:
                            del td[key]
                            modified = True

        # 3) Deduplicate product.features against the spec table
        new_features = dedupe_features(pid, features, new_spec_id)
        if new_features != features:
            modified = True

        if modified:
            updates.append((json.dumps(td, ensure_ascii=False), json.dumps(new_features, ensure_ascii=False), new_spec_id, pid))

    for sid, st in new_spec_tables.items():
        conn.execute(
            'INSERT OR REPLACE INTO spec_tables (id, columns_json, rows_json) VALUES (?, ?, ?)',
            (sid, json.dumps(st['columns'], ensure_ascii=False), json.dumps(st['rows'], ensure_ascii=False))
        )

    conn.executemany(
        'UPDATE products SET template_data = ?, features = ?, spec_table_id = ? WHERE id = ?',
        updates
    )

    conn.commit()
    conn.close()

    log_path = DB_PATH.parent / f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    log_path.write_text(''.join(log_lines), encoding='utf-8')
    print(f'[log] {log_path}')
    print(f'[summary] new spec tables: {len(new_spec_tables)}, updated products: {len(updates)}')


if __name__ == '__main__':
    main()
