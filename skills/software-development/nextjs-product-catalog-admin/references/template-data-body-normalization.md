# Template Data Body Normalization

## Problem

During migration from hardcoded JSX data arrays to SQLite + React templates, the `description` field
(often a multi-paragraph ReactNode in v1) is flattened into a single `body` string. That string
frequently contains section headers inline:

```
body: "Пента®-219 — высокотемпературная антифрикционная пластичная смазка ...
Ключевые преимущества: Минимальное изменение вязкости ... Отличные диэлектрические свойства ...
ТУ: 2257-156-40245042-2006
Область применения Пента®-219: Хлебопекарное и другое высокотемпературное оборудование ..."
```

When rendered in the template, this becomes a wall of text with random colons — poor UX and bad SEO.

## Solution: Structured Extraction

After migration, run a normalization pass over `template_data` that:

1. **Identifies inline headers** — regex `\b([А-Я][А-Яа-я\s]+):\s*(.*)`
2. **Maps headers to fields**:
   | Header pattern | Target field | Data transformation |
   |---|---|---|
   | `Ключевые свойства` / `Ключевые преимущества` / `Характеристики` | `bullets` | Split by period into sentences, filter short ones |
   | `Область применения` / `Применение` / `Области применения` | `application_industrial` | Same split |
   | `Состав` | `composition` | Keep as single string |
   | Any other header | — | Leave in body or log for manual review |
3. **Removes extracted content from body** so it doesn't duplicate
4. **Deletes empty body** if nothing remains

## Python Normalization Snippet

```python
import re, json, sqlite3

def normalize_template_data(conn):
    c = conn.cursor()
    c.execute("SELECT id, template_data FROM products")
    for pid, td_json in c.fetchall():
        if not td_json:
            continue
        td = json.loads(td_json)
        body = td.get('body', '')
        if not body:
            continue

        parts = re.split(r'(?=\b[А-Я][А-Яа-я\s]+:)', body)
        new_body = ''
        for part in parts:
            part = part.strip()
            if not part:
                continue
            m = re.match(r'([А-Я][А-Яа-я\s]+):\s*(.*)', part, re.DOTALL)
            if not m:
                new_body += part + ' '
                continue
            header, content = m.groups()
            header = header.strip()
            content = content.strip()

            if header in ('Ключевые свойства', 'Ключевые преимущества', 'Характеристики'):
                td.setdefault('bullets', []).extend(
                    s.strip() for s in content.split('.')
                    if len(s.strip()) > 5
                )
            elif header in ('Область применения', 'Применение', 'Области применения'):
                td.setdefault('application_industrial', []).extend(
                    s.strip() for s in content.split('.')
                    if len(s.strip()) > 5
                )
            elif header == 'Состав':
                td['composition'] = content
            else:
                new_body += part + ' '

        td['body'] = new_body.strip()
        if not td['body']:
            del td['body']

        c.execute("UPDATE products SET template_data = ? WHERE id = ?",
                   (json.dumps(td, ensure_ascii=False), pid))
    conn.commit()
```

## Verification

After normalization, query for any remaining inline headers:

```sql
SELECT id, json_extract(template_data, '$.body') AS body
FROM products
WHERE body LIKE '%:%'
  AND body REGEXP 'Ключевые|Применение|Состав|Характеристики';
```

## When to Apply

- **Immediately after initial migration** — before the first build
- **After manual data entry** — admins may paste text with headers
- **Periodically** — add to migration audit script

## Prevention

In the admin editor (`TemplateDataEditor`), never provide a single monolithic "Description" textarea.
Instead, provide separate fields per section:

```tsx
const TEMPLATE_FIELDS = {
  release: [
    { key: 'intro', label: 'Вводное описание', type: 'textarea' },
    { key: 'composition', label: 'Состав', type: 'textarea' },
    { key: 'bullets', label: 'Основные свойства (по строке)', type: 'lines' },
    { key: 'application_industrial', label: 'Промышленное применение', type: 'lines' },
    // ...
  ],
};
```

This prevents the problem from recurring.
