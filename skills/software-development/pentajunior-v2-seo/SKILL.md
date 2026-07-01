---
name: pentajunior-v2-seo
description: End-to-end workflow for SEO optimization of categories, subcategories and products in the pentajunior-v2 Next.js/SQLite project, including meta tags, JSON-LD verification and Yandex Wordcraft data usage.
title: SEO-оптимизация pentajunior-v2
version: 1.0
trigger:
  - pentajunior-v2
  - SEO
  - meta tags
  - категория
  - подкатегория
  - товар
  - title
  - description
  - keywords
  - JSON-LD
  - Wordcraft
---

# SEO-оптимизация pentajunior-v2

Навык описывает end-to-end workflow SEO-оптимизации категорий, подкатегорий и товаров для Next.js/SQLite проекта **pentajunior-v2**.

## Предварительные условия

- Рабочая директория: `/home/natan/pentajunior-v2`.
- Node.js v24.13.1 через nvm (см. [hermes-agent] для работы с nvm в фоновых процессах).
- База данных: `pentajunior.db` (SQLite).
- Поля мета-данных: `meta_title`, `meta_description`, `page_description`, `keywords`, `seo_text`, `features`, `pack`, `price`, `price_unit`, `image`.
- В `page.tsx` категории и товара дублирование бренда убрано: `meta_title` из БД используется как есть.
- Пользователь предпочитает **одноразовое/постоянное одобрение** действий, не любит повторные WebUI-запросы.

## Workflow

### Режим 1: SEO-аудит (когда пользователь просит «проанализируй SEO»)

1. **Получить данные из SQLite** напрямую — без запуска dev-сервера:
   ```bash
   cd /home/natan/pentajunior-v2
   python3 /home/natan/.hermes/skills/software-development/pentajunior-v2-seo/references/pentajunior-seo-sqlite-audit.py
   ```
2. **Проверить build output:**
   ```bash
   cd /home/natan/pentajunior-v2 && npx tsc --noEmit && npm run build
   ```
3. **Проверить сгенерированный HTML** для одной страницы каждого типа:
   - категория: `.next/server/app/production/{slug}.html`
   - подкатегория: `.next/server/app/production/{cat}/{sub}.html`
   - товар: `.next/server/app/production/{cat}/{sub}/{product}.html`
   - искать: `<title>`, `<meta name="description">`, `<h1>`, `application/ld+json`, `canonical`, `og:title`.
4. **Собрать отчёт** по 7 категориям: техническое SEO, on-page SEO, контент, коммерческие факторы, поведенческие факторы, JSON-LD, AI-поиск/GEO.
5. **Сохранить отчёт** в Obsidian `Projects/pentajunior-v2-seo-audit-YYYY-MM-DD.md` и обновить `Projects/MOC — Projects.md`.

### Режим 2: SEO-правки (когда пользователь одобрил изменения)

1. **git pull** перед правками (пользователь может сам запушить изменения без предупреждения).
2. **Никогда не запускать `deploy.sh` без явного одобрения пользователя.** Пользователь прямо попросил: «не делай пожалуйста деплой без моего разрешения =) лучше спроси». После push сообщать, что деплой готов, и ждать команды «задеплой».
3. **Прочитать SEO-отчёт** (`.md` файл), который предоставляет пользователь.
4. **Извлечь текущие метаданные** из SQLite:
   - категория по `slug`,
   - все подкатегории по `category_id`,
   - все товары по `subcategory_id`.
5. **Составить черновик** мета-тегов:
   - `meta_title` — **≤70 символов** (цель для Яндекс-сниппета), с коммерческими словами («купить», «от производителя»), бренд-суффикс `| Пента Юниор` добавляем в БД;
   - `meta_description` — **120–160 символов**, без дублирования бренда;
   - `page_description` — краткое описание под H1 (можно длиннее description), не путать с `seo_text`;
   - `keywords` — 5–7 релевантных запросов;
   - `seo_text` — если отчёт содержит SEO-блок, вставлять в `seo_text` категории/подкатегории в соответствии с контекстом. **Краткий подзаголовок/H1 support** → `page_description`, **полный SEO-блок с H2/H3** → `seo_text`.
6. **Показать черновик** и получить одобрение (одноразовое).
7. **Создать backup БД** перед изменениями: `pentajunior.db.seo-<cat>-backup-<YYYYMMDD-HHMMSS>`.
8. **Внести изменения** в `categories`, `subcategories`, `products`.
9. **Запустить аудит JSON-LD**:
    ```bash
    python3 /home/natan/.hermes/skills/software-development/pentajunior-v2-seo/references/seo_jsonld_audit.py
    ```
10. **Проверить и собрать**:
    ```bash
    cd /home/natan/pentajunior-v2 && npx tsc --noEmit && npm run build
    ```
    Build gate обязателен перед заявлением о завершении.
11. **git add pentajunior.db**, commit, push в `master`.
12. **Деплой только по команде пользователя.** После push сообщить: «Изменения запушены. Деплой не делаю без твоего разрешения — скажи «задеплой», когда будешь готов».

## Добавление недостающих товаров

Если категория/подкатегория пустые или содержит только агрегированный товар:
- взять данные с legacy-сайта `https://penta-junior.ru/production/<category>/`;
- добавить новые товары в пустые подкатегории, сохранив структуру `products`;
- заполнить `template_data`, `features`, `pack`, `keywords`.

## JSON-LD: что проверять

- **Глобальный** `Organization` / `WebSite` / `LocalBusiness` в `layout.tsx` ссылается на `/logo.png` — файл должен быть в `public/`.
- **Категория** (`[category]/page.tsx`): `CollectionPage` + `ItemList` подкатегорий + `BreadcrumbList`.
- **Подкатегория** (`[category]/[subcategory]/page.tsx`): `CollectionPage` + `ItemList` товаров, в каждом `Product` должен быть `offers` с числовой ценой.
- **Товар** (`[category]/[subcategory]/[product]/page.tsx`): `Product` + `BreadcrumbList`, `offers.price` очищается от пробелов и запятых, `priceValidUntil` = +1 год.

## JSON-LD: отладка в рантайме

- Если админка или страница падает с `SyntaxError: Unexpected end of JSON input`, сначала проверить **все поля, которые парсятся через `JSON.parse`** (`related_categories`, `features`, `keywords`, `stock_info`, `template_data`, `columns_json`, `rows_json`), а не только то поле, которое упоминается в stack trace. Next.js может маскировать реальный источник.
- Для быстрой диагностики API выполнить `curl /api/admin/categories`, `/api/admin/subcategories`, `/api/admin/products` с авторизацией, либо воспроизвести логику route локально через `sqlite3` + `json.loads`.

## JSON-LD: отладка в рантайме

- Если админка или страница падает с `SyntaxError: Unexpected end of JSON input`, сначала проверить **все поля, которые парсятся через `JSON.parse`** (`related_categories`, `features`, `keywords`, `stock_info`, `template_data`, `columns_json`, `rows_json`), а не только то поле, которое упоминается в stack trace. Next.js может маскировать реальный источник.
- Для быстрой диагностики API выполнить `curl /api/admin/categories`, `/api/admin/subcategories`, `/api/admin/products` с авторизацией, либо воспроизвести логику route локально через `sqlite3` + `json.loads`.
- Если `/api/admin/categories` падает, но данные в SQLite выглядят нормально, перезапустить dev-сервер — Next.js мог кэшировать старый handle. После обновления кода API требуется перезапуск.

## JSON-LD: распространённые ошибки и исправления

- **Акционная цена** `stock_info.newPrice` должна участвовать в `Offer` вместо обычной `price`, если задана. В `metadata.other` тоже выводить акционную цену.
- **Пустые `features`** у товара ломают fallback `description` в JSON-LD подкатегории. Всегда держать `features` заполненным или использовать `product.meta_description` как fallback.
- **Пустые `meta_title`/`meta_description`/`page_description`** у категорий/подкатегорий/товаров приводят к неполноценным сниппетам и ошибкам JSON-LD. Перед JSON-LD-аудитом проверять все записи.
- **Логотип** `/logo.png` должен существовать в `public/`. Если отсутствует — создать симлинк на `/images/fav.svg` или другой актуальный файл.
- **Цена** в `Offer` должна быть чистой числовой строкой: убрать пробелы, заменить запятую на точку.
- **`openGraph.title` в категории** не должен добавлять `| Пента Юниор`, если `meta_title` уже содержит бренд.
- **`page_description` у категорий и подкатегорий** тоже влияет на рендер и должен быть заполнен.
- **Поле `seo_text` в админке не сохраняется.** Если правки через `/admin/categories` не применяются, проверить, что API `PUT /api/admin/categories/[id]` и `POST /api/admin/categories` включают поле `seo_text` в SQL-запрос. Форма отправляет его, но если сервер игнорирует — обновления пропадают.

## Подводные камни

- **Производитель vs дистрибьютор.** Не пишем «Пента Юниор производит», если компания только официальный дистрибьютор. Для СОЖ/ТЕХМОЛ Экстра формулировка: «ООО «ПЕНТА ЮНИОР» — официальный дистрибьютор ООО «ТЕХГРАНТ» по реализации смазочно-охлаждающих жидкостей».
- **Стиль SEO-текстов и описаний.** Пользователь предпочитает человечный, практический текст без AI-слоупа: конкретно, с пользой, с натуральными внутренними ссылками. Для `page_description` — 2–3 предложения, без общих фраз вроде «широкий ассортимент» и «высокое качество». Пример хорошего тона: «Если не знаете, какой выбрать — начните с Юнисил 9110 или 9500».
- **Рефакторинг CSS — только пошагово.** Не удалять `globals.css`-классы массово по статическому аудиту. Многие классы используются через динамическую генерацию, Bootstrap-состояния или JS. Любое изменение `globals.css` должно сопровождаться `npm run build` и визуальной проверкой ключевых страниц. Массовое удаление классов ломает вёрстку.
- **Админка не сохраняет SEO-текст категории.** Если правки `seo_text` через `/admin/categories` не применяются, проверить, что API `PUT /api/admin/categories/[id]` и `POST /api/admin/categories` включают поле `seo_text` в SQL-запрос. Иначе форма отправляет его, но сервер игнорирует.
- **Sitemap и robots: исключить `/admin`.** Админ-панель (`/admin` и `/admin/*`) не должна попадать в `sitemap.xml` и должна быть запрещена в `robots.ts` через `disallow: ["/admin/"]`. В текущем проекте `/admin` не включена в sitemap, но в `robots.ts` явно не запрещена — рекомендуется добавить.
- **Админка категории: форма редактирования показывает `seo_text`, но PUT не обновляет его.** При обновлении кода API категорий включать `seo_text` в параметры SQL. Проверить через `curl /api/admin/categories` после сохранения.
- `openGraph.title` в категории раньше добавлял `| Пента Юниор` к `meta_title`, что давало дублирование. Исправлено: использовать `meta_title` как есть.
- Description должен быть ≤~160 символов; page_description может быть длиннее.
- Для товаров без `image` используется fallback `/images/hero.webp`. Рассмотреть массовую конвертацию изображений в WebP — см. навык `pentajunior-v2-nextjs-sqlite`, раздел "Image optimization for performance".
- `keywords` хранится как JSON-массив в SQLite.
- После внесения изменений в БД запускать `seo_jsonld_audit.py` **перед** build gate, чтобы поймать пустые мета-поля, некорректные цены или отсутствующие файлы до коммита.
- **Уточнение после Wordcraft:** если появляются данные Яндекс.Wordcraft после первого прохода, можно уточнить `meta_title`/`meta_description` с высокочастотными запросами. Делать refine-коммит отдельным.
- **Blog articles:** для скрытия статьи с сайта добавить поле `published: false` в `src/data/blog/article-XX.ts` и убедиться, что `/blog`, `/blog/[id]`, `RelatedArticles` и `generateStaticParams` фильтруют по `published`. Не удалять файл и не убирать `relatedProducts` — это не скроет статью из блога.

## HTML-семантика и перелинковка

См. `pentajunior-v2-nextjs-sqlite/references/html-semantics-seo-audit.md` для чек-листа:
- единственный `<h1>` на странице,
- структура `seo_text` (внешний `<h2>` + внутренние `<h2>` подразделов),
- `BreadcrumbList` JSON-LD на всех целевых страницах,
- `ItemList` / `ListItem` JSON-LD для списков,
- внутренние ссылки в `seo_text` и связи `related_categories` / `relatedProducts`.

## References

- `references/project-rules.md` — сводка проектных правил pentajunior-v2 (routing, build gate, Node.js, порты PM2, JSON-LD audit step).
- `references/seo-checklist.md` — чеклист проверки JSON-LD и мета-тегов.
- `references/category-admin-api-fix.md` — рецепт исправления API админки, когда поле `seo_text` категории не сохраняется.
- `references/seo_jsonld_audit.py` — актуальный скрипт полного аудита данных для JSON-LD (мета-теги, цены, features, изображения, логотип, валидность JSON). Запускать перед build gate.
- `references/pentajunior-seo-sqlite-audit.py` — быстрый аудит meta_title / meta_description через прямой доступ к SQLite, без запуска dev-сервера.
- `references/humanizer-page-description-examples.md` — approved short category descriptions in the user's preferred human, non-AI style.
- `references/sitemap-robots-admin-disallow.md` — how to keep `/admin` and service routes out of `sitemap.xml` and `robots.txt`.
- `references/html-validate-workflow.md` — how to validate compiled HTML for one page per template type and which validator warnings are actionable.
- `references/seo-audit-report-template.md` — template for producing a structured Yandex SEO audit report from live site checks and SQLite data.
- `references/html-validate-workflow.md` — how to validate compiled HTML for one page per template type and which validator warnings are actionable.