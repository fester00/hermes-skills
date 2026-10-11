# Next.js + SQLite site — data edits and deploy workflow

Class-level recipe for sites that store content in a committed SQLite `.db` file,
use Next.js with static/dynamic generation, and run under PM2.

## When this applies

- Source of truth for site data is `*.db` in the repo, read via `better-sqlite3`.
- Deploy is handled by a shell script (often `~/deploy.sh`, not `./deploy.sh`).
- Runtime is PM2 + nvm Node.
- Typical projects: `pentajunior-v2` and similar Next.js/SQLite stacks.

## Decision: where to edit

| If the change is… | Edit via… | Why |
|-------------------|-----------|-----|
| A single product price, stock flag, or small text field | Direct SQLite UPDATE through Node/`better-sqlite3` | Fast, deterministic, no need to start a dev server |
| Many products / schema changes / new fields | Admin API or migration script | Safer validation and batching |
| Content pages, SEO fields, structured templates | Prefer admin UI or migration script to keep JSON valid |

Do NOT hand-edit the binary `.db` with a hex editor. Do NOT rely on the system `sqlite3` CLI — it is often not installed; use the project's `better-sqlite3` instead.

## Step-by-step: edit a value and deploy

### 1. Locate the record

```bash
cd ~/project
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 24
export PATH="/home/natan/.nvm/versions/node/v24.13.1/bin:$PATH"

npx tsx -e "
const Database = require('better-sqlite3');
const path = require('path');
const db = new Database(path.join(process.cwd(), 'project.db'));
const rows = db.prepare(\"SELECT id, name, price, price_currency, price_unit, stock_info FROM products WHERE name LIKE ?\").all('%Product Name%');
console.table(rows);
db.close();
"
```

### 2. Update the value

```bash
npx tsx -e "
const Database = require('better-sqlite3');
const path = require('path');
const db = new Database(path.join(process.cwd(), 'project.db'));
const before = db.prepare('SELECT id, name, price FROM products WHERE id = ?').get('product-id');
console.log('Before:', before);
const result = db.prepare('UPDATE products SET price = ? WHERE id = ?').run('190', 'product-id');
console.log('Updated rows:', result.changes);
const after = db.prepare('SELECT id, name, price FROM products WHERE id = ?').get('product-id');
console.log('After:', after);
db.close();
"
```

### 3. Verify only the intended row changed

```bash
git diff --stat
git diff project.db   # binary: shows changed, but not readable
```

For a human-readable confirmation, re-run the SELECT from step 1.

### 4. Commit and push

```bash
git add project.db
git commit -m "update: цена Product (product-id) 155 → 190 ₽"
git push origin master
```

Keep the commit message short and in the project language. Include old → new value and the record id.

### 5. Run the deploy script

```bash
bash /home/natan/deploy.sh
```

**Do not assume the script is in the project root.** Search `~` first if unsure:
```bash
find ~ -maxdepth 2 -name "deploy.sh" -type f
```

A typical deploy script for this stack does:
1. `git pull`
2. `npm install`
3. `npm run migrate`
4. `npm run build`
5. `pm2 reload|start ecosystem.config.js`
6. `pm2 save`

### 6. Verify after deploy

Re-run the SELECT or curl the live page. For product pages, also check the static build included the new value by inspecting the generated HTML or the API response.

## Common pitfalls

| Problem | Why it happens | Fix |
|---------|----------------|-----|
| `sqlite3: command not found` | The CLI is not installed | Use `npx tsx` with `better-sqlite3` — already a project dependency |
| `deploy.sh: No such file or directory` | The script lives in `~`, not in the project root | Run `find ~ -maxdepth 2 -name "deploy.sh" -type f` |
| `npm: command not found` inside deploy.sh | Non-interactive shell does not activate nvm | Ensure the script does `nvm use <version>` after sourcing `nvm.sh` and sets PATH explicitly |
| Deploy succeeds but old price still shown | Next.js ISR/static cache or browser cache | Hard-refresh the page; if the value is baked into a prerendered page, rebuild already happened during deploy, so check that the deploy actually rebuilt |
| `git diff project.db` is unreadable | SQLite is binary | Verify via SELECT query, not diff |
| `.db` conflict on `git pull` | Binary file changed on both sides | See `hermes-ops-devops/references/sqlite-binary-merge-smart.md` — smart-merge structured data instead of picking `ours`/`theirs` |
| Accidentally updated the wrong column | No schema validation on raw SQL | Always SELECT before and after; use id, not name, as the WHERE clause |

## One-liner for price updates

For a quick price change when the id is known:

```bash
cd ~/project && export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh" && nvm use 24 && export PATH="/home/natan/.nvm/versions/node/v24.13.1/bin:$PATH" && npx tsx -e "
const Database = require('better-sqlite3');
const db = new Database('project.db');
const id = 'product-id';
const newPrice = '190';
const before = db.prepare('SELECT price FROM products WHERE id = ?').get(id);
db.prepare('UPDATE products SET price = ? WHERE id = ?').run(newPrice, id);
const after = db.prepare('SELECT id, name, price FROM products WHERE id = ?').get(id);
console.log(before.price, '→', after.price, after);
db.close();
"
```

After running it, commit `project.db`, push, and run `bash ~/deploy.sh`.
