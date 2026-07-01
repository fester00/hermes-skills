# Admin product slug/id generation in pentajunior-v2

When creating a product through the admin panel, `POST /api/admin/products` generates the product `id` from `body.name`. The original implementation stripped only non-ASCII characters, which turned Cyrillic-plus-number names like **«Юнисил® 9220»** into broken IDs such as `-9220`.

## Root cause

Original code in `src/app/api/admin/products/route.ts`:

```ts
const id = body.name?.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '') || Date.now().toString();
```

For `Юнисил® 9220`:
1. `toLowerCase()` → `юнисил® 9220`
2. `replace(/\s+/g, '-')` → `юнисил®-9220`
3. `replace(/[^a-z0-9-]/g, '')` → deletes Cyrillic and `®`, leaving `-9220`

## Known-good fix

Add transliteration and slug normalization:

```ts
function transliterate(str: string): string {
  const map: Record<string, string> = {
    а: 'a', б: 'b', в: 'v', г: 'g', д: 'd', е: 'e', ё: 'yo', ж: 'zh', з: 'z', и: 'i',
    й: 'y', к: 'k', л: 'l', м: 'm', н: 'n', о: 'o', п: 'p', р: 'r', с: 's', т: 't',
    у: 'u', ф: 'f', х: 'h', ц: 'ts', ч: 'ch', ш: 'sh', щ: 'sch', ъ: '', ы: 'y', ь: '',
    э: 'e', ю: 'yu', я: 'ya',
  };
  return str
    .toLowerCase()
    .split('')
    .map((ch) => map[ch] || ch)
    .join('');
}

function slugify(name: string): string {
  return transliterate(name)
    .replace(/[^a-z0-9\s-]/g, '')   // remove ®, ™, ©, etc.
    .trim()
    .replace(/\s+/g, '-')            // spaces → hyphens
    .replace(/-+/g, '-')             // collapse multiple hyphens
    .replace(/^-|-$/g, '');          // trim leading/trailing hyphens
}

// In POST:
const id = slugify(body.name || '') || Date.now().toString();
```

For `Юнисил® 9220` this produces `yunisil-9220`.

## Scope

- Affects only **new** products created via the admin panel (`POST /api/admin/products`).
- `PUT /api/admin/products/[id]` keeps the existing `id` unchanged — good, because changing IDs breaks URLs and references.
- If a product already has a broken ID (e.g. `-9220`), fix it with a targeted SQL `UPDATE` only after checking all references: `products.id`, blog article `{product:ID}` markers, related products lists, JSON-LD URLs, and any hardcoded redirects.

## Verification

After editing the API route, run the build gate:

```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
cd /home/natan/pentajunior-v2
./node_modules/.bin/tsc --noEmit
rm -rf .next
npm run build
```

Then create a test product with a Cyrillic-plus-number name in the admin panel and confirm the generated `id` is readable and does not start with `-`.

## Related

- For the broader admin API pitfalls, see `references/admin-api-pitfalls.md`.
