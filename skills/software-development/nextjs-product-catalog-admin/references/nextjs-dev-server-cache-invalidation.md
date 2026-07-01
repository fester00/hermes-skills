# Кэширование Next.js dev-сервера: когда изменения не появляются

При работе с Next.js 16 + Turbopack + `next start` важно понимать разницу между режимами и жизненным циклом кэша.

## Разница режимов

| Команда | Пересборка на лету | Кэш | Когда использовать |
|---|---|---|---|
| `next dev` | Да, Hot Module Replacement | В памяти | Активная разработка |
| `next start` | Нет | `.next/server`, `.next/static` | Проверка production-сборки |

## Симптомы устаревшей сборки

- CSS-изменения не применяются.
- В браузере виден старый JSX/HTML (например, удалённые элементы всё ещё есть).
- `curl` отдаёт HTML со старыми классами, хотя `git status` показывает новый код.

## Почаговое решение

1. **Убедиться, что нет зомби-процессов (особенно PM2-запущенных)**
   ```bash
   ss -tlnp | grep 3001
   pkill -9 -f 'next start --port 3001'
   pkill -9 -f 'next-server'
   pm2 list
   pm2 stop pentajunior
   pm2 delete pentajunior
   ```

   Если порт всё ещё занят, `next-server` может быть запущен через `npm start`/`PM2`. Ищи родительский `npm start` и убивай его вместе с дочерними процессами:
   ```bash
   pgrep -a npm
   kill -9 <PID_npm_start_parent>
   ```

   Если `pkill` не убивает процесс (например, `next start` запущен через `npx`/оболочку), найди PID через `ss` и убей вручную:
   ```bash
   ss -tlnp | grep 3001   # покажет PID
   kill -9 <PID>
   ```

2. **Полная пересборка**
   ```bash
   rm -rf .next
   npm run build
   ```

3. **Запуск dev-сервера заново**
   ```bash
   npx next start --port 3001
   ```

   В некоторых окружениях `npx` может не находиться в `PATH` у фоновых процессов; тогда используй полный путь:
   ```bash
   ~/.nvm/versions/node/v24.13.1/bin/npx next start --port 3001
   ```

4. **Проверка по HTTP**
   ```bash
   curl -s http://localhost:3001/production | grep -o 'category-card-link\|bi-check-circle' | sort | uniq -c
   ```

## Почему `next start` не видит изменения

`next start` обслуживает артефакты из `.next/server` и `.next/static`. Он не пересобирает код автоматически. Даже если файл `SKILL.md` или `.tsx` изменён, сервер продолжает отдавать старую HTML/CSS до следующего `npm run build`.

## Почему иногда помогает только `rm -rf .next`

Next.js инкрементально обновляет `.next`. При некоторых изменениях (особенно CSS-переменных, классов, глобальных стилей) старый кэш может конфликтовать с новым. Полная очистка гарантирует чистую сборку.

## Практическое правило для проектов пентаюниор

После любого изменения CSS или компонента карточки:

```bash
cd /home/natan/pentajunior-v2
pkill -9 -f 'next start --port 3001'
rm -rf .next
npm run build
npx next start --port 3001
```

## Связанные приёмы

- Всегда проверяй `npm run build` и `npx tsc --noEmit` перед коммитом.
- Для быстрой визуальной проверки можно открыть статический HTML из `.next/server/app/<page>.html`, но финальная проверка — через запущенный сервер.
