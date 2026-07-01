# News page cards — markdown intro and currency symbols

The `/news` page lists new products and stock-action products via two card
components defined in `src/app/news/page.tsx` (`NewItemCard`) and
`src/components/UI/Cards/StockActionsCard.tsx` (`StockCard`).

Both card types show `template_data.intro`, which editors write with minimal
markdown (e.g. `**Юнисил® 9231** — ...`). If the intro is rendered as plain
text, the `**` markers stay visible and the bold emphasis is lost.

## Render intro with the project markdown helper

Use `MarkdownParagraph` from `src/lib/markdown.tsx` instead of a plain `<p>`:

```tsx
import { MarkdownParagraph } from "@/lib/markdown";

// NewItemCard in src/app/news/page.tsx
{product.template_data?.intro && (
  <div className="small text-muted mb-3">
    <MarkdownParagraph>{product.template_data.intro}</MarkdownParagraph>
  </div>
)}
```

```tsx
// StockCard in src/components/UI/Cards/StockActionsCard.tsx
{item.template_data.intro && (
  <div className="small text-muted">
    <MarkdownParagraph>{item.template_data.intro}</MarkdownParagraph>
  </div>
)}
```

`MarkdownParagraph` supports `**bold**`, line breaks, and simple lists. It does
not use `dangerouslySetInnerHTML`.

## Show currency next to the price

The related-products inline section and stock cards previously printed a bare
number. Use `product.price_currency` (`'RUB'` → `₽`, otherwise `$`):

```tsx
const currencySymbol = item.price_currency === 'USD' ? '$' : '₽';

<span className="product-related-price fw-medium">
  от {rp.price} {currencySymbol}
  {rp.price_unit && <span className="text-muted small">/{rp.price_unit}</span>}
</span>
```

Keep the existing `price_unit` suffix if it is present.

## Verification

After changing either card, run the build gate:

```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
cd /home/natan/pentajunior-v2
./node_modules/.bin/tsc --noEmit
rm -rf .next
npm run build
```

Then open `/news` and confirm markdown markers are rendered as bold and prices
include `₽` or `$`.
