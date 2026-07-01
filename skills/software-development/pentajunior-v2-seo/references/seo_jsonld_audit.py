#!/usr/bin/env python3
"""Полный аудит данных pentajunior-v2 для корректного JSON-LD и SEO-мета-тегов.

Проверяет:
- заполненность meta_title / meta_description / page_description у категорий, подкатегорий, товаров
- заполненность features у товаров (fallback description в JSON-LD)
- числовой формат price и stock_info.newPrice
- наличие логотипа /logo.png в public/
- существование файлов product.image в public/

Запуск:
    python3 /home/natan/pentajunior-v2/scripts/seo_jsonld_audit.py
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
    # разрешаем одну точку
    return normalized.replace(".", "", 1).isdigit()


def main() -> int:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    issues: list[str] = []

    # Categories
    for c in cur.execute(
        "SELECT slug, title, meta_title, meta_description, page_description FROM categories"
    ).fetchall():
        if not c["meta_title"]:
            issues.append(f"Category '{c['title']}' ({c['slug']}): empty meta_title")
        if not c["meta_description"]:
            issues.append(f"Category '{c['title']}' ({c['slug']}): empty meta_description")
        if not c["page_description"]:
            issues.append(f"Category '{c['title']}' ({c['slug']}): empty page_description")

    # Subcategories
    for s in cur.execute(
        "SELECT sub.slug, sub.title, sub.meta_title, sub.meta_description, sub.page_description, "
        "c.title AS cat_title FROM subcategories sub JOIN categories c ON sub.category_id = c.id"
    ).fetchall():
        if not s["meta_title"]:
            issues.append(f"Subcategory '{s['title']}' ({s['slug']}) in '{s['cat_title']}': empty meta_title")
        if not s["meta_description"]:
            issues.append(f"Subcategory '{s['title']}' ({s['slug']}) in '{s['cat_title']}': empty meta_description")
        if not s["page_description"]:
            issues.append(f"Subcategory '{s['title']}' ({s['slug']}) in '{s['cat_title']}': empty page_description")

    # Products
    for p in cur.execute(
        "SELECT id, name, meta_title, meta_description, price, price_currency, "
        "price_unit, image, features, pack, stock_info, template_data FROM products"
    ).fetchall():
        if not p["meta_title"]:
            issues.append(f"Product '{p['name']}' ({p['id']}): empty meta_title")
        if not p["meta_description"]:
            issues.append(f"Product '{p['name']}' ({p['id']}): empty meta_description")

        # Validate all JSON fields that API routes parse
        for json_field in ("features", "stock_info", "template_data"):
            val = p[json_field]
            if val:
                try:
                    json.loads(val)
                except json.JSONDecodeError as e:
                    issues.append(f"Product '{p['name']}' ({p['id']}): {json_field} is invalid JSON: {e}")

        features = json.loads(p["features"] or "[]")
        if not features and not p["meta_description"]:
            issues.append(f"Product '{p['name']}' ({p['id']}): empty features and meta_description")

        if p["price"] and not is_numeric_price(p["price"]):
            issues.append(f"Product '{p['name']}' ({p['id']}): price '{p['price']}' is not numeric")

        stock_info = json.loads(p["stock_info"] or "{}")
        if stock_info.get("newPrice") and not is_numeric_price(stock_info["newPrice"]):
            issues.append(
                f"Product '{p['name']}' ({p['id']}): stock_info.newPrice '{stock_info['newPrice']}' is not numeric"
            )

        if p["image"] and not os.path.exists(os.path.join(PUBLIC, p["image"].lstrip("/"))):
            issues.append(f"Product '{p['name']}' ({p['id']}): image '{p['image']}' not found in public/")

    # Subcategories: JSON-valid seo_text is not required, but empty meta fields are checked above
    # Categories: related_categories must be valid JSON
    for c in cur.execute("SELECT slug, title, related_categories FROM categories").fetchall():
        try:
            json.loads(c["related_categories"] or "[]")
        except json.JSONDecodeError as e:
            issues.append(f"Category '{c['title']}' ({c['slug']}): related_categories invalid JSON: {e}")

    # Spec tables JSON validity (optional, since JSON-LD does not use them directly but admin API does)
    for t in cur.execute("SELECT id, columns_json, rows_json FROM spec_tables").fetchall():
        for field in ("columns_json", "rows_json"):
            val = t[field]
            if val:
                try:
                    json.loads(val)
                except json.JSONDecodeError as e:
                    issues.append(f"Spec table {t['id']}: {field} invalid JSON: {e}")

    # Global logo
    if not os.path.exists(os.path.join(PUBLIC, "logo.png")):
        issues.append("Global Organization JSON-LD: /logo.png does not exist in public/")

    if issues:
        print(f"Found {len(issues)} issue(s):")
        for i in issues:
            print(f"  - {i}")
        return 1

    print("All SEO/JSON-LD data checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
