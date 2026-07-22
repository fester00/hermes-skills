# Rolling pentajunior-v2 production back to a known-good commit

Use this when the site breaks after a deploy and the user wants to restore the last working state immediately.

## When

- Production CSS/JS chunks return 500/404 after deploy.
- PM2 error log shows `ChunkLoadError`, `prerender-manifest.json` missing, or other partial-build symptoms.
- The user says "откатись на коммит X" / "вернёмся на рабочий коммит".

## Why a hard reset is safe here

`pentajunior-v2` is deployed from a single `master` branch on one host. The DB (`pentajunior.db`) is **not** part of the git tree; migrations run via `npm run migrate`. Rolling back the code does not roll back the database. If the broken deploy did not run migrations, a code rollback is low-risk. Always check whether migrations changed schema or data before claiming DB safety.

## Steps

1. Confirm the target SHA and that it is reachable locally:
   ```bash
   cd /home/natan/pentajunior-v2
   git log --oneline -10
   git show --stat <sha>
   ```

2. Clean the working tree and reset:
   ```bash
   git checkout -- package-lock.json  # in case it is modified
   git reset --hard <sha>
   ```

3. Force-push to make remote match:
   ```bash
   git push --force origin master
   ```
   Do not run `git pull` after this unless the user explicitly asks.

4. Rebuild and reload PM2 on the production host:
   ```bash
   export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
   cd /home/natan/pentajunior-v2
   rm -rf .next tsconfig.tsbuildinfo
   npm run build
   pm2 reload pentajunior-v2 --update-env
   ```

5. Verify that repo and production are on the same commit:
   ```bash
   # local HEAD must equal origin/master
   git rev-parse HEAD origin/master

   # production HTML must match local build signature
   curl -sL https://pentajunior.ru/ | grep -o 'data-scroll-behavior="smooth"' | head -1
   # and static chunks must return 200
   curl -sI https://pentajunior.ru/_next/static/chunks/<name>.css | head -1
   ```

## Common mistakes

- Forgetting to wipe `.next` and `tsconfig.tsbuildinfo` before rebuild.
- Treating `pm2 reload` exit code 0 as proof of success — always check `pm2 logs` and static chunk HTTP status.
- Assuming the rollback fixed the DB. Verify `npm run migrate` status if schema/data changed.
- Hard-resetting without force-pushing — the next `deploy.sh` run would pull the broken commits again.
