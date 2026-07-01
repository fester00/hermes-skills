#!/usr/bin/env python3
"""SEO-аудит pentajunior-v2 через прямой доступ к SQLite.

Используется, когда нужно быстро получить статистику по meta-тегам,
внутренним ссылкам, JSON-полям и длинам title/description без запуска dev-сервера.

Запуск:
    cd /home/natan/pentajunior-v2
    python3 /home/natan/.hermes/skills/software-development/pentajunior-v2-seo/references/pentajunior-seo-sqlite-audit.py
"""
import json
import os
import re
import sqlite3
from collections import Counter

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../../pentajunior-v2/pentajunior.db")


def connect():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found: {DB_PATH}")
    return sqlite3.connect(DB_PATH)


def length_stats(rows, label):
    print(f"\n=== {label} ===")
    print(f"Total: {len(rows)}")
    empty = sum(1 for r in rows if not r["meta_title"] and not r["meta_description"])
    print(f"Empty meta: {empty}")
    long_titles = [(r["key"], len(r["meta_title"])) for r in rows if len(r["meta_title"]) > 70]
    long_descs = [(r["key"], len(r["meta_description"])) for r in rows if len(r["meta_description"]) > 160]
    if long_titles:
        print(f"Title > 70 chars: {len(long_titles)}")
        for key, l in long_titles:
            print(f"  {key}: {l}")
    if long_descs:
        print(f"Description > 160 chars: {len(long_descs)}")
        for key, l in long_descs:
            print(f"  {key}: {l}")


def check_json_fields(conn):
    print("\n=== JSON FIELDS VALIDITY ===")
    invalid = []
    for table, fields in [
        ("categories", ["related_categories"]),
        ("subcategories", []),
        ("products", ["features", "keywords", "stock_info", "template_data", "price_tiers"]),
    ]:
        for field in fields:
            for id_, val in conn.execute(f"SELECT id, {field} FROM {table}").fetchall():
                if val:
                    try:
                        json.loads(val)
                    except Exception as e:
                        invalid.append((table, field, id_, str(e)[:50]))
    if invalid:
        print("Invalid JSON found:")
        for item in invalid[:10]:
            print(f"  {item}")
    else:
        print("All JSON fields valid")


def internal_link_stats(conn):
    print("\n=== INTERNAL LINKS IN seo_text ===")
    for slug, text in conn.execute(
        "SELECT slug, seo_text FROM categories WHERE seo_text LIKE '%href=%'"
    ).fetchall():
        links = re.findall(r'href="([^"]+)"', text or "")
        print(f"  {slug}: {len(links)} links")

    for slug, cat, text in conn.execute(
        "SELECT s.slug, c.slug, s.seo_text FROM subcategories s "
        "JOIN categories c ON s.category_id = c.id WHERE s.seo_text LIKE '%href=%'"
    ).fetchall():
        links = re.findall(r'href="([^"]+)"', text or "")
        print(f"  {cat}/{slug}: {len(links)} links")


def main():
    conn = connect()
    conn.row_factory = sqlite3.Row

    categories = [
        {
            "key": r["slug"],
            "meta_title": r["meta_title"] or "",
            "meta_description": r["meta_description"] or "",
        }
        for r in conn.execute("SELECT slug, meta_title, meta_description FROM categories ORDER BY slug").fetchall()
    ]
    length_stats(categories, "CATEGORIES")

    subcategories = [
        {
            "key": f"{r['cat']}/{r['slug']}",
            "meta_title": r["meta_title"] or "",
            "meta_description": r["meta_description"] or "",
        }
        for r in conn.execute(
            "SELECT s.slug, c.slug as cat, s.meta_title, s.meta_description "
            "FROM subcategories s JOIN categories c ON s.category_id = c.id "
            "ORDER BY c.slug, s.slug"
        ).fetchall()
    ]
    length_stats(subcategories, "SUBCATEGORIES")

    products = [
        {
            "key": f"{r['cat']}/{r['id']}",
            "meta_title": r["meta_title"] or "",
            "meta_description": r["meta_description"] or "",
        }
        for r in conn.execute(
            "SELECT p.id, c.slug as cat, p.meta_title, p.meta_description "
            "FROM products p JOIN categories c ON p.category_id = c.id "
            "ORDER BY p.id"
        ).fetchall()
    ]
    length_stats(products, "PRODUCTS")

    check_json_fields(conn)
    internal_link_stats(conn)

    print("\n=== DB SUMMARY ===")
    for table in ["categories", "subcategories", "products"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count}")


if __name__ == "__main__":
    main()
