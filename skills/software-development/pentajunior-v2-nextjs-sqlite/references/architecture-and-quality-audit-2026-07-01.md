# Архитектурный и качественный аудит pentajunior-v2 — 2026-07-01

Дата проведения: 2026-07-01
Контекст: после UI/API/types рефакторинга (коммиты `228bd36`..`65387f9`) потребовалась оценка зрелости проекта по критериям: компоненты/поддерживаемость, SEO-разметка, скорость загрузки, архитектура.

## 1. Компоненты и поддерживаемость

| Метрика | Значение |
|---------|----------|
| Компонентов в `src/components/` | 35 |
| Средний размер компонента | ~100 строк |
| Самые крупные | `UniversalTemplate.tsx` 400, `TemplateDataEditor.tsx` 387, `ContactForm.tsx` 275 |
| Inline `style={{...}}` | 37 штук |
| JS-чанков в `.next/static/chunks` | 20 |
| Суммарный JS-бандл | ~959 KB |
| `globals.css` | 3672 строки / ~82 KB |
| Потенциально неиспользуемые компоненты | `ProductTemplates/index.tsx`, `UI/RelatedArticles/index.tsx`, `UI/Tables/PriceTable.tsx`, `UI/Buttons/OrderButtonForm.tsx` — требуется ручная проверка |

### Рекомендации
- `UniversalTemplate.tsx` и `TemplateDataEditor.tsx` разбивать только при явной необходимости — там сложная бизнес-логика.
- Остаточные inline styles — в `app/info/faq/page.tsx` (7), `app/price/page.tsx` (4), `components/UI/Searcher.tsx` (3). Можно постепенно выносить в CSS-классы, но это не критично.

## 2. SEO / HTML-разметка

### Сильные стороны
- `robots.ts`, `sitemap.ts` — корректно закрывают `/api/`, `/_next/`, `/admin/`.
- JSON-LD на каждой странице через `JsonLd.tsx`.
- `generateMetadata` на всех production-страницах и блоге.
- Canonical, OpenGraph, Twitter metadata присутствуют.

### Проблемы
| Проблема | Где | Важность |
|----------|-----|----------|
| Нет `<h1>` | `/production/page.tsx` | Средняя |
| Нет `<h1>` | `/production/[category]/[subcategory]/[product]/page.tsx` | **Высокая** — карточка товара без главного заголовка |
| Пустые `<h2>` | `/blog/[articleId]/page.tsx` | Средняя |
| Нет `<h1>` | `/contacts/page.tsx`, `/info/page.tsx`, `/news/page.tsx` | Средняя |
| `dangerouslySetInnerHTML` | `blog/[articleId]`, `SeoTextSection`, `JsonLd`, `YandexMetrika` | Принимаемо, но рискованно при внешнем контенте |
| Партнёры на `/contacts` как `<h3>` | `/contacts/page.tsx` | Размывает структуру заголовков; лучше `<strong>` |

## 3. Скорость загрузки

| Фактор | Статус |
|--------|--------|
| Bootstrap CSS | Весь Bootstrap импортируется в `layout.tsx` |
| Bootstrap JS | Грузится только `collapse` — оптимально |
| `globals.css` | Один файл 82 KB — допустимо, но монолит |
| next/image | 12 использований, есть `sizes` |
| Plain `<img>` | 2 (Yandex pixel, Searcher) — норма |
| Yandex Metrika | `afterInteractive` — OK |
| Yandex Maps iframes | На `/contacts` — могут влиять на LCP/CLS |
| Статические заголовки Cache-Control | Настроены в `next.config.ts` |
| Изображения | PNG/JPG в `public/images/` — есть запас для WebP-конвертации |

### Рекомендации
- Конвертация изображений в WebP + обновление путей в БД — самый простой способ ускорить загрузку.
- Рассмотреть lazy-loading для iframes карт на `/contacts` (уже `loading="lazy"`).

## 4. Архитектурные риски

| Риск | Рейтинг | Почему |
|------|---------|--------|
| Хардкод fallback admin password | **Критический** | `src/app/api/admin/auth/route.ts:3` и `src/proxy.ts:4` имеют `process.env.ADMIN_PASSWORD \|\| 'пента2...al'` |
| Cookie хранит plaintext password | **Критический** | `admin_token` = raw password в cookie |
| SQL-инъекции в admin API | **Высокий** | API routes интерполируют поля из `request.json()` в SQL-строки |
| DDL/DML-миграции в `lib/db.ts` | **Высокий** | `ALTER TABLE`, `CREATE TABLE`, data migration выполняются при каждом импорте, включая сборку |
| Нет `middleware.ts` / защита через `proxy.ts` | **Средний** | Нестандартно; API routes не перепроверяют auth индивидуально |
| 72 ESLint errors | **Средний** | `loadData` accessed before declared, `any`, setState in effect, refs during render |
| Множественные DB-соединения | **Средний** | Каждый API route открывает своё соединение с `pentajunior.db` |
| `dangerouslySetInnerHTML` для SEO/blog | **Средний** | Контент локальный, но паттерн рискованный |

### Рекомендации
1. **Security** — убрать fallback password, хранить в cookie hash/JWT, добавить per-route auth middleware.
2. **Migrations** — вынести из `lib/db.ts` в `drizzle-kit` или отдельный `scripts/migrate.ts`.
3. **ESLint** — пофиксить критические `react-hooks/immutability` и `react-hooks/no-ref-in-render` в admin-страницах.
4. **SQL injection** — параметризовать все поля через `?` placeholders.

## 5. Итоговая оценка

Проект — рабочий, SEO-ориентированный каталог с админкой. Рефакторинг UI/API/types улучшил поддерживаемость. Главные риски — безопасность и data-layer гигиена, а не скорость или SEO-разметка. Для дальнейшего роста приоритеты:
1. Устранить критические security-риски.
2. Вынести миграции из `lib/db.ts`.
3. Исправить ESLint errors в admin-коде.
4. Добавить `<h1>` на страницы товаров и каталога.
5. Конвертировать изображения в WebP.
