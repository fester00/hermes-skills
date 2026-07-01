# PostCSS Config Format Fix — Next.js 14 + Tailwind 3.4

## Problem

Using `postcss.config.js` with CommonJS syntax (`module.exports = {...}`) causes
a **Sucrase parse error** during `npx next build`:

```
SyntaxError: Unexpected token, expected "," (2:1)
    at unexpected (...
  ...sucrase/dist/parser/traverser/expression.js:759:20)
```

This happens because Next.js 14's bundled webpack loader (Sucrase) expects ESM
syntax in `.mjs` files.

## Solution

### Step 1: Rename config file

```bash
mv postcss.config.js postcss.config.mjs
```

### Step 2: Use ESM export syntax

```js
/** @type {import('postcss-load-config').Config} */
const config = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};

export default config;
```

### Step 3: Tailwind config should be `.ts`

```ts
import type { Config } from 'tailwindcss'
const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: { extend: {} },
  plugins: [],
}
export default config
```

## Verify

```bash
npx next build
# Should compile without Sucrase parse errors
```

## Environment

- next: 14.2.35
- tailwindcss: 3.4.19
- postcss: 8.5.15
- autoprefixer: 10.5.0
