#!/usr/bin/env python3
"""
Search Ozon for products using Playwright with persistent Chrome profile + Xvfb.

Usage:
    cd /mnt/data/natan-storage/playwright-search
    source .venv/bin/activate
    xvfb-run -a --server-args="-screen 0 1920x1080x24" python ozon_search.py --query "SSD M.2 NVMe 1TB" --max-price 10000 --limit 5
"""

import argparse
import asyncio
import json
from playwright.async_api import async_playwright

PROFILE_DIR = '/mnt/data/natan-storage/.chrome-vk-profile'
VIEWPORT = {'width': 1920, 'height': 1080}
USER_AGENT = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/120.0.0.0 Safari/537.36'
)


def parse_args():
    parser = argparse.ArgumentParser(description='Search Ozon products')
    parser.add_argument('--query', required=True, help='Search query')
    parser.add_argument('--max-price', type=int, default=None, help='Max price in rubles')
    parser.add_argument('--limit', type=int, default=5, help='Number of results')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    return parser.parse_args()


async def search_ozon(query: str, max_price: int | None, limit: int):
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            args=['--disable-blink-features=AutomationControlled'],
            viewport=VIEWPORT,
            user_agent=USER_AGENT,
        )
        page = context.pages[0] if context.pages else await context.new_page()

        q = query.replace(' ', '+')
        url = f'https://www.ozon.ru/search/?text={q}'
        if max_price:
            url += f'&price_to={max_price}'

        await page.goto(url, wait_until='networkidle', timeout=60000)
        await asyncio.sleep(3)

        cards = await page.query_selector_all('div[data-widget="tileGridDesktop"] .tile-root')
        results = []
        for card in cards[:limit * 2]:
            try:
                link_el = await card.query_selector('a[href*="/product/"]')
                href = await link_el.get_attribute('href') if link_el else 'N/A'
                full_url = f'https://ozon.ru{href}' if href.startswith('/') else href

                text = await card.inner_text()
                lines = [line.strip() for line in text.split('\n') if line.strip()]

                price = next((line for line in lines if '₽' in line), '')
                name_candidates = [
                    line for line in lines
                    if any(kw in line.lower() for kw in ['ssd', 'тб', 'tb', 'kingston', 'digma', 'samsung', 'adata', 'netac', 'silicon', 'nvme', 'm.2'])
                ]
                name = name_candidates[0] if name_candidates else ''

                rating = ''
                for line in lines:
                    if 'отзыв' in line.lower() or ('.' in line and len(line) < 5):
                        rating = line
                        break

                if name and price:
                    results.append({
                        'name': name[:120],
                        'price': price,
                        'rating': rating,
                        'url': full_url,
                    })
            except Exception:
                continue

            if len(results) >= limit:
                break

        await context.close()
        return results


async def main():
    args = parse_args()
    results = await search_ozon(args.query, args.max_price, args.limit)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"💰 {r['price']}")
            print(f"   {r['name']}")
            print(f"   {r['rating']}")
            print(f"   {r['url'][:100]}")
            print()


if __name__ == '__main__':
    asyncio.run(main())
