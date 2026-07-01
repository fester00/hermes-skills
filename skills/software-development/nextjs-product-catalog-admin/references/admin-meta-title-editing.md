# Редактирование meta_title для категорий и подкатегорий в админке

## Контекст

В каталоге на Next.js + SQLite часто нужно, чтобы SEO-заголовок страницы (`<title>`) отличался от отображаемого названия категории/подкатегории. Для этого добавляется отдельное поле `meta_title` в таблицы `categories` и `subcategories` и выносится в админку.

## Что нужно изменить

### 1. Схема SQLite

```sql
ALTER TABLE categories ADD COLUMN meta_title TEXT DEFAULT '';
ALTER TABLE subcategories ADD COLUMN meta_title TEXT DEFAULT '';
```

### 2. Интерфейсы TypeScript

В `src/lib/db.ts` добавить `meta_title: string` в `Category` и `Subcategory`.

### 3. API админки

Обновить `INSERT` и `UPDATE` в:
- `src/app/api/admin/categories/route.ts`
- `src/app/api/admin/categories/[id]/route.ts`
- `src/app/api/admin/subcategories/route.ts`
- `src/app/api/admin/subcategories/[id]/route.ts`

Пример для категории:

```ts
const result = db.prepare(
  `UPDATE categories SET
    slug = ?, title = ?, href = ?, image = ?, meta_title = ?, meta_description = ?, page_description = ?, related_categories = ?, template_type = ?
   WHERE id = ?`
).run(
  body.slug,
  body.title,
  body.href,
  body.image || null,
  body.meta_title || '',
  body.meta_description || '',
  body.page_description || '',
  JSON.stringify(body.related_categories || []),
  body.template_type || 'default',
  id
);
```

### 4. Админ-форма

В `src/app/admin/categories/page.tsx` добавить поле перед «Meta описание»:

```tsx
<div className="col-12">
  <label className="form-label">Meta title (заголовок страницы)</label>
  <input
    className="form-control"
    value={editing.meta_title}
    onChange={(e) => setEditing({ ...editing, meta_title: e.target.value })}
  />
  <small className="text-muted">Если пусто — используется название категории.</small>
</div>
```

Аналогично для подкатегории.

### 5. Использование на публичных страницах

В `generateMetadata` страниц категории и подкатегории использовать `meta_title`, если задан, иначе `title`:

```tsx
const title = category.meta_title || category.title;
return {
  title: `${title} — Пента Юниор`,
  // ...
};
```

```tsx
const subTitle = subcategory.meta_title || subcategory.title;
return {
  title: `${subTitle} — ${category.title} — Пента Юниор`,
  // ...
};
```

## Проверка

1. `tsc --noEmit`.
2. `npm run build`.
3. Открыть `/admin/categories`, отредактировать категорию, заполнить Meta title, сохранить.
4. Проверить `<title>` на странице категории/подкатегории.
5. При пустом `meta_title` должен использоваться `title`.

## Связанные заметки

- `admin-sql-insert-mismatch-trap.md` — после добавления колонок важно, чтобы количество `?` в SQL совпадало с числом колонок.
- `nextjs-sqlite-types.md` — разделение DB-facing и component-facing типов.
