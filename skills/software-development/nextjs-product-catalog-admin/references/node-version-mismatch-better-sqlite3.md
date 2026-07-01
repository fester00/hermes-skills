# Node.js Version Mismatch: better-sqlite3 Native Module

## Symptom

```
Error: The module '/path/to/better_sqlite3.node'
was compiled against a different Node.js version using
NODE_MODULE_VERSION 137. This version of Node.js requires
NODE_MODULE_VERSION 109.
```

Or: `npm run build` fails with cryptic `better-sqlite3` loading errors.

## Root Cause

`better-sqlite3` contains a native C++ addon (`.node` file) compiled against a specific Node.js ABI version. When Node.js version changes (e.g. via `nvm use`), the compiled binary becomes incompatible.

Common trigger:
- `npm install` was run under Node.js v24
- Later a command runs under system Node.js v18 (which lacks `npm` in PATH or has different ABI)
- Or vice versa

## Fix

### 1. Check current Node.js version

```bash
node -v   # If this shows v18 but project needs v24, that's the problem
```

### 2. Switch to correct Node.js version

```bash
source ~/.nvm/nvm.sh
nvm use 24.13.0   # or whichever version the project expects
```

### 3. Rebuild native modules

```bash
npm rebuild better-sqlite3
```

This recompiles the C++ addon against the currently active Node.js version.

### 4. Verify

```bash
node -e "const Database = require('better-sqlite3'); console.log('OK')"
```

## Prevention

- Set default Node.js alias: `nvm alias default 24.13.0`
- In project README: document required Node.js version
- Use `.nvmrc` file in project root:
  ```
  24.13.0
  ```
  Then: `nvm use` (reads `.nvmrc` automatically)

## Server Environment Note

When setting up a new server or CI environment:
1. Install `nvm`
2. `nvm install 24.13.0`
3. `nvm alias default 24.13.0`
4. `npm install` (installs deps under correct Node version)
5. `npm rebuild better-sqlite3` (ensures native module matches)

The system Node.js (e.g. v18 via apt) may remain installed but should not be used for the project.

## Windows / PowerShell Equivalent

On Windows with `nvm-windows`:
```powershell
nvm use 24.13.0
npm rebuild better-sqlite3
```
