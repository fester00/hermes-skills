#!/usr/bin/env python3
"""
Minimal smoke test: confirm Yandex and Google search work via Playwright profile.
"""
import asyncio
from playwright.async_api import async_playwright

PROFILE_DIR = '/mnt/data/natan-storage/.chrome-vk-profile'
VIEWPORT = {'width': 1920, 'height': 1080}
USER_AGENT = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/120.0.0.0 Safari/537.36'
)

async def test_search(engine: str, query: str):
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            args=['--disable-blink-features=AutomationControlled'],
            viewport=VIEWPORT,
            user_agent=USER_AGENT,
        )
        page = context.pages[0] if context.pages else await context.new_page()

        if engine == 'google':
            url = f'https://www.google.com/search?q={query.replace(" ", "+")}'
        elif engine == 'yandex':
            url = f'https://ya.ru/search/?text={query.replace(" ", "+")}'
        else:
            raise ValueError(engine)

        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(4)

        title = await page.title()
        print(f'[{engine}] title: {title}')
        print(f'[{engine}] url: {page.url}')

        text = await page.inner_text('body')
        blocked = any(k in text.lower() for k in [
            'не робот', 'captcha', 'sorry',
            'почему это могло произойти', 'вы не робот'
        ])
        print(f'[{engine}] {"❌ BLOCKED" if blocked else "✅ OK"}')

        await page.screenshot(path=f'/tmp/{engine}_search.png', full_page=True)
        await context.close()

async def main():
    await test_search('google', 'SSD M.2 NVMe 1TB цена')
    await test_search('yandex', 'SSD M.2 NVMe 1TB цена')

if __name__ == '__main__':
    asyncio.run(main())
