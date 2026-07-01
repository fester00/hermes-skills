# Project Context Retention

Avoid losing track of an existing project's exact identity, location, and explored structure across Hermes sessions.

## Why this matters

Hermes sessions can compress or restart. The user may expect the agent to "remember" a project that was studied in a previous conversation. Similar directory names (`pentajunior` vs `pentajunior-v2`), multiple clones, or stale paths make it easy to open the wrong codebase and waste a full exploration cycle.

## Rules

1. **Capture the exact project identity immediately.**
   - Project name as the user spelled it (case-sensitive).
   - Absolute path on disk.
   - Primary branch and remote, if known.
   - Persist this to `memory` (user profile) so it survives session restarts.

2. **Confirm before acting on a similarly named directory.**
   - If the user names a project, open only the directory whose name matches exactly.
   - If unsure, ask: `Подтверди путь: работаем в <полный путь>?`
   - Do not assume an old path from memory when a new name is given.

3. **Keep a lightweight project map.**
   - After the first exploration, save a short note with:
     - key directories (`src/app`, `src/components`, `src/lib`, `src/data`, `src/admin`);
     - data layer location (e.g. SQLite file or `db.ts`);
     - build/test commands that were verified;
     - any unusual conventions the project follows.
   - Store the map in the project's own notes if available, or as a skill reference.

4. **Resume from the map, not from scratch.**
   - At the start of a new task, re-read the saved map and the relevant files.
   - Update the map when significant structure changes (new routes, new templates, renamed folders).

5. **Push and commit discipline.**
   - When the user expects the repo to stay current, commit and push after each completed unit of work.
   - Verify `tsc --noEmit` / `npm run build` / tests before claiming the repo is clean.

## Example memory entry

```text
Project pentajunior-v2 is at /home/natan/pentajunior-v2. Next.js 16 + React 19 + Bootstrap 5 + better-sqlite3. Key dirs: src/app, src/components, src/lib, src/components/admin, src/components/ProductTemplates. Build verified with `npx tsc --noEmit && npm run build`. Commits pushed to origin/master.
```

## Anti-patterns

- Opening `/home/natan/workspace/pentajunior` when the user said `pentajunior-v2`.
- Re-exploring the whole directory tree on every session instead of consulting the map.
- Assuming a project path from system prompt context without checking the filesystem.
