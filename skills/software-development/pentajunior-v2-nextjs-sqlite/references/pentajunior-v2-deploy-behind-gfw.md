# Deploying pentajunior-v2 from a host with firewall-blocked GitHub and Google Fonts

> Session: 2026-07-21. `deploy.sh` lived at `/home/natan/deploy.sh`, outside the repo, and failed because the host could not reach GitHub or Google Fonts over plain HTTPS. The local xray SOCKS5 proxy (`127.0.0.1:1080`) worked for web traffic but git and `next/font/google` needed explicit configuration and retry logic.

## Environment

- Host: Ubuntu router/server behind network-level blocks.
- `xray` runs on the same host with SOCKS5 inbound on `127.0.0.1:1080`.
- GitHub `https://github.com/...` is blocked at TLS handshake.
- `fonts.googleapis.com` / `fonts.gstatic.com` are also unreachable at build time.
- User launches `./deploy.sh` remotely over SSH from a `zsh` shell.

## Why direct SSH through xray failed

`git pull origin master` over `git@github.com:...` (SSH) was unreliable because the interactive shell's `SSH_AUTH_SOCK` pointed to a GPG agent with no loaded identities. The wrapper that explicitly loaded `~/.ssh/id_ed25519` still failed with `Connection closed by UNKNOWN port 65535`, meaning the xray reality tunnel drops SSH sessions.

The reliable path was **HTTPS git over the local xray SOCKS5 proxy**:

```bash
export http_proxy=socks5h://127.0.0.1:1080
export https_proxy=socks5h://127.0.0.1:1080
git -c http.proxy=socks5h://127.0.0.1:1080 -c http.version=HTTP/1.1 pull origin master
```

Using `socks5h://` (remote DNS resolution) is important; plain `socks5://` can leak DNS.

## Working deploy.sh

```bash
#!/bin/bash
set -e

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 24 >/dev/null 2>&1

cd ~/pentajunior-v2

echo "📥 Получаем изменения..."
# GitHub is blocked at TLS level on this host; route git through the local xray SOCKS5 proxy
for i in 1 2 3 4 5; do
  git -c http.proxy=socks5h://127.0.0.1:1080 -c http.version=HTTP/1.1 pull origin master && break
  echo "⚠️ git pull failed, retrying in 2s... (attempt $i/5)"
  sleep 2
done

echo "📦 Устанавливаем зависимости..."
npm install

echo "🗄️  Применяем миграции базы данных..."
npm run migrate

echo "🔨 Собираем проект..."
# Google Fonts can fail transiently behind the firewall; retry before giving up
for i in 1 2 3; do
  npm run build && break
  echo "⚠️ Build failed, retrying in 3s... (attempt $i/3)"
  sleep 3
done

echo "🔄 Перезапускаем сервер..."
pm2 describe pentajunior-v2 >/dev/null 2>&1 && pm2 reload pentajunior-v2 --update-env || pm2 start /home/natan/pentajunior-v2/ecosystem.config.js

pm2 save

echo "✅ Деплой завершён!"
```

## Key points

1. **Git remote must be HTTPS**, not SSH, for the SOCKS5 proxy path to work reliably:
   ```bash
   git remote set-url origin https://github.com/fester00/penta-junior-v2.git
   ```

2. **`git config http.proxy` alone was not enough** in this environment. Passing `-c http.proxy=... -c http.version=HTTP/1.1` on the command line was reliable; the persistent config was ignored or overridden.

3. **Retry is mandatory.** The xray tunnel to GitHub is unstable; expect `Recv failure: Connection reset by peer` on some attempts.

4. **Google Fonts failures are also transient.** `next/font/google` downloads `Inter` during `npm run build`. A 3-attempt retry loop was enough in practice.

5. **If Google Fonts stays down**, temporarily disable `Inter` in `src/app/layout.tsx`:
   ```tsx
   // import { Inter } from "next/font/google";
   <html lang="ru" data-scroll-behavior="smooth">
     <body>{children}</body>
   </html>
   ```
   Re-enable once `fonts.googleapis.com` / `fonts.gstatic.com` are reachable again.

6. **Keep `deploy.sh` in the repo.** The user kept it at `/home/natan/deploy.sh`, which is not versioned. Re-create it inside `/home/natan/pentajunior-v2/` and symlink from `~` so changes are tracked.

## Verification commands

```bash
# Confirm GitHub is reachable through the proxy
curl -I --socks5-hostname 127.0.0.1:1080 https://github.com/fester00/penta-junior-v2

# Confirm Google Fonts is reachable (used during build)
curl -I --socks5-hostname 127.0.0.1:1080 "https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap"
```

If these work, the deploy script with retry loops should succeed.
