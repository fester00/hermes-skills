# Performance: SSG + SQLite vs Hardcoded Data

## Decision Matrix

| Catalog Size | Hardcoded JSX | SQLite + SSG | Recommendation |
|---|---|---|---|
| < 100 items | Fast, simple | Slight overhead | Either works |
| 100-1000 | Build bloat, search is O(n) | Same client speed, indexed search | **SQLite** |
| 1000+ | Painful updates, slow builds | Scales linearly | **SQLite strongly** |

## Measurement Checklist

Before claiming "slower", measure:

1. **Build time:** `time npx next build` — compare v1 vs v2. Expect <10% increase.
2. **Client TTFB:** Both versions serve static HTML. No difference expected.
3. **Memory:** SQLite opens the file once per process. No persistent memory cost for visitors.

## When SQLite IS Slower (and fixes)

| Scenario | Why | Fix |
|---|---|---|
| SSR page hits DB per request | `getServerSideProps` or `generateStaticParams` on dynamic routes with `fallback: true` | Use `generateStaticParams` at build time only |
| Heavy JOINs in `generateStaticParams` | N+1 query pattern | Batch with `JOIN` or denormalized views |
| Network disk (NFS/SMB) | SQLite needs local FS locking | Use local SSD; replicate if needed |
| No indexes on filter columns | Full table scan | `CREATE INDEX idx_products_category ON products(category_id)` |

## Summary

For SSG sites (Next.js `output: 'export'`), SQLite is a **build-time dependency**, not a runtime one. Your visitors never touch the database. The only cost is milliseconds added to `next build`. The benefit is programmatic updates, search, and scaling without code changes.
