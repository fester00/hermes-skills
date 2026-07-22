#!/usr/bin/env python3
"""
Session-specific helper: validate proposed SEO drafts for pentajunior-v2
categories/subcategories/products before applying them to SQLite.

Usage: paste the proposals dict and run. Prints any title/description length
violations so they can be fixed before UPDATE.
"""

proposals = {
    # 'slug_or_name': {
    #     'title': '...',
    #     'meta_title': '...',
    #     'meta_description': '...',
    # },
}

for name, p in proposals.items():
    t_len = len(p.get('meta_title', ''))
    d_len = len(p.get('meta_description', ''))
    h1_len = len(p.get('title', ''))
    issues = []
    if t_len > 70:
        issues.append(f"title {t_len}>70")
    if not (160 <= d_len <= 170):
        issues.append(f"desc {d_len} not in 160-170")
    if issues:
        print(f"{name}: {' | '.join(issues)}")
        print(f"  H1  ({h1_len}): {p.get('title')}")
        print(f"  TTL ({t_len}): {p.get('meta_title')}")
        print(f"  DESC({d_len}): {p.get('meta_description')}")

if not any(
    len(p.get('meta_title', '')) > 70 or not (160 <= len(p.get('meta_description', '')) <= 170)
    for p in proposals.values()
):
    print("All drafts fit limits.")
