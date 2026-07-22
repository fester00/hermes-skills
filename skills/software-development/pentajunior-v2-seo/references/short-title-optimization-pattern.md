# Short title optimization pattern for pentajunior-v2

## When to use

A geo/SEO audit shows service pages with `<title>` under ~40 characters. Very short titles waste snippet space and miss commercial keywords.

## Identification

From the audit JSON, filter URLs where `titleLength < 40`:
- `/news` — "Новинки и акции | Пента Юниор" (29 chars)
- `/info` — "Доставка и оплата | Пента Юниор" (31 chars)
- `/contacts` — "Контакты и партнёры | Пента Юниор" (33 chars)

## Goal

Lengthen each title to 50–60 characters by adding the core product keyword phrase naturally, without keyword stuffing.

## Pattern

| Page | Original title | Optimized title | Length |
|------|----------------|-----------------|--------|
| `/news` | Новинки и акции \| Пента Юниор | Новинки силиконовых материалов и акции — Пента Юниор | 52 |
| `/info` | Доставка и оплата \| Пента Юниор | Доставка и оплата силиконовых материалов — Пента Юниор | 54 |
| `/contacts` | Контакты и партнёры \| Пента Юниор | Контакты Пента Юниор: адрес, телефон и дилеры по России | 55 |

## Implementation

1. Read the page's `page.tsx`.
2. Extract title strings into constants:
   ```ts
   const pageTitle = "Доставка и оплата силиконовых материалов — Пента Юниор";
   const pageDescription = "...";
   ```
3. Use `pageTitle` consistently in:
   - `metadata.title`
   - `metadata.openGraph.title`
   - `metadata.twitter.title`
   - JSON-LD `WebPage` `name` if present
4. Keep H1 unchanged unless the user specifically asks to align H1 with the title.
5. Run build gate:
   ```bash
   ./node_modules/.bin/tsc --noEmit && rm -rf .next tsconfig.tsbuildinfo && npm run build
   ```
6. Verify the new title length in the rendered HTML.

## Pitfalls

- Do not exceed ~60 characters for service-page titles; category/product titles may be longer, but service pages should stay concise.
- Do not change H1 just to match the title unless the page's main topic genuinely changes.
- Do not stuff multiple unrelated keywords; one core phrase is enough.
- Keep OG and Twitter titles in sync with `<title>` to avoid mismatch warnings in future audits.
