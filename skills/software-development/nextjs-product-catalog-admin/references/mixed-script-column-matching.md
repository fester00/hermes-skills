# Matching current-product columns in mixed-script comparison tables

Problem arises in Next.js + SQLite projects that render spec/comparison tables.
Product IDs are URL-friendly ASCII (`unicast-6v`, `unicast-trans`), but the
matching column header in the database is written in Cyrillic or uppercase
(`6В`, `TRANS`). A naive `productId.split('-').pop() === col` check fails even
after lower-casing because the scripts differ (`v` vs `В`).

## Reproduction recipe

- Product row in DB: `id = 'unicast-6v'`, `spec_table_id = 'unicast-xxx'`
- Spec table JSON: `columns = ["МАРКА", "6В", "4", "TRANS"]`
- Old matching code:
  ```tsx
  const productMark = productId.split('-').pop();      // "6v"
  const isCurrent = (col: string) => col.toLowerCase() === productMark.toLowerCase();
  ```
- Result: `"6В".toLowerCase()` → `"6в"` ≠ `"6v"`, so the column is **not**
  highlighted.

## Durable fix: a `normalize()` helper

Implement a small helper that:

1. lower-cases the string;
2. strips spaces, hyphens, and trademark symbols (`®`, `™`, `©`);
3. transliterates Latin look-alikes that have Cyrillic twins commonly used in
   product names (`a→а`, `b→б`, `c→ц`, `e→е`, `k→к`, `m→м`, `o→о`, `p→р`,
   `t→т`, `v→в`, `x→х`, `y→у`).

Then compare the normalized product mark with the normalized column header:

```tsx
const normalize = (str: string | null | undefined) => {
  if (!str) return '';
  return str
    .toLowerCase()
    .replace(/[\s\-®™©]/g, '')
    .replace(/[a-z]/g, (ch) => {
      const map: Record<string, string> = {
        a: 'а', b: 'б', c: 'ц', e: 'е', k: 'к', m: 'м',
        o: 'о', p: 'р', t: 'т', v: 'в', x: 'х', y: 'у',
      };
      return map[ch] ?? ch;
    });
};
```

Keep exact case-insensitive suffix matching as the fast path, then fall back
to normalized equality, then to substring containment in the column header.

## Pitfalls

- **Incomplete transliteration map.** A subagent once added the helper but
  forgot `v→в`; the page still failed to highlight `unicast-6v`. After a local
  dev-server restart, the missing mapping was found. Verify the full set of
  product ID suffixes against column headers in the database, not just one
  case.
- **Stale dev server cache.** When a fix does not appear in the browser, the
  running `next dev` server may still serve a previous build. Kill the old
  process and restart it on the correct port before concluding the fix failed.
- **Reference-first design rule still applies.** When porting the table style
  from an existing project, read the reference component source first and
  reuse the same Bootstrap utility classes before inventing custom CSS.
