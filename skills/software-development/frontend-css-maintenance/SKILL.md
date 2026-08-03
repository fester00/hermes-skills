---
name: frontend-css-maintenance
description: "Safely audit, clean up, and refactor large global CSS files in Next.js / React projects without breaking production layouts."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [CSS, Refactoring, Cleanup, Next.js, globals.css, Frontend]
    related_skills: [superpowers-workflow, code-quality-gates, simplify-code]
---

# Frontend CSS Maintenance

How to safely audit, shrink, and refactor large global stylesheets (typically `globals.css` or `index.css`) in Next.js / React projects where a single malformed edit can break the entire site layout.

## When to use

- The global CSS file is >50 KB or >2000 lines.
- You suspect dead CSS classes, duplicate selectors, or unused component styles.
- Build passes but visual layout is wrong / broken after CSS changes.
- You need to roll back CSS changes quickly without losing unrelated work.

## Core principles

1. **Never treat static class-name grep as proof a class is unused.** Classes can be assembled dynamically, injected by Bootstrap/JS libraries, or referenced from strings. Static analysis only gives *candidates* for manual review.
2. **One change at a time, then build.** Do not batch deletions, merges, and moves in a single commit.
3. **Keep layout/design changes separate from cleanup changes.** If a redesign and a cleanup happen together, you cannot tell which one broke the page.
4. **Always have a fast rollback path.** Know the last known-good commit hash before touching CSS.
5. **Run the build gate after every edit.** `tsc --noEmit` alone is not enough; CSS syntax errors can fail the Next.js build only at `next build`.

## Step-by-step workflow

### 1. Snapshot and audit

- Note the file size, line count, rule count, duplicate selectors, and `!important` count.
- Generate a candidate list of unused classes using static analysis (grep over `className=`).
- **Use PurgeCSS as a fast, high-confidence first pass:**
  ```bash
  npx -y purgecss \
    --css src/app/globals.css \
    --content "src/**/*.{ts,tsx}" \
    --output /tmp/globals-purged.css
  ```
  Compare line counts / selector counts. PurgeCSS removes rules whose selectors never appear in the scanned content, which is much more reliable than class-name grep alone.
- **Cross-check PurgeCSS output with grep** for any class whose removal looks risky:
  - classes assembled dynamically (`classNames(...)`, template literals, conditional arrays)
  - classes injected by markdown content or third-party JS
  - Bootstrap classes that might be referenced implicitly
- Save the audit as a markdown file in the workspace for the user to review.

Use the audit script: `references/css-audit-script.py`

### 0. React 19 + TypeScript 5 return-type pitfall

Before auditing, check whether the project uses React 19 with TypeScript 5 strict mode. If component return types are written as `JSX.Element`, `tsc --noEmit` will fail with:

```
error TS2503: Cannot find namespace 'JSX'.
```

React 19 removes the global `JSX` namespace. Replace `JSX.Element` with `React.JSX.Element` (or `React.ReactElement`, or omit the return type). See `references/nextjs15-react19-jsx-namespace.md` for the full recipe and verification command.

### 0b. framer-motion variant typing under strict mode

If the project uses framer-motion with `strict: true`, inline animation objects without type annotations will fail `tsc --noEmit` with errors like:

```
Type 'string' is not assignable to type 'AnimationGeneratorType | undefined'.
Type 'number[]' is not assignable to type 'Easing[]'.
Type '{ ... }' is not assignable to type 'Variants'.
```

Annotate the variant object as `Variants` (imported as a type from `framer-motion`) or cast string-literal easing values with `as const`. See `references/framer-motion-strict-variants.md` for the exact patterns and verification command.

### 2. First pass: only safe wins

Allowed first-pass actions (low risk):
- Delete CSS files that are completely unused (e.g., `page.module.css` with zero `styles.xxx` references).
- Merge duplicate selectors that are **obvious** copies of the same block and not inside `@media`.
- Remove classes that are confirmed unused by both grep **and** a manual code search for dynamic assembly.

Forbidden in the first pass:
- Renaming classes.
- Moving rules between files.
- Touching Bootstrap overrides unless you are certain of the impact.
- Deleting classes that are referenced via string concatenation, template literals, or conditional arrays.

### 3. Build after every commit

```bash
npx tsc --noEmit && npm run build
```

If the build fails:
- Stop. Do not fix forward by adding more CSS.
- Identify the bad edit. Common failures:
  - Leftover comma after merging selector lists (`.foo, }`).
  - Deleted a class still used in JSX.
  - Collided with Bootstrap classes.
- Revert the exact change that caused the failure.

### 4. Push and verify on the live preview

After build passes, push and check the actual pages visually (or ask the user to verify). CSS can compile but still render wrong.

## Recovery when layout breaks

If the user reports broken layout:

1. Ask which page is broken and what looks wrong.
2. Find the last known-good commit: `git log --oneline -10`.
3. Restore the broken file from that commit:
   ```bash
   git show <good-commit>:src/app/path/to/file.ext > /tmp/file.ext
   cp /tmp/file.ext src/app/path/to/file.ext
   ```
4. If the file was changed in multiple recent commits, restore the entire file rather than trying to surgically patch it.
5. Commit the restore and push.
6. If the broken commits were already pushed to `origin/master`, reset both local and remote to the known-good commit using `--force-with-lease`. See `references/css-force-push-recovery.md`.
7. Do **not** immediately retry the same cleanup. Re-audit, identify the exact offending class/selector, and apply only that single fix.

## Pitfalls

- **Merging `.spec-table thead th,` without a second selector** leaves a trailing comma and breaks the CSS parser.
- **Deleting `.footer`, `.navbar-collapse`, `.product-detail-*` classes** can break shared components even if a quick grep says they are unused in `className=` (they may be used by Bootstrap, by JS state toggles, or by child components).
- **Combining redesign + cleanup in one commit** makes rollback harder. Always separate them.
- **`git push --force-with-lease` on shared branches** is acceptable only when recovering from a broken pushed state and after confirming no one else pushed in the meantime.
- **"Broken icon background" is often the icon silhouette fighting the container shape**, not a CSS background/opacity bug. Verify computed styles and the SVG viewBox before rewriting CSS. See `references/diagnosing-broken-icon-backgrounds.md`.

## Verification checklist

- [ ] File size and line count recorded before and after.
- [ ] PurgeCSS (or equivalent) run and diff reviewed.
- [ ] Build passes (`tsc --noEmit && npm run build`).
- [ ] No trailing commas or empty selector lists.
- [ ] Deleted classes manually verified as unused.
- [ ] Key pages visually checked (home, category, product, contacts, admin).
- [ ] Rollback commit hash noted before risky changes.

## References

- `references/css-audit-script.py` — static audit of duplicate and unused CSS classes.
- `references/pentajunior-css-rollback-recipe.md` — real recovery recipe from a broken `globals.css` refactor.
- `references/css-force-push-recovery.md` — when a broken CSS refactor has already been pushed to `origin/master`, how to reset local and remote state to the last known-good commit safely.
- `references/purgecss-dead-code-recipe.md` — using PurgeCSS to remove unused rules from `globals.css` and verify the result.
- `references/diagnosing-broken-icon-backgrounds.md` — when icons appear to have broken/artifacted backgrounds, verify the icon silhouette against the container shape before editing CSS.
- `references/silicone-landing-contacts-redesign.md` — example of redesigning contact-card icon wells from small circles to squircle wells for non-square Lucide icons.
- `references/framer-motion-strict-variants.md` — annotate framer-motion variants as `Variants` or use `as const` to avoid strict-mode `tsc` failures.
- `references/nextjs15-react19-jsx-namespace.md` — replace `JSX.Element` with `React.JSX.Element` under React 19 + TypeScript 5.
- `references/uniform-product-card-height.md` — patterns for making product cards the same height in a Tailwind grid while keeping badges and pricing aligned at the bottom.

## Related skills

- `code-quality-gates` — build gates and verification workflows.
- `frontend-efficiency-audit` — performance review and optimization.