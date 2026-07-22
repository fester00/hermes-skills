#!/usr/bin/env python3
"""
Generic anti-bot site scraper starter using Playwright + persistent Chrome profile + Xvfb.

Copy this file, replace SITE_URL and SELECTORS for the target site, and run:

    cd /mnt/data/natan-storage/playwright-search
    source .venv/bin/activate
    xvfb-run -a --server-args="-screen 0 1920x1080x24" python my_site.py

"""

import asyncio
import json
from playwright.async_api import async_playwright

PROFILE_DIR = "/mnt/data/natan-storage/.chrome-vk-profile"
VIEWPORT = {"width": 1920, "height": 1080}
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

SITE_URL = "https://example.com/search?q="
CARD_SELECTOR = "article.result"  # TODO: replace with real card selector
TITLE_SELECTOR = "h2"
PRICE_SELECTOR = ".price"
LINK_SELECTOR = "a"


async def scrape(query: str, limit: int = 5) -> list[dict]:
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            viewport=VIEWPORT,
            user_agent=USER_AGENT,
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto(SITE_URL + query.replace(" ", "+"), wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)

        cards = await page.query_selector_all(CARD_SELECTOR)
        results = []
        for card in cards[:limit]:
            try:
                title_el = await card.query_selector(TITLE_SELECTOR)
                price_el = await card.query_selector(PRICE_SELECTOR)
                link_el = await card.query_selector(LINK_SELECTOR)

                title = await title_el.inner_text() if title_el else ""
                price = await price_el.inner_text() if price_el else ""
                href = await link_el.get_attribute("href") if link_el else ""
                url = href if href.startswith("http") else f"https://example.com{href}"

                results.append({"title": title.strip(), "price": price.strip(), "url": url})
            except Exception:
                continue

        await context.close()
        return results


async def main():
    results = await scrape("QUERY", limit=5)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
