# Скрипт финальной глобальной SEO-проверки pentajunior-v2

import sqlite3
import json
import re
from collections import defaultdict

DB_PATH = '/home/natan/pentajunior-v2/pentajunior.db'


def check_lengths(table, fields, limits):
    issues = []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    for field, limit in zip(fields, limits):
        for r in c.execute(f"SELECT id, {field} FROM {table} WHERE {field} IS NOT NULL AND {field} != ''").fetchall():
            if len(r[field]) > limit:
                issues.append((table, r['id'], field, len(r[field]), limit))
    conn.close()
    return issues


def find_producer_claims():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    claims = []
    for table in ['categories', 'subcategories']:
        if table == 'categories':
            rows = c.execute("SELECT id, slug, meta_title, meta_description, page_description, seo_text FROM categories").fetchall()
        else:
            rows = c.execute('''SELECT s.id, s.slug, c.slug as cat_slug, s.meta_title, s.meta_description, s.page_description, s.seo_text
FROM subcategories s JOIN categories c ON s.category_id=c.id''').fetchall()
        for r in rows:
            for field in ['meta_title', 'meta_description', 'page_description', 'seo_text']:
                val = r[field] or ''
                if 'от производителя' in val.lower() or re.search(r'производитель\s*[.\s]*$', val.lower()):
                    slug = f"{r['cat_slug']}/{r['slug']}" if table == 'subcategories' else r['slug']
                    claims.append((table, slug, field, val[:80]))
    for r in c.execute("SELECT id, name, meta_title, meta_description FROM products").fetchall():
        for field in ['meta_title', 'meta_description']:
            val = r[field] or ''
            if 'от производителя' in val.lower() or re.search(r'производитель\s*[.\s]*$', val.lower()):
                claims.append(('products', r['id'], field, val[:80]))
    conn.close()
    return claims


def find_duplicate_keywords():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    kw_groups = defaultdict(list)
    for r in c.execute("SELECT id, keywords FROM products").fetchall():
        try:
            kw = tuple(sorted(json.loads(r['keywords'] or '[]')))
            kw_groups[kw].append(r['id'])
        except Exception:
            pass
    conn.close()
    return [(list(kw), len(prods)) for kw, prods in kw_groups.items() if len(prods) > 1 and kw]


def main():
    title_issues = check_lengths('categories', ['meta_title'], [70]) + \
                   check_lengths('subcategories', ['meta_title'], [70]) + \
                   check_lengths('products', ['meta_title'], [70])
    desc_issues = check_lengths('categories', ['meta_description'], [170]) + \
                  check_lengths('subcategories', ['meta_description'], [170]) + \
                  check_lengths('products', ['meta_description'], [170])
    claims = find_producer_claims()
    duplicates = find_duplicate_keywords()

    print(f'title >70: {len(title_issues)}')
    print(f'description >170: {len(desc_issues)}')
    print(f'producer claims: {len(claims)}')
    print(f'duplicate keyword sets: {len(duplicates)}')

    if title_issues:
        print('\nTitle >70:')
        for i in title_issues[:10]:
            print(f'  {i}')
    if desc_issues:
        print('\nDescription >170:')
        for i in desc_issues[:10]:
            print(f'  {i}')
    if claims:
        print('\nProducer claims:')
        for i in claims[:10]:
            print(f'  {i}')
    if duplicates:
        print('\nDuplicate keyword sets:')
        for kw, cnt in duplicates[:5]:
            print(f'  ({cnt} products) {kw[:5]}')


if __name__ == '__main__':
    main()
