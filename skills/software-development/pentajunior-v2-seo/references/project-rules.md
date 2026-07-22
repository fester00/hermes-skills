# Project rules for pentajunior-v2

- **Path**: `/home/natan/pentajunior-v2`
- **Node.js**: v24.13.1 via nvm.
- **Ports**: legacy pentajunior on 3000 (PM2); v2 on 3001.
- **Routing**: strict 3-level `/production/[category]/[subcategory]/[product]`.
- **Build gate**: `tsc --noEmit && npm run build` must pass before claiming done.
- **Meta title format in DB**: ends with `| Пента Юниор`; code must not append brand unconditionally.
- **DB backups**: create `pentajunior.db.seo-<cat>-backup-<YYYYMMDD-HHMMSS>` before SEO writes.
- **Git workflow**: `git pull` before edits; commit and push `master` after successful build.
- **JSON-LD audit before build**: run `python3 /home/natan/.hermes/skills/software-development/pentajunior-v2-seo/references/seo_jsonld_audit.py` to catch empty meta, bad prices, missing images/logo before build gate.
- **Final meta verification before commit**: after all SEO edits, run a script or quick check that enforces:
  - `meta_title` ≤ 70 symbols;
  - `meta_description` ≤ 170 symbols;
  - no price mentions (`₽/`, `цена`) in `meta_description`;
  - no forbidden phrases (`материал дышит`, `кожа дышит`, `разведение`, `разводится`) in `meta_description`;
  - no producer claim (`от производителя`) in `meta_title`/`meta_description`/`seo_text`.
  See `references/global-seo-final-check.py` and `references/seo-description-forbidden-phrases-replacements.md`.
- **Admin `seo_text` save**: when category edits don't persist, verify `PUT /api/admin/categories/[id]` and `POST /api/admin/categories` include `seo_text` in the SQL statement; add it if missing.
