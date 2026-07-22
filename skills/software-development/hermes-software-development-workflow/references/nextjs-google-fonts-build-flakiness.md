# Next.js + Google Fonts Build Flakiness

## Symptom

`npm run build` fails with Turbopack / Next.js font errors like:

```
Turbopack build failed with 1 errors:
[next]/internal/font/google/inter_a21f69b3.module.css:61:8
Module not found: Can't resolve '@vercel/turbopack-next/internal/font/google/font'

Import trace:
  ./src/app/layout.tsx
```

The failing resource is a `.woff2` file from `https://fonts.gstatic.com`.

## Root Cause

`next/font/google` tries to download font files at build time. When
`fonts.gstatic.com` is slow, drops packets, or rate-limits the build host, the
download fails and the build aborts. This is an environmental / network issue,
not a code bug.

## Quick Fix: Wait and Retry

1. Wait 60–120 seconds.
2. Clear the build cache: `rm -rf .next tsconfig.tsbuildinfo`.
3. Run `npm run build` again.
4. Repeat up to 3 times before escalating.

This is the preferred fix when the project already uses Google Fonts and the
user does not want to change the font strategy.

## Stronger Fix: Self-Host or Disable

If flakiness repeats often:

1. **Self-host Inter** — download the font files once, place them under
   `public/fonts/`, and import via CSS `@font-face` or a local `next/font/local`
   setup. Eliminates network dependency during builds.
2. **Temporarily disable Google Fonts** — comment out the `next/font/google`
   import and usage in `src/app/layout.tsx`, fall back to system fonts, and
   re-enable after the network issue passes. This is a last resort because it
   changes rendered output.

## Decision Checklist

| Situation | Action |
|-----------|--------|
| One-off build failure, user wants minimal change | Wait + retry |
| Repeated failures across multiple builds | Self-host Inter |
| User explicitly wants a quick green build | Temporary disable |

## Verification After Fix

Always confirm the build produces the expected number of static pages and that
no font errors remain in the terminal output.

## Communication Pattern

Tell the user:

> Билд упал на скачивании шрифта Inter с Google Fonts (проблема сети). Пробую
> пересобрать через минуту.

If the user wants a different strategy, ask before disabling or self-hosting.

## See Also

- `hermes-software-development-workflow` Phase 5: Verification Gate
- Next.js docs: https://nextjs.org/docs/app/building-your-application/optimizing/fonts
