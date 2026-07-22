# Пост-рефакторный аудит и P3-задачи — pentajunior-v2

## Когда применять

После завершения крупного UI/API-рефактора, когда проект нужно оценить заново по критериям:
- приемлемое количество компонентов и поддерживаемость;
- корректная HTML-разметка для поисковиков;
- скорость загрузки;
- корректная архитектурная структура.

Цель — не идеальный проект, а рабочий качественный продукт.

## Как работать с сохранённым отчётом

Отчёт сохраняется в корне проекта (`ANALYSIS_REPORT_YYYY-MM.md`) и используется в последующих сессиях. Если пользователь говорит «пункты N, M, K» или «сделаем 16–19», работать строго по этим пунктам, не перескакивая на другие приоритеты, даже если они выглядят важнее.

Порядок:
1. Открыть `ANALYSIS_REPORT_YYYY-MM.md`.
2. Найти пункты по номерам.
3. Создать todo с этими пунктами.
4. Выполнять по одному с build gate.
5. После завершения группы спросить, с какого следующего пункта продолжить.

Не начинать P0/P1-работу самостоятельно, пока пользователь явно не сказал «давай P1 пункт 6» или аналогичное.

## Методология аудита

1. Запустить 4 параллельных агента:
   - компоненты и поддерживаемость;
   - SEO/HTML-разметка;
   - скорость загрузки;
   - архитектура.
2. Собрать метрики из `src/` и `.next/`:
   - количество компонентов и строк;
   - JS/CSS бандл;
   - inline-стили;
   - heading-иерархия;
   - импорты из `@/lib/db` в клиентских компонентах.
3. Прогнать `tsc --noEmit && rm -rf .next && npm run build`.
4. Прогнать ESLint: `./node_modules/.bin/eslint . --ext .ts,.tsx --max-warnings=100`.
5. Свести в отчёт с P0/P1/P2/P3 и сохранить в корне проекта (`ANALYSIS_REPORT_YYYY-MM.md`).
6. Удалить временные файлы агентов, если они создали отчёты в корне.

## Типичные находки после рефактора

| Область | Что искать | Где |
|---|---|---|
| Компоненты | oversized files, дублирование типов/CRUD/JSON-LD | `src/app/admin/*`, `src/components/ProductTemplates/UniversalTemplate.tsx`, `src/components/admin/TemplateDataEditor.tsx` |
| SEO | `<h3>` перед `<h1>`, отсутствующий/спрятанный H1, пустые `<h2>`, OG URL mismatch | `CategorySidebarClient.tsx`, `ProductCard.tsx`, `blog/[articleId]/page.tsx` |
| Скорость | Bootstrap CSS full bundle, `globals.css` монолит, неоптимизированные изображения, тяжёлые iframe | `layout.tsx`, `globals.css`, `public/images/`, `contacts/page.tsx` |
| Архитектура | hardcoded пароли, plaintext cookie, SQL-инъекции, миграции в `lib/db.ts` | `src/app/api/admin/auth/route.ts`, `src/proxy.ts`, `src/lib/db.ts` |

## P3-задачи — безопасные quick wins

После согласования с пользователем выполнять по одной, с build gate.

### P3-16. Удалить мёртвый код

Файлы, которые обычно оказываются пустыми/неиспользуемыми после рефактора:
- `src/components/UI/Tables/PriceTable.tsx`
- `src/components/Sections/` (пустая папка)
- `src/app/page.module.css` (шаблон Next.js, не импортируется)

```bash
cd /home/natan/pentajunior-v2
rm -f src/components/UI/Tables/PriceTable.tsx
rm -rf src/components/Sections/
rm -f src/app/page.module.css
```

### P3-17. `<img>` → `<Image>`

Частый случай — поисковый dropdown `src/components/UI/Searcher.tsx`.

```tsx
import Image from "next/image";

// внутри результата поиска
<Image
  src={product.image}
  alt={product.title}
  width={40}
  height={40}
  className="rounded"
  style={{ objectFit: "cover" }}
  unoptimized
/>
```

Использовать `unoptimized`, если изображения лежат в `public/` и нет image-optimization server.

### P3-18. OG-изображения категорий/подкатегорий/товаров

Страницы каталога обычно шарят `/images/hero.webp`. Лучше использовать поле `image` сущности:

```tsx
// /production/[category]/page.tsx
const categoryImage = category.image
  ? `${baseUrl}${category.image}`
  : `${baseUrl}/images/hero.webp`;

// /production/[category]/[subcategory]/page.tsx
const subcategoryImage = subcategory.image
  ? `${baseUrl}${subcategory.image}`
  : `${baseUrl}/images/hero.webp`;

// /production/[category]/[subcategory]/[product]/page.tsx — обычно уже product.image
const productImage = product.image
  ? `${baseUrl}${product.image}`
  : `${baseUrl}/images/hero.webp`;
```

### P3-19. `next/font/google` для Inter

Если в `globals.css` используется `'Inter'` в `font-family`, но шрифт не загружается:

```tsx
// src/app/layout.tsx
import { Inter } from "next/font/google";

const inter = Inter({
  subsets: ["latin", "cyrillic"],
  display: "swap",
  variable: "--font-inter",
});

// <html className={inter.variable}>
// <body className={inter.variable}>
```

```css
/* src/app/globals.css */
body {
  font-family: var(--font-inter), -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
```

## Build gate

После каждого пункта:

```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
cd /home/natan/pentajunior-v2
./node_modules/.bin/tsc --noEmit && rm -rf .next tsconfig.tsbuildinfo && npm run build
```

Ожидаемый результат: 156/156 static pages.
