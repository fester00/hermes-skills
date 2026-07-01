# Фиксация Node.js версии для проекта

Hermes-окружение по умолчанию использует системный `node` (в данном случае v18). Проект `pentajunior-v2` требует Node.js >= 20.9.0, поэтому используем nvm и фиксируем версию.

## Быстрое использование в сессии

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use v24.13.1
node -v
```

В фоновом процессе Hermes `nvm use` не всегда работает автоматически. Если нужно запустить `next start` в фоне, используй полный путь к Node из nvm:

```bash
/home/natan/.nvm/versions/node/v24.13.1/bin/node ./node_modules/.bin/next start --port 3000
```

Или через `nvm use` внутри одной shell-команды, но не через `npm run start` (которая может подхватить системный node):

```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1 && ./node_modules/.bin/next start --port 3000
```

## Фиксация версии в проекте

### 1. `.nvmrc`

Создать файл `.nvmrc` в корне проекта:

```
v24.13.1
```

Теперь `nvm use` без аргументов переключится на нужную версию.

### 2. `package.json` — engines

```json
"engines": {
  "node": ">=20.9.0",
  "pnpm": ">=9"
}
```

Это не блокирует запуск через npm, но документирует требование и влияет на некоторые CI/CD.

### 3. `ecosystem.config.js` (PM2)

Явно указать интерпретатор Node v24:

```js
module.exports = {
  apps: [{
    name: 'pentajunior',
    script: './node_modules/.bin/next',
    args: 'start',
    cwd: '/home/natan/pentajunior-v2',
    interpreter: '/home/natan/.nvm/versions/node/v24.13.1/bin/node',
    // ...
  }]
};
```

## Проверка

```bash
# Убедиться, что сборка идёт на правильной версии
node -v
cd /home/natan/pentajunior-v2
npm run build
```

## Питфоллы

- **Системный `node` v18.** Простой `npm run build` без `nvm use` выдаст `Error: Node.js version ">=20.9.0" is required`. Всегда активируй nvm перед билдом.
- **Next.js dev server на неправильной версии.** Если dev-сервер запущен на v18, а затем переключился на v24, порт может быть занят старым процессом. Проверяй `pgrep -a next` и при необходимости убивай зомби-процессы.
- **Разные версии в `package-lock.json` и `pnpm-lock.yaml`.** Если проект переключился между npm и pnpm, убедись, что lockfile синхронизирован с выбранным менеджером. `pentajunior-v2` использует pnpm.
- **`.nvmrc` не работает без nvm.** На сервере без nvm нужен другой менеджер версий (n, fnm) или явный путь к Node в systemd/PM2.

## Рекомендуемый стартовый шаблон для `.nvmrc`

```
v24.13.1
```

## Рекомендуемый стартовый шаблон для `ecosystem.config.js`

```js
module.exports = {
  apps: [{
    name: 'pentajunior',
    script: './node_modules/.bin/next',
    args: 'start',
    cwd: process.cwd(),
    interpreter: '/home/natan/.nvm/versions/node/v24.13.1/bin/node',
    env: { NODE_ENV: 'production', PORT: 3000 },
    autorestart: true,
    max_memory_restart: '512M',
  }]
};
```
