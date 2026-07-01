# Port and project identity verification

When a user asks to check or fix something on a local URL like `http://localhost:3000/...`, do not assume the project from the workspace tag alone. On this host there are two similarly-named Next.js projects running concurrently:

- `http://localhost:3000` — legacy project `pentajunior` (v1), located at `/home/natan/workspace/pentajunior`
- `http://localhost:3001` — current project `pentajunior-v2`, located at `/home/natan/pentajunior-v2`

## Verification steps

1. Read the port from the URL the user provides.
2. Map port to project before checking code or logs:
   - `3000` → `/home/natan/workspace/pentajunior`
   - `3001` → `/home/natan/pentajunior-v2`
3. If the user gives no port, ask which one.
4. Check `git log`, source files, and running process against the mapped project, not the workspace tag default.

## Pitfall avoided

Opening the wrong project leads to stale code analysis, false "everything is up-to-date" reports, and wasted cycles. In this session the user reported a hydration error on `localhost:3000` while the fixes were committed to `pentajunior-v2` on port 3001. The v1 server on 3000 still served the old markup.
