# SEO session: Обработка поверхности и пропитки — 2026-06-22

Category: `/production/obrabotka-poverhnosti-propitki`

## Applied metadata

### Category
- **title**: `Гидрофобизатор для бетона, кирпича и плитки — купить от производителя | Пента Юниор`
- **meta_description**: `Кремнийорганические гидрофобизаторы Пента-811 и смывка высолов Пента-870. Защита бетона, кирпича, камня, плитки от влаги. Эффект 10+ лет. Оптовые цены.`
- **page_description**: `Кремнийорганические пропитки для защиты бетона, кирпича, камня и тротуарной плитки от влаги, высолов и мороза. Производство «Пента Юниор».`
- **seo_text**: updated with H3 sections:
  - "Для каких поверхностей подходит гидрофобизатор Пента-811?"
  - "Высолы на кирпиче и бетоне — как убрать?"

### Subcategories
- **Гидрофобизаторы**: title/description/page_description with Пента-811 and surface list.
- **Смывки-очистители**: title/description/page_description with Пента-870.

### Products
- **penta-811**: title/description/keywords covering гидрофобизатор for бетон/кирпич/плитка/камень.
- **penta-870**: title/description/keywords covering смывка высолов / средство для удаления высолов.

## Key decisions
- SEO-text from the brief was inserted into `categories.seo_text` as additional H3 sections, while `page_description` remained the short subtitle.
- `meta_description` trimmed to ≤160 chars by removing redundant location/brand phrases.

## Verification
- `tsc --noEmit` passed.
- `npm run build` passed (146 pages).
- Committed and pushed to `master`.
