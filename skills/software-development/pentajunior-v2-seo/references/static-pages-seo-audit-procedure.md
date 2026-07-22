# SEO-аудит статических страниц pentajunior-v2

Часть данных SEO pentajunior-v2 находится в SQLite (категории, подкатегории, товары), а часть — в статических файлах Next.js. Глобальный `global-seo-final-check.py` проверяет только БД, поэтому статику нужно проверять отдельно.

## Что проверять

1. **`src/app/page.tsx`** — главная страница:
   - `metadata.title` и `metadata.description`;
   - `openGraph.title` / `openGraph.description`;
   - `homeJsonLd["@graph"][0].name` и `.description` (WebPage);
   - H1 в JSX.

2. **`src/app/layout.tsx` + `src/app/syte-config.ts`** — глобальные мета:
   - `metadata.title` и `metadata.description` в layout;
   - `CONFIG.description` — используется в `metadata`, `openGraph`, `twitter`, `Organization.description`;
   - JSON-LD `Organization.description`.

3. **Статические `page.tsx` с `export const metadata`**:
   - `src/app/price/page.tsx`;
   - `src/app/info/page.tsx`;
   - `src/app/info/faq/page.tsx`;
   - `src/app/contacts/page.tsx`;
   - `src/app/blog/page.tsx`;
   - `src/app/news/page.tsx`;
   - `src/app/policy/page.tsx`;
   - `src/app/production/page.tsx` (если есть).
   Проверять `title`, `description`, `openGraph`, `twitter`.

4. **Блог-статьи** (`src/data/blog/article-*.ts`):
   - `metaTitle` и `metaDescription`;
   - поле `published` (скрытые статьи должны иметь `published: false`).

## Как проверять

### Поиск «от производителя» / «производитель»

```bash
cd /home/natan/pentajunior-v2
grep -Rin "от производителя\|производство силиконовых" src/app src/data/blog
```

### Поиск длинных title/description в статических page.tsx

```bash
cd /home/natan/pentajunior-v2
python3 - <<'PY'
import os, re
ROOT='src/app'
for dirpath, dirs, files in os.walk(ROOT):
    if 'page.tsx' in files:
        path=os.path.join(dirpath,'page.tsx')
        text=open(path,encoding='utf-8').read()
        for kind in ['title','description']:
            for m in re.findall(rf'{kind}:\s*"([^"]+)"', text):
                limit = 70 if kind=='title' else 160
                if len(m)>limit or 'от производителя' in m.lower():
                    print(f"{path}: {kind} ({len(m)}): {m[:100]}")
PY
```

### Живая проверка title/description/H1/JSON-LD

```python
import requests, re, json
BASE='https://pentajunior.ru'
HEADERS={'User-Agent':'Mozilla/5.0 (compatible; HermesSEO-bot/1.0)'}
urls=['/','/production','/info','/contacts','/price','/info/faq','/blog','/news','/policy']
for u in urls:
    t=requests.get(BASE+u, headers=HEADERS, timeout=30).text
    title=re.search(r'<title>(.*?)</title>', t, re.S)
    desc=re.search(r'<meta[^>]*name="description"[^>]*content="([^"]*)"', t, re.S|re.I)
    h1=re.findall(r'<h1[^>]*>(.*?)</h1>', t, re.S)
    print(f"{u}: title({len(title.group(1) if title else '')}) desc({len(desc.group(1) if desc else '')}) h1={len(h1)}")
```

## Типичные находки и исправления

| Находка | Где править | Что делать |
|---|---|---|
| Title главной >70 | `src/app/page.tsx` metadata.title | Укоротить до ≤70, убрать «от производителя» |
| Description главной >160 | `src/app/page.tsx` metadata.description + openGraph | Переписать ≤160, нейтральное позиционирование |
| H1 «Силиконовые материалы от производителя» | `src/app/page.tsx` JSX | Заменить на «Силиконовые материалы — поставка и продажа» или аналогичное |
| Organization.description «Производство...» | `src/app/syte-config.ts` CONFIG.description | Сделать нейтральнее: «Поставка силиконовых материалов, герметиков, смазок» |
| openGraph/twitter price содержат «от производителя» | `src/app/price/page.tsx` | Заменить на «актуальные цены», «прайс-лист» |

## Правило позиционирования

Для дистрибьюторских линеек (ТЕХМОЛ Экстра, СОЖ и др.) не писать «от производителя». Безопасные замены:
- «купить»;
- «в Москве»;
- «официальный дистрибьютор ООО «ТЕХГРАНТ»» (для ТЕХМОЛ);
- «поставка» / «продажа».
