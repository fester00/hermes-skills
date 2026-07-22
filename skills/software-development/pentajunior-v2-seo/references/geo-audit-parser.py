"""
Parse rendered Next.js build output for SEO fields and compare with an external audit JSON.
Usage:
  python3 geo-audit-parser.py
"""

import json
import re
from pathlib import Path
from html.parser import HTMLParser

BUILD_DIR = Path('/home/natan/pentajunior-v2/.next/server/app')


class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_head = False
        self.title = ''
        self.meta = {}
        self.canonical = ''
        self.og = {}
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'head':
            self.in_head = True
        if self.in_head:
            if tag == 'title':
                self.current_tag = 'title'
            elif tag == 'link' and attrs_dict.get('rel') == 'canonical':
                self.canonical = attrs_dict.get('href', '')
            elif tag == 'meta':
                name = attrs_dict.get('name', '') or attrs_dict.get('property', '')
                content = attrs_dict.get('content', '')
                if name.startswith('og:'):
                    self.og[name] = content
                elif name:
                    self.meta[name] = content

    def handle_endtag(self, tag):
        if tag == 'head':
            self.in_head = False
        if self.current_tag == tag:
            self.current_tag = None

    def handle_data(self, data):
        if self.current_tag == 'title':
            self.title += data


def count_headings_in_body(text: str):
    body_match = re.search(r'<body[^\u003e]*\u003e(.*)\u003c/body\u003e', text, re.S)
    if not body_match:
        return 0, 0
    body = body_match.group(1)
    h1 = len(re.findall(r'\u003ch1[\s\u003e]', body, re.I))
    h2 = len(re.findall(r'\u003ch2[\s\u003e]', body, re.I))
    return h1, h2


def extract_data_from_html(html_path: Path):
    text = html_path.read_text(encoding='utf-8')
    parser = HeadParser()
    parser.feed(text)
    h1_count, h2_count = count_headings_in_body(text)
    return {
        'title': parser.title.strip(),
        'description': parser.meta.get('description', ''),
        'canonical': parser.canonical,
        'ogTitle': parser.og.get('og:title', ''),
        'ogDescription': parser.og.get('og:description', ''),
        'ogImage': parser.og.get('og:image', ''),
        'h1Count': h1_count,
        'h2Count': h2_count,
    }


def build_url_map():
    current = {}
    for html_file in BUILD_DIR.rglob('*.html'):
        rel = html_file.relative_to(BUILD_DIR).as_posix()
        if 'admin' in rel:
            continue
        if rel == 'index.html':
            url = 'https://pentajunior.ru/'
        else:
            url = 'https://pentajunior.ru/' + rel.replace('.html', '')
        current[url] = extract_data_from_html(html_file)
    return current


def compare_with_audit(audit_path: Path, current: dict):
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    audit_by_url = {item['url']: item for item in audit}

    common = set(audit_by_url.keys()) & set(current.keys())
    changes = []
    for url in sorted(common):
        a = audit_by_url[url]
        c = current[url]
        diffs = []
        for key in ['title', 'description', 'canonical', 'ogTitle', 'ogDescription', 'ogImage', 'h1Count', 'h2Count']:
            av = a.get(key, '')
            cv = c.get(key, '')
            if str(av) != str(cv):
                diffs.append((key, av, cv))
        if diffs:
            changes.append((url, diffs))

    only_audit = sorted(set(audit_by_url.keys()) - set(current.keys()))
    only_current = sorted(set(current.keys()) - set(audit_by_url.keys()))

    print(f"URLs in audit: {len(audit_by_url)}")
    print(f"URLs in build: {len(current)}")
    print(f"Common URLs: {len(common)}")
    print(f"URLs with differences: {len(changes)}")
    if only_audit:
        print(f"Only in audit: {len(only_audit)} — {only_audit[:5]}...")
    if only_current:
        print(f"Only in build: {len(only_current)} — {only_current[:5]}...")

    for url, diffs in changes:
        print(f"\n{url}")
        for key, old, new in diffs:
            print(f"  {key}:")
            print(f"    audit:   {old}")
            print(f"    current: {new}")


if __name__ == '__main__':
    audit_path = Path('/home/natan/.hermes/cache/documents/doc_3245245ad180_seo-geo-audit-2026-07-01.json')
    current = build_url_map()
    compare_with_audit(audit_path, current)
