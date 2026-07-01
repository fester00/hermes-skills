# Port conflict when Next.js is managed by PM2

If `next start` keeps restarting on a port even after `pkill -9 -f next`, check whether PM2 is managing the process. In the `pentajunior-v2` session a stale PM2 process named `pentajunior` respawned `npm start --port 3000` immediately after every SIGKILL, holding ports 3000/3001.

## Diagnosis

```bash
ss -ltnp | grep -E ':300[0-2]'
# shows "next-server (v16.2.1)" with parent "npm start --port 3000"

ps aux | grep -E 'npm start|next start' | grep -v grep
# parent PID belongs to PM2 God daemon

pm2 list
# shows app "pentajunior" status online
```

## Resolution

Stop and delete the PM2 app, then verify the port is free:

```bash
pm2 stop pentajunior
pm2 delete pentajunior
sleep 2
ss -ltnp | grep -E ':300[0-2]' || echo 'ports free'
```

## Why plain `pkill` fails

PM2 respawns killed processes within seconds. Killing the child `next-server` or even the parent `npm start` shell does not remove the PM2 entry, so the daemon immediately forks a replacement.

## Prevention

If you no longer want PM2 to manage the dev/prod server, ensure the ecosystem config is also removed or disabled:

```bash
pm2 save
# or delete ecosystem.config.js / pm2 delete all
```

For Hermes-managed background testing, prefer a direct `./node_modules/.bin/next start --port 3001` via `terminal(background=true)` rather than PM2, so `process(action='kill')` actually terminates the server.

## Running pentajunior-v2 on a dedicated port

If the legacy `pentajunior` app is already served by PM2 on port 3000, run `pentajunior-v2` on port 3001. Update `ecosystem.config.js` in the v2 project:

```js
module.exports = {
  apps: [
    {
      name: 'pentajunior-v2',
      script: './node_modules/next/dist/bin/next',
      args: 'start --port 3001',
      cwd: '/home/natan/pentajunior-v2',
      interpreter: '/home/natan/.nvm/versions/node/v24.13.1/bin/node',
      env: {
        NODE_ENV: 'production',
        PORT: 3001,
      },
      // ... autorestart, logs, memory limits
    },
  ],
};
```

Then:

```bash
pm2 start ecosystem.config.js
pm2 save
```

## Related

- `references/nextjs-dev-server-cache-invalidation.md` — full dev-server restart recipe.
- `references/nextjs-node-version-lock.md` — pinning Node v24 for the project.
- `references/strict-three-level-subcategory-routing.md` — port separation example from the same session.
