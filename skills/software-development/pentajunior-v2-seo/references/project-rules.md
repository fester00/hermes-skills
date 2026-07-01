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
- **Admin `seo_text` save**: when category edits don't persist, verify `PUT /api/admin/categories/[id]` and `POST /api/admin/categories` include `seo_text` in the SQL statement; add it if missing.
