# Project rules for pentajunior-v2

- **Path**: `/home/natan/pentajunior-v2`
- **Node.js**: v24.13.1 via nvm.
- **Ports**: the PM2 process `pentajunior-v2` serves on `127.0.0.1:3000` (nginx `proxy_pass` → 3000). For a temporary preview of a local build use a spare port (e.g. `next start --port 3001`); do not touch the PM2 process.
- **Routing**: strict 3-level `/production/[category]/[subcategory]/[product]`.
- **Build gate**: `tsc --noEmit && npm run build` must pass before claiming done.
  - If `next/font/google` fails with `Module not found: Can't resolve '@vercel/turbopack-next/internal/font/google/font'`, the host cannot reach Google Fonts. Comment out `import { Inter }`, the `const inter` declaration, and `className={inter.variable}` in `src/app/layout.tsx` to build behind the firewall. Re-enable Inter after deployment unless the user approves a system font stack.
- **Static meta sources**: `src/app/syte-config.ts` `description` feeds `layout.tsx` metadata, OpenGraph, Twitter, and JSON-LD `Organization.description` — check it for producer wording («производство», «от производителя») too.
- **Meta title format in DB**: ends with `| Пента Юниор`; code must not append brand unconditionally.
- **DB backups**: create `pentajunior.db.seo-<cat>-backup-<YYYYMMDD-HHMMSS>` before SEO writes.
- **Git workflow**: `git pull` before edits; commit and push `master` after successful build.
  - If `git fetch`/`git pull` hangs on this host, verify local sync state before assuming the repo is outdated:
    ```bash
    cd ~/pentajunior-v2
    git rev-parse HEAD origin/master
    git diff HEAD origin/master --stat
    ```
    Report the result to the user and continue only when the actual state is known.
- **Deploy script**: the project root has no `deploy.sh`; use `~/deploy.sh`. Never run it without explicit user approval (the deploy command is `задеплой`).
- **Push command**: `git -c http.proxy= -c https.proxy= -c http.version=HTTP/1.1 push origin master` — GitHub HTTPS on this host only tolerates the proxy in this form (same flags as in `deploy.sh`).
- **A rebuild does not publish**: writing `.next` while the PM2 process runs leaves the live site on the old build — changes go live only after `pm2 reload` (i.e. deploy). Verify prod with `curl`/Python, never with the local build alone.
- **Visual check of a local build**: start a spare preview (`next start --port 3001`) and screenshot with headless Chromium via Playwright (`PLAYWRIGHT_BROWSERS_PATH=/mnt/data/natan-storage/playwright-browsers node shot.js`, `chromium.launch({args:['--no-sandbox']})`). The managed browser helper refuses localhost URLs, so use this route for local pages; kill the preview and its forked `next-server` child when done.
- **JSON-LD audit before build**: run `python3 /home/natan/.hermes/skills/software-development/pentajunior-v2-seo/references/seo_jsonld_audit.py` to catch empty meta, bad prices, missing images/logo before build gate.
- **Final meta verification before commit**: after all SEO edits, run a script or quick check that enforces:
  - `meta_title` ≤ 70 symbols;
  - `meta_description` ≤ 170 symbols;
  - no price mentions (`₽/`, `цена`) in `meta_description`;
  - no forbidden phrases (`материал дышит`, `кожа дышит`, `разведение`, `разводится`) in `meta_description`;
  - no producer claim (`от производителя`) in `meta_title`/`meta_description`/`seo_text`.
  See `references/global-seo-final-check.py` and `references/seo-description-forbidden-phrases-replacements.md`.
- **Admin `seo_text` save**: when category edits don't persist, verify `PUT /api/admin/categories/[id]` and `POST /api/admin/categories` include `seo_text` in the SQL statement; add it if missing.
