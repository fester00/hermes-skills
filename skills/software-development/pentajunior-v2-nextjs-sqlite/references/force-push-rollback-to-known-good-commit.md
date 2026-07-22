>
# Force-Push Recovery to a Known-Good Commit on `origin/master`

## When to use this recipe

- The user says the remote repository is "испорчено" (broken / contains wrong commits).
- A specific local commit SHA is identified as the last known-good state.
- The goal is to restore `origin/master` to that exact commit, discarding all
  commits pushed after it.

## Symptom

```bash
$ git log --oneline --graph --all -10
* 4008246 test(pricing): add vitest + unit tests for pricing helpers   (local master)
* 75ea374 refactor(seo): extract shared JSON-LD helpers to lib/seo.ts
* ...
| * a691451 refactor(table): remove SyncScrollTable, keep single top scrollbar via CSS rotateX   (origin/master before force-push)
| * 730e49b feat(table): dual top/bottom scrollbars for spec tables
| |/
* 1295d55 seo(shlangi): add detailed seo_text with two styled tables   (known-good base)
```

`origin/master` is ahead of the desired commit and contains work that must be
removed.

## Recovery steps

1. Confirm the local commit SHA matches the desired state:
   ```bash
   git log --oneline -1 <sha>
   ```

2. Clean any uncommitted changes in the working tree if present:
   ```bash
   git checkout -- .
   ```

3. Point local `master` to the known-good commit:
   ```bash
   git checkout master
   git reset --hard <sha>
   ```

4. Force-push the known-good commit to `origin/master`:
   ```bash
   git push --force origin <sha>:master
   # or, if already on master:
   git push --force origin master
   ```

5. Verify both local and remote are aligned:
   ```bash
   git rev-parse master
   git rev-parse origin/master
   # Both should print the same SHA.
   ```

6. Do **not** run `git pull` afterwards unless the user explicitly asks.
   Pulling would re-fetch the discarded commits from other contributors' clones.

## Communication pattern

Tell the user:

> Откатил `origin/master` на <short-sha> <subject>. Локальный и удалённый
> master теперь совпадают. Деплой пока не делал.

## Safety rules

- Only do this when the user explicitly asks for a rollback to a specific SHA.
- Never force-push to `master` without confirming the target commit first.
- If the user has collaborators, warn them that they will need to reset their
  local branches to the new `origin/master`.
- After the rollback, run the build gate before any further work:
  ```bash
  npm run typecheck && npm run build
  ```

## See Also

- `pentajunior-v2-nextjs-sqlite` § "Resetting repo state to a known-good commit"
- `hermes-software-development-workflow` Phase 6: Finishing
