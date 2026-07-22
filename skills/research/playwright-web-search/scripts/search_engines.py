#!/usr/bin/env python3
"""
Search Yandex or Google using Playwright with persistent Chrome profile + Xvfb.

Usage:
    cd /mnt/data/natan-storage/playwright-search
    source .venv/bin/activate
    xvfb-run -a --server-args="-screen 0 1920x1080x24" python search_engines.py \
        --engine yandex --query "SSD M.2 NVMe 1TB цена" --limit 5
"""

import argparse
import asyncio
import json
import urllib.parse
from playwright.async_api import async_playwright

PROFILE_DIR = '/mnt/data/natan-storage/.chrome-vk-profile'
VIEWPORT = {'width': 1920, 'height': 1080}
USER_AGENT = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/120.0.0.0 Safari/537.36'
)

ENGINE_CONFIG = {
    'google': {
        'url': 'https://www.google.com/search?q={query}',
        'result_selector': 'div.g, div[data-hveid]',
        'title_selector': 'h3',
        'link_selector': 'a[href]',
        'snippet_selector': 'div.VwiC3b, span.st, div.s',
        'wait': 4,
    },
    'yandex': {
        'url': 'https://ya.ru/search/?text={query}',
        'result_selector': 'li.serp-item, .serp-item',
        'title_selector': '.OrganicTitle-LinkText, h2 a span, .organic__url-text',
        'link_selector': '.OrganicTitle-Link, h2 a, .organic__url',
        'snippet_selector': '.OrganicContent, .organic__content-wrapper, .text-container',
        'wait': 5,
    },
}


def parse_args():
    parser = argparse.ArgumentParser(description='Search Yandex or Google via Playwright')
    parser.add_argument('--engine', choices=['yandex', 'google'], required=True)
    parser.add_argument('--query', required=True, help='Search query')
    parser.add_argument('--limit', type=int, default=5, help='Number of results')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    return parser.parse_args()


async def search(engine: str, query: str, limit: int) -> list[dict]:
    cfg = ENGINE_CONFIG[engine]
    encoded = urllib.parse.quote(query)
    url = cfg['url'].format(query=encoded)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            args=['--disable-blink-features=AutomationControlled'],
            viewport=VIEWPORT,
            user_agent=USER_AGENT,
        )
        page = context.pages[0] if context.pages else await context.new_page()

        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(cfg['wait'])

        body_text = await page.inner_text('body')
        blocked = any(k in body_text.lower() for k in [
            'не робот', 'captcha', 'sorry', 'почему это могло произойти',
            'вы не робот', 'unusual traffic'
        ])

        if blocked:
            await context.close()
            raise RuntimeError(f'{engine} returned anti-bot page')

        cards = await page.query_selector_all(cfg['result_selector'])
        results = []
        for card in cards[:limit * 2]:
            try:
                title_el = await card.query_selector(cfg['title_selector'])
                link_el = await card.query_selector(cfg['link_selector'])
                snippet_el = await card.query_selector(cfg['snippet_selector'])

                title = await title_el.inner_text() if title_el else ''
                snippet = await snippet_el.inner_text() if snippet_el else ''
                href = await link_el.get_attribute('href') if link_el else ''

                if not href or href.startswith('#') or href.startswith('/search'):
                    continue

                if title.strip() and len(results) < limit:
                    results.append({
                        'title': title.strip()[:160],
                        'url': href[:500],
                        'snippet': snippet.strip()[:300],
                    })
            except Exception:
                continue

        await context.close()
        return results


async def main():
    args = parse_args()
    results = await search(args.engine, args.query, args.limit)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f'🔍 {args.engine.capitalize()}: {args.query}')
        print()
        for i, r in enumerate(results, 1):
            print(f'{i}. {r["title"]}')
            print(f'   {r["url"]}')
            if r['snippet']:
                print(f'   {r["snippet"]}')
            print()


if __name__ == '__main__':
    asyncio.run(main())
