# React child editor with local state + onChange

Use this pattern when a child component edits a complex value (array of objects, structured blocks) and needs to notify a parent form.

## Why not synchronously call `onChange` inside `setState`?

Calling the parent's setter from inside the updater passed to `setXxx` triggers React's warning:

```
Cannot update a component (`ParentForm`) while rendering a different component (`ChildEditor`).
```

The child is still rendering when the parent state is updated, so React detects a setState during render.

## Recipe

1. Keep local `draft` state in the child.
2. Sync it with props only when the prop content really changes (compare serialized value).
3. Notify the parent via `useEffect` driven by the local `draft`, but only when the result differs from the last prop value.
4. Use `useRef` for the `onChange` callback so it does not become a dependency of the effect.

```tsx
'use client';
import { memo, useCallback, useEffect, useRef, useState } from 'react';

interface Tier { minQty: string; maxQty: string; unit: string; price: string; currency: 'RUB' | 'USD'; id?: string; }

const generateId = () => Math.random().toString(36).slice(2, 9);
const serialize = (tiers: Tier[]) => JSON.stringify(tiers.map(({ id, ...rest }) => rest));

const ChildEditor = memo(function ChildEditor({ value, onChange }: { value: Tier[]; onChange: (v: Tier[]) => void }) {
  const [draft, setDraft] = useState<Tier[]>(() => value.map((t) => ({ ...t, id: t.id || generateId() })));
  const lastPropRef = useRef(serialize(value));
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  // Sync with prop only when the prop value really changes
  useEffect(() => {
    const serialized = serialize(value);
    if (serialized === lastPropRef.current) return;
    lastPropRef.current = serialized;
    setDraft(value.map((t) => ({ ...t, id: t.id || generateId() })));
  }, [value]);

  // Notify parent safely after render
  useEffect(() => {
    const stripped = draft.map(({ id, ...rest }) => rest);
    const serialized = JSON.stringify(stripped);
    if (serialized === lastPropRef.current) return;
    lastPropRef.current = serialized;
    onChangeRef.current(stripped);
  }, [draft]);

  const update = useCallback((id: string, field: keyof Tier, val: string) => {
    setDraft((prev) => prev.map((t) => (t.id === id ? { ...t, [field]: val } : t)));
  }, []);

  return (
    <div>
      {draft.map((tier) => (
        <input
          key={tier.id}
          value={tier.minQty}
          onChange={(e) => update(tier.id!, 'minQty', e.target.value)}
        />
      ))}
    </div>
  );
});
```

## Variation: fully controlled without local state

If the parent can re-render cheaply and there are no focus/scroll issues, the child can be fully controlled:

```tsx
<input value={tier.minQty} onChange={(e) => onChange(updateValue(value, tier.id, e.target.value))} />
```

Use this only when:
- the parent state update does not cause modal body scroll jumps,
- the value array is small,
- inputs are not inside a heavy form.

For modal forms with many fields, prefer local-state-with-useEffect.

## Testing the pattern

1. Open the admin form in browser.
2. Type into the child editor fields.
3. Check console for:
   - `Cannot update a component ... while rendering` — means `onChange` is still called during render.
   - `Maximum update depth exceeded` — means effect/prop comparison is missing or wrong.
4. Save the parent form and verify the persisted value in the DB / API response.

## Common variants that fail

### Variant A: calling `onChange` inside `setDrafts`
```ts
// BAD
setDrafts((prev) => {
  const next = prev.map(...);
  onChange(next);   // <-- triggers parent setState during render
  return next;
});
```
Fix: split into local `setDrafts` + `useEffect` that calls `onChange`.

### Variant B: useEffect without serialized comparison
```ts
// BAD
useEffect(() => {
  setDrafts(value.map(...));
}, [value]);

useEffect(() => {
  onChange(draft.map(...));
}, [draft, onChange]);
```
This loops because `onChange` updates parent `draft.price_tiers`, producing a new array reference, which triggers the first effect again.
Fix: compare `JSON.stringify(strippedDraft)` with `JSON.stringify(lastProp)` before calling `setDrafts` or `onChange`, and keep `onChange` in a ref so it is not a dependency.

### Variant C: using the callback as a useEffect dependency
Even if you compare values, adding `onChange` to the effect dependency array causes the effect to fire whenever the parent re-renders and re-creates the callback. Store the callback in `useRef` and read `.current` inside the effect instead.