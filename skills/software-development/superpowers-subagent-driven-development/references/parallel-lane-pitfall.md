# Parallel Lane Dispatch — Checklist

Use this checklist when splitting a plan into multiple concurrent `delegate_task` subagents.

## When parallel lanes are safe

- Each lane's primary modified files do not overlap with another lane's primary modified files.
- Shared files are only *read/imported*, not modified, by secondary lanes.
- The controller is available to reconcile after all lanes finish.

## When to serialize instead

- Two lanes must edit the same file.
- One lane's output is a hard dependency for another lane's implementation (e.g., Lane B cannot start until Lane A creates a component).
- The shared file is small and tightly coupled to both changes.

## Recommended lane split for landing-page redesigns

| Lane | Owns | Reads |
|---|---|---|
| UI Components | `src/components/*.tsx` | `src/data/site.ts`, `src/utils/*` |
| Sections | `src/sections/*.tsx` | components, data, utils |
| Global Styles / Config | `src/index.css`, `tailwind.config.js` | components, sections |

## Reconcile after parallel lanes

1. Re-read all files a lane could have touched.
2. Run `npx tsc --noEmit` and `npm run build`.
3. Run Playwright screenshots (desktop, mobile, modal, form).
4. Compare before/after images visually.
5. Only then update the ledger and mark tasks complete.

## Warning signs of a race

- A subagent reports: "another agent modified this file".
- `tsc` passes but visual result is inconsistent.
- One lane's report mentions a file outside its assigned scope.

If any appear, stop and serialize the remaining work.
