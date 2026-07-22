# Yandex SEO-аудит pentajunior-v2: практический чек-лист

Проверенный на проекте pentajunior-v2 порядок аудита по 20-пунктовому чек-листу Яндекс Вебмастера. Использовать вместе с `yandex-seo-optimization/SKILL.md`.

## Порядок работы

1. Проверить живой сайт (`curl`/Python):
   - HTTPS, главное зеркало, 200/404.
   - `robots.txt`, `sitemap.xml`.
   - title/description/H1 на главной, категории, подкатегории, товаре, `/info`, `/contacts`, `/policy`.
2. Проверить SQLite (`pentajunior.db`):
   - `meta_title`, `meta_description`, `page_description`, `seo_text` — пустые/заполненные.
   - длина title/description.
   - товары без `price` и без `image`.
   - шаблонные keywords внутри подкатегории.
3. Проверить собранный HTML из `.next/server/app`:
   - JSON-LD типы.
   - `Product`/`Offer` цены.
   - H1-H3 структура.
4. Проверить коммерческие факторы:
   - Яндекс.Метрика установлена?
   - цены у всех товаров?
   - изображения у всех товаров?
   - контакты/адрес в JSON-LD.
5. Сформировать отчёт и сохранить в Obsidian `Projects/pentajunior-v2-yandex-seo-audit-YYYY-MM-DD.md`.

## SQLite-рецепты

### Сводка по подкатегориям

```python
import sqlite3
conn = sqlite3.connect('/home/natan/pentajunior-v2/pentajunior.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()
rows = c.execute('''SELECT s.id, s.slug sub_slug, c.slug cat_slug, COUNT(p.id) cnt,
SUM(CASE WHEN p.keywords IS NULL OR p.keywords='' OR p.keywords='[]' THEN 1 ELSE 0 END) empty_kw,
SUM(CASE WHEN p.price IS NULL OR p.price='' OR p.price='None' THEN 1 ELSE 0 END) no_price,
SUM(CASE WHEN p.image IS NULL OR p.image='' THEN 1 ELSE 0 END) no_image
FROM subcategories s JOIN categories c ON s.category_id=c.id
LEFT JOIN products p ON p.subcategory_id=s.id
GROUP BY s.id ORDER BY c.id, s.id''').fetchall()
for r in rows:
    print(f"{r['cat_slug']}/{r['sub_slug']}: товаров={r['cnt']}, пустых keywords={r['empty_kw']}, без цены={r['no_price']}, без image={r['no_image']}")
```

### Title/description по длине

```python
# Категории
for r in c.execute("SELECT slug, meta_title, LENGTH(meta_title) l FROM categories WHERE LENGTH(meta_title) > 70 ORDER BY l DESC"):
    print(r['slug'], r['l'], r['meta_title'])
# Подкатегории
for r in c.execute("SELECT s.slug, c.slug cat, s.meta_title, LENGTH(s.meta_title) l FROM subcategories s JOIN categories c ON s.category_id=c.id WHERE LENGTH(s.meta_title) > 70 ORDER BY l DESC"):
    print(r['cat'], r['slug'], r['l'], r['meta_title'])
# Товары
for r in c.execute("SELECT p.id, p.name, p.meta_title, LENGTH(p.meta_title) l FROM products p WHERE LENGTH(p.meta_title) > 70 ORDER BY l DESC"):
    print(r['id'], r['name'], r['l'], r['meta_title'])
```

### Товары без цены

```python
for r in c.execute('''SELECT c.slug cat, s.slug sub, p.id, p.name
FROM products p JOIN subcategories s ON p.subcategory_id=s.id
JOIN categories c ON s.category_id=c.id
WHERE p.price IS NULL OR p.price='' OR p.price='None' ORDER BY c.id, s.id''').fetchall():
    print(f"{r['cat']}/{r['sub']}/{r['id']}: {r['name']}")
```

### Товары без image

```python
for r in c.execute('''SELECT c.slug cat, s.slug sub, p.id, p.name
FROM products p JOIN subcategories s ON p.subcategory_id=s.id
JOIN categories c ON s.category_id=c.id
WHERE p.image IS NULL OR p.image='' ORDER BY c.id, s.id''').fetchall():
    print(f"{r['cat']}/{r['sub']}/{r['id']}: {r['name']}")
```

### Шаблонные keywords

```python
import sqlite3, json
conn = sqlite3.connect('/home/natan/pentajunior-v2/pentajunior.db')
c = conn.cursor()
for s in c.execute('SELECT id, slug FROM subcategories').fetchall():
    prods = c.execute('SELECT id, name, keywords FROM products WHERE subcategory_id=?', (s['id'],)).fetchall()
    kw_sets = [tuple(sorted(json.loads(p['keywords'] or '[]'))) for p in prods]
    if len(set(kw_sets)) == 1 and len(prods) > 1 and any(kw_sets):
        print(f"{s['slug']}: у всех {len(prods)} товаров одинаковые keywords: {kw_sets[0]}")
```

## Живые проверки

### Title/description/H1

```python
import urllib.request, ssl, re
ctx = ssl.create_default_context()
urls = ['https://pentajunior.ru/', 'https://pentajunior.ru/production/silikon-dlya-zalivki-form']
for url in urls:
    html = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=15, context=ctx).read().decode()
    title = re.search(r'<title>(.*?)</title>', html, re.S)
    desc = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)', html, re.I)
    h1 = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.S|re.I)
    print(url, len(title.group(1) if title else ''), len(desc.group(1) if desc else ''), len(h1))
```

### JSON-LD

```python
import urllib.request, ssl, re, json
ctx = ssl.create_default_context()
html = urllib.request.urlopen(urllib.request.Request('https://pentajunior.ru/production/silikon-dlya-zalivki-form/silikon-platinovyj-dla-form', headers={'User-Agent':'Mozilla/5.0'}), timeout=15, context=ctx).read().decode()
for js in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
    data = json.loads(js)
    types = [item.get('@type') for item in data.get('@graph', [])]
    print(types)
```

## Формат отчёта

Сохранять в `~/obsidian-memory/Projects/pentajunior-v2-yandex-seo-audit-YYYY-MM-DD.md`:
- резюме со статусами блоков;
- таблицу P0/P1/P2 находок;
- список товаров без цены и без image;
- примеры длинных title/description;
- 20-пунктовый чек-лист навыка со статусом;
- следующий рекомендуемый шаг.
