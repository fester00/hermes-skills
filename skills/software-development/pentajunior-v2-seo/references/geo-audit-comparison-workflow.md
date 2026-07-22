# Geo-audit comparison workflow for pentajunior-v2

## When to use

The user sends a JSON/CSV SEO audit file covering many URLs and asks "Сравни с текущим состоянием".

## Method

1. Build the project under the correct Node version:
   ```bash
   export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
   cd /home/natan/pentajunior-v2
   ./node_modules/.bin/tsc --noEmit
   rm -rf .next tsconfig.tsbuildinfo
   npm run build
   ```
2. Parse the audit JSON (path is usually `~/.hermes/cache/documents/*.json`).
3. Scan rendered HTML files under `.next/server/app/` for every public page, excluding admin routes and Next.js internal pages (`_not-found`, `_global-error`).
4. Extract these fields:
   - `<title>`
   - `<meta name="description" content="...">`
   - `<link rel="canonical" href="...">`
   - `<meta property="og:title" content="...">`
   - `<meta property="og:description" content="...">`
   - `<meta property="og:image" content="...">`
   - body `<h1>` and `<h2>` counts
5. Map build file paths to canonical URLs:
   - `index.html` → `https://pentajunior.ru/`
   - `{path}.html` → `https://pentajunior.ru/{path}`
6. Compare extracted values with the audit on a per-URL basis.

## What to report

- **Match count / difference count.** If all values match, the audit reflects the current build and is not stale.
- **URLs only in the audit** (old pages) or **only in the build** (new pages).
- **Real issues found in the audit data**, even when the audit matches the build:
  - titles longer than ~60 characters;
  - descriptions longer than ~160 characters;
  - canonical with trailing slash when the public URL has none;
  - empty `og:image`;
  - OG title/description that diverge significantly from the page meta or share homepage defaults.

## Prioritization

| Priority | Items |
|---|---|
| P1 | Empty og:image, wrong canonical, OG completely mismatched (e.g. `/policy` showing homepage OG) |
| P2 | Long title/description that need content edits and user approval |

## Common P1 fixes

### Empty og:image
Add explicit `openGraph.images` to the page's `metadata`:
```ts
openGraph: {
  images: [{ url: "/images/hero.webp", width: 1200, height: 630, alt: "Пента Юниор — FAQ" }],
}
```

### Trailing slash in canonical/OG URL
Replace `${baseUrl}/path/` with `${baseUrl}/path` in `alternates.canonical` and `openGraph.url`. Also update any JSON-LD `url` fields on the page.

### Homepage OG leaking onto a service page
Set explicit `openGraph.title`, `openGraph.description`, and `openGraph.images` in the page's `metadata` instead of letting the root layout defaults apply.

## Verification

After fixes:
```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
cd /home/natan/pentajunior-v2
./node_modules/.bin/tsc --noEmit
rm -rf .next tsconfig.tsbuildinfo
npm run build
```
Expected: `156/156 static pages`.

Then re-scan the affected pages and confirm the fields are correct.

## Reference implementation

A Python snippet for parsing the build output is in `references/geo-audit-parser.py`.
