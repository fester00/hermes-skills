# Рецепт: добавление SEO-статьи в блог pentajunior-v2

Блог в pentajunior-v2 — это набор TypeScript-файлов (`src/data/blog/article-*.ts`), экспортируемых через `src/data/blog/index.ts`. Страница статьи рендерит `content` как HTML, заменяя плейсхолдеры `{product:ID}` на ссылки и оборачивая `<table>` в `.blog-table-scroll`.

## Структура файла статьи

Каждая статья экспортирует объект `BlogArticle` из `src/data/blog/types.ts`:

```typescript
export interface BlogArticle {
  id: string;                          // URL-safe slug: /blog/<id>
  title: string;                       // H1 и headline JSON-LD
  metaTitle: string;                     // ≤70 символов
  metaDescription: string;               // 160–170 символов
  keywords: string[];                    // 5–7 запросов
  category: "compounds" | "lubricants" | "industry";
  publishDate: string;                   // YYYY-MM-DD
  readTime: number;                      // минуты чтения
  relatedProducts: string[];             // ID товаров из SQLite
  relatedCategories: string[];           // slug категорий
  published: boolean;                    // true → видна на сайте
  content: string;                       // HTML-шаблон с плейсхолдерами
}
```

## Алгоритм добавления новой статьи

1. **Определить ID статьи.** Использовать короткий URL-safe slug на латинице через дефисы, отражающий тему. Примеры существующих: `antiprigarnye-materialy-dlya-pekarni`, `germetiki-dlya-elektroniki`. Новая статья: `gidrofobizatory-dlya-betona-kirpicha-kamnya`.
2. **Найти relatedProducts и relatedCategories.** Для SEO-статьи о группе товаров:
   - `relatedProducts` — ID товаров из SQLite (колонка `products.id`), которые упоминаются в тексте.
   - `relatedCategories` — slug категорий (`categories.slug`), к которым относится тема.
   Пример для гидрофобизаторов: `relatedProducts: ["penta-811"]`, `relatedCategories: ["obrabotka-poverhnosti-propitki"]`.
3. **Выбрать category.** Для отраслевых/строительных/примененческих тем использовать `"industry"`.
4. **Заполнить metaTitle и metaDescription.**
   - `metaTitle`: ≤70 символов, бренд не обязателен (title берётся как есть).
   - `metaDescription`: 160–170 символов, без «от производителя», без технических спецификаций.
5. **Отформатировать content.**
   - Вводный абзац(ы) без отдельного заголовка — текст идёт сразу под H1.
   - Основные разделы — `<h2>`.
   - Подразделы — `<h3>`.
   - Списки — `<ul><li>...</li></ul>`. Не использовать `·` или другие ASCII-маркеры.
   - Сравнительные таблицы — `<table><thead>...</thead><tbody>...</tbody></table>`. Страница обернёт таблицу в `.blog-table-scroll` автоматически.
   - FAQ — `<dl><dt>Вопрос</dt><dd>Ответ</dd></dl>`.
   - Заключение — `<h2>Заключение</h2>` + абзац.
6. **Добавить плейсхолдеры `{product:ID}`.** Рендер заменит их на ссылки к товарам. ID — это `products.id`, а не slug подкатегории. Пример: `{product:penta-811}`.
7. **Номер нового файла.** Использовать следующий свободный номер: `article-16.ts`, `article-17.ts` и т.д.
8. **Обновить `src/data/blog/index.ts`.** Импортировать новый `articleXX` и добавить его в массив `articles`, и в named-экспорт.
9. **Проверить типизацию.** Без запуска dev-сервера:
   ```bash
   cd /home/natan/pentajunior-v2 && npx tsc --noEmit
   ```
10. **Сделать commit.** Dev-сервер и deploy не запускать без явного разрешения пользователя.

## Стиль контента

- Человечный, практический тон, без AI-слоупа.
- Конкретные применения и примеры.
- Без упоминаний «от производителя» / «производитель».
- Без цен в description и видимом тексте (цена только на карточке товара).
- Без медицинских/пищевых claims, кроме продуктов, которым это действительно свойственно (например, ТСМ-1).

## Пример мини-шаблона content

```typescript
content: `
<h2>Введение в тему</h2>
<p>...вводный абзац...</p>

<h2>Раздел 1</h2>
<p>...</p>
<ul>
  <li>пункт 1</li>
  <li>пункт 2</li>
</ul>

<h3>Подраздел</h3>
<p>...с упоминанием {product:penta-811}...</p>

<h2>Сравнение</h2>
<table>
  <thead><tr><th>Параметр</th><th>Вариант A</th><th>Вариант B</th></tr></thead>
  <tbody>
    <tr><td>паропроницаемость</td><td>да</td><td>нет</td></tr>
  </tbody>
</table>

<h2>Часто задаваемые вопросы</h2>
<dl>
  <dt>Вопрос?</dt>
  <dd>Ответ.</dd>
</dl>

<h2>Заключение</h2>
<p>...</p>
`
```

## Вывод статьи на странице категории

Страница категории (`src/app/production/[category]/page.tsx`) автоматически показывает блок «Полезные статьи» через компонент `RelatedArticles`. В блок попадают опубликованные статьи (`published: true`), у которых `relatedCategories` содержит слаг текущей категории (`category.slug`).

Чтобы статья появилась на странице категории:
1. Добавить slug нужной категории в `relatedCategories` статьи.
   ```typescript
   relatedCategories: ["obrabotka-poverhnosti-propitki"]
   ```
2. Убедиться, что `published: true`.
3. Пересобрать проект, чтобы статическая страница категории сгенерировалась с актуальным списком статей.

Компонент выводит до 3 статей с заголовком и временем чтения. Никаких дополнительных правок в админке или БД не требуется.

## Проверки после добавления

- Страница `/blog` отображает новую карточку (фильтр `published === true`).
- Страница `/blog/<id>` генерируется статически (`generateStaticParams` фильтрует по `published`).
- На страницах категорий, указанных в `relatedCategories`, появился блок «Полезные статьи».
- JSON-LD `Article` и `BreadcrumbList` присутствуют.
- `npx tsc --noEmit` проходит без ошибок.

## Скрытие и публикация

- Чтобы скрыть статью: `published: false`. Не удалять файл и не очищать `relatedProducts` — это не скроет статью из списка, если другие места фильтруют только по `published`.
- Чтобы опубликовать: `published: true`. После изменения пересобрать проект, чтобы `generateStaticParams` увидел новый/удалённый параметр.
- При изменении `relatedCategories` не требуется править код страницы категории — фильтрация происходит автоматически.
