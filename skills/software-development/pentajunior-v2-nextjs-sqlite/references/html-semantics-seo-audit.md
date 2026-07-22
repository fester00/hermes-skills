# HTML-семантика и SEO-аудит — pentajunior-v2

## Цель

Проверить, что публичные страницы имеют корректную семантическую структуру для поисковиков (Yandex/Google) и assistive-технологий.

## Чек-лист

### 1. Единственный логический H1

Каждая публичная страница должна иметь ровно один `<h1>`.

Способы поиска:
```bash
# page.tsx с явным <h1>
grep -R "<h1" src/app/*/page.tsx src/app/*/*/page.tsx src/app/*/*/*/page.tsx

# page.tsx с PageHeader (рендерит <h1> внутри)
grep -R "PageHeader" src/app/**/page.tsx
```

Частые проблемы:
| Проблема | Решение |
|---|---|
| `<h1>` внутри shared-карточки (`ProductCard.tsx`) | Сделать тег заголовка configurable через проп `titleTag` |
| `<h1>` отсутствует на странице, но есть `PageHeader` | OK — `PageHeader` рендерит `<h1>` |
| `<h1>` отсутствует полностью | Добавить `PageHeader` или явный `<h1>` |

### 2. Heading-иерархия без скачков

Правила:
- `<h1>` — один на страницу.
- `<h2>` — основные разделы.
- `<h3>` — подразделы внутри `<h2>`.
- Не допускать `<h2>` → `<h4>` без `<h3>`.

Конкретная проблема проекта — сайдбар `CategorySidebarClient.tsx` раньше использовал `<h3 className="category-sidebar-title">`, который в DOM шёл **перед** `<h1>` страницы:

```tsx
// ДО: плохо
<h3 className="category-sidebar-title">{title}</h3>

// ПОСЛЕ: хорошо
<span className="category-sidebar-title h5 d-block">{title}</span>
```

### 3. Заголовок товара — вынести H1 на уровень страницы

`ProductCard.tsx` используется на странице товара и потенциально может использоваться в списках. Лучшее решение — убрать заголовок товара изнутри `ProductCard` и рендерить его на уровне `page.tsx`.

```tsx
// src/components/UI/Cards/ProductCard.tsx
interface ProductCardProps {
  categorySlug: string;
  subcategorySlug?: string;
  product: Product;
}

export default function ProductCard({ categorySlug, subcategorySlug, product }: ProductCardProps) {
  // карточка без собственного H1/H2 — только изображение, характеристики, цена, CTA
  return (...);
}
```

На странице товара:

```tsx
// /production/[category]/[subcategory]/[product]/page.tsx
<div className="col-lg-8">
  <h1 className="mb-4 fs-2 fw-bold">{product.name}</h1>
  <ProductCard
    categorySlug={category.slug}
    subcategorySlug={subcategory.slug}
    product={product}
  />
</div>
```

**Почему это лучше, чем `titleTag` проп:**
- H1 видимый и находится на уровне страницы — чистая семантика.
- `ProductCard` становится безопасно reusable в списках и админ-превью.
- Нет risk'а accidental дублирования H1.
- Не нужны скрытые `visually-hidden` заголовки.

Если компонент уже использует `titleTag`, это приемлемый过渡ный вариант, но конечная цель — вынести H1 из компонента.

### 4. Пустые заголовки

Проверка:
```bash
rg "<h[1-6][^\u003e]*>\s*</h[1-6]>" src/
```

Пустые `<h2>` встречаются, когда внутри только `{variable}` которая может быть пустой. Заменить на условный рендеринг или `<div>`.

### 5. Семантические теги

Обязательные landmarks:
- `<header>`
- `<nav>` с `aria-label`
- `<main>`
- `<footer>`

Проверка:
```bash
rg "<header|<nav|<main|<footer" src/components/Layout/ src/app/layout.tsx
```

### 6. Image alt

Все `next/image` должны иметь описательный `alt`. Исключение — Яндекс-пиксель метрики: `alt=""`.

### 7. Breadcrumbs

Проверить, что на всех публичных страницах есть `Breadcrumbs` и соответствующий JSON-LD `BreadcrumbList`. Исключения: редко `/news`.

### 8. OG / canonical

- Каждая страница должна иметь `canonical` и `openGraph.url`.
- `openGraph.url` должен совпадать с `canonical`.
- OG-изображение лучше использовать специфичное для страницы (category/subcategory/product image), а не всегда `hero.webp`.

## Автоматизация

Скрипт для поиска страниц без H1:
```python
from pathlib import Path
import re

SRC = Path('src')
for f in SRC.rglob('page.tsx'):
    if 'admin' in str(f):
        continue
    content = f.read_text(encoding='utf-8')
    has_explicit_h1 = bool(re.search(r'<h1\b', content))
    has_pageheader = 'PageHeader' in content
    if not has_explicit_h1 and not has_pageheader:
        print(f"No H1: {f.relative_to(SRC)}")
```

## Build gate

После правок:
```bash
./node_modules/.bin/tsc --noEmit && rm -rf .next tsconfig.tsbuildinfo && npm run build
```
