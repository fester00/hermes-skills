#!/usr/bin/env python3
"""Page-pair parity report: words, link targets, price values.

Usage:
  python3 parity-report.py --old http://localhost:3000 --new http://localhost:3001 --pairs pairs.json
  python3 parity-report.py ... --report /tmp/parity.json

pairs.json:
[
  {"path": "/price", "twin": "/price"},
  {"path": "/directions/a/price.html", "twin": "/price",
   "twins": {"catalog.html": "/production", "product.html": "/production/x",
             "price.html": "/price", "contacts.html": "/contacts"}}
]

`path` is the address on the new side, `twin` the same page on the original side. `twins` is needed only
for a static prototype: it maps a file link onto the live path that page stands for, so links are compared
as targets instead of as strings. Any other *.html link in that mode resolves to "/".

Exit code 0 when nothing diverges, 1 otherwise.
"""
import argparse
import json
import re
import subprocess
import sys
from collections import Counter

ENTITIES = (('&nbsp;', ' '), ('&laquo;', '«'), ('&raquo;', '»'), ('&mdash;', '—'),
            ('&ndash;', '–'), ('&amp;', '&'), ('&quot;', '"'), ('&#39;', "'"), ('&hellip;', '…'))
STOP = {'для', 'или', 'при', 'это', 'как', 'что', 'все', 'уже', 'еще', 'был', 'была', 'были',
        'the', 'and', 'for', 'with', 'from', 'that', 'this'}


def fetch(url: str) -> str:
    return subprocess.run(['curl', '-sL', '--max-time', '25', url],
                          capture_output=True, text=True).stdout


def visible(html: str) -> str:
    h = re.sub(r'<(script|style|noscript|svg)\b.*?</\1>', ' ', html, flags=re.S | re.I)
    h = re.sub(r'<[^>]+>', ' ', h)
    for a, b in ENTITIES:
        h = h.replace(a, b)
    return re.sub(r'&[a-zA-Z]+;|&#\d+;', ' ', h)


def words(html: str) -> Counter:
    t = visible(html).lower().replace('ё', 'е')
    t = re.sub(r'[^а-яa-z0-9\s\-.]', ' ', t)
    return Counter(w for w in re.findall(r'[а-яa-z0-9][а-яa-z0-9\-.]{2,}', t) if w not in STOP)


def links(html: str, twins: dict | None = None) -> Counter:
    out = Counter()
    # Only <a href> is a link a crawler follows; <link rel="preconnect"> and other head hrefs are not,
    # and counting them makes the report demand markup the original never had.
    for h in re.findall(r'<a\b[^>]*href="([^"]+)"', html, re.I):
        if h.startswith(('mailto:', 'tel:', '//', '/_next/')):
            continue
        if not h.startswith('/'):
            if not (twins and h.endswith('.html')):
                continue
            h = twins.get(h.split('/')[-1], '/')
        if re.search(r'\.(css|js|mjs|png|jpe?g|webp|svg|ico|xml|txt|pdf|json)$', h, re.I):
            continue
        out[h.split('#')[0].split('?')[0] or '/'] += 1
    return out


def prices(html: str) -> Counter:
    """Values, not formatting: the number in front of the currency sign."""
    t = re.sub(r'\s+', ' ', visible(html))
    out = Counter()
    for m in re.finditer(r'[₽$€]', t):
        seg = t[max(0, m.start() - 14):m.start()]
        runs = re.findall(r'\d+', seg)
        if not runs:
            continue
        last = runs[-1]
        if len(runs) > 1 and len(last) == 3 and 1 <= len(runs[-2]) <= 3 and re.search(r'\d\s\d{3}$', seg):
            last = runs[-2] + last          # «5 600 ₽» → 5600
        out[last] += 1
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--old', required=True, help='original side, e.g. http://localhost:3000')
    ap.add_argument('--new', required=True, help='new side, e.g. http://localhost:3001')
    ap.add_argument('--pairs', required=True, help='JSON list of page pairs')
    ap.add_argument('--report', help='where to write the JSON report')
    args = ap.parse_args()

    pairs = json.loads(open(args.pairs, encoding='utf-8').read())
    rows, bad = [], 0
    for pair in pairs:
        twin, path = pair['twin'], pair['path']
        old, new = fetch(args.old + twin), fetch(args.new + path)
        if not old or not new:
            print(f'  {path[:48]:50} ОТВЕТА НЕТ (оригинал {len(old)}, новый {len(new)})')
            bad += 1
            continue

        ow, nw = words(old), words(new)
        ol, nl = links(old), links(new, pair.get('twins'))
        lost_words, gained_words = ow - nw, nw - ow
        lost_links, gained_links = ol - nl, nl - ol
        only_old = sorted(set(prices(old)) - set(prices(new)))
        only_new = sorted(set(prices(new)) - set(prices(old)))

        w = sum(lost_words.values())
        l = sum(lost_links.values())
        ok = not w and not l and not only_old and not only_new
        print(f'  {path[:48]:50} слов потеряно {w:4}  ссылок {l:3}  '
              f'цены {len(only_old)}/{len(only_new)}  — {"совпадает" if ok else "РАСХОЖДЕНИЕ"}')
        for word, n in lost_words.most_common(5):
            print(f'      ПОТЕРЯНО СЛОВО: {word!r} × {n}')
        for url, n in lost_links.most_common(5):
            print(f'      ПОТЕРЯНА ССЫЛКА: {url} × {n}')
        for url, n in gained_links.most_common(3):
            print(f'      НОВАЯ ССЫЛКА:    {url} × {n}')
        if only_old:
            print(f'      ЦЕНА ТОЛЬКО В ОРИГИНАЛЕ: {only_old}')
        if only_new:
            print(f'      ЦЕНА ТОЛЬКО В НОВОМ:    {only_new}')

        rows.append({'path': path, 'twin': twin,
                     'words_lost': dict(lost_words), 'words_added': dict(gained_words),
                     'links_lost': dict(lost_links), 'links_added': dict(gained_links),
                     'prices_only_original': only_old, 'prices_only_new': only_new})
        bad += w + l + len(only_old) + len(only_new)

    if args.report:
        open(args.report, 'w', encoding='utf-8').write(json.dumps(rows, ensure_ascii=False, indent=1))
        print(f'  отчёт: {args.report}')
    print(f'\n  страниц: {len(rows)}, расхождений всего: {bad}')
    print('  ВЕРДИКТ: ' + ('содержимое, ссылки и цены совпадают с оригиналом' if bad == 0
                           else 'есть расхождения — разобрать до деплоя'))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
