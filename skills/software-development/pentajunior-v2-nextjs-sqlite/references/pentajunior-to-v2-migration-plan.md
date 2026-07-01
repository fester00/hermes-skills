# Переход с legacy pentajunior на pentajunior-v2 в продакшене

> Session: 2026-06-23. Legacy `pentajunior` крутится на порту 3000 под PM2, БД пустая (0 байт). Новый `pentajunior-v2` готов на порту 3001. Nginx проксирует `pentajunior.ru:443` → `localhost:3000`.

## Текущая инфраструктура

| Компонент | Состояние |
|-----------|-----------|
| Legacy `pentajunior` | `/home/natan/pentajunior`, порт 3000, PM2 name `pentajunior`, БД `pentajunior.db` = 0 байт |
| Новый `pentajunior-v2` | `/home/natan/pentajunior-v2`, порт 3001, PM2 name `pentajunior-v2`, БД заполнена |
| Nginx | `/etc/nginx/sites-available/pentajunior` → `proxy_pass http://localhost:3000` |
| SSL | `/etc/nginx/ssl/fullchain.crt`, `/etc/nginx/ssl/certificate.key` |
| Домен | `pentajunior.ru`, `www.pentajunior.ru` |

## Варианты миграции

### Вариант 1 — Переключение nginx на порт 3001 (рекомендуется)

Самый быстрый, легко откатить.

```bash
# 1. Подготовить v2
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
cd /home/natan/pentajunior-v2
rm -rf .next
npm run build
pm2 start ecosystem.config.js   # или pm2 restart pentajunior-v2

# 2. Проверить, что v2 отвечает на 3001
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/

# 3. Отредактировать nginx
sudo sed -i 's|proxy_pass http://localhost:3000;|proxy_pass http://localhost:3001;|' \
  /etc/nginx/sites-available/pentajunior

# 4. Проверить конфиг и перезагрузить
sudo nginx -t
sudo systemctl reload nginx   # graceful reload, downtime ~1-2 сек

# 5. Проверить прод
open https://pentajunior.ru

# 6. Остановить legacy
pm2 stop pentajunior
pm2 save
```

**Преимущества:** минимальный downtime, один шаг отката (вернуть `3000` и reload nginx).
**Недостатки:** внутри проекта порт остаётся 3001; ссылки/конфиги могут забыть это.

### Вариант 2 — Замена директории и порта 3000

Более «чистый» — новый проект занимает привычный путь и порт.

```bash
# 1. Остановить оба
pm2 stop pentajunior
pm2 stop pentajunior-v2
pm2 save

# 2. Переименовать директории
mv /home/natan/pentajunior /home/natan/pentajunior-old
mv /home/natan/pentajunior-v2 /home/natan/pentajunior

# 3. Поменять порт в ecosystem.config.js с 3001 на 3000
sed -i "s|args: 'start --port 3001'|args: 'start --port 3000'|" \
  /home/natan/pentajunior/ecosystem.config.js
sed -i 's|PORT: 3001|PORT: 3000|' /home/natan/pentajunior/ecosystem.config.js

# 4. Собрать и запустить
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
cd /home/natan/pentajunior
rm -rf .next
npm run build
pm2 start ecosystem.config.js --name pentajunior
pm2 save
```

**Преимущества:** nginx не трогается, проект лежит по привычному пути.
**Недостатки:** больше downtime (30–60 сек), нужно менять git remote/path если CI/ssh скрипты ожидают старый путь.

### Вариант 3 — Blue/Green без downtime

Держать оба процесса, переключать трафик через nginx upstream.

```nginx
upstream pentajunior {
    server localhost:3000;   # blue — legacy
    server localhost:3001;   # green — v2 (backup)
}

# После проверки v2:
upstream pentajunior {
    server localhost:3001;   # green — v2
    server localhost:3000 backup;
}
```

Плюс `ip_hash` или sticky sessions если есть состояние (в Next.js нет серверной сессии, но admin-cookie важна). Избыточно для статического каталога.

## Рекомендуемый план

Для этого проекта оптимален **Вариант 1**:

1. v2 уже запущен на 3001 — проверить его работу.
2. Изменить nginx `proxy_pass` на `localhost:3001`.
3. Graceful reload nginx (~1–2 сек downtime).
4. Проверить домен и ключевые страницы.
5. Остановить legacy pentajunior (3000).
6. (Опционально) потом переименовать директории и переключить v2 на порт 3000 для единообразия.

## Предполётный чек-лист

- [ ] В `pentajunior-v2/.env.local` правильные `ADMIN_PASSWORD`, SMTP, базовый URL.
- [ ] `next.config.ts` v2 не конфликтует с nginx-заголовками (HSTS, X-Frame и т.д.).
- [ ] Редиректы в `next.config.ts` v2 покрывают старые URL товаров.
- [ ] `/robots.txt` и `/sitemap.xml` v2 доступны и корректны.
- [ ] SSL-сертификаты не истекают в ближайшие дни.
- [ ] Почтовый SMTP в v2 работает (форма на `/contacts`).
- [ ] PM2 autorestart и log-rotation настроены для `pentajunior-v2`.

## Откат

Если что-то пошло не так:

```bash
# Вернуть nginx на legacy
sudo sed -i 's|proxy_pass http://localhost:3001;|proxy_pass http://localhost:3000;|' \
  /etc/nginx/sites-available/pentajunior
sudo nginx -t && sudo systemctl reload nginx

# Запустить legacy если он остановлен
cd /home/natan/pentajunior
pm2 start ecosystem.config.js
pm2 save
```
