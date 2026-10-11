#!/usr/bin/env python3
"""Вживить HTML-фрагмент в скачанный HTML живой страницы penta-junior.ru и замерить результат.

Печатает: баланс тегов фрагмента, геометрию фото и заголовков, горизонтальное
переполнение, вычисленные цвета текста и число «голых» текстовых узлов —
на ширинах 1280 / 768 / 375. Скриншоты складывает рядом.

Playwright лежит в venv Hermes, а браузеры — вне дефолтного каталога, поэтому
перед запуском выставить окружение (иначе `launch()` не найдёт chromium):

    export TMPDIR=/mnt/data/natan-storage/tmp
    export HOME=/mnt/data/natan-storage/tmp
    export PLAYWRIGHT_BROWSERS_PATH=/mnt/data/natan-storage/playwright-browsers

    /mnt/data/natan-storage/.hermes/hermes-agent/venv/bin/python \
        scripts/verify_legacy_page_fragment.py --page page.html --fragment frag.html

Режимы:
  --mode article   (по умолчанию) — заменить всё содержимое <article class="content_article">;
                     существующий <h1> сохраняется, если во фрагменте его нет.
  --mode topblock                — заменить только верхний legacy-блок float-колонок
                     (28% картинка + 72% текст) внутри статьи.

Страницу скачивать curl'ом с браузерным User-Agent: web_extract по penta-junior.ru даёт 403.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ARTICLE_OPEN = '<article class="content_article">'
FLOAT_ANCHOR = '<div style="margin-right: 4rem; float: left; width: 28%;">'
TEXT_ANCHOR = '<div style="float: left; width: 72%;">'
WIDTHS = (1280, 768, 375)
VOID = {'br', 'img', 'hr', 'meta', 'link', 'input'}

MEASURE = """(() => {
  const rr = el => { if (!el) return null; const b = el.getBoundingClientRect();
    return {w: Math.round(b.width), h: Math.round(b.height),
            top: Math.round(b.top), left: Math.round(b.left)}; };
  const art = document.querySelector('.content_article');
  if (!art) return {error: 'нет .content_article'};
  const col = el => el ? getComputedStyle(el).color : null;
  const imgs = [...art.querySelectorAll('img')];
  const h3s = [...art.querySelectorAll('h3')];
  let bare = 0;
  const walker = document.createTreeWalker(art, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const t = walker.currentNode;
    if (!t.textContent.trim()) continue;
    const tag = t.parentElement ? t.parentElement.tagName : '';
    if (tag === 'DIV' || tag === 'ARTICLE') bare++;
  }
  return {
    article: rr(art),
    images: imgs.map(i => Object.assign(rr(i), {loaded: i.complete && i.naturalWidth > 0})),
    firstH3: h3s.length ? Object.assign({text: h3s[0].textContent.trim().slice(0, 30)}, rr(h3s[0])) : null,
    textBesideImages: (imgs[0] && h3s[0]) ? rr(imgs[0]).top === rr(h3s[0]).top : null,
    overflowSection: art.scrollWidth - art.clientWidth,
    overflowDoc: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    colors: {p: col(art.querySelector('p')), li: col(art.querySelector('li')),
             h3: col(h3s[0]), td: col(art.querySelector('td'))},
    bareTextNodes: bare,
    tables: art.querySelectorAll('table.price').length,
  };
})()"""


def tag_balance(fragment: str):
    body = re.sub(r'<!--.*?-->', '', fragment, flags=re.S)
    stack, problems = [], []
    for m in re.finditer(r'<(/?)([a-zA-Z0-9]+)[^>]*?(/?)>', body):
        closing, tag, selfclose = m.group(1), m.group(2).lower(), m.group(3)
        if tag in VOID or selfclose:
            continue
        if closing:
            if not stack or stack[-1] != tag:
                problems.append(f'непарный </{tag}> (стек: {stack[-3:]})')
                break
            stack.pop()
        else:
            stack.append(tag)
    if stack:
        problems.append(f'не закрыто: {stack}')
    return problems


def replace_article(page: str, fragment: str) -> str:
    a = page.find(ARTICLE_OPEN)
    b = page.find('</article>', a) if a >= 0 else -1
    if a < 0 or b < 0:
        sys.exit('не найден <article class="content_article"> — проверь, что скачана страница товара')
    inner = page[a + len(ARTICLE_OPEN):b]
    if '<h1' in fragment.lower():
        head = ''
    else:
        m = re.search(r'<h1.*?</h1>', inner, re.S)
        head = (m.group(0) if m else '<h1>Товар</h1>') + '\n'
    return page[:a + len(ARTICLE_OPEN)] + '\n' + head + fragment + '\n' + page[b:]


def replace_float_block(page: str, fragment: str) -> str:
    start = page.find(FLOAT_ANCHOR)
    text = page.find(TEXT_ANCHOR, start) if start >= 0 else -1
    if start < 0 or text < 0:
        sys.exit('не найден legacy float-блок (28% картинка + 72% текст)')
    depth, end = 0, None
    for m in re.finditer(r'<div\b|</div>', page[text:]):
        if m.group(0) == '<div':
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                end = text + m.end()
                break
    if end is None:
        sys.exit('не найден конец текстового блока')
    return page[:start] + fragment + page[end:]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--page', required=True, help='скачанный HTML живой страницы')
    ap.add_argument('--fragment', required=True, help='проверяемый HTML-фрагмент')
    ap.add_argument('--mode', choices=('article', 'topblock'), default='article')
    ap.add_argument('--screenshots', default='.', help='куда положить скриншоты')
    args = ap.parse_args()

    page = Path(args.page).read_text(encoding='utf-8', errors='replace')
    fragment = Path(args.fragment).read_text(encoding='utf-8')

    problems = tag_balance(fragment)
    print('баланс тегов:', 'OK' if not problems else ' | '.join(problems))

    merged = replace_article(page, fragment) if args.mode == 'article' else replace_float_block(page, fragment)
    out = Path(args.screenshots) / 'live-merged.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(merged, encoding='utf-8')
    print('вживлено ->', out)

    from playwright.sync_api import sync_playwright

    shots = Path(args.screenshots)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width in WIDTHS:
            pg = browser.new_page(viewport={'width': width, 'height': 900})
            pg.goto(out.resolve().as_uri(), wait_until='load', timeout=45000)
            pg.wait_for_timeout(2000)
            print(f'=== {width} px ===')
            print(json.dumps(pg.evaluate(MEASURE), ensure_ascii=False))
            pg.screenshot(path=str(shots / f'check-{width}.png'), full_page=(width == WIDTHS[0]))
            pg.close()
        browser.close()

    print('\nГлазами по итогу:', str((shots / 'check-%d.png' % WIDTHS[0]).resolve()), '(отдать vision_analyze)')
    print('Помни: голых текстовых узлов должно быть 0 — иначе текст будет чёрным на тёмном фоне.')


if __name__ == '__main__':
    main()
