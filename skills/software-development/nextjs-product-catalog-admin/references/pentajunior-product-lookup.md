# Pentajunior Product Lookup — Cross-Version Data Archaeology

## The Multi-Version Landscape

The pentajunior project exists in 3+ versions. When a product is missing from the primary database, search the others:

| Version | Path | Format | Product Count | Notes |
|---------|------|--------|--------------|-------|
| **v2 (active)** | `~/pentajunior-v2` | SQLite (`pentajunior.db`) | 57 products | Primary DB with `template_type`, `template_data` |
| **workspace** | `~/workspace/pentajunior` | Hardcoded TSX (`src/data/products.tsx`) | ~60+ products | ReactNode descriptions, specTableId |
| **v3** | `~/pentajunior-v3` | JSON (`src/data/products.json`) | Unknown | Different schema, possibly newer data |
| **VK exports** | `~/pentajunior_vk_*.xml` | YML catalog | Subset | Price tiers, packaging variants |

## Naming Variations to Handle

The user uses these interchangeably — search with both:
- **Пенталаст** vs **Пентэласт** (with "э") — e.g. `Пенталаст-1159` is actually `Пентэласт-1159` in the DB
- **Пенталюкс** vs **Пента-Люкс** vs **Пента®-116**

## Lookup Protocol

When user asks about a product and it's not found in v2 DB:

1. **Search v2 DB first** (Node 24 + better-sqlite3):
   ```bash
   source ~/.nvm/nvm.sh && nvm use 24.13.1
   node -e "const db = require('better-sqlite3')('./pentajunior.db'); ..."
   ```
   Use `LIKE '%partial%'` for fuzzy matching.

2. **Fallback: workspace TSX** (`~/workspace/pentajunior/src/data/products.tsx`):
   ```bash
   grep -n "ProductName" ~/workspace/pentajunior/src/data/products.tsx
   ```
   Extract `description`, `application`, `features`, `price`, `pack` from the TSX object.

3. **Fallback: v3 JSON** (`~/pentajunior-v3/src/data/products.json`):
   ```bash
   grep -n "ProductName" ~/pentajunior-v3/src/data/products.json
   ```

4. **Fallback: VK YML exports** (`~/pentajunior_vk_v2.xml`, `~/pentajunior_vk_v3.xml`):
   ```bash
   grep -n -A 10 "ProductName" ~/pentajunior_vk_v*.xml
   ```
   Good for pricing tiers and packaging data.

## Known Gaps (as of 2026-06-13)

These products exist in workspace/v3 but are **missing from v2 DB**:
- `Пентэласт-1161` — not in v2 DB, not in workspace TSX
- `Пентэласт-1162` — not in v2 DB, not in workspace TSX  
- `Пентэласт-1165` — not in v2 DB, not in workspace TSX

When user asks about these, they likely exist in paper docs or VK. Ask for source file.

## Migration Rule

If data is found in workspace TSX but missing from v2 DB, migrate it:
1. Extract scalar fields from TSX object
2. Parse `description`/`application` JSX into `template_data` JSON
3. Determine `template_type` from `categoryId` → category slug mapping
4. INSERT into `pentajunior.db`
5. Verify with `npx tsc --noEmit && npm run build`
6. Commit + push

## Quick Verification Query

```bash
cd ~/pentajunior-v2 && source ~/.nvm/nvm.sh && nvm use 24.13.1 && node -e "
const db = require('./node_modules/better-sqlite3')('./pentajunior.db');
const cols = db.prepare('PRAGMA table_info(products)').all().map(c => c.name);
const count = db.prepare('SELECT COUNT(*) as n FROM products').get().n;
console.log('Columns:', cols);
console.log('Products:', count);
"
```
