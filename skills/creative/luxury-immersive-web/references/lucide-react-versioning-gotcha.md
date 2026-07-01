# Lucide-React Versioning Gotcha in Luxury/React Projects

## Symptom

Build or dev fails with:

```
Module not found: Can't resolve 'lucide-react'
```

or a specific icon (e.g. `Sparkles`, `ArrowLeft`, `Phone`) is reported as missing even though `lucide-react` appears installed.

## Root Cause

`lucide-react` has **non-linear version numbering**. The older `1.x` line (`1.22.0`) is a stale release that predates many modern icons. The actively maintained line uses `0.x` versions (e.g. `0.487.0`) and is what `npm install lucide-react@latest` should resolve to, but a `package.json` pinned to `^1.22.0` keeps the stale release.

```json
// WRONG — stale 1.x line, missing icons
"lucide-react": "^1.22.0"

// CORRECT — current maintained line
"lucide-react": "^0.487.0"
```

## Fix

1. Check the installed version:
   ```bash
   npm ls lucide-react
   ```
2. If it shows `1.x`, downgrade/upgrade to current `0.x`:
   ```bash
   npm install lucide-react@0.487.0
   ```
3. Verify the icon exists in the installed package:
   ```bash
   grep -r "Sparkles" node_modules/lucide-react/dist/esm/lucide-react.mjs | head -1
   ```
4. Re-run build.

## Verification

- `npm run build` succeeds.
- `npx tsc --noEmit` is clean.

## Prevention

When adding Lucide icons to an existing project, always check the installed major version first. Do not assume `^1.x` is newer than `^0.x` for this package. Pin to the current `0.x` line in `package.json`.
