# Внедрение подкатегорий в Next.js App Router + SQLite

Когда категория объединяет несколько семейств товаров с разной семантикой (например, «Силикон для заливки форм» содержит оловянный силикон, платиновый, полиуретановые компаунды и наполнители), SEO выигрывает, если для каждого семейства создать собственную посадочную страницу.

Этот рецепт описывает полноценную таблицу `subcategories`, новую маршрутизацию и 301-редиректы. Использован в проекте `pentajunior-v2` (категория «Силикон для заливки форм»).

## Целевая структура URL

```
/production/<categorySlug>
/production/<categorySlug>/<subcategorySlug>
/production/<categorySlug>/<subcategorySlug>/<productId>
```

Пример:

```
/production/silikon-dlya-zalivki-form
/production/silikon-dlya-zalivki-form/platinovyj-silikon
/production/silikon-dlya-zalivki-form/platinovyj-silikon/unisil-9500
```

## 1. Схема БД

```sql
CREATE TABLE subcategories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
  slug TEXT NOT NULL,
  title TEXT NOT NULL,
  meta_description TEXT,
  page_description TEXT,
  seo_text TEXT,
  image TEXT,
  sort_order INTEGER DEFAULT 0,
  UNIQUE(category_id, slug)
);

ALTER TABLE products ADD COLUMN subcategory_id INTEGER REFERENCES subcategories(id);

CREATE INDEX idx_subcategories_category ON subcategories(category_id);
CREATE INDEX idx_products_subcategory ON products(subcategory_id);
```

## 2. Data layer helpers (src/lib/db.ts)

```ts
export interface Subcategory {
  id: number;
  category_id: number;
  slug: string;
  title: string;
  meta_description: string;
  page_description: string;
  seo_text?: string | null;
  image: string | null;
  sort_order: number;
}

export function getSubcategoriesByCategoryId(categoryId: number): Subcategory[] {
  return db.prepare('SELECT * FROM subcategories WHERE category_id = ? ORDER BY sort_order, id').all(categoryId) as any[];
}

export function getSubcategoryBySlug(categoryId: number, slug: string): Subcategory | undefined {
  return db.prepare('SELECT * FROM subcategories WHERE category_id = ? AND slug = ?').get(categoryId, slug) as any;
}

export function getProductsBySubcategoryId(subcategoryId: number) {
  return db.prepare('SELECT * FROM products WHERE subcategory_id = ? ORDER BY sort_order, id').all(subcategoryId) as any[];
}
```

## 3. Маршрутизация: единый optional catch-all

Главная ошибка — создавать два маршрута `[categorySlug]/[subcategorySlug]` и `[categorySlug]/[productId]`. Next.js не различит `/cat/sub` от `/cat/prod`, потому что оба сегмента динамические.

Решение: один optional catch-all роут.

```
src/app/production/[categorySlug]/[[...rest]]/page.tsx
```

Параметры:

- `/production/cat` → `{ categorySlug: 'cat' }`
- `/production/cat/sub` → `{ categorySlug: 'cat', rest: ['sub'] }`
- `/production/cat/sub/prod` → `{ categorySlug: 'cat', rest: ['sub', 'prod'] }`

Резолвинг внутри страницы:

```ts
const { categorySlug, rest } = await params;
const segments = rest || [];
const subcategorySlug = segments.length >= 1 ? segments[0] : undefined;
const productId = segments.length >= 2 ? segments[1] : undefined;
```

## 4. generateStaticParams

```ts
export function generateStaticParams() {
  const params: { categorySlug: string; rest?: string[] }[] = [];
  for (const category of getAllCategories()) {
    params.push({ categorySlug: category.slug });
    for (const sub of getSubcategoriesByCategoryId(category.id)) {
      params.push({ categorySlug: category.slug, rest: [sub.slug] });
      for (const product of getProductsBySubcategoryId(sub.id)) {
        params.push({ categorySlug: category.slug, rest: [sub.slug, product.id] });
      }
    }
    // Продукты без подкатегории (legacy)
    for (const product of getProductsByCategoryId(category.id).filter(p => !p.subcategory_id)) {
      params.push({ categorySlug: category.slug, rest: [product.id] });
    }
  }
  return params;
}
```

## 5. Логика страницы

1. Найти категорию по `categorySlug`. Если нет — `notFound()`.
2. Если `productId` присутствует:
   - Найти товар, проверить `category_id`.
   - Если `subcategorySlug` указан — найти подкатегорию и проверить, что товар ей принадлежит.
   - Если `subcategorySlug` не указан, а у товара есть `subcategory_id` — `notFound()`.
   - **Рендерить страницу товара через полноценный компонент карточки товара** (например, `ProductCard`), а не через встроенную вёрстку внутри страницы. Иначе теряются шаблон описания, spec-таблица, акционные цены, кнопка заказа и прочие детали, которые уже реализованы в компоненте карточки.
3. Если `subcategorySlug` без `productId` — рендерить страницу подкатегории.
4. Если нет `rest` — рендерить страницу категории. Если у категории есть подкатегории, показывать плитки подкатегорий вместо сетки товаров.

### 5.1 Страница товара: не встраивайте вёрстку заново

В рабочих версиях страница товара импортирует и использует `ProductCard`:

```tsx
import ProductCard from "@/components/UI/Cards/ProductCard";

// внутри product-ветки JSX:
<ProductCard
  categorySlug={category.slug}
  subcategorySlug={subcategory?.slug}
  product={product}
/>
```

`ProductCard` обычно содержит:
- изображение с бейджами «Новинка» / «Акция»;
- название, фасовку, список особенностей;
- цену / акционную цену с единицей измерения;
- кнопку «Заказать»;
- шаблонное описание (`TemplateComponent`);
- spec-таблицу (`TableIncluder`).

Если вместо этого написать inline-вёрстку прямо в `page.tsx`, вся эта функциональность дублируется в урезанном виде или пропадает. Поэтому product-ветка страницы должна делегировать отображение компоненту карточки товара.

## 6. 301-редиректы старых URL

В `next.config.ts` не используйте `import('./src/lib/db')` — build-time transpiler не резолвит алиасы проекта. Запрашивайте `better-sqlite3` напрямую.

```ts
async redirects() {
  const Database = (await import('better-sqlite3')).default;
  const path = (await import('path')).default;
  const db = new Database(path.join(process.cwd(), 'pentajunior.db'));

  const categories = db.prepare('SELECT id, slug FROM categories').all() as { id: number; slug: string }[];
  const subcategories = db.prepare('SELECT id, category_id, slug FROM subcategories').all() as { id: number; category_id: number; slug: string }[];
  const products = db.prepare('SELECT id, category_id, subcategory_id FROM products WHERE subcategory_id IS NOT NULL').all() as { id: string; category_id: number; subcategory_id: number }[];

  const categoryMap = new Map(categories.map(c => [c.id, c]));
  const subcategoryMap = new Map(subcategories.map(s => [s.id, s]));

  const productRedirects = products
    .map((p) => {
      const category = categoryMap.get(p.category_id);
      const subcategory = subcategoryMap.get(p.subcategory_id);
      if (!category || !subcategory) return null;
      return {
        source: `/production/${category.slug}/${p.id}`,
        destination: `/production/${category.slug}/${subcategory.slug}/${p.id}`,
        permanent: true,
      };
    })
    .filter(Boolean) as { source: string; destination: string; permanent: boolean }[];

  db.close();

  return [
    { source: '/sitemap', destination: '/sitemap.xml', permanent: true },
    ...productRedirects,
  ];
}
```

Проверка: `curl -L -I http://localhost:3000/production/silikon-dlya-zalivki-form/unisil-9500` должен вернуть `308 → 200` (Next.js отдаёт 308 для permanent-редиректа с методами, отличными от GET).

## 7. Админка

- API `/api/admin/subcategories` (GET/POST) и `/api/admin/subcategories/[id]` (GET/PUT/DELETE).
- В `/admin/categories` добавить UI управления подкатегориями под каждой категорией.
- В `/admin/products` добавить селектор подкатегории, фильтрующий по выбранной категории. При смене категории сбрасывать `subcategory_id`.
- Проверять связанность: при создании/редактировании товара категория и подкатегория должны быть согласованы (`subcategory.category_id == product.category_id`).

## 8. SEO-шаблоны

- H1 на странице категории — название категории.
- H1 на странице подкатегории — название подкатегории.
- Breadcrumbs включают категорию и подкатегорию.
- JSON-LD `ItemList` для подкатегорий и товаров.
- `meta_description` и `seo_text` берутся из подкатегории, если она есть.

## Питфолты

- **Конфликт маршрутов.** Не создавай одновременно `[categorySlug]/[subcategorySlug]` и `[categorySlug]/[productId]` — Next.js скажет `Ambiguous route pattern "/production/[*]/[*]"`.
- **next.config.ts не видит `src/lib/db`.** Используй `better-sqlite3` напрямую внутри `async redirects()`.
- **Не указывай `permanent: true` для непроверенных редиректов.** Сначала проверь на dev-сервере. 301/308 сложно откатить в индексе поисковиков.
- **Старый slug категории.** Если slug категории тоже поменялся, старый URL `/production/old-slug/product` не попадёт в автоматический редирект. Нужен отдельный редирект на уровне категории или обработка 404.
- **Binary SQLite в git.** После миграции данных делай `git commit` сразу. Merge-конфликты в `.db` неразрешимы автоматически.
- **Код ответа 308 вместо 301.** Next.js отдаёт `308 Permanent Redirect` для `permanent: true`, когда запрос содержит тело или не GET-метод. Это корректно и SEO-безопасно; поисковики обрабатывают 308 аналогично 301.

## Verification checklist

- [ ] `tsc --noEmit` чисто.
- [ ] `npm run build` успешен.
- [ ] `/production/<category>` отдаёт 200 и показывает плитки подкатегорий.
- [ ] `/production/<category>/<subcategory>` отдаёт 200 и сетку товаров.
- [ ] `/production/<category>/<subcategory>/<product>` отдаёт 200 и рендерит полноценный `ProductCard` (шаблон описания, spec-таблица, цена, кнопка заказа).
- [ ] Неверная комбинация `/production/<category>/<wrong-subcategory>/<product>` отдаёт 404.
- [ ] Старый URL `/production/<category>/<product>` редиректит на новый с подкатегорией (ожидайте код 308 для `permanent: true`).
- [ ] Sitemap содержит новые URL с подкатегориями.
- [ ] Админка позволяет назначать подкатегорию товару.
