# SEO geo-audit comparison — pentajunior-v2 (2026-07-01)

## Context
The user received a JSON SEO audit (`seo-geo-audit-2026-07-01.json`) covering 125 public URLs and asked: "Сравни с текущим состоянием".

## Methodology
1. Build the current site: `tsc --noEmit && rm -rf .next tsconfig.tsbuildinfo && npm run build`.
2. Parse rendered HTML from `.next/server/app/` for every public page (excluding admin routes and Next.js internal pages like `_not-found` / `_global-error`).
3. Extract `<title>`, `<meta name="description">`, `<link rel="canonical">`, `og:title`, `og:description`, `og:image`, and body `<h1>`/`<h2>` counts.
4. Compare extracted values with the audit on a per-URL basis.

## Result
- **125 URLs** in the audit match the current build.
- **0 differences** in title, description, canonical, OG tags, H1 count, or H2 count.
- The audit reflects the current state of the site after recent fixes (visible product H1, OG images per category/subcategory).

This means the audit is not from an older version; it is already aligned with the latest deployed code.

## Real problems found by the audit (not differences, but existing issues)

### 1. Long titles (>60 chars)
- **103 of 125 URLs** have titles longer than 60 characters.
- Examples:
  - `/` — 84 chars
  - `/production/silikon-dlya-zalivki-form` — 79 chars
  - `/production/production-release` — 74 chars
- Impact: search engines may truncate the title in SERP.
- Decision needed: the project policy (see SKILL.md § meta_title length policy) prefers meaning over strict length. Do not shorten without user approval and a CTR testing plan.

### 2. Long descriptions (>160 chars)
- **10 URLs**:
  - `/`
  - `/info`
  - `/price`
  - `/info/faq`
  - Several product pages (e.g. `silagerm-1041`)
- Frontend already truncates descriptions at 160 chars, but the source DB values are longer.

### 3. Canonical trailing slash mismatch
- `/contacts` → canonical is `/contacts/`
- `/info` → canonical is `/info/`
- Other pages use canonical without trailing slash. This is a minor inconsistency that may dilute signals if sitemap uses one convention and canonical another.

### 4. Empty og:image
- `/info/faq` has `ogImage: ""`.
- Should fall back to `/images/hero.webp` like other pages.

### 5. OG / meta mismatches
- **11 pages** where `og:title` or `og:description` does not match the corresponding meta tag. Some are intentional (different OG copy), but `/policy` is completely wrong — it shares the homepage OG.

| URL | Issue |
|-----|-------|
| `/production` | ogTitle ≠ title, ogDescription ≠ description |
| `/contacts` | ogDescription ≠ description |
| `/news` | ogDescription ≠ description |
| `/info` | ogTitle ≠ title, ogDescription ≠ description |
| `/price` | ogDescription ≠ description |
| `/policy` | ogTitle and ogDescription are homepage defaults |
| `/info/faq` | ogTitle ≠ title, ogImage empty |

## Recommended fixes (by priority)

### P1 — technical SEO quick wins
1. Add fallback `og:image` for `/info/faq`.
2. Fix `/policy` OG to match the page content.
3. Normalize canonical for `/contacts` and `/info` to match the URL without trailing slash.

### P2 — content
4. Shorten titles where truncation hurts readability (requires user approval).
5. Shorten descriptions to ≤160 chars at the DB level.

## Verification after fixes
```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
cd /home/natan/pentajunior-v2
./node_modules/.bin/tsc --noEmit
rm -rf .next tsconfig.tsbuildinfo
npm run build
```
Expected: 156/156 static pages.

## Files
- Audit JSON: `/home/natan/.hermes/cache/documents/doc_3245245ad180_seo-geo-audit-2026-07-01.json`
- Build output: `/home/natan/pentajunior-v2/.next/server/app/`
