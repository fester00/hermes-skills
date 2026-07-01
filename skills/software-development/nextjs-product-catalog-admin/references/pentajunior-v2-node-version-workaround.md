# Node.js version mismatch when building pentajunior-v2

## Symptom

Commands like `npx tsc --noEmit` or `npm run build` fail with:

```
You are using Node.js 18.19.1. For Next.js, Node.js version ">=20.9.0" is required.
```

or

```
/usr/bin/bash: line 3: npx: command not found
```

## Root cause

The system `/usr/bin/node` is v18 and the system `npm`/`npx` may be missing or incompatible. The project was built with Node v24.13.1 installed via `nvm` at:

```
/home/natan/.nvm/versions/node/v24.13.1/bin
```

## Fix for a single command

Prefix the command with the nvm Node bin directory:

```bash
cd /home/natan/pentajunior-v2
PATH=/home/natan/.nvm/versions/node/v24.13.1/bin:$PATH npx tsc --noEmit
PATH=/home/natan/.nvm/versions/node/v24.13.1/bin:$PATH npm run build
```

## Fix for the whole shell session

```bash
export PATH=/home/natan/.nvm/versions/node/v24.13.1/bin:$PATH
node --version   # should show v24.13.1
npm run build
```

## Persistent fix (optional)

If the project always uses this Node version, add the export to the project-specific shell config or a `.envrc`:

```bash
# .envrc in /home/natan/pentajunior-v2
export PATH=/home/natan/.nvm/versions/node/v24.13.1/bin:$PATH
```

Or source nvm in the shell profile so `nvm use 24` works automatically.

## Verification

```bash
which node && node --version
which npm && npm --version
which npx && npx --version
```

All should point to the nvm v24 paths.

## Related

- `references/nextjs-dev-server-cache-invalidation.md` — restart recipe for the dev server after a successful build.
