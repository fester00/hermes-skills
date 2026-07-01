# VK ↔ Website Audit Example — Pentajunior

Real transcript from 2026-06-06.

## Sources
- **VK:** `https://vk.com/pentajunior` (community "Пента Юниор", 54 followers)
- **Website:** `https://pentajunior.ru/price` (CakePHP, pricelist table)

## Method
1. Browser navigated to vk.com/pentajunior → "Товары" → "Показать все" → scrolled until all 72 products loaded.
2. Browser navigated to pentajunior.ru/price → scrolled through full pricelist table (56 rows).
3. Checked auxiliary product pages (e.g. `/silikony-produkciya/silikonovye-kovriki`) for items not in pricelist.

## Results Summary

### Exact Matches (~90% of items)
All matched: Вс-М, Si-M, КС-М, Ткань ТСМ-1, ВГО-1 (1–24 шт), ПМС-50/100/200/350/400/1000, Пента-107/111/119/126/150/219/811/870, ПАСТА КПД, КВ–3/10Э, Эмульсия КЭ-60, Пентэласт-1100/1101/1110/1130/1143/711/712, Пенталюкс, ПЕНТАКЛИН, ПЕНТАКЛЕЩ, пасты/кремы, Люминофор, Юнисил 9641/9629/9628/9512/9610.

### Discrepancies Found
| Product | VK Price | Site Price | Delta |
|---------|----------|-----------|-------|
| ПМС-5 (от 5 кг) | 550 ₽ | 650 ₽/кг | -100 ₽ |
| ПМС-5 (от 200 кг) | 520 ₽ | 620 ₽/кг | -100 ₽ |
| ПМС-10 (от 5 кг) | 550 ₽ | 590 ₽/кг | -40 ₽ |
| ПМС-10 (от 200 кг) | 520 ₽ | 560 ₽/кг | -40 ₽ |
| ПМС-20 (от 5 кг) | 450 ₽ | 550 ₽/кг | -100 ₽ |
| ПМС-20 (от 200 кг) | 420 ₽ | 520 ₽/кг | -100 ₽ |

**Root cause:** VK prices for low-viscosity PMS oils were systematically understated.

### VK-Only Items
- ВГО-1 (≥25 шт) — 1 050 ₽ (site only lists 1–24 шt tier)
- Юнисил 9730 (от 1 кг) — 5 400 ₽ (not on site pricelist)
- Пентэласт-1159 (≥25 шт) — 800 ₽ (site only lists 1–24 шt tier)

### Website-Only Items
- Юникаст 6В / 4 / 6W / Trans (1 300–1 980 ₽)
- Юнисил bulk packs 5.2 kg / 20.8 kg (4 420–18 930 ₽)
- Silicone rubber products (price on request)

## Key Lessons
- VK slug was `pentajunior`, not `penta-junior` as user initially thought.
- Pricelist URL was `/price`, not `/prayc` (user typo).
- Tiered pricing is the #1 discrepancy vector — capture ALL tiers.
- Subagent was effective for this scale; manual browser would have been too slow.
