# Pentajunior → Pentajunior-v2 category migration decisions

Concrete field mappings chosen while migrating the legacy `products.tsx` `application` blocks into `pentajunior-v2` `template_data`.
Use this as a reference when resuming the remaining categories or when migrating similar projects.

## 1. Силикон для изготовления и заливки форм (`silikonovye-i-poliuretanovye-kompaundy`, id 1)

- v1 `application` contained a short free-form paragraph for each product.
- v1 product page also rendered a **shared** `SectionUnisilApplication` with fixed instructions (surface prep, mixing, degassing, safety).
- v2 approach:
  - Keep the per-product short `application` paragraph as `application` in `template_data` (renders as "Применение" intro).
  - Add the **same reusable instructional block** to every product in the category:
    - `surface_prep`
    - `mixing_steps`
    - `degassing`
    - `important_note`
    - `safety`
  - This fills the `ApplicationSection` in `UniversalTemplate`.
- Products affected: 17 (`luminofor`, `unicast-6v`, `unicast-trans`, `uniflex-9940`, `unisil-*` family).
- Outcome: each product page now has a full "Применение" section.

## 2. Силиконовые и восковые разделительные смазки (`production-release`, id 2)

- v1 `application` mixed **areas of use** (`Область применения`) with **method** (`Способ нанесения`) and **warnings** (`Важно`).
- v2 mapping:
  - `Область применения` list → `applications`
  - `Способ нанесения` prose → `method`
  - `Важно` warning → `important_note`
  - clear legacy `application` field
- Products affected: 7 (`si-m-aero`, `ks-m-aero`, `vs-m-aero`, `penta-107`, `penta-126p`, `penta-150`, `emulsion-ke`).
- Pitfall found: first attempt stored raw HTML, which `MarkdownParagraph` escaped and displayed as tags. Fixed by converting to Markdown first.

## 3. Масла ПМС (`pms`, id 3)

- v1 `application` was a clean list of areas of use.
- v2 mapping:
  - All list items → `applications`
  - clear legacy `application`
- Products affected: 9 (`pms-5`, `pms-10`, `pms-20`, `pms-50`, `pms-100`, `pms-200`, `pms-350`, `pms-400`, `pms-1000`).
- `intro`/`body` were already populated in v2, so only `applications` was backfilled.

## 4. Высокотемпературные смазки (`production-grease`, id 4)

- v1 `application` was a list of areas of use.
- v2 mapping:
  - All list items → `applications`
  - clear legacy `application`
  - strip trailing `Область применения {Name}:` from `body`
- Products affected: 2 (`penta-200`, `penta-219`).
- Pitfall found: `application_industrial` had been populated with the same list as `applications`, causing `ApplicationAreasSection` to render the list twice (general + "В промышленности"). Removed the duplicate `application_industrial`.

## 5. Силиконовые герметики (`production-sealant`, id 5)

- v1 `application` was a clean list of areas of use.
- v2 mapping:
  - All list items → `applications`
  - clear legacy `application`
  - strip trailing application heading from `body`
- Products affected: 7 (`pentelast-1100`, `pentelast-1101`, `pentelast-1110`, `pentelast-1130`, `pentelast-1143`, `pentelast-1159`, `vgo-1`).
- Pitfall found: the same list had also been stored as `surfaces` (likely from an earlier migration). `DescriptionSection` rendered it as "Применимые поверхности" while `ApplicationAreasSection` rendered it again as "Области применения". Deleted `surfaces` to avoid duplication.

## 6. Силиконовые коврики ТСМ-1 (`silikonovye-kovriki-tsm`, id 6)

- v1 `application` had explicit **"В промышленности"** and **"Бытовое"** subsections.
- v2 mapping:
  - "В промышленности" list → `application_industrial`
  - "Бытовое" list → `application_domestic`
  - do **not** create a general `applications` array
  - clear legacy `application`
- Product affected: 1 (`tsm-1`).
- Pitfall found: creating a general `applications` array with the domestic items caused the list to render three times (general, industrial, domestic). Removing `applications` fixed it.

## 7. Изделия из силиконовых резин (`izdelija-iz-silikonovyh-rezin`, id 7)

- v2 already had `application` as a plain-text newline list.
- v2 mapping:
  - Convert the plain-text list → `applications` array
  - clear legacy `application`
- Products affected: 6 (`silicon-sheet`, `silicon-sheet-porous`, `silicon-sheet-fabric`, `silicon-tube`, `silicon-hose-reinforced`, `silicon-cord`).

## 8. Гидрофобизаторы (`production-waterproof`, id 8)

- v1 `application` was instructions (`Способы применения`, numbered steps, warnings, recommendation), not areas of use.
- v2 mapping:
  - bullet/numbered list items → `recommendations`
  - `Рекомендация` paragraph → `method`
  - `Важно` / `Внимание` → `important_note`
  - do **not** create `applications`
  - clear legacy `application`
  - strip trailing `Способ применения {Name}:` / `Способы применения {Name}:` from `body`
- Products affected: 2 (`penta-811`, `penta-870`).

## Remaining categories (not yet migrated)

9. Средства защиты рук (`production-hand-care`, id 9)
10. Кремнийорганические компаунды для электроники (`production-electrosealant`, id 10)
11. Уход за обувью (`production-shoes`, id 11)
12. СОЖ (`smazochno-ohlazhdayushhie-zhidkosti`, id 12)

## Reusable process

For each remaining category:

1. Extract v1 `application` JSX for the category.
2. Inspect existing v2 `template_data` for each product to see which fields are missing.
3. Decide if the v1 block is:
   - **areas of use** → map to `applications` / `application_industrial` / `application_domestic`
   - **instructions/how-to** → map to `recommendations` / `method` / `important_note`
   - **shared category instructions** → map to `surface_prep` / `mixing_steps` / `degassing` / `safety` / `important_note`
4. Convert HTML/JSX to Markdown before storing.
5. Clear the legacy `application` field.
6. Clean `body` of trailing application-heading fragments.
7. Check for duplicate `surfaces`, `application_industrial`, or `application_domestic`.
8. Run `npx tsc --noEmit && npm run build`.
9. Commit `pentajunior.db` with a category-specific message and push.
10. Kill and restart `next start` to serve the new build.
11. Verify visually in browser.

## Commit messages used

```text
data(products): добавить инструкционные блоки Применения для категории 1
data(products): перенести секцию Применение для категории разделительных смазок
data(products): перенести области применения для масел ПМС
data(products): перенести области применения для высокотемпературных смазок
data(products): перенести области применения для силиконовых герметиков
data(products): перенести область применения для силиконового коврика ТСМ-1
data(products): структурировать application для изделий из силиконовых резин
data(products): перенести способы применения для гидрофобизаторов
```

All commits were followed by `git pull --rebase origin master && git push origin master`.
