# Deploy Script GitHub Access — pentajunior-v2

## Context

On the Hermes host, native HTTPS connections to `github.com` fail at the TLS handshake:

```
fatal: unable to access 'https://github.com/fester00/penta-junior-v2.git/':
gnutls_handshake() failed: The TLS connection is non-properly terminated.
```

The host runs a local xray proxy with listeners:

| Listener | Address | Works for |
|----------|---------|-----------|
| SOCKS5 | `127.0.0.1:1080` | HTTPS git with explicit `-c http.proxy=socks5h://127.0.0.1:1080` |
| SOCKS5 | `127.0.0.1:10808` | Alias, also SOCKS5 |
| HTTP proxy | `127.0.0.1:1081` | `curl` to GitHub, **not reliable for `git pull`** |

Verified behavior on 2026-07-18:
- `http_proxy=http://127.0.0.1:1081 git pull origin master` — **fails** with `Recv failure: Connection reset by peer` during TLS handshake.
- `git -c http.proxy=socks5h://127.0.0.1:1080 -c http.version=HTTP/1.1 pull origin master` — **works**.
- `GIT_SSH_COMMAND="ssh -o ProxyCommand='nc -X 5 -x 127.0.0.1:1080 %h %p' ..." git pull` over SSH remote — works from `bash` manually, but **fails from `zsh`/`./deploy.sh`** with `Connection closed by UNKNOWN port 65535`, because `SSH_AUTH_SOCK` points to a GPG agent with no SSH identities.

**Recommended production deploy path: HTTPS git over xray SOCKS5 with explicit per-command config and a retry loop.**

## Setup

### 1. Ensure remote is HTTPS

```bash
cd ~/pentajunior-v2
git remote set-url origin https://github.com/fester00/penta-junior-v2.git
git remote -v
```

### 2. Patch deploy.sh

Replace the plain `git pull origin master` with a retry loop:

```bash
echo "📥 Получаем изменения..."
for i in 1 2 3 4 5; do
  git -c http.proxy=socks5h://127.0.0.1:1080 -c http.version=HTTP/1.1 pull origin master && break
  echo "⚠️ git pull failed, retrying in 2s... (attempt $i/5)"
  sleep 2
done
```

Why explicit `-c` flags instead of `git config http.proxy`:
- `git config http.proxy` in `.git/config` may be ignored by libcurl in some env states.
- `-c http.proxy=... -c http.version=...` is honored reliably in every shell tested (bash, zsh, non-interactive).

### 3. For manual pushes from this host

```bash
cd ~/pentajunior-v2
git -c http.proxy=socks5h://127.0.0.1:1080 -c http.version=HTTP/1.1 push origin master
```

## Verification

### Check proxy is running

```bash
ss -tlnp | grep -E '1080|1081|10808|xray|v2ray'
```

Expected:

```
LISTEN 0 4096 127.0.0.1:1080 ... users:(("xray",...))
LISTEN 0 4096 127.0.0.1:1081 ... users:(("xray",...))
```

### Test HTTPS through SOCKS5

```bash
curl -sL --socks5-hostname 127.0.0.1:1080 \
  https://github.com/fester00/penta-junior-v2/info/refs?service=git-upload-pack | head -c 200 | xxd
```

Expected: starts with `0000` pack header bytes, not an HTTP error.

### Test git pull through SOCKS5

```bash
cd ~/pentajunior-v2
git -c http.proxy=socks5h://127.0.0.1:1080 -c http.version=HTTP/1.1 pull origin master
```

If this works but `./deploy.sh` fails, the script is probably still using SSH or missing the retry loop.

## Why SSH variant failed in zsh/deploy.sh

When running `./deploy.sh` from `zsh`, the session may set:

```bash
SSH_AUTH_SOCK=/run/user/1000/gnupg/S.gpg-agent.ssh
```

`ssh` tries that agent, finds no SSH identities, and GitHub closes the connection with:

```
Connection closed by UNKNOWN port 65535
fatal: Could not read from remote repository.
```

Workarounds attempted:
- `unset SSH_AUTH_SOCK` in wrapper — works in some shells.
- Forcing a key with `-i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes` — helps but still fails intermittently from `zsh`.

The HTTPS+SOCKS5 variant bypasses SSH entirely and is more reliable.

## Debugging deploy.sh failures

Add `GIT_CURL_VERBOSE=1` to the pull command:

```bash
GIT_CURL_VERBOSE=1 git -c http.proxy=socks5h://127.0.0.1:1080 -c http.version=HTTP/1.1 pull origin master
```

Look for:
- `Connected to 127.0.0.1 (127.0.0.1) port 1080` — proxy reached.
- `SOCKS5 request granted.` — tunnel established.
- `Recv failure: Connection reset by peer` — proxy/server reset; retry usually helps.

## Pitfalls

1. **Do not rely on `http_proxy`/`https_proxy` env vars for `git pull`** on this host. They may work for `curl`/`git push` but fail for pull.
2. **Do not rely only on `git config http.proxy`**. Use explicit `-c` flags in `deploy.sh`.
3. **SSH over SOCKS5 is not reliable from `zsh`/non-interactive shells here** due to GPG-agent interference. Prefer HTTPS+SOCKS5.
4. **Run deploy.sh under the same user that owns the repo and SSH keys**. `sudo ./deploy.sh` will look for root's git config/keys, not natan's.
5. **Add retry loops for both `git pull` and `npm run build`**. The xray reality tunnel can reset intermittently; 3–5 attempts with 2–3s delay solve it.
6. **`npm run build` can fail due to Google Fonts fetch, not code errors.** If the build fails once and succeeds on retry, it is the xray tunnel, not the project.

## One-liner health check

```bash
cd ~/pentajunior-v2
git -c http.proxy=socks5h://127.0.0.1:1080 -c http.version=HTTP/1.1 ls-remote https://github.com/fester00/penta-junior-v2.git HEAD
```

Success prints a commit SHA and `HEAD`.

### 3. Add build retry for transient Google Fonts failures

`next/font/google` in this project fetches `Inter` from `fonts.googleapis.com` / `fonts.gstatic.com` at build time. The xray tunnel can be unstable, so `npm run build` may fail once and succeed on the next attempt. Wrap the build in a retry loop:

```bash
echo "🔨 Собираем проект..."
for i in 1 2 3; do
  npm run build && break
  echo "⚠️ Build failed, retrying in 3s... (attempt $i/3)"
  sleep 3
done
```

If all three attempts fail, fall back to the temporary Inter-removal recipe in `references/google-fonts-gstatic-build-outage.md`.

## Full known-good deploy.sh fragment

```bash
#!/bin/bash
set -e

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 24 >/dev/null 2>&1

cd ~/pentajunior-v2

echo "📥 Получаем изменения..."
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
