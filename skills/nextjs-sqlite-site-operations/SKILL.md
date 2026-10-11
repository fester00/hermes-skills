---
name: nextjs-sqlite-site-operations
description: Use when operating a Next.js site backed by a committed SQLite database. Use better-sqlite3 via npx tsx, then commit, push, and deploy.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nextjs, sqlite, pm2, deploy, operations, pentajunior]
    related_skills: [hermes-ops-devops, hermes-webui-operations]
---

# Next.js + SQLite site operations

## When to use

- The project is a Next.js app.
- Site data (products, prices, pages, etc.) lives in a committed SQLite `.db` file, read via `better-sqlite3`.
- Runtime is PM2 + nvm-managed Node.
- Deploy is done via a shell script, often `~/deploy.sh` rather than `./deploy.sh`.
- Primary example: `pentajunior-v2`.

## Core workflow: edit a value and deploy

### 1. Identify the record in SQLite

Use the project's `better-sqlite3` via `npx tsx`. The system `sqlite3` CLI is frequently unavailable.

```bash
cd ~/project
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 24
export PATH="/home/natan/.nvm/versions/node/v24.13.1/bin:$PATH"

npx tsx -e "
const Database = require('better-sqlite3');
const db = new Database('project.db');
const rows = db.prepare(\"SELECT id, name, price, price_currency, price_unit, stock_info FROM products WHERE name LIKE ?\").all('%Product%');
console.table(rows);
db.close();
"
```

### 2. Update the value

```bash
npx tsx -e "
const Database = require('better-sqlite3');
const db = new Database('project.db');
const id = 'product-id';
const newPrice = '190';
const before = db.prepare('SELECT id, name, price FROM products WHERE id = ?').get(id);
console.log('Before:', before);
db.prepare('UPDATE products SET price = ? WHERE id = ?').run(newPrice, id);
const after = db.prepare('SELECT id, name, price FROM products WHERE id = ?').get(id);
console.log('After:', after);
db.close();
"
```

### 3. Commit and push

```bash
git diff --stat
git add project.db
git commit -m "update: цена Product (product-id) 155 → 190 ₽"
git push origin master
```

### 4. Deploy

```bash
bash /home/natan/deploy.sh
```

Do not assume the deploy script is in the project root. If unsure:
```bash
find ~ -maxdepth 2 -name "deploy.sh" -type f
```

### 5. Verify

Re-run the SELECT query or check the live page. If the value is baked into a static page, confirm the build step ran during deploy.

## Decision: how to make the edit

| Change type | Preferred method | Reason |
|-------------|------------------|--------|
| Single product price, stock flag, small text | Direct SQLite UPDATE via `better-sqlite3` + `npx tsx` | Fast, no dev server needed |
| Many products, schema changes, new fields | Admin API or migration script (`scripts/migrate.ts`) | Validation, batching, safety |
| Structured JSON templates (`template_data`) | Admin UI or migration script | Keeps JSON valid and complete |

## Pitfalls

1. **Do not use the system `sqlite3` command.** It is usually not installed. Rely on `better-sqlite3` through Node.
2. **Always SELECT before and after an UPDATE.** Binary `.db` diffs are unreadable; the query is the only reliable verification.
3. **Use the record `id` in the WHERE clause, not the display name.** Names can be ambiguous or change.
4. **The deploy script may live in `~`, not in the project root.** Search `~` if `./deploy.sh` is missing.
5. **nvm must be explicitly activated in non-interactive shells.** A deploy script must do `nvm use <version>` after sourcing `nvm.sh`; just sourcing `nvm.sh` does not select a Node version.
6. **If a `git pull` conflicts on the binary `.db`, do not blindly choose `ours` or `theirs`.** Smart-merge the structured data via SQL. See `references/nextjs-sqlite-data-edit-deploy.md` and, for conflict resolution, `hermes-ops-devops/references/sqlite-binary-merge-smart.md`.
7. **If the site still shows the old value after deploy**, check whether the build step actually ran and whether the page is statically generated. Browser cache can also cause this; instruct a hard refresh.

## One-liner for known product id

```bash
cd ~/project && export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh" && nvm use 24 && export PATH="/home/natan/.nvm/versions/node/v24.13.1/bin:$PATH" && npx tsx -e "
const Database = require('better-sqlite3');
const db = new Database('project.db');
const id = 'product-id';
const newPrice = '190';
const before = db.prepare('SELECT price FROM products WHERE id = ?').get(id);
db.prepare('UPDATE products SET price = ? WHERE id = ?').run(newPrice, id);
console.log(before.price, '→', db.prepare('SELECT price FROM products WHERE id = ?').get(id).price);
db.close();
"
```

After the one-liner, commit `project.db`, push, and run the deploy script.

## References

- `references/nextjs-sqlite-data-edit-deploy.md` — full step-by-step recipe with examples from `pentajunior-v2`
- `hermes-ops-devops/references/pm2-nodejs-service-config.md` — PM2 ecosystem config and nvm pitfalls
- `hermes-ops-devops/references/sqlite-binary-merge-smart.md` — resolving git conflicts in tracked SQLite databases
