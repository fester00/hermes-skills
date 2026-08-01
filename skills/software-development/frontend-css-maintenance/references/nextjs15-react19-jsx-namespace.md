# React 19 / TypeScript 5 — `JSX.Element` is undefined

## Symptom

`tsc --noEmit` in a Next.js 15 + React 19 project with `strict: true` reports:

```
error TS2503: Cannot find namespace 'JSX'.
```

for component return types declared as `JSX.Element`.

## Root cause

React 19 removes the global `JSX` namespace. The legacy return type `JSX.Element` no longer resolves. TypeScript 5 with `strict: true` surfaces the error immediately.

## Fix

Use `React.JSX.Element` (or `React.ReactElement`, or rely on inference):

```tsx
// ❌ breaks under React 19 / TS 5 strict
export function Navbar(): JSX.Element { ... }

// ✅ resolves correctly
export function Navbar(): React.JSX.Element { ... }
```

## Scope

- Any component explicitly typed with a return type.
- Client components (`"use client"`) and Server Components are equally affected.
- Does not apply to inferred return types; leaving off the return type also works.

## Verification

```bash
npx tsc --noEmit
```

## Related

- React 19 release notes: global JSX namespace removal.
- `frontend-css-maintenance` SKILL.md references this file under Pitfalls / References.
