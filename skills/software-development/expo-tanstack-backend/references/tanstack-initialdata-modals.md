# TanStack Query `initialData` + `staleTime` — The "Empty Modal" Bug

## Symptom

A modal that displays a list of items (e.g. tariff selector, service picker) opens **empty/blank** on first visit. After any mutation (e.g. "connect service") the list suddenly populates.

## Root cause

`useQuery` is configured with both `initialData: []` and a long `staleTime`:

```ts
export function useTariffs() {
  return useQuery({
    queryKey: queryKeys.catalog.tariffs(),
    queryFn: getTariffs,
    staleTime: 3 * 60_000,  // 3 minutes
    initialData: [],        // ← treated as "already have valid data"
  });
}
```

**How TanStack Query sees this:**
1. First render: `initialData` means "data is already present"
2. `staleTime: 3 min` means "this data is fresh for 3 minutes"
3. The real `queryFn` is **never called** — the query stays in `success` state with empty array
4. UI opens modal → maps over `[]` → renders nothing

## When a mutation "fixes" it

After `connectService.mutate()`, the `onSuccess` runs:
```ts
onSuccess: () => invalidateAll(queryClient)
```

This marks the cache entry as **stale**, and TanStack Query finally runs the real fetch in the background. The next time the modal opens, data is present.

## Fix

**Remove `initialData` for catalog/reference data** — let TanStack Query fetch from the server on first mount:

```ts
export function useTariffs() {
  return useQuery({
    queryKey: queryKeys.catalog.tariffs(),
    queryFn: getTariffs,
    staleTime: 3 * 60_000,
    // NO initialData — fetch from server
  });
}
```

With `initialData` gone:
- First render: `status === 'pending'` → show loading spinner
- Background fetch completes → list populates
- Subsequent mounts within 3 min: cached data used (no refetch)
- After `staleTime` expires: next mount triggers refetch

## When `initialData` IS appropriate

Use `initialData` only when:
1. The query has been **pre-populated** elsewhere (e.g. SSR, initial props)
2. You have a **sensible default** that is immediately useful (e.g. empty object for a form)
3. The data is **guaranteed** to come from a parent query's cache with `queryClient.setQueryData`

**NEVER** use `initialData: []` + long `staleTime` for server-fetched lists that the user expects to see populated.

## Pattern for modals that need guaranteed data

If a modal MUST have data before opening, prefetch:

```tsx
const { data: allTariffs } = useTariffs();

// In the open handler:
const openTariffModal = useCallback(() => {
  // If no data yet, trigger immediate fetch (will show spinner)
  if (!allTariffs) {
    queryClient.prefetchQuery({
      queryKey: queryKeys.catalog.tariffs(),
      queryFn: getTariffs,
    });
  }
  setTariffModalVisible(true);
}, [allTariffs]);
```

Or show a loading state inside the modal:

```tsx
<Modal visible={tariffModalVisible} ...>
  {allTariffs?.length ? (
    <ScrollView>
      {allTariffs.map(t => <TariffItem key={t.id} tariff={t} />)}
    </ScrollView>
  ) : (
    <ActivityIndicator />
  )}
</Modal>
```

## `useMemo` inside `useCallback` — React hook violation

### Symptom
`eslint-plugin-react-hooks` flags: `React Hook "useMemo" is called in function "TariffModal" which is neither a React function component or a custom React Hook function.`

Or runtime: `Rendered fewer hooks than expected` / `Rendered more hooks than expected`.

### Root cause

```tsx
const TariffModal = useCallback(() => {
  // ❌ useMemo inside useCallback — violates Rules of Hooks
  const currentIds = useMemo(() => new Set(...), [account?.tariffs]);
  
  return <Modal>...</Modal>;
}, [...]);
```

`useMemo` must be at the **top level** of a component or custom hook. Inside `useCallback` it's called conditionally based on when the callback executes, violating React's hook rules.

### Fix — hoist `useMemo` outside `useCallback`:

```tsx
// ✅ useMemo at component top level
const currentTariffIds = useMemo(
  () => new Set((account?.tariffs || []).map(t => t.id)),
  [account?.tariffs]
);

const TariffModal = useCallback(() => {
  // Just reference the pre-computed value
  return (
    <Modal ...>
      {allTariffs?.map(t => (
        <Item
          key={t.id}
          isActive={currentTariffIds.has(t.id)}  // ← no useMemo here
        />
      ))}
    </Modal>
  );
}, [allTariffs, currentTariffIds, ...]);
```

### Why this matters with modals

A modal's visibility toggles frequently. If `useMemo` is inside a callback that only executes when the modal is visible, React sees a changing number of hooks between renders (modal hidden = 0 hooks; modal visible = 1 hook). This corrupts the hook order and causes crashes.

## Checklist for modal data fetching

- [ ] Remove `initialData: []` from catalog queries (tariffs, services, references)
- [ ] Add loading state (`isLoading` / `isPending`) inside the modal
- [ ] Hoist all `useMemo`/`useCallback` outside of other `useCallback` closures
- [ ] Use `queryClient.prefetchQuery` if modal needs data before opening
- [ ] Keep `staleTime` for performance, but let first mount trigger real fetch
