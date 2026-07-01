# CSS force-push recovery recipe

Real incident: pentajunior-v2, 2026-06-23.

## Scenario

A CSS refactor was committed and pushed to `origin/master`. It broke the production layout. The user needs the site restored to a known-good commit, and the remote branch must also be reset so that other machines do not pull the broken state.

## Preconditions

- You have a known-good commit SHA (e.g., `60b2b76`).
- You have push access to `origin/master`.
- You are sure no teammate pushed after the broken commit.

## Steps

### 1. Identify the last known-good commit

```bash
cd /home/natan/pentajunior-v2
git log --oneline -10
# note the good SHA, e.g. 60b2b76
```

### 2. Restore broken files from that commit

```bash
git show 60b2b76:src/app/globals.css > /tmp/globals_60b2b76.css
cp /tmp/globals_60b2b76.css src/app/globals.css

git show 60b2b76:src/app/contacts/page.tsx > /tmp/contacts_page_60b2b76.tsx
cp /tmp/contacts_page_60b2b76.tsx src/app/contacts/page.tsx
```

### 3. Verify the build

```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
cd /home/natan/pentajunior-v2
npx tsc --noEmit && npm run build
```

### 4. Commit the restore

```bash
git add src/app/globals.css src/app/contacts/page.tsx
git commit -m "Restore contacts page and globals.css from 60b2b76"
```

### 5. Reset local and remote to the good commit

If `origin/master` still contains the broken commits:

```bash
# Reset local master to the known-good commit
git reset --hard 60b2b76

# Force-push it to origin (safe variant)
git push --force-with-lease origin master
```

Why `--force-with-lease`? It aborts if someone else pushed in the meantime, preventing accidental overwrite of a teammate's work.

### 6. Verify remote is clean

```bash
git fetch origin
git log --oneline origin/master -3
```

### 7. Help teammates recover

Anyone who already pulled the broken state should run:

```bash
git fetch origin
git reset --hard origin/master
```

Not just `git pull`, because a plain pull may fast-forward or merge the broken commits back in.

## Pitfalls

- Do NOT use bare `git push --force`. Always use `--force-with-lease`.
- Do NOT leave `origin/master` on the broken commit. Otherwise the next `git pull` reintroduces it.
- If a teammate pushed after the broken commit, coordinate with them instead of force-pushing.

## Related

- `pentajunior-css-rollback-recipe.md` — restoring individual files from a good commit.
