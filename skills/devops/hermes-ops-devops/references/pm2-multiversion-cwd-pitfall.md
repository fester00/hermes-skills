# Multi-Version PM2 Config — Stale `cwd` Pitfall

## Context
- Server hosts multiple versions of the same app (e.g., `pentajunior`, `pentajunior-v2`, `pentajunior-v3`)
- Each version may have its own `ecosystem.config.js`
- Accidental copy-paste of config from main project into version folder

## The Problem
`pentajunior-v2/ecosystem.config.js` was copied from the main project but still contained:
```javascript
cwd: '/home/natan/pentajunior'   // ← Points to MAIN project, not v2!
```
This means PM2 would start v2's code but run from the main project's directory,
reading the wrong `.env`, wrong database, and potentially overwriting main project's state.

## Detection
```bash
# Check all ecosystem.config.js files for cwd mismatches
grep -rn "cwd:" ~/pentajunior*/ecosystem.config.js ~/deploy.sh 2>/dev/null
# Verify actual directory vs cwd in config
realpath ~/pentajunior-v2
grep "cwd" ~/pentajunior-v2/ecosystem.config.js
```

## Fix
Update `ecosystem.config.js` in each version folder:
```javascript
cwd: '/home/natan/pentajunior-v2'   // Must match the folder the config lives in
```

## Prevention
- Always verify `cwd` matches the directory containing the config
- Use `__dirname` or `process.cwd()` in config if possible
- Add a deploy-script validation step: `assert ["$PWD" == "$(node -e 'console.log(require("./ecosystem.config.js").apps[0].cwd)')"]`
