# Recovery recipe: broken `globals.css` refactor

Real incident: pentajunior-v2, 2026-06-23.

## What happened

A big-bang cleanup of `src/app/globals.css` deleted/merged many selectors and broke the site layout. The broken commits were already pushed to `origin/master`. The fix required reverting to the last known-good commit and restoring the contacts-page redesign separately.

## Last known-good commit

```bash
git log --oneline -10
# found: 60b2b76 Redesign /contacts page: variant 1 layout, add Silagerm partner...
```

## Steps to restore one file from a good commit

```bash
# 1. Restore the broken file from the known-good commit
git show 60b2b76:src/app/globals.css > /tmp/globals_60b2b76.css
cp /tmp/globals_60b2b76.css src/app/globals.css

# 2. If the page also changed, restore it the same way
git show 60b2b76:src/app/contacts/page.tsx > /tmp/contacts_page_60b2b76.tsx
cp /tmp/contacts_page_60b2b76.tsx src/app/contacts/page.tsx

# 3. Build
cd /home/natan/pentajunior-v2
npx tsc --noEmit && npm run build

# 4. Commit and push
git add src/app/globals.css src/app/contacts/page.tsx
git commit -m "Restore contacts page redesign (60b2b76) and contacts CSS"
git pull --rebase  # if origin is ahead
# if rebase conflicts: abort and force-with-lease only after confirming safe
git push
```

## When to force push

If `origin/master` contains the broken CSS refactor and no one else has pushed after it, you can reset local state to the good commit and then:

```bash
git reset --hard 60b2b76
git push --force-with-lease origin master
```

Only use `--force-with-lease`, never bare `--force`, and only when you are sure no teammate pushed in the meantime.

## Why the layout broke

- Static grep for unused classes flagged `.footer`, `.navbar-collapse`, `.product-detail-*` etc. as unused, but some were used by shared components or Bootstrap.
- Merging `.spec-table thead th,` left a trailing comma and invalid CSS block.
- The cleanup was combined with unrelated page redesign, making rollback harder.

## Lessons

1. Static class-name grep is a candidate list, not a deletion list.
2. Build after every small CSS change.
3. Keep redesign and cleanup in separate commits.
4. Note the last known-good commit before risky work.
