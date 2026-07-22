# API route refactoring pattern — pentajunior-v2

Session context: July 2026 refactor of duplicated `try/catch` / `NextResponse.json` boilerplate in `/api/admin/*` routes.

## Created utilities

File: `src/lib/api-utils.ts`

| Function | Purpose |
|----------|---------|
| `handleApiError(error)` | Returns `{ error: message }` with status 500. In dev includes `error.message`; in production returns generic "Ошибка сервера". |
| `parseIdParam(value)` | Parses a numeric route param; returns `{ id }` or `{ error: NextResponse }` with status 400 on invalid input. |
| `parseQueryNumber(value)` | Parses a query string to `number \| undefined`. |
| `notFoundResponse(message?)` | Standard 404 response. |
| `successResponse(data?)` | Standard `{ success: true, ...data }` response. |

## Routes updated

- `src/app/api/admin/categories/route.ts` + `[id]/route.ts`
- `src/app/api/admin/subcategories/route.ts` + `[id]/route.ts`
- `src/app/api/admin/products/route.ts` + `[id]/route.ts`
- `src/app/api/admin/spec-tables/route.ts` + `[id]/route.ts`

## Patterns applied

1. **Replace inline error responses** with `handleApiError` in every catch block.
2. **Replace success responses** with `successResponse({ ... })` when there is extra data.
3. **Use `parseIdParam`** for `params.id` so invalid IDs return 400 instead of being passed as strings to SQLite.
4. **Keep 4xx responses as `NextResponse.json(...)`** because they carry specific user-facing messages (validation, conflict, etc.).

## What was deliberately not changed

- `/api/admin/auth/route.ts` — has custom cookie logic and auth-specific responses.
- `/api/admin/upload/route.ts` — file-upload specific.
- `/api/admin/templates/route.ts` — still uses inline responses; can be migrated later.
- `/api/search/route.ts` — can be migrated later.

## Build gate

After touching API routes:
```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
cd /home/natan/pentajunior-v2
./node_modules/.bin/tsc --noEmit
rm -rf .next tsconfig.tsbuildinfo
npm run build
```

All admin API routes remained dynamic (`ƒ`) after the refactor; static page count stayed at 156/156.
