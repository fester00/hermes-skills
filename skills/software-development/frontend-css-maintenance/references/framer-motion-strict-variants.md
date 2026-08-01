# framer-motion + TypeScript strict-mode variant typing

When using framer-motion in a TypeScript project with `strict: true` or strict inference, inline animation objects often fail `tsc --noEmit` because their `type`, `ease`, or `transition` fields widen to `string` or `number[]` instead of literal unions.

## Common errors

```
Type 'string' is not assignable to type 'AnimationGeneratorType | undefined'.
Type 'string' is not assignable to type 'Easing | Easing[] | undefined'.
Type 'number[]' is not assignable to type 'Easing[]'.
Type '{ ... }' is not assignable to type 'Variants'.
```

These usually come from this shape:

```tsx
const modalVariants = {
  hidden: { opacity: 0, scale: 0.92 },
  visible: {
    opacity: 1,
    transition: { type: 'spring', ease: [0.25, 0.46, 0.45, 0.94] },
  },
};
<motion.div variants={modalVariants} />
```

TypeScript widens `'spring'` to `string` and the cubic-bezier array to `number[]`, so the variant object no longer satisfies `Variants`.

## Fix

### 1. Annotate the variant object as `Variants`

```tsx
import { motion } from 'framer-motion';
import type { Variants } from 'framer-motion';

const modalVariants: Variants = {
  hidden: { opacity: 0, scale: 0.92, y: 40 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      type: 'spring',
      stiffness: 260,
      damping: 24,
      delayChildren: 0.1,
      staggerChildren: 0.06,
    },
  },
  exit: { opacity: 0, scale: 0.96, y: 20, transition: { duration: 0.2 } },
};
```

### 2. Or use `as const` on the whole object

```tsx
const modalVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { type: 'spring' as const } },
} as const;
```

For complex spring/tween configs the `Variants` import is usually cleaner.

### 3. For inline `animate` objects, cast `ease` with `as const`

```tsx
const shakeAnimation = {
  x: [0, -8, 8, -6, 6, -4, 4, 0],
  transition: { duration: 0.5, ease: 'easeInOut' as const },
};

<motion.form animate={shake ? shakeAnimation : {}} />
```

Without `as const`, `'easeInOut'` widens to `string` and `tsc` rejects the object.

## Verification

After adding framer-motion variants, always run:

```bash
npx tsc --noEmit
```

Next.js `npm run build` also checks types, but `tsc --noEmit` is the fastest feedback loop for these exact variant-typing failures.

## References

- framer-motion `Variants` type definition in `node_modules/framer-motion/dist/index.d.ts`
