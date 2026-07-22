# DB migration extraction pattern for pentajunior-v2

## When to use
When `src/lib/db.ts` contains `ALTER TABLE`, `CREATE TABLE`, or data-migration logic that runs on every module import. This causes builds and static generation to mutate the SQLite database, which is risky for CI, preview deploys, and reproducibility.

## Goal
Move all schema and data migrations into an explicit `scripts/migrate.ts` command (`npm run migrate`) that is run once at deploy time, not during `npm run build`.

## Steps

### 1. Create `scripts/migrate.ts`

```ts
import Database from 'better-sqlite3';
import fs from 'fs';
import path from 'path';

const dbPath = path.join(process.cwd(), 'pentajunior.db');
const db = new Database(dbPath);

// Track applied migrations
db.prepare(`
  CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
  )
`).run();

function hasMigration(name: string): boolean {
  return db.prepare('SELECT 1 FROM migrations WHERE name = ?').get(name) !== undefined;
}

function recordMigration(name: string): void {
  db.prepare('INSERT INTO migrations (name) VALUES (?)').run(name);
}

function runMigrations(): void {
  // Example: add a column only if missing
  if (!hasMigration('add_price_currency_to_products')) {
    const cols = db.prepare(`PRAGMA table_info(products)`).all() as { name: string }[];
    if (!cols.find((c) => c.name === 'price_currency')) {
      db.prepare(`ALTER TABLE products ADD COLUMN price_currency TEXT DEFAULT 'RUB'`).run();
      console.log('[migrate] Added price_currency column');
    }
    recordMigration('add_price_currency_to_products');
  }

  // Example: create a table only if missing
  if (!hasMigration('create_subcategories_table')) {
    const tables = db.prepare(`SELECT name FROM sqlite_master WHERE type='table' AND name='subcategories'`).all() as { name: string }[];
    if (tables.length === 0) {
      db.prepare(`CREATE TABLE subcategories (...)`).run();
      db.prepare(`CREATE INDEX ...`).run();
    }
    recordMigration('create_subcategories_table');
  }

  // Example: one-time data migration
  if (!hasMigration('extract_price_unit_from_prices')) {
    const rows = db.prepare("SELECT id, price FROM products WHERE price IS NOT NULL AND price_unit IS NULL").all() as { id: string; price: string | null }[];
    // ... transform and UPDATE
    recordMigration('extract_price_unit_from_prices');
  }
}

try {
  runMigrations();
  console.log('[migrate] Done');
  process.exit(0);
} catch (e) {
  console.error('[migrate] Failed:', e instanceof Error ? e.message : e);
  process.exit(1);
}
```

### 2. Add `tsx` and a script

```bash
npm install --save-dev tsx
```

```json
{
  "scripts": {
    "migrate": "tsx scripts/migrate.ts"
  }
}
```

### 3. Strip migration code from `src/lib/db.ts`

Remove:
- `ALTER TABLE` blocks
- `CREATE TABLE` blocks
- Data migration loops
- Image path cleanup that writes to the DB

Keep in `lib/db.ts` only:
- `Database` connection
- Query helpers (`getAllProducts`, `getCategoryBySlug`, etc.)
- Formatting helpers (`formatPrice`, `formatPriceFull`)
- `export { db }`

### 4. Run and verify

```bash
npm run migrate
./node_modules/.bin/tsc --noEmit
rm -rf .next tsconfig.tsbuildinfo
npm run build
```

Expected: `156/156 static pages`, no `[DB] Migrated` log lines during build.

### 5. Update the deploy script
Add `npm run migrate` to the deployment workflow between `npm install` and `npm run build`. For `pentajunior-v2` this is `/home/natan/deploy.sh`:
```bash
echo "🗄️  Применяем миграции базы данных..."
npm run migrate
```

## When to run migrations
- The schema changes (new column, table, index).
- A one-time data migration is required for all environments.
- `scripts/migrate.ts` was modified in the commit being deployed.
- First deployment to a new server where the database may be missing or outdated.

Do **not** run migrations when only content data, UI, or API logic changed. The deploy script runs it automatically before every build, which is safe because migrations are idempotent.

## Pitfalls

1. **Do not delete migration code from `lib/db.ts` until the production DB already matches the final schema.** The `scripts/migrate.ts` must first be run on the server, then the runtime code can be cleaned.
2. **Migration names must never change.** They are the primary keys of the `migrations` table. Renaming a migration causes it to re-run.
3. **Keep migrations idempotent inside the guard.** Even though `hasMigration()` prevents re-runs, the inner schema check (`PRAGMA table_info`, `sqlite_master`) should still be safe if called manually.
4. **Do not import `lib/db.ts` from `scripts/migrate.ts`** if `lib/db.ts` still has side effects. Use a fresh `new Database(...)` in the script until the side effects are removed.
5. **Backup the DB before running new migrations on production.**

## Connection to the rest of the project

- After extraction, all API routes should import the shared `db` from `@/lib/db` instead of creating `new Database(...)`.
- The shared `db` module should be pure: no migrations, no FS cleanup, no `console.log` side effects beyond unavoidable warnings.
