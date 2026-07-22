# SQLite-рецепты для аудита keywords и мета-тегов pentajunior-v2

Набор SQL-запросов через Python + `sqlite3` для быстрой диагностики SEO-проблем в `pentajunior.db` без запуска dev-сервера.

## Подключение

```python
import sqlite3, json
conn = sqlite3.connect('/home/natan/pentajunior-v2/pentajunior.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()
```

## 1. Сводка по длине title/description

```python
def length_summary(table, id_col='id'):
    print(f'\n=== {table} ===')
    for field, limit in [('meta_title', 70), ('meta_description', 160)]:
        rows = c.execute(f'''
            SELECT {id_col}, {field}, LENGTH({field}) as l FROM {table}
            WHERE LENGTH({field}) > ? AND {field} IS NOT NULL AND {field} != ''
            ORDER BY l DESC
        ''', (limit,)).fetchall()
        print(f'{field} >{limit}: {len(rows)}')
        for r in rows[:10]:
            print(f'  [{r[id_col]}] ({r["l"]}) {r[field][:80]}')

length_summary('categories')
length_summary('subcategories')
length_summary('products', 'id')
```

## 2. Поиск шаблонных keywords внутри подкатегории

```python
from collections import defaultdict

rows = c.execute('''
    SELECT c.slug cat, s.slug sub, p.id, p.name, p.keywords
    FROM products p
    JOIN subcategories s ON p.subcategory_id=s.id
    JOIN categories c ON s.category_id=c.id
''').fetchall()

kw_groups = defaultdict(list)
for r in rows:
    try:
        kw = tuple(sorted(json.loads(r['keywords'] or '[]')))
        kw_groups[(r['cat'], r['sub'], kw)].append(r)
    except Exception:
        pass

for (cat, sub, kw), prods in kw_groups.items():
    if len(prods) > 1 and kw:
        print(f'{cat}/{sub}: {len(prods)} товаров с одинаковыми keywords')
        for p in prods:
            print(f'  {p["id"]} | {p["name"]}')
```

## 3. Поиск проблемных формулировок

### «От производителя»

```python
for table in ['categories', 'subcategories', 'products']:
    id_col = 'id' if table != 'products' else 'id'
    rows = c.execute(f'''
        SELECT * FROM {table}
        WHERE meta_title LIKE '%от производителя%'
           OR meta_description LIKE '%от производителя%'
           OR page_description LIKE '%от производителя%'
           OR seo_text LIKE '%от производителя%'
    ''').fetchall()
    if rows:
        print(f'{table}: {len(rows)}')
        for r in rows[:5]:
            print(f'  [{r[id_col]}] {r["title" if "title" in r.keys() else "name"]}')
```

### Пищевая промышленность / FDA / BfR

```python
terms = ['FDA', 'BfR', 'пищевая', 'пищевой', 'медицинские', 'медицинский']
for table in ['categories', 'subcategories', 'products']:
    conditions = ' OR '.join(f"meta_title LIKE '%{t}%' OR meta_description LIKE '%{t}%' OR page_description LIKE '%{t}%' OR seo_text LIKE '%{t}%'" for t in terms)
    rows = c.execute(f'SELECT * FROM {table} WHERE {conditions}').fetchall()
    if rows:
        print(f'{table}: {len(rows)} упоминаний')
        for r in rows[:5]:
            id_col = 'id'
            print(f'  [{r[id_col]}] {r.get("title") or r.get("name")}')
```

## 4. Товары без цены и изображения

```python
no_price = c.execute('''
    SELECT c.slug cat, s.slug sub, p.id, p.name
    FROM products p
    JOIN subcategories s ON p.subcategory_id=s.id
    JOIN categories c ON s.category_id=c.id
    WHERE p.price IS NULL OR p.price='' OR p.price='None'
''').fetchall()

no_image = c.execute('''
    SELECT c.slug cat, s.slug sub, p.id, p.name
    FROM products p
    JOIN subcategories s ON p.subcategory_id=s.id
    JOIN categories c ON s.category_id=c.id
    WHERE p.image IS NULL OR p.image=''
''').fetchall()

print(f'Без цены: {len(no_price)}')
print(f'Без image: {len(no_image)}')
```

## 5. Проверка JSON-полей на валидность

```python
json_fields = ['features', 'keywords', 'stock_info', 'template_data', 'related_categories', 'price_tiers']
rows = c.execute('SELECT id, ' + ', '.join(json_fields) + ' FROM products').fetchall()
for r in rows:
    for field in json_fields:
        val = r[field]
        if val and val not in ('[]', '{}'):
            try:
                json.loads(val)
            except Exception as e:
                print(f'{r["id"]} {field}: INVALID JSON - {e}')
```

## 6. Проверка keywords на релевантность предмету страницы

Простая эвристика: keywords должны пересекаться с названием/подкатегорией/категорией.

```python
rows = c.execute('''
    SELECT c.slug cat, s.slug sub, p.id, p.name, p.title, p.keywords
    FROM products p
    JOIN subcategories s ON p.subcategory_id=s.id
    JOIN categories c ON s.category_id=c.id
''').fetchall()

for r in rows:
    kw = json.loads(r['keywords'] or '[]')
    name_lower = r['name'].lower()
    sub_lower = r['sub'].lower().replace('-', ' ')
    cat_lower = r['cat'].lower().replace('-', ' ')
    relevant = any(
        k.lower() in name_lower or k.lower() in sub_lower or k.lower() in cat_lower
        for k in kw
    )
    if not relevant:
        print(f'{r["cat"]}/{r["sub"]}/{r["id"]} | {r["name"]}')
        print(f'  keywords: {kw}')
```

> Важно: эта эвристика может давать ложные срабатывания, если keywords построены по марке/применению, а не по slug. Использовать как сигнал, а не как истину.
