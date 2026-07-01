---
name: layered-api-training
description: |
  Progressive training scaffolds for frontend developers learning layered HTTP architecture
  and TanStack Query. Covers: client → services → hooks → components, auth interceptors,
  cache invalidation, optimistic updates, and reusable mutation patterns.
trigger: |
  User wants hands-on practice with:
  - HTTP client wrappers, fetch, URLSearchParams, Promise.all
  - React Query / TanStack Query (useQuery, useQueries, infiniteQuery, optimistic updates)
  - Layered frontend architecture (client → services → hooks → components)
  - Progressive difficulty training dojos
  - Socratic course on React Query, auth patterns, or three-layer data architecture
---

# Layered API Training Dojo

## Purpose
Generate a 5-layer progressive training scaffold for frontend developers learning HTTP APIs and React Query patterns. Uses a real public API (default: SWAPI) with zero authentication.

## API Selection Criteria
- Free, open, no API key
- Returns JSON with nested/relational URLs (e.g. `films: string[]` of absolute URLs)
- Supports search, pagination, and detail endpoints
- Stable CORS and uptime

**Default choice:** [SWAPI](https://www.swapi.tech/api) — returns absolute URLs in relational fields (films, starships, homeworld).

## Project Scaffold
```
swapi-training/
├── tasks/
│   ├── 01-api-client.ts     # fetch wrapper, URLSearchParams, Promise.all
│   ├── 02-services.ts      # pure endpoint functions, zero React imports
│   ├── 03-hooks.ts         # useQuery, useQueries, pagination patterns
│   ├── 04-components.tsx   # loading / error / pagination / debounce UI
│   └── 05-advanced.ts      # prefetch, infiniteQuery, optimistic UI, select
├── SOLUTIONS/              # answer key (seed after user attempts)
├── README.md
└── package.json + tsconfig.json
```

## Layer-by-Layer Content

### Layer 1 — API Client
**Concepts:** generic `request<T>`, absolute vs relative URL detection, `URLSearchParams`, `Promise.all`, empty-array guards.

```ts
// Critical pattern: SWAPI returns absolute URLs in relational fields
const trueUrl = url.startsWith('http') ? url : `${BASE_URL}${url}`;
```

**Common bug:** `reduce()` without capturing/computing the return value silently yields nothing — prefer `map()` after `Promise.all()`:
```ts
// Good
const responses = await Promise.all(urls.map(u => request<SwapiItemResponse<T>>(u)));
return responses.map(r => r.result.properties);

// Bug-prone (student often forgets to return reduce result)
responses.reduce((acc, r) => { acc.push(r.result.properties); return acc; }, [] as T[]);
// Must assign the result or reduce is wasted
```

**Empty-params guard:** when `params = {}`, naive `toString()` on `URLSearchParams` still produces `""`, but double-checking prevents `/people?` trailing-`?` output:
```ts
const qs = searchParams.toString();
return qs ? `${basePath}?${qs}` : basePath;
```

### Layer 2 — Services
Pure TypeScript functions that know endpoints but zero React. Patterns:
- Pass-through wrappers (`getPersonById`, `getPeople`)
- Early return guards (`searchPeople`: empty string → `[]`)
- Conditional parallel resolution (`getPersonStarships`: empty URLs → `[]`, else `resolveUrls`)

### Layer 3 — Hooks
Patterns:
- `useQuery({ queryKey: ['people', 'list', page], placeholderData: keepPreviousData })`
- Conditional fetch: `enabled: !!id`
- Parallel sub-queries via `useQueries` for film/starship arrays
- Debounced search: `enabled: name.length > 2`, `staleTime: 30_000`

### Layer 4 — Components
- Pagination with disabled-state guards (`currentPage <= 1`, `currentPage >= totalPages`)
- Master-detail split pane
- Debounced input with `useEffect + setTimeout + clearTimeout`
- Strict conditional rendering: `isLoading` → `isError` → data branches

### Layer 5 — Advanced
- `queryClient.prefetchQuery` for next page (hover/focus button)
- `useInfiniteQuery` with `getNextPageParam` calculating page from `allPages.length`
- Optimistic toggle with `onMutate` / `onError` rollback using `context.previous`
- `select` option on `useQuery` to derive names-only arrays without extra state

## SWAPI Response Shape (critical for typing)
```ts
// List endpoint
{ message: "ok", total_records: 82, total_pages: 17,
  results: [{ uid: "1", name: "Luke Skywalker", url: "..." }] }

// Detail endpoint
{ message: "ok",
  result: { properties: { name, height, films: ["https://..."] },
            uid: "1", description: "..." } }
```

Note: `films`, `starships`, `homeworld` are **full absolute URLs**, not relative paths.

## Verification Commands
```bash
# List with pagination
curl -s 'https://www.swapi.tech/api/people?page=1&limit=5'

# Detail
curl -s 'https://www.swapi.tech/api/people/1'

# Search
curl -s 'https://www.swapi.tech/api/people?name=luke'
```

## Student Pitfalls Observed
1. Forgetting `url.startsWith('http')` check → doubled base URLs on relational fields.
2. `reduce` without capturing return value → function returns `[]` or `undefined`.
3. Missing empty-array guard before firing `Promise.all` → unnecessary requests or runtime errors.
4. `buildUrl` without empty-params guard → trailing `?` on clean URLs.
5. Confusing `useQueries` (array of objects) with `useQuery` (single config).

## Support files

- `references/react-query-beginner-pitfalls.md` — 12 real mistakes observed during live socratic teaching (TaskBoard auth+tasks). Covers: calling fetch directly, loose typing, returning error objects, confusing mutate/mutateAsync, forgetting enabled, await without return, etc.
- `templates/taskboard-practice.md` — Ready-to-fill scaffold for `api/client.ts`, `services/auth.service.ts`, `hooks/useAuth.ts`. Includes extension exercises for tasks CRUD.

## Dependencies
```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@tanstack/react-query": "^5.0.0"
  },
  "devDependencies": {
    "typescript": "^5.7.0",
    "@types/react": "^19.0.0",
    "vitest": "^3.0.0"
  }
}
```