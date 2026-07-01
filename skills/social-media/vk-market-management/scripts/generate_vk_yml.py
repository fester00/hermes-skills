#!/usr/bin/env python3
"""
Генератор YML-фида для VK Market.
Принимает список товаров, группирует варианты по group_id.

Пример входных данных (list of dict):
    products = [
        {"name": "Юнисил 9110", "group_id": "junisil_9110",
         "variants": [
             {"weight": "1.04 кг", "price": 2809, "offer_id": "junisil_9110_1040"},
             {"weight": "5.2 кг", "price": 10807, "offer_id": "junisil_9110_5200"},
         ],
         "category_id": 1,
         "description": "Двухкомпонентный силиконовый компаунд",
        },
    ]

Использование:
    python3 generate_vk_yml.py products.json > out.yml
"""

import json
import sys
from xml.sax.saxutils import escape
from datetime import datetime


def generate_yml(products, shop_name="Магазин", company="ООО", url="https://example.com"):
    cats = set()
    for p in products:
        cats.add((p["category_id"], p.get("category_name", "Категория " + str(p["category_id"]))))

    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        f'<yml_catalog date="{datetime.now().strftime("%Y-%m-%d %H:%M")}">',
        "  <shop>",
        f"    <name>{escape(shop_name)}</name>",
        f"    <company>{escape(company)}</company>",
        f"    <url>{escape(url)}</url>",
        "    <currencies>",
        '      <currency id="RUB" rate="1"/>',
        "    </currencies>",
        "    <categories>",
    ]
    for cid, cname in sorted(cats):
        lines.append(f'      <category id="{cid}">{escape(cname)}</category>')
    lines.append("    </categories>")
    lines.append("    <offers>")

    for p in products:
        for v in p["variants"]:
            lines.append(f'      <offer id="{v["offer_id"]}" available="true" group_id="{p["group_id"]}">')
            lines.append(f'        <price>{v["price"]}</price>')
            lines.append(f'        <currencyId>RUB</currencyId>')
            lines.append(f'        <categoryId>{p["category_id"]}</categoryId>')
            lines.append(f'        <name>{escape(p["name"])} — {escape(v["weight"])}</name>')
            lines.append(f'        <description>{escape(p.get("description", ""))}</description>')
            lines.append(f'        <param name="Вес/объём">{escape(v["weight"])}</param>')
            lines.append(f'        <picture></picture>')
            lines.append('      </offer>')

    lines.append("    </offers>")
    lines.append("  </shop>")
    lines.append("</yml_catalog>")
    return "\n".join(lines)


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        products = json.load(f)
    print(generate_yml(products))
