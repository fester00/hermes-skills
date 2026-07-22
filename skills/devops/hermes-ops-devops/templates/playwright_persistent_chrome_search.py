from playwright.async_api import async_playwright
import asyncio

# Template: persistent Chrome profile + xvfb + marketplace search
# Run with:
#   xvfb-run -a --server-args="-screen 0 1920x1080x24" python playwright_persistent_chrome_search.py

USER_DATA_DIR = '/mnt/data/natan-storage/.chrome-vk-profile'
USER_AGENT = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)


async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=False,
            args=['--disable-blink-features=AutomationControlled'],
            viewport={'width': 1920, 'height': 1080},
            user_agent=USER_AGENT,
        )
        page = context.pages[0] if context.pages else await context.new_page()

        url = 'https://www.ozon.ru/search/?text=SSD+M2+NVMe+1TB&price_to=10000'
        print('Opening', url)
        await page.goto(url, wait_until='networkidle', timeout=60000)
        await asyncio.sleep(3)

        print('title:', await page.title())

        # Accept cookie banner if present
        try:
            ok_btn = await page.query_selector('button:has-text("OK"), button:has-text("ОК")')
            if ok_btn:
                await ok_btn.click()
                await asyncio.sleep(1)
        except Exception:
            pass

        # Ozon product cards
        cards = await page.query_selector_all('div[data-widget="tileGridDesktop"] .tile-root')
        print(f'Found {len(cards)} cards')

        results = []
        for card in cards[:10]:
            try:
                link_el = await card.query_selector('a[href*="/product/"]')
                href = await link_el.get_attribute('href') if link_el else 'N/A'
                full_url = f'https://ozon.ru{href}' if href.startswith('/') else href

                text = await card.inner_text()
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                price = next((line for line in lines if '₽' in line), '')
                name = next(
                    (line for line in lines
                     if any(kw in line.lower() for kw in ['ssd', 'тб', 'tb', 'kingston', 'digma', 'samsung', 'adata', 'netac', 'silicon', 'nvme', 'm.2'])),
                    lines[-3] if len(lines) > 2 else ''
                )

                results.append({
                    'name': name[:120],
                    'price': price,
                    'link': full_url,
                })
            except Exception as e:
                print('card error:', e)

        for r in results[:5]:
            print(f"- {r['price']} | {r['name']} | {r['link'][:60]}")

        await page.screenshot(path='ozon_search.png', full_page=False)
        print('screenshot saved: ozon_search.png')
        await context.close()


if __name__ == '__main__':
    asyncio.run(main())
