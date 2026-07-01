#!/usr/bin/env python3
"""Post-migration audit script for pentajunior-v2 SQLite database.

Run after JSX-to-SQLite migration to verify data integrity, detect
common corruption patterns, and report actionable fixes.

Usage:
    python3 scripts/migration-audit.py /path/to/pentajunior.db

Exit codes:
    0 — all checks passed
    1 — one or more issues found (see stdout for details)
"""

import sqlite3, json, re, sys, os

def main(db_path: str) -> int:
    if not os.path.exists(db_path):
        print(f"ERROR: Database not found: {db_path}")
        return 1

    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    issues = []

    # ─── 1. Price normalization audit ───
    rows = db.execute("SELECT id, name, price, price_unit FROM products WHERE price IS NOT NULL AND price != '' AND price != 'по запросу'").fetchall()
    for r in rows:
        price = r['price']
        # price should be digits only
        if re.search(r'[^\d]', str(price)):
            issues.append(f"PRICE_NON_DIGIT: {r['id']} '{price}' (unit='{r['price_unit']}') — contains currency symbols or text")
        # price_unit should be set
        if not r['price_unit']:
            issues.append(f"PRICE_UNIT_MISSING: {r['id']} price='{price}' — no price_unit")

    # ─── 2. stock_info audit ───
    rows = db.execute("SELECT id, stock_info FROM products WHERE stock_info IS NOT NULL AND stock_info != '{}'").fetchall()
    for r in rows:
        si = json.loads(r['stock_info'])
        new_price = si.get('newPrice', '')
        if new_price and re.search(r'[^\d]', str(new_price)):
            issues.append(f"STOCKINFO_NON_DIGIT: {r['id']} newPrice='{new_price}' — contains text/currency")

    # ─── 3. template_data audit ───
    rows = db.execute("SELECT id, name, template_type, template_data FROM products ORDER BY id").fetchall()
    for r in rows:
        td_raw = r['template_data']
        if not td_raw or td_raw == '{}':
            issues.append(f"TEMPLATE_DATA_EMPTY: {r['id']} ({r['name']}) type='{r['template_type']}' — template_data is empty")
            continue
        try:
            td = json.loads(td_raw)
        except json.JSONDecodeError:
            issues.append(f"TEMPLATE_DATA_CORRUPT: {r['id']} — invalid JSON")
            continue

        # Check for inline headers in body that should be extracted
        body = td.get('body', '')
        if body:
            inline_headers = re.findall(r'([А-Я][А-Яа-я\s]+):', body)
            if inline_headers:
                for h in inline_headers:
                    if h.strip() in ('Ключевые свойства', 'Ключевые преимущества', 'Характеристики',
                                     'Область применения', 'Применение', 'Области применения', 'Состав'):
                        issues.append(f"TEMPLATE_BODY_HAS_HEADER: {r['id']} body contains '{h}' — run body normalization")
                        break  # report once per product

    # ─── 4. Image existence audit ───
    base_dir = os.path.dirname(db_path)
    rows = db.execute("SELECT id, image FROM products WHERE image IS NOT NULL AND image != ''").fetchall()
    for r in rows:
        img_path = os.path.join(base_dir, 'public', r['image'].lstrip('/'))
        if not os.path.exists(img_path):
            issues.append(f"IMAGE_MISSING: {r['id']} image='{r['image']}' — file not found at {img_path}")

    # ─── 5. spec_table_id dangling reference ───
    rows = db.execute("""
        SELECT p.id, p.spec_table_id
        FROM products p
        LEFT JOIN spec_tables s ON p.spec_table_id = s.id
        WHERE p.spec_table_id IS NOT NULL AND p.spec_table_id != '' AND s.id IS NULL
    """).fetchall()
    for r in rows:
        issues.append(f"SPEC_TABLE_DANGLING: {r['id']} spec_table_id='{r['spec_table_id']}' — no matching table")

    # ─── 6. Category product count ───
    cat_counts = db.execute("""
        SELECT c.title, COUNT(p.id) as cnt
        FROM categories c LEFT JOIN products p ON c.id = p.category_id
        GROUP BY c.id
    """).fetchall()
    for r in cat_counts:
        if r['cnt'] == 0:
            issues.append(f"CATEGORY_EMPTY: '{r['title']}' — no products in category")

    # ─── Report ───
    if not issues:
        print("✅ All migration checks passed.")
        return 0

    print(f"⚠️  Found {len(issues)} issue(s):\n")
    for issue in issues:
        print(f"  • {issue}")
    print()
    print("Suggested fixes:")
    print("  • PRICE_NON_DIGIT: UPDATE products SET price = '<digits>', price_unit = '<unit>' WHERE id = '...';")
    print("  • STOCKINFO_NON_DIGIT: Clean newPrice field in stock_info JSON")
    print("  • TEMPLATE_DATA_EMPTY: Populate template_data from v1 source (see references/template-data-population-workflow.md)")
    print("  • IMAGE_MISSING: Copy missing files from v1 public/images/ or set image = NULL")
    print("  • SPEC_TABLE_DANGLING: Insert missing spec table or set spec_table_id = NULL")
    print("  • CATEGORY_EMPTY: Verify category has products in v1 data file")
    return 1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} /path/to/pentajunior.db")
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
