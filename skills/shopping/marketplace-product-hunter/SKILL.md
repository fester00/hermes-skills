---
name: marketplace-product-hunter
category: shopping
description: >
  Hunt for the best price/quality products on Russian and international marketplaces.
  Handles cases where live scraping is blocked by bot protection and falls back to
  curated recommendations plus manual search instructions.
tags: [marketplace, shopping, price-comparison, product-research, e-commerce]
---

# Marketplace Product Hunter

## Trigger
Use this skill when the user asks to:
- Find the best product options in a category and budget on marketplaces.
- Compare price/quality across marketplaces.
- Recommend specific models to buy online.
- Track down where to buy a product cheapest.

## Workflow

### 1. Clarify the request
Before searching, confirm at least:
- Product category and exact specs (e.g., "SSD M.2 NVMe 1 TB").
- Budget currency and cap.
- Must-have features vs. nice-to-have.
- Preferred marketplaces or retailers (Yandex Market, Ozon, Wildberries, DNS, Citilink, etc.).
- Region / delivery constraints.

### 2. Set expectations
Tell the user that Russian marketplaces aggressively block automated access. Live prices may be unavailable. Promise only what you can verify.

### 3. Attempt data collection
Try, in order:
1. **Aggregators** (often less blocked than marketplaces): Price.ru, Hotline.ua, e-katalog.ru, Regard.
2. **Large retailers with public catalogs**: DNS, Citilink, KNS, Regard, 123.ru, Elmir.
3. **Marketplaces**: Yandex Market, Ozon, Wildberries.

Use delays between requests. If a site returns 403/429/captcha/empty, stop hammering it and note the block.

### 4. If blocked: fallback to curated recommendations
When live prices are inaccessible:
- List 3–5 well-known models that fit the budget and spec.
- Explain why each is a good candidate (controller, NAND type, reviews, brand reliability).
- Give exact search queries and manual verification steps for the user to check prices themselves.
- Be explicit about data freshness.

### 5. Format the answer
Present as a Markdown table:
| Model | Key specs | Why it fits | Where to look |
Include a short verdict ("best budget", "best reliability", "best speed", etc.).

## Pitfalls

- **Do not invent prices.** If you cannot verify a price, say so and give a typical range or "check current price".
- **Do not claim "available on X" without loading the page.** Bot protection can make pages look empty.
- **Do not assume older recommendations still cost the same.** SSD/tech prices move fast.
- **Hermes browser has no saved-profile support.** "Open with my profile" is not possible; use viewport/stealth only.
- **Avoid QLC vs TLC confusion.** For SSDs, note interface (PCIe 3/4), form factor (M.2 2280), and NAND type when relevant.

## Related skills
- `cross-platform-content-audit` — if the task is to audit or reconcile existing product content/prices across platforms, use that instead.
- `yandex-seo-optimization` — if the task is SEO for product pages, not shopping research.

## References
- `references/russian-marketplace-bot-landscape.md` — what blocks what and workarounds discovered in the field.
- `templates/product-hunt-report.md` — starter report format.
