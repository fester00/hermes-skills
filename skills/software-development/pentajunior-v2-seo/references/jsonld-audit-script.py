#!/usr/bin/env python3
"""Полный аудит данных pentajunior-v2 для корректного JSON-LD.

Проверяет:
- заполненность meta_title / meta_description у категорий, подкатегорий, товаров
- заполненность features у товаров (fallback description в JSON-LD)
- числовой формат price и stock_info.newPrice
- наличие логотипа /logo.png в public/
- существование файлов product.image в public/

Запуск:
    python3 /home/natan/pentajunior-v2/scripts/jsonld_audit.py
"""
import sqlite3
import json
import os
import sys

DB = "/home/natan/pentajunior-v2/pentajunior.db"
PUBLIC = "/home/natan/pentajunior-v2/public"


def is_numeric_price(value: str | None) -> bool:
    if not value:
        return True  # NULL/пустая цена допустима
    normalized = str(value).replace(" ", "").replace(",", ".")
    return normalized.replace(".", "", 1).isdigit()


def main() -> int:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    issues: list[str] = []

    # Categories
    for c in cur.execute("SELECT slug, title, meta_title, meta_description FROM categories").fetchall():
        if not c["meta_title"]:
            issues.append(f"Category '{c['title']}' ({c['slug']}): empty meta_title")
        if not c["meta_description"]:
            issues.append(f"Category '{c['title']}' ({c['slug']}): empty meta_description")

    # Subcategories
    for s in cur.execute(
        "SELECT sub.slug, sub.title, sub.meta_title, sub.meta_description, c.title AS cat_title "
        "FROM subcategories sub JOIN categories c ON sub.category_id = c.id"
    ).fetchall():
        if not s["meta_title"]:
            issues.append(f"Subcategory '{s['title']}' ({s['slug']}) in '{s['cat_title']}': empty meta_title")
        if not s["meta_description"]:
            issues.append(f"Subcategory '{s['title']}' ({s['slug']}) in '{s['cat_title']}': empty meta_description")

    # Products
    for p in cur.execute(
        "SELECT id, name, meta_title, meta_description, price, price_currency, "
        "price_unit, image, features, pack, stock_info FROM products"
    ).fetchall():
        if not p["meta_title"]:
            issues.append(f"Product '{p['name']}' ({p['id']}): empty meta_title")
        if not p["meta_description"]:
            issues.append(f"Product '{p['name']}' ({p['id']}): empty meta_description")

        features = json.loads(p["features"] or "[]")
        if not features and not p["meta_description"]:
            issues.append(f"Product '{p['name']}' ({p['id']}): empty features and meta_description")

        if p["price"] and not is_numeric_price(p["price"]):
            issues.append(f"Product '{p['name']}' ({p['id']}): price '{p['price']}' is not numeric")

        stock_info = json.loads(p["stock_info"] or "{}")
        if stock_info.get("newPrice") and not is_numeric_price(stock_info["newPrice"]):
            issues.append(f"Product '{p['name']}' ({p['id']}): stock_info.newPrice '{stock_info['newPrice']}' is not numeric")

        if p["image"] and not os.path.exists(os.path.join(PUBLIC, p["image"].lstrip("/"))):
            issues.append(f"Product '{p['name']}' ({p['id']}): image '{p['image']}' not found in public/")

    # Global logo
    if not os.path.exists(os.path.join(PUBLIC, "logo.png")):
        issues.append("Global Organization JSON-LD: /logo.png does not exist in public/")

    if issues:
        print(f"Found {len(issues)} issue(s):")
        for i in issues:
            print(f"  - {i}")
        return 1

    print("All JSON-LD data checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
