# Многофото-галерея товара (несколько фото в карточке)

Как устроена поддержка нескольких фото у товара в pentajunior-v2 и как её проверять.

## Модель данных

- Колонка `products.images` (SQLite, `TEXT DEFAULT NULL`) — JSON-массив путей к фото; **первый элемент = обложка**.
- Колонка `products.image` сохранена как производная: сервер всегда пишет `image = images[0] ?? null`. Её читают OG/Twitter (`generateMetadata`), JSON-LD, карточки каталога, `RelatedProducts` — трогать их не нужно.
- Обратная совместимость: если `images` пуст/`NULL`, хелпер `resolveProductImages` возвращает `[image]` (или `[]`, если и `image` нет). Товары с одним фото рендерятся как раньше.
- Миграция в `scripts/migrate.ts` — `add_images_to_products`: `ALTER TABLE ... ADD COLUMN images TEXT` + backfill `UPDATE products SET images = json_array(image) WHERE images IS NULL AND image IS NOT NULL AND trim(image) <> ''`.
- Хелпер `resolveProductImages(p)` в `src/lib/product-utils.ts` — источник истины для рендера и JSON-LD.

## Код

- `src/components/UI/Gallery/ProductGallery.tsx` (client, `"use client"`) — вариант B: главное фото (`next/image` fill, object-fit-contain) + ряд миниатюр `<button>`; при 1 фото миниатюр нет. Управляется `useState(active)`.
- `src/components/UI/Cards/ProductCard.tsx` — рендерит `ProductGallery`, если `resolveProductImages(product).length > 0`, иначе `ProductImagePlaceholder`.
- `src/components/admin/ProductImagesEditor.tsx` (client) — упорядоченный список фото: URL-инпут, ↑/↓, ✕, «Загрузить файл» через `POST /api/admin/upload`, «Добавить фото»; первый помечен «Обложка». При изменении также синхронизирует `image = images[0]`.
- API `api/admin/products/route.ts` (GET/POST) и `[id]/route.ts` (PUT) — принимают `images: string[]`, фильтруют пустые, `image = body.image || images[0] || null`.
- `db.ts`: `images` добавлен во все 4 явных SELECT-списка products + JSON-парсинг в маппере.
- JSON-LD `Product.image` на странице товара — теперь массив всех фото (schema.org допускает массив), fallback — `/images/hero.webp`.

## Подводные камни

- **`browser_exec` блокирует localhost** («URL targets a private or internal address»). Для визуальной проверки локальной сборки поднимай `next start --port 3001` (PM2 :3000 не трогать) и снимай скриншоты через **headless Chromium (Playwright)**: `PLAYWRIGHT_BROWSERS_PATH=/mnt/data/natan-storage/playwright-browsers node script.js`, где `chromium.launch({args:['--no-sandbox']})`. Playwright 1.59 установлен глобально и резолвится через `require('playwright')`.
- **`kill <pid>` от `next start` может оставить дочерний `next-server`** — родителя убьёт, дочка остаётся в списке процессов (порт уже не слушается). Прибирать `pgrep`/`kill -9` отдельно.
- Пересборка `.next` в каталоге, где PM2 уже держит запущенный сервер, **не публикует** изменения: живой сайт отдаёт старую сборку до `pm2 reload` (деплой). Проверяй прод через `curl`, а не только локальную сборку.
- `sqlite3` CLI в системе нет — работай через `python3` (модуль `sqlite3`) или `npm run migrate`.
- Подсчёт миниатюр по подстроке `product-gallery__thumb` в HTML даёт ложный «+1»: подстрока входит и в `.product-gallery__thumbs` (CSS). Считай `product-gallery__thumb ` (с пробелом) или через DOM.

## Как деплоить (проект)

`~/deploy.sh` (pull → npm install → npm run migrate → npm run build → pm2 reload + save). Деплой — только по явной команде пользователя. PM2-процесс `pentajunior-v2` на `127.0.0.1:3000`, прод `https://pentajunior.ru`.
