---
name: cross-platform-content-audit
description: Audit and reconcile content, prices, and products between a company's social media storefront (VK, Instagram, etc.) and their main website/catalog.
category: productivity
version: 1.0
---

# Cross-Platform Content Audit

Audit consistency between a company's social media presence (VK community products, Instagram shop, etc.) and their main website catalog/pricelist.

## Trigger
- User asks to compare prices/products between social media and website
- User wants to check if VK shop matches website catalog
- Content sync verification across platforms
- "Сверь цены" / "Проверь, всё ли совпадает" запросы

## Steps

1. **Identify sources**: Confirm the social media page URL and website URL from the user. VK slugs often differ from expected (`pentajunior` vs `penta-junior`).
2. **Gather social media data**: Use browser tools to navigate the social media storefront.
   - For VK: navigate to `vk.com/<slug>` → click **"Товары"** (Products) tab → click **"Показать все"** if available.
   - Scrape all visible products with names and prices.
   - Scroll and paginate to ensure completeness. VK uses lazy loading for product grids.
3. **Gather website data**: Navigate to the website's catalog or pricelist.
   - Common paths: `/price`, `/prices`, `/pricelist`, `/catalog`, `/products`.
   - The URL may differ from user expectation (e.g., `/prayc` → 404, actual path `/price`).
   - Scrape the full table/list. Scroll down if table is long.
4. **Normalize product names**: Strip whitespace, unify units (шт., кг, л, м), handle tiered pricing tiers.
5. **Compare and categorize**:
   - ✅ **Exact matches**: same product, same price
   - ⚠️ **Price discrepancies**: same product, different price (flag magnitude and direction)
   - 🛒 **Social-only**: exists on social media but not on website
   - 📦 **Website-only**: exists on website but not on social media
6. **Report**: Present findings in markdown tables with clear, actionable recommendations.

## Pitfalls

- **VK guest limitations**: VK allows limited product viewing for guests. Some items may be hidden. If critical data is missing, inform the user that VK admin access may be needed.
- **Chrome profile check**: On this user's system, Chrome may already run with profile `~/.chrome-vk-profile` (per `russian-retail-search` skill). If VK still shows "Войти" buttons, the VK session has expired — do NOT ask for password. Fall back to VK API token or YML feed.
- **Pricelist URL guessing**: The pricelist URL may not be obvious. Try `/price`, `/prices`, `/pricelist`, `/catalog`, `/products`. Check the main navigation if these fail. User may typo the path (e.g., `/prayc` → 404, actual is `/price`).
- **Tiered pricing blindness**: Products often have multiple price tiers (1–24 шт, ≥25 шт, от 5 кг, от 200 кг). Capture ALL tiers. Missing tiers are the #1 discrepancy source.
- **Naming variations**: VK and website may use slightly different names for the same product. Do fuzzy matching.
- **Unit confusion**: Ensure units match (₽/шт vs ₽/кг). VK may show per-unit while website shows per-kg.
- **Lazy loading**: Both VK and modern websites load content on scroll. Scroll repeatedly and re-scan to ensure completeness.
- **VK slug mismatch**: The short URL slug on VK often differs from the domain name. Search VK if direct slug guess fails.

## Subagent Delegation

For complex audits (>20 products or >2 platforms), delegate to a subagent with:
- Full browser toolset enabled
- Explicit instructions: scroll until no new items appear
- Clear reporting format (markdown tables with four categories)
- Timeout: 1800s for heavy DOM scraping

## References

- `references/vk-website-audit-example.md` — Real audit transcript: Pentajunior VK vs pentajunior.ru price reconciliation