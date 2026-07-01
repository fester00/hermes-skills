# Чеклист проверки JSON-LD и мета-тегов pentajunior-v2

## Мета-теги

- [ ] `meta_title` не пустой у всех категорий, подкатегорий, товаров.
- [ ] `meta_description` не пустой у всех категорий, подкатегорий, товаров.
- [ ] `meta_title` заканчивается на `| Пента Юниор` (в БД), код не добавляет бренд повторно.
- [ ] `meta_description` ≤~160 символов, без дублирования бренда.
- [ ] `page_description` заполнен и отличается от `meta_description`.
- [ ] `keywords` — JSON-массив, 5–7 релевантных ключей.
- [ ] `features` не пустой у товаров (fallback description в JSON-LD).
- [ ] `pack` заполнен у товаров, где есть фасовка.
- [ ] `price` — числовая строка или NULL; при наличии акции `stock_info.newPrice` тоже числовая строка.

## JSON-LD

- [ ] Глобальный `Organization` / `WebSite` / `LocalBusiness` в `layout.tsx` корректен.
- [ ] `/logo.png` существует в `public/` или используется fallback.
- [ ] Категория: `CollectionPage` + `ItemList` подкатегорий + `BreadcrumbList`.
- [ ] Подкатегория: `CollectionPage` + `ItemList` товаров + `BreadcrumbList`; каждый `Product` имеет `offers` с числовой ценой.
- [ ] Все JSON-поля в SQLite валидны (`related_categories`, `features`, `keywords`, `stock_info`, `template_data`, `columns_json`, `rows_json`).
- [ ] Акционная цена `stock_info.newPrice` участвует в `Offer`, если есть.
- [ ] Изображения товаров абсолютные пути (`/images/...`) и файлы существуют в `public/`.

## Проверка админки (категории)

- [ ] API `PUT /api/admin/categories/[id]` и `POST /api/admin/categories` обновляют поле `seo_text`.
- [ ] После сохранения категории через админку изменения `seo_text` видны в `curl /api/admin/categories`.

## Проверка сборки

- [ ] `npx tsc --noEmit` без ошибок.
- [ ] `npm run build` успешен, статические страницы сгенерированы.

## Автоматический аудит (Python/SQLite)

```python
import sqlite3, json, os
DB = "/home/natan/pentajunior-v2/pentajunior.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
issues = []

for c in cur.execute("SELECT slug, title, meta_title, meta_description, related_categories FROM categories").fetchall():
    if not c['meta_title']: issues.append(f"Category {c['slug']}: empty meta_title")
    if not c['meta_description']: issues.append(f"Category {c['slug']}: empty meta_description")
    try:
        json.loads(c['related_categories'] or '[]')
    except Exception as e:
        issues.append(f"Category {c['slug']}: related_categories invalid JSON: {e}")

for s in cur.execute("SELECT slug, title, meta_title, meta_description FROM subcategories").fetchall():
    if not s['meta_title']: issues.append(f"Subcategory {s['slug']}: empty meta_title")
    if not s['meta_description']: issues.append(f"Subcategory {s['slug']}: empty meta_description")

for p in cur.execute("SELECT id, name, meta_title, meta_description, price, features, stock_info, template_data FROM products").fetchall():
    if not p['meta_title']: issues.append(f"Product {p['id']}: empty meta_title")
    if not p['meta_description']: issues.append(f"Product {p['id']}: empty meta_description")
    for field in ('features', 'stock_info', 'template_data'):
        try:
            json.loads(p[field] or ('[]' if field == 'features' else '{}' if field == 'template_data' else '{}'))
        except Exception as e:
            issues.append(f"Product {p['id']}: {field} invalid JSON: {e}")

print("Issues:", len(issues))
for i in issues: print(i)
```
