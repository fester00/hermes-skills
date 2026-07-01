# better-sqlite3: Node.js Version Mismatch

## Symptom

When running Node scripts that require `better-sqlite3`, you see:

```
Error: The module '/path/to/better_sqlite3.node'
was compiled against a different Node.js version using
NODE_MODULE_VERSION 137. This version of Node.js requires
NODE_MODULE_VERSION 109.
```

Or via `execute_code` with Python `subprocess.run(['node', ...])`:
- System Node may differ from project Node (e.g., system = v18, project = v24)
- `execute_code` uses system Node, terminal uses `.nvm` or `pnpm` shim Node

## Root Cause

`better-sqlite3` is a native C++ addon. It must be compiled against the exact Node.js ABI version that will load it. Changing Node versions (via nvm, system upgrade, or different shells) breaks the compiled binary.

## Fix

```bash
# In project directory, using the correct Node version:
cd ~/project
cd ~/project && pnpm rebuild better-sqlite3
# Or with npm:
npm rebuild better-sqlite3
# Or with bun:
bun install better-sqlite3
```

After rebuild, verify:
```bash
node -e "const Database = require('better-sqlite3'); const db = new Database('./db.sqlite'); console.log('OK'); db.close();"
```

## Prevention

1. **Pin Node version** in project root:
   ```bash
   echo "24.13.1" > .nvmrc
   ```

2. **Pre-build hook** in CI:
   ```yaml
   - run: pnpm rebuild better-sqlite3
     if: steps.cache-deps.outputs.cache-hit == 'true'
   ```

3. **Check before build** in `package.json`:
   ```json
   {
     "scripts": {
       "prebuild": "node -e \"require('better-sqlite3')\" || pnpm rebuild better-sqlite3"
     }
   }
   ```

## Tool Selection Rule

When working with `better-sqlite3` from Hermes:

| Tool | Node version used | Best for |
|------|-------------------|----------|
| `terminal()` | `.nvm` / `pnpm` shim | Building, installing, rebuilding |
| `execute_code` (Python) | System Node (often older) | Avoid requiring `better-sqlite3` |
| `execute_code` (JS via node directly) | Depends on `$PATH` | Use only after verifying version |

**Rule of thumb:** Always run `better-sqlite3` operations through `terminal()` in the project directory. Never rely on `execute_code` Python subprocess spawning Node — version mismatch is guaranteed on multi-Node systems.

## When `sqlite3` CLI is unavailable

If `sqlite3` command-line tool is not installed, use Node + `better-sqlite3`:
```bash
cd ~/project && node -e "
const Database = require('better-sqlite3');
const db = new Database('./db.sqlite');
const tables = db.prepare(\"SELECT name FROM sqlite_master WHERE type='table'\").all();
console.log(tables.map(t => t.name));
"
```

This is slower than the CLI but works without installing system packages.
