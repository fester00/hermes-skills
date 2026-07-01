# HTML-семантика и SEO-аудит страниц pentajunior-v2

Контекст: проект pentajunior-v2 на Next.js 16 + Bootstrap 5. Нужно проверять, как структура HTML-разметки влияет на SEO (Yandex/Google): иерархия заголовков, семантические теги, хлебные крошки, JSON-LD.

## Что проверять

### 1. Единственность `<h1>`

На каждой странице должен быть ровно один `<h1>`.

Страницы проекта:
- `/` — H1 в hero-секции.
- `/production` — H1 «Каталог продукции».
- `/production/[category]` — H1 `category.title`.
- `/production/[category]/[subcategory]` — H1 `subcategory.title`.
- `/production/[category]/[subcategory]/[product]` — H1 внутри `ProductCard`, обычно `product.name`.
- `/price` — H1 «Прайс-лист...».
- `/blog/[articleId]` — H1 `article.title`.

Проверка:
```bash
cd /home/natan/pentajunior-v2
grep -R "<h1" src/app --include="*.tsx"
grep -R "<h1" src/components --include="*.tsx"
```

### 2. Структура SEO-текстов (`seo_text`)

Раньше `seo_text` содержал собственную обёртку `<section>` и заголовок `<h2>`. Это приводило к дублированию или неявной иерархии.

Рекомендуемый паттерн (после 2026-06-23):
- Убрать внешнюю обёртку `<section>` из `seo_text`.
- Убрать первый `<h2>` из `seo_text`.
- Повысить оставшиеся `<h3>` до `<h2>`.
- В шаблоне страницы добавить единый внешний заголовок:
  ```tsx
  <section className="category-seo-text mt-5 pt-4 border-top" aria-labelledby="category-seo-heading">
    <h2 id="category-seo-heading" className="h5 mb-3">
      Подробнее о {category.title.toLowerCase()}
    </h2>
    <div dangerouslySetInnerHTML={{ __html: category.seo_text }} />
  </section>
  ```

### 3. Хлебные крошки (UI + JSON-LD)

- UI: `<nav aria-label="Breadcrumb">` + `<ol className="breadcrumb">`.
- JSON-LD: `BreadcrumbList` с `ListItem`, position 1..N.

Покрытие:
- `/production` — Главная → Продукция.
- `/production/[category]` — Главная → Продукция → Категория.
- `/production/[category]/[subcategory]` — + Подкатегория.
- `/production/[category]/[subcategory]/[product]` — + Товар.
- `/blog` — Главная → Блог.
- `/blog/[id]` — Главная → Блог → Статья.
- `/contacts` — Главная → Контакты.
- `/price` — Главная → Прайс-лист.

### 4. `ItemList` / `ListItem` JSON-LD

Уже реализовано:
- `/production` — список категорий.
- `/production/[category]` — список подкатегорий.
- `/production/[category]/[subcategory]` — список товаров.
- `/blog` — список статей.

### 5. Внутренняя перелинковка

Проверять:
- `related_categories` в категориях (JSON-массив ID).
- `relatedProducts` в статьях блога.
- Ссылки внутри `seo_text` на подкатегории и товары.
- Блок «Другие товары в ...» на странице товара.

## Скрипт быстрой проверки

```python
import sqlite3, re
DB = "/home/natan/pentajunior-v2/pentajunior.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# H1 в seo_text
for table in ['categories', 'subcategories']:
    print(f"\n{table}:")
    for row in cur.execute(f"SELECT slug, seo_text FROM {table} WHERE seo_text IS NOT NULL").fetchall():
        text = row['seo_text'] or ''
        print(f"  {row['slug']}: h2={len(re.findall(r'<h2', text, re.I))}, h3={len(re.findall(r'<h3', text, re.I))}, links={len(re.findall(r'<a[^>]+href', text, re.I))}")
```

## Валидация скомпилированного HTML

Для поиска ошибок разметки, дублирующих классов, пропущенных уровней заголовков и проблем accessibility проверяй уже собранные статические HTML-файлы, а не исходный TSX.

```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
cd /home/natan/pentajunior-v2
rm -rf .next
npm run build

./node_modules/.bin/html-validate \
  .next/server/app/index.html \
  .next/server/app/production/electrosealant.html \
  .next/server/app/production/electrosealant/zalivka-electro-komponentov.html \
  .next/server/app/production/electrosealant/zalivka-electro-komponentov/pentelast-711.html \
  .next/server/app/news.html \
  .next/server/app/blog/germetiki-dlya-elektroniki.html \
  .next/server/app/info.html \
  .next/server/app/price.html \
  .next/server/app/contacts.html \
  .next/server/app/policy.html
```

Что игнорировать (Next.js / Bootstrap особенности):
- `void-style` — самозакрывающие `<meta/>`, `<img/>`, `<input/>`, `<hr/>`, `<link/>`.
- `attr-case` — React атрибуты `noModule`, `rowSpan`.
- `attribute-boolean-style` — `async="true"`, `hidden="until-found"`.
- `no-inline-style` — Bootstrap и Next.js DevTools вставляют инлайн-стили.
- `prefer-native-element` / `valid-id` — служебные элементы Next.js DevTools (`role="progressbar"`, `id="_R_"`).

Что исправлять обязательно:
- `no-dup-class` — дублирование классов (`text-light text-light`).
- `unique-landmark` — несколько `<nav>` без `aria-label`.
- Пропуск уровней заголовков (`H1 → H3`, `H2 → H4`).
- Отсутствующие `alt` у изображений.

## Паттерн: повышение релевантности заголовков на главной

Сервисы вроде SeoLik оценивают, насколько текст заголовка соответствует тематике страницы. Низкорелевантные заголовки стоит переписывать с ключевыми словами про силиконовые материалы, не убирая их из иерархии.

Пример замен для `/`:

| Было | Стало |
|------|-------|
| H2: «Наша продукция» | H2: «Каталог силиконовых материалов» |
| H2: «Почему выбирают нас» | H2: «Преимущества силиконовых материалов Пента Юниор» |
| H3: «Уникальные свойства силиконов» | H3: «Зачем нужны силиконовые материалы» |
| H4: «Доставка по всей России» | H4: «Доставка силиконовых материалов по России» |
| H4: «Собственное производство» | H4: «Производство силиконовых компаундов и смазок» |
| H4: «Доступные цены» | H4: «Цены на силиконовые материалы» |
| H4: «Техническая поддержка» | H4: «Подбор силиконовых материалов под задачу» |
| H4: «Широкий ассортимент» | H4: «Ассортимент силиконовых материалов» |

После замен проверить, что иерархия заголовков не нарушена (лучше H1 → H2 → H3 → H4 без пропусков), и не появились дубли H1.

## Подводные камни

- Bootstrap-разметка часто использует избыточные `<div>`. Стараться заменять на `<section>`, `<article>`, `<aside>` где это уместно.
- `CategorySidebar` обёрнут в `<aside>` — правильно, это вспомогательный контент.
- `ProductCard` использует `<article>` — правильно для карточки товара.
- Не оставлять пустые `<section>` без заголовка или `aria-label`.
- `next/image` с `fill` + `sizes` нужен для производительности; для изображений выше viewport добавить `priority`.
