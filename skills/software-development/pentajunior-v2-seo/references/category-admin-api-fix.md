# Исправление API админки категорий: сохранение `seo_text`

## Контекст

Форма редактирования категории в `/admin/categories` показывает поле «SEO-текст (HTML)» и отправляет его на сервер, но API маршрутов `/api/admin/categories` и `/api/admin/categories/[id]` изначально не включали `seo_text` в SQL-запросы. В результате изменения сохранялись только локально в React-стейте, в БД не попадали, и после перезагрузки страницы правки исчезали.

## Исправление

### `src/app/api/admin/categories/route.ts` (POST)

Добавить `seo_text` в список колонок и параметров:

```ts
const result = db.prepare(`INSERT INTO categories (slug, title, href, image, meta_title, meta_description, page_description, seo_text, related_categories, template_type)
  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`)
  .run(
    body.slug,
    body.title,
    body.href,
    body.image || null,
    body.meta_title || '',
    body.meta_description || '',
    body.page_description || '',
    body.seo_text ?? null,
    JSON.stringify(body.related_categories || []),
    body.template_type || 'default'
  );
```

### `src/app/api/admin/categories/[id]/route.ts` (PUT)

Добавить `seo_text = ?` в UPDATE и параметр:

```ts
const result = db.prepare(`UPDATE categories SET 
  slug = ?, title = ?, href = ?, image = ?, meta_title = ?, meta_description = ?, page_description = ?, seo_text = ?, related_categories = ?, template_type = ?
  WHERE id = ?`)
  .run(
    body.slug,
    body.title,
    body.href,
    body.image || null,
    body.meta_title || '',
    body.meta_description || '',
    body.page_description || '',
    body.seo_text ?? null,
    JSON.stringify(body.related_categories || []),
    body.template_type || 'default',
    id
  );
```

## Проверка

1. Сохранить категорию через `/admin/categories` с изменённым SEO-текстом.
2. Выполнить:
   ```bash
   curl -s -b /tmp/cookies.txt http://localhost:3002/api/admin/categories | python3 -m json.tool | grep -A2 '"seo_text"'
   ```
   или через `sqlite3 pentajunior.db "SELECT seo_text FROM categories WHERE slug = '<slug>';"`.
3. Убедиться, что текст обновился.

## Связанные файлы

- `src/app/admin/categories/page.tsx` — UI формы (уже содержит поле `seo_text`).
- `src/app/api/admin/categories/route.ts`
- `src/app/api/admin/categories/[id]/route.ts`
