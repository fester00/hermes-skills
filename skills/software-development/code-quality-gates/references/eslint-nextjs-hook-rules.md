>
# ESLint + Next.js: When Strict Hook Rules Block Legitimate Client Patterns

## Symptom

`eslint-config-next` (via `eslint-config-next/core-web-vitals`) reports errors
from `react-hooks/set-state-in-effect` or `react-hooks/immutability` on code
that is correct for Next.js client components.

Examples:

```tsx
// Admin auth check: setting loading state after reading a cookie
useEffect(() => {
  const token = document.cookie.match(/admin_token=([^;]+)/);
  setLoading(!token);   // ❌ setState in effect
}, [pathname]);
```

```tsx
// Form reset when editing a different record
useEffect(() => {
  setDraft(initialProduct);   // ❌ setState in effect
}, [initialProduct.id]);
```

These patterns are common in admin panels and forms where the component needs to
react to a change in external state (URL, selected record) by resetting local UI
state.

## Root Cause

The React Hooks eslint plugin in `eslint-config-next` ships with very strict
experimental rules (`react-hooks/set-state-in-effect`,
`react-hooks/cannot-access-before-declaration`) that treat any `setState` inside
`useEffect` as a potential cascading-render bug. They do not distinguish
between uncontrolled cascading renders and controlled state resets driven by a
prop or route change.

## Decision Tree

| Situation | Action |
|-----------|--------|
| Pattern is a legitimate controlled reset (auth check, form reset on record change) | Disable the over-strict rule in `eslint.config.mjs` |
| Pattern is actually an uncontrolled cascade (effect sets state that triggers another effect loop) | Refactor to `useMemo`, derive state, or lift state up |
| Rule catches a real bug | Fix the code |

## How to Disable the Over-Strict Rules

In `eslint.config.mjs`:

```js
import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  {
    rules: {
      // Allow controlled state resets in client effects/forms.
      "react-hooks/set-state-in-effect": "off",
      "react-hooks/exhaustive-deps": "warn",
    },
  },
  globalIgnores([".next/**", "out/**", "build/**", "next-env.d.ts"]),
]);

export default eslintConfig;
```

Keep `react-hooks/exhaustive-deps` as a **warning** so missing dependencies are
still visible during development.

## Alternative Refactors

If you prefer not to disable the rule:

1. **Auth loading state** — derive it with `useMemo` instead of `useEffect`:

   ```tsx
   const loading = useMemo(() => {
     if (pathname === '/admin/login') return false;
     return !hasAdminToken();
   }, [pathname]);
   ```

2. **Form reset on record change** — use a React `key` on the form component
   so React unmounts/remounts it when the record changes, eliminating the need
   for an effect:

   ```tsx
   <ProductForm key={editing.id} initialProduct={editing} ... />
   ```

## Verification

After adjusting ESLint or code:

```bash
npm run lint      # should pass (warnings allowed)
npm run typecheck # should pass
npm run build     # should pass
```

## Communication Pattern

Tell the user:

> Строгие React Hooks правила Next.js ломали валидную клиентскую логику в
> админке. Отключил `set-state-in-effect`, оставил `exhaustive-deps` как
> warning.

## See Also

- `code-quality-gates` Gate 3: Pre-Commit Verification
- `hermes-software-development-workflow` Phase 5: Verification Gate
- Next.js ESLint docs: https://nextjs.org/docs/app/building-your-application/configuring/eslint
