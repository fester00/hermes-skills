## Pentajunior-v2: port coexistence with legacy pentajunior

Legacy `pentajunior` lives in `/home/natan/pentajunior` and is served by PM2 on port 3000.
Pentajunior-v2 lives in `/home/natan/pentajunior-v2` and must run on port 3001.

## PM2 config for v2 (`/home/natan/pentajunior-v2/ecosystem.config.js`)
```js
{
  name: 'pentajunior-v2',
  script: './node_modules/next/dist/bin/next',
  args: 'start --port 3001',
  cwd: '/home/natan/pentajunior-v2',
  env: { NODE_ENV: 'production', PORT: 3001 }
}
```

## Restoration commands

Restore legacy on 3000:
```bash
cd /home/natan/pentajunior
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
pm2 start ecosystem.config.js
pm2 save
```

Run v2 dev on 3001:
```bash
cd /home/natan/pentajunior-v2
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
./node_modules/.bin/next start --port 3001
```

## Diagnose port conflict
```bash
ss -ltnp | grep ':3000\|:3001'
pm2 list
```

## Kill a stuck v2 server
```bash
kill -9 $(ss -ltnp | grep ':3001' | grep -oP 'pid=\K[0-9]+')
```
