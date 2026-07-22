> # TDD Regression Discovery for Extracted Legacy Helpers

## Symptom

A TypeScript build passes and the application appears to work, but a helper
extracted from a page into `lib/*.ts` silently mishandles real production data.

Example from `pentajunior-v2/src/lib/pricing.ts`:

```ts
export function extractPrice(priceString: string): string {
  if (!priceString) return "0";
  const normalized = priceString.replace(/\s/g, "").replace(",", ".");
  const match = normalized.match(/[\d.]+/);
  return match ? match[0] : "0";
}
```

The regex `[\d.]+` matched a lone dot for formatted prices such as
`"1 250,50 ₽"`, returning `"0"` instead of `"1250.50"`. The build passed and
the original page rendered, but JSON-LD `offers` prices were wrong.

## Root Cause

When a function lives inline in a page file, it is exercised only by the data
paths that page happens to hit. Extracting it to a shared `lib/*.ts` file
exposes it to new callers and makes it a permanent contract — but the original
implementation is often shaped only by the one input it was originally written
for. A loose regex or partial string handling may go unnoticed until tests or
new data exercise edge cases.

## Fix

After extraction, write unit tests for the real input shapes from the database
and UI before trusting the existing behavior:

```ts
// src/lib/pricing.test.ts
import { describe, it, expect } from 'vitest';
import { extractPrice } from './pricing';

describe('extractPrice', () => {
  it('extracts numeric value from a formatted price string', () => {
    expect(extractPrice('1 250,50 ₽')).toBe('1250.50');
  });

  it('returns "0" for non-numeric values', () => {
    expect(extractPrice('по запросу')).toBe('0');
  });

  it('handles simple integers', () => {
    expect(extractPrice('1000')).toBe('1000');
  });
});
```

The corrected regex should match an integer or decimal number, not any
sequence of digits and dots:

```ts
const match = normalized.match(/\d+(?:\.\d+)?/);
```

## Decision Tree

| Situation | Action |
|-----------|--------|
| Helper is new / trivial | Still write tests for expected production inputs |
| Helper extracted from page code | Write tests for the exact shapes seen in DB and UI |
| Helper has any regex / string parsing | Add adversarial cases: spaces, commas, currency signs, empty strings |
| Helper has no observable production inputs yet | At minimum write a contract test against the current caller |

## Verification

```bash
npm run typecheck
npm test
npm run build
```

## Communication Pattern

Tell the user:

> При вынесении хелпера нашёлся скрытый баг: regex ловил отдельную точку вместо
> числа. Дописал unit-тесты на реальные форматы цен — теперь проходят.

## See Also

- `code-quality-gates` Gate 1: Test-Driven Development
- `code-quality-gates` Gate 3: Pre-Commit Verification
