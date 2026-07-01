# Проверка root-level deploy.sh перед запуском

> Session: 2026-06-23. Пользователь отредактировал `/home/natan/deploy.sh`, чтобы он указывал на `~/pentajunior-v2`, и попросил проверить, запустит ли он новый проект.

## Что обычно ломает такой deploy.sh

1. **Неправильная git-ветка.**
   В репозитории `pentajunior-v2` дефолтная ветка называется `master`, а не `main`.
   ```bash
   git pull origin main   # ❌ упадёт с "couldn't find remote ref main"
   git pull origin master # ✅
   ```

2. **Неправильное имя процесса PM2.**
   В `ecosystem.config.js` имя приложения `pentajunior-v2`, а не `pentajunior`.
   ```bash
   pm2 restart pentajunior     # ❌ перезапустит старый legacy-процесс или не найдёт его
   pm2 restart pentajunior-v2  # ✅
   ```

3. **Несовпадение порта.**
   Nginx проксирует на `localhost:3000` или `3001`. В `ecosystem.config.js` должны совпадать:
   - `args: 'start --port 3000'`
   - `env.PORT: 3000`
   После переключения v2 на порт 3000 nginx уже настроен, но процесс `pentajunior` (legacy) занимает порт 3000 — его надо остановить перед стартом v2.

## Корректный фрагмент deploy.sh

```bash
#!/bin/bash
set -e

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 24 >/dev/null 2>&1

cd ~/pentajunior-v2

echo "📥 Получаем изменения..."
git pull origin master

echo "📦 Устанавливаем зависимости..."
npm install

echo "🔨 Собираем проект..."
npm run build

echo "🔄 Перезапускаем сервер..."
if pm2 describe pentajunior-v2 >/dev/null 2>&1; then
  pm2 reload pentajunior-v2 --update-env
else
  pm2 start /home/natan/pentajunior-v2/ecosystem.config.js
fi
pm2 save

echo "✅ Деплой завершён!"
```

## Чек-лист перед первым запуском

- [ ] Ветка в `git pull origin <branch>` — `master`.
- [ ] `pm2 restart` / `pm2 reload` использует имя `pentajunior-v2`.
- [ ] `ecosystem.config.js` указывает порт, который ждёт nginx (`3000` или `3001`).
- [ ] Если v2 переезжает на порт 3000, legacy `pentajunior` остановлен (`pm2 stop pentajunior`).
- [ ] `npm install` заменено на `npm ci`, если нужна воспроизводимость.
- [ ] Есть health-check после старта (например, `curl http://localhost:$PORT`).

## Правило поведения агента

1. **Всегда спрашивай разрешения перед деплоем.** Если пользователь ранее не давал одноразового или постоянного разрешения на запуск `deploy.sh`, не запускай его самостоятельно. Покажи, что именно будет задеплоено (коммиты, изменённые файлы), и попроси подтвердить командой вида «задеплой». Это предотвращает нежелательные изменения на production, особенно когда пользователь сам хочет контролировать переключение инфраструктуры.

2. **Никогда не выполняй `deploy.sh` «просто проверить».** Сначала прочитай файл, найди эти три ловушки и укажи пользователю конкретные строки, которые нужно исправить. После правки можно запускать.
