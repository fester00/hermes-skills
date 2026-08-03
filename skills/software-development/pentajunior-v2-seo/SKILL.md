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

### Общие правила сессии

- **SEO-источник:** загружать `yandex-seo-optimization` как основной SEO-навык; `pentajunior-v2-seo` — как проектный workflow (SQLite, JSON-LD, build gate, deploy).
- **Последовательность:** сначала править **статические страницы** (`/`, `/production`, `/price`, `/contacts`, блог), затем обрабатывать категории **по одной**, не массово. Внутри категории: категория → подкатегории → товары.
- **Функционально-предметная семантика (обязательно):** каждый `meta_title`, `meta_description` и `H1` категории/подкатегории должен содержать не только название товара/группы, но и **предметное применение** — «для чего используется». Примеры: `силикон для заливки форм под гипс и смолы`, `разделители для опалубки и литья ПУ`, `герметики для электроники и автомобилей`, `СОЖ для станков ЧПУ и фрезерования`. См. `references/functional-semantic-examples.md`.
- **Длины:** `meta_title` — **60–70 символов** (целиться в ~60; 70 — редкий потолок); `meta_description` — **160–170 символов (включая пробелы)**. H1 может быть длиннее title, главное — естественность и функциональный контекст.
- **Семантическая связь:** title, description, keywords, H1 и видимый контент должны перекликаться по марке, типу и применению.
- **Одобрение:** показывать черновик и получать «давай». После push говорить: «Деплой не делаю без разрешения — скажи «задеплой», когда будешь готов»; ждать именно эту команду.
- **Dev-сервер не запускать без явного запроса пользователя.** Для SEO-правок достаточно `npx tsc --noEmit` (и `npm run build`, если пользователь одобрил). Пользователь может сам проверить внешний вид локально, особенно при работе с блог-статьями и статическими страницами.
- **Build gate обязателен** перед каждым коммитом: `npx tsc --noEmit && npm run build`.
- **Backup БД** перед правками: `pentajunior.db.seo-<cat>-backup-<YYYYMMDD-HHMMSS>`.
- **Проверка продакшена** после deploy: `curl`/Python — title/description, HTTP 200, Яндекс.Метрика (если установлена).

### Режим 1: SEO-аудит (когда пользователь просит «проанализируй SEO»)

1. **Загрузить `yandex-seo-optimization`** как основной SEO-источник для аудита. Пользователь предпочитает использовать именно этот навык для SEO pentajunior-v2.
2. **Работать по категориям последовательно**, не массово по всему каталогу. См. `../marketing/yandex-seo-optimization/references/pentajunior-v2-category-optimization-recipe.md`.
3. **Получить данные из SQLite** напрямую — без запуска dev-сервера:
   ```bash
   cd /home/natan/pentajunior-v2
   python3 /home/natan/.hermes/skills/software-development/pentajunior-v2-seo/references/pentajunior-seo-sqlite-audit.py
   ```
4. **Проверить build output:**
   ```bash
   cd /home/natan/pentajunior-v2 && npx tsc --noEmit && npm run build
   ```
5. **Проверить сгенерированный HTML** для одной страницы каждого типа: категория, подкатегория, товар, главная, `/info`, `/contacts`, `/policy`.
6. **Проверить статические мета-источники**, которых нет в SQLite:
   - `src/app/page.tsx` — title/description/openGraph/JSON-LD WebPage/H1;
   - `src/app/layout.tsx` и `src/app/syte-config.ts` — глобальный `description`, `Organization.description`;
   - `src/app/price/page.tsx`, `src/app/info/faq/page.tsx` и другие `page.tsx` со статическим `metadata`;
   - `src/data/blog/article-*.ts` — `metaTitle`/`metaDescription`.
   См. `references/static-pages-seo-audit-procedure.md`.
7. **Проверить живой сайт** через `curl`/Python: title/description/H1, JSON-LD, robots, sitemap, 404, скорость.
8. **Собрать отчёт** по чек-листу `yandex-seo-optimization`: техническое SEO, on-page, контент, коммерческие факторы, поведенческие, JSON-LD, AI-поиск/GEO.
9. **Сохранить отчёт** в Obsidian `Projects/pentajunior-v2-yandex-seo-audit-YYYY-MM-DD.md` и обновить `Projects/MOC — Projects.md`. Удалить устаревшие SEO-аудиты по запросу пользователя.

### Режим 2: SEO-правки (когда пользователь одобрил изменения)

1. **git pull** перед правками (пользователь может сам запушить изменения без предупреждения).
2. **Начинать со статических страниц.** Сперва исправить `/`, `/production`, `/price`, `/contacts`, `/info/*`, `/news`, `/blog` и блог-статьи (`src/data/blog/article-*.ts`), если там есть проблемы: «от производителя», перебор длины, слабые OpenGraph/Twitter, H1 без функции. Эти источники не покрываются SQLite-аудитом. Для добавления новой SEO-статьи в блог см. `references/blog-article-format-and-publishing-recipe.md`.
3. **Никогда не запускать `deploy.sh` без явного одобрения пользователя.** Пользователь прямо попросил: «не делай пожалуйста деплой без моего разрешения =) лучше спроси». После push сообщать: «Изменения запушены. Деплой не делаю без твоего разрешения — скажи «задеплой», когда будешь готов». Затем ждать именно команду «задеплой».
4. **Работать по одной категории за раз** (установленный в сессиях паттерн). Не делать массовый проход по всему каталогу без согласования. Последовательность внутри категории:
   - категория (`meta_title`, `meta_description`, иногда `page_description`);
   - каждая подкатегория (`meta_title`, `meta_description`, `page_description`);
   - каждый товар (`meta_title`, `meta_description`, `keywords`).
   См. `../marketing/yandex-seo-optimization/references/pentajunior-v2-category-optimization-recipe.md` и `references/category-seo-pass-recipe.md`.
5. **Уточнять scope с пользователем.** Если пользователь говорит «для этой категории просто title подправь, подкатегорию тоже можешь не исправлять» — применять правки только к категории и не трогать подкатегории/товары внутри неё без явного разрешения. Точно так же: если пользователь просит «сео текст не меняй пока что» — оставить `seo_text` неизменным, даже если в нём есть запрещённые обороты; исправлять только `meta_title`, `meta_description` и, по согласованию, `features`.
6. **Составить черновик** мета-тегов по формуле из `references/keyword-formula-and-content-rules.md`:
   - `meta_title` — **60–70 символов** (целиться в ~60; 70 — редкий потолок), акцент на марке и целевом применении, бренд-суффикс `| Пента Юниор` добавляем в БД;
   - `meta_description` — **160–170 символов (включая пробелы)**, целевое использование продукта, без технических спецификаций (Шор, сСт и т.п. — в карточку);
   - description должен усиливать семантическую связь с title, keywords и H1: повторяться марка/тип/основное применение, добавляться второстепенные применения и коммерческий CTA;
   - `keywords` — 5–7 запросов: `марка` + `тип/термин` + `целевое применение 1` + `целевое применение 2` + `коммерческий термин`.
7. **Валидировать черновик до применения:** проверить длины всех `meta_title` (≤70) и `meta_description` (160–170). Особенно важно при обновлении `categories`: поле `title` используется как H1, и при массовом UPDATE легко затереть его вместе с мета-полями — всегда включать `title` в список обновляемых полей категории.
8. **Показать черновик** и получить одобрение (одноразовое).
9. **Создать backup БД** перед изменениями: `pentajunior.db.seo-<cat>-backup-<YYYYMMDD-HHMMSS>`.
10. **Внести изменения** в `categories`, `subcategories`, `products` через Python `sqlite3`.
11. **После массового UPDATE проверить длины.** Легко затереть `title` категории или выйти за лимит description при составлении черновика. Перезапустить `pentajunior-seo-sqlite-audit.py` или быструю проверку длин title/description.
12. **Запустить аудит JSON-LD**:
    ```bash
    python3 /home/natan/.hermes/skills/software-development/pentajunior-v2-seo/references/seo_jsonld_audit.py
    ```
13. **Проверить и собрать**:
    ```bash
    cd /home/natan/pentajunior-v2 && npx tsc --noEmit && npm run build
    ```
    Build gate обязателен перед заявлением о завершении.
14. **git add pentajunior.db**, commit, push в `master`.
15. **Деплой только по команде пользователя.** После push сообщить: «Изменения запушены. Деплой не делаю без твоего разрешения — скажи «задеплой», когда будешь готов».

### Режим 3: короткие метатеги и статические страницы

Когда пользователь просит «пройдись по метатегам» или «допиши короткие title/description», применять рецепт из `references/short-meta-and-static-pages-optimization-recipe.md`:

- Находить **короткие** title (<50–55 символов) и description (<150–155 символов).
- Усиливать их по формуле: марка/тема + целевое применение + коммерческий сигнал, сохраняя семантическую связь с H1 и контентом.
- Обрабатывать статические страницы (`/contacts`, `/info`, `/news`, `/price`, `/production`, `/blog`) и блог-статьи (`src/data/blog/article-*.ts`).
- Для статических страниц править `metadata` в `page.tsx`; для блог-статей — `metaTitle`/`metaDescription` в `.ts` файлах.
- После правок запускать `references/global-seo-final-check.py` и build gate.

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
- Если `/api/admin/categories` падает, но данные в SQLite выглядят нормально, перезапустить dev-сервер — Next.js мог кэшировать старый handle. После обновления кода API требуется перезапуск.

## JSON-LD: распространённые ошибки и исправления

- **Акционная цена** `stock_info.newPrice` должна участвовать в `Offer` вместо обычной `price`, если задана. В `metadata.other` тоже выводить акционную цену.
- **Пустые `features`** у товара ломают fallback `description` в JSON-LD подкатегории. Всегда держать `features` заполненным или использовать `product.meta_description` как fallback.
- **Пустые `meta_title`/`meta_description`/`page_description`** у категорий/подкатегорий/товаров приводят к неполноценным сниппетам и ошибкам JSON-LD. Перед JSON-LD-аудитом проверять все записи.
- **Логотип** `/logo.png` должен существовать в `public/`. Если отсутствует — создать симлинк на `/images/fav.svg` или другой актуальный файл.
- **Цена** в `Offer` должна быть чистой числовой строкой: убрать пробелы, заменить запятую на точку.
- **Товары без `price` или с `price = 'None'`** ломают JSON-LD `Product`/`Offer` и карточки каталога. Перед аудитом искать `WHERE price IS NULL OR price='' OR price='None'`.
- **Товары без `image`** используют fallback `/images/hero.webp`, что снижает CTR и валидность Product-разметки. Лучше добавить реальное изображение или временный fallback на категорию/подкатегорию.
- **`openGraph.title` в категории** не должен добавлять `| Пента Юниор`, если `meta_title` уже содержит бренд.
- **`page_description` у категорий и подкатегорий** тоже влияет на рендер и должен быть заполнен.
- **Поле `seo_text` в админке не сохраняется.** Если правки через `/admin/categories` не применяются, проверить, что API `PUT /api/admin/categories/[id]` и `POST /api/admin/categories` включают поле `seo_text` в SQL-запрос. Форма отправляет его, но если сервер игнорирует — обновления пропадают.

## Подводные камни

- **Производитель vs дистрибьютор.** Не пишем «Пента Юниор производит», если компания только официальный дистрибьютор. Для СОЖ/ТЕХМОЛ Экстра формулировка: «ООО «ПЕНТА ЮНИОР» — официальный дистрибьютор ООО «ТЕХГРАНТ» по реализации смазочно-охлаждающих жидкостей». Если неясно — безопаснее убрать «от производителя» и заменить на «купить» или «в Москве».
- **Пищевая промышленность / медицина / FDA / BfR.** Прямые упоминания пищевых/медицинских свойств разрешены только для продукции, которой это действительно свойственно. На момент сессий единственный такой продукт — **ТСМ-1** (антипригарный материал). Для силиконовых трубок/шлангов/пластин убрать акцент на пищевую/медицинскую отрасль; оставить нейтральное техническое описание.
- **Запрещённые обороты в description (категория, подкатегория, товар).** Пользователь требовал убрать:
  - упоминание **цены** (`от 590 ₽/кг`, `цена от …`) — description — функциональный/коммерческий текст, цена только на карточке;
  - оборот **«материал дышит»** / **«кожа дышит»** — заменять на **«паропроницаемый»**, **«сохраняет воздухопроницаемость»** или убирать;
  - слово/оборот **«разведение» / «разводится»** — заменять на **«концентрат»**, **«готовая формула»**, **«смешивается с водой»**, **«разбавляется водой»**.
  После правки `meta_description` проверить и согласованно заменить остатки этих оборотов в `features` товара и в `seo_text` категорий/подкатегорий, если они там тоже встречаются (например, заменить «Разводится 1:10» в `features` на «Концентрат 65%», а «Разведение 1:2–1:10» на «Концентрат, разбавляется водой»). См. `references/seo-description-forbidden-phrases-replacements.md`.
- **Технические спецификации в description.** Не указывать параметры вроде «разводится 1:10», «+200 °C», «70 Шор D», «100 сСт» в `meta_description`, если они уже есть в карточке товара и не несут поискового веса. Вместо этого добавлять конкретные предметные применения: «для заливки форм под гипс и смолы», «для опалубки и литья ПУ», «для выпечки и кондитерских». Это увеличивает description до целевого диапазона 160–170 и привлекает качественный трафик.
- **«Аэрозольный» → «в аэрозольной упаковке».** Пользователь предпочитает формулировку «в аэрозольной упаковке» вместо «аэрозольный разделитель». Использовать её в title/description, если речь о спреях и аэрозолях.
- **Лимит description в скрипте.** Встроенный `global-seo-final-check.py` считает допустимым потолком 160 символов, тогда как проектная договорённость — 160–170. Если description регулярно выходят за 160, но укладываются в 170, скорректировать лимит в скрипте или держать description строго ≤160 до согласования с пользователем.
- **ID vs название в keywords.** Ориентироваться на **название товара (марку)**, а не на технический ID. Пример: товар с ID `-9240` называется «Юнисил 9240» — в keywords и title использовать «Юнисил 9240».
- **Стиль SEO-текстов и описаний.** Пользователь предпочитает человечный, практический текст без AI-слоупа: конкретно, с пользой, с натуральными внутренними ссылками. Для `page_description` — 2–3 предложения, без общих фраз вроде «широкий ассортимент» и «высокое качество». Пример хорошего тона: «Если не знаете, какой выбрать — начните с Юнисил 9110 или 9500».
- **Рефакторинг CSS — только пошагово.** Не удалять `globals.css`-классы массово по статическому аудиту. Многие классы используются через динамическую генерацию, Bootstrap-состояния или JS. Любое изменение `globals.css` должно сопровождаться `npm run build` и визуальной проверкой ключевых страниц. Массовое удаление классов ломает вёрстку.
- **Админка не сохраняет SEO-текст категории.** Если правки `seo_text` через `/admin/categories` не применяются, проверить, что API `PUT /api/admin/categories/[id]` и `POST /api/admin/categories` включают поле `seo_text` в SQL-запрос. Иначе форма отправляет его, но сервер игнорирует.
- **Sitemap и robots: исключить `/admin`.** Админ-панель (`/admin` и `/admin/*`) не должна попадать в `sitemap.xml` и должна быть запрещена в `robots.ts` через `disallow: ["/admin/"]`. В текущем проекте `/admin` не включена в sitemap, но в `robots.ts` явно не запрещена — рекомендуется добавить.
- **Админка категории: форма редактирования показывает `seo_text`, но PUT не обновляет его.** При обновлении кода API категорий включать `seo_text` в параметры SQL. Проверить через `curl /api/admin/categories` после сохранения.
- `openGraph.title` в категории раньше добавлял `| Пента Юниор` к `meta_title`, что давало дублирование. Исправлено: использовать `meta_title` как есть.
- Description должен быть 160–170 символов (включая пробелы); page_description может быть длиннее, но лучше держать в том же диапазоне.
- Для товаров без `image` используется fallback `/images/hero.webp`. Рассмотреть массовую конвертацию изображений в WebP — см. `references/image-optimization-recipe.md` (внутри этого навыка).
- `keywords` хранится как JSON-массив в SQLite.
- **Проверка keywords:** убедиться, что они отражают предмет страницы, а не только общую тему подкатегории. Искать шаблонные наборы внутри подкатегории и дублирование слов в `name`/`title`/`meta_description`. См. `references/seo-audit-sqlite-keywords-checklist.md`.
- **Пользователь предпочитает Yandex-навык.** Для SEO-аудита и правок pentajunior-v2 использовать `yandex-seo-optimization` как основной источник рекомендаций, а `pentajunior-v2-seo` — как проектный workflow (SQLite-аудит, JSON-LD, build gate, deploy).
- После внесения изменений в БД запускать `seo_jsonld_audit.py` **перед** build gate, чтобы поймать пустые мета-поля, некорректные цены или отсутствующие файлы до коммита.
- **Уточнение после Wordcraft:** если появляются данные Яндекс.Wordcraft после первого прохода, можно уточнить `meta_title`/`meta_description` с высокочастотными запросами. Делать refine-коммит отдельным.
- **Blog articles:** для скрытия статьи с сайта добавить поле `published: false` в `src/data/blog/article-XX.ts` и убедиться, что `/blog`, `/blog/[id]`, `RelatedArticles` и `generateStaticParams` фильтруют по `published`. Не удалять файл и не убирать `relatedProducts` — это не скроет статью из блога. Чтобы статья появилась в блоке «Полезные статьи» на странице категории, добавьте slug категории в `relatedCategories` статьи; фильтрация происходит автоматически в `src/app/production/[category]/page.tsx`.

## Final verification after all category passes

Target end-state before declaring work complete:

- 0 title >70
- 0 description >160
- 0 «от производителя» / «производитель» в БД **и** в статических `page.tsx`/`syte-config.ts`
- 0 дублирующихся наборов keywords у товаров

Глобальный скрипт проверяет только БД. Статические страницы (`/`, `/price`, `/info/faq`, `layout.tsx`, `syte-config.ts`, блог-статьи) проверить отдельно через поиск или live-сканирование.

Запустить готовый скрипт:

```bash
python3 /home/natan/.hermes/skills/software-development/pentajunior-v2-seo/references/global-seo-final-check.py
```

Если что-то не ноль — исправить и перезапустить до достижения нулей.

Также применять этот скрипт после прохода по коротким метатегам и статическим страницам. См. `references/short-meta-and-static-pages-optimization-recipe.md`.

## HTML-семантика и перелинковка

См. `references/html-semantics-seo-audit.md` (внутри `pentajunior-v2-seo`) для чек-листа:
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
- `references/seo-audit-sqlite-keywords-checklist.md` — SQLite-рецепты для проверки релевантности `keywords` товаров, поиска шаблонных keywords, сводок по пустым ценам и изображениям.
- `references/humanizer-page-description-examples.md` — approved short category descriptions in the user's preferred human, non-AI style.
- `references/sitemap-robots-admin-disallow.md` — how to keep `/admin` and service routes out of `sitemap.xml` and `robots.txt`.
- `references/html-validate-workflow.md` — how to validate compiled HTML for one page per template type and which validator warnings are actionable.
- `references/seo-audit-report-template.md` — template for producing a structured Yandex SEO audit report from live site checks and SQLite data.
- `references/static-pages-seo-audit-procedure.md` — how to audit static `page.tsx`, `layout.tsx`, `syte-config.ts`, and blog articles that are not covered by SQLite checks.
- `references/blog-article-format-and-publishing-recipe.md` — рецепт добавления новой SEO-статьи в блог: формат content, relatedProducts/relatedCategories, плейсхолдеры `{product:ID}`, проверки, публикация/скрытие.
- `references/geo-audit-comparison-workflow.md` — comparing an external SEO audit JSON with the rendered Next.js build output.
- `references/geo-audit-parser.py` — reusable parser that extracts SEO fields from `.next/server/app/*.html` and diffs them against an audit JSON.
- `references/short-title-optimization-pattern.md` — finding and lengthening service-page titles that are too short for SEO without keyword stuffing.
- `references/short-meta-and-static-pages-optimization-recipe.md` — рецепт усиления коротких title/description и прохода по статическим страницам + блог.
- `references/product-seo-optimization-recipe.md` — шаблоны title/description/keywords и чек-лист обработки товаров в подкатегории с функционально-предметной семантикой.
- `references/seo-description-forbidden-phrases-replacements.md` — запрещённые обороты в description (цена, «дышит», «разведение») и формулы замены для категорий, подкатегорий и товаров.
- `references/category-title-shortness-pattern.md` — что делать, когда `meta_title` категории слишком короткий, и как удлинить его через конкретные операции/применения.
- `references/global-seo-final-check.py` — готовый скрипт финальной проверки: длины, «производитель», дубли keywords.
- `references/category-seo-pass-recipe.md` — пошаговый рецепт обработки одной категории: как выгружать данные, что проверять, как составлять черновик, формулировки длин, паттерны keywords по типам товаров (RTV-2, ПМС, герметики, изделия из резин, СОЖ, ТСМ-1).
- `references/yandex-metrika-nextjs-install.md` — как встроить счётчик Яндекс.Метрики (с webvisor, clickmap, trackLinks, ecommerce dataLayer) в `src/app/layout.tsx` и проверить его на проде.
- `references/keyword-formula-and-content-rules.md` — формула keywords и правила контента для pentajunior-v2: марка + RTV-2/тип + целевое применение, без технических specs в keywords, без пищевых упоминаний кроме ТСМ-1, производитель vs дистрибьютор.
- `../marketing/yandex-seo-optimization/references/pentajunior-v2-seo-conventions.md` — проверенные на проекте pentajunior-v2 конвенции: формула keywords, позиционирование, RTV-2, workflow оптимизации категории.
- `../marketing/yandex-seo-optimization/references/pentajunior-v2-category-optimization-recipe.md` — пошаговый рецепт обработки одной категории pentajunior-v2 по формуле из Yandex-навыка.