# Создание HTML-прототипов вариантов дизайна

Когда пользователь просит выбрать визуальный стиль для страницы, лучший рабочий паттерн — собрать несколько вариантов в один самодостаточный HTML-файл и отдать на выбор.

## Зачем

- Позволяет сравнить варианты бок о бок без пересборки Next.js.
- Фиксирует цветовую палитру и типографику до внесения изменений в код.
- Дает пользователю точку принятия решения.

## Структура HTML-файла

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page — 5 style variants</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --dark-graphite: #212529;
      --olive-green: #8fb34f;
      --dark-bordo: #160b0d;
      --mint-green: #6bdb85;
      --ash-rose: #d1c5c6;
      --white: #ffffff;
      /* ... */
    }

    .variant { padding: 60px 20px; border-top: 1px solid rgba(...); }
    .variant-label { /* uppercase label */ }
    /* v1, v2, v3 ... override common component classes */
  </style>
</head>
<body>
  <div class="page-intro">...</div>

  <section class="variant v1"> ... </section>
  <section class="variant v2"> ... </section>
  <!-- etc -->

  <script>
    // render shared data into each variant container
  </script>
</body>
</html>
```

## Правила

1. **Общая база компонентов** — карточки, бейджи, кнопки-фильтры используют одни и те же классы внутри каждого варианта.
2. **Вариант переопределяет только внешний вид** — не разметку.
3. **Реалистичный контент** — используй настоящие данные из БД проекта (заголовки, описания, изображения, количество товаров).
4. **CSS-переменные палитры** в `:root` — чтобы варианты оставались в рамках бренда.
5. **Файл кладётся в `~/workspace/`** — вне репозитория, чтобы не попадать в коммит.
6. **После выбора** — переносишь только выбранный вариант в проект: React-компонент + CSS.

## Пример именования

- `blog-style-variants.html`
- `production-style-variants.html`
- `product-card-style-variants.html`

## Реалистичные данные

Используй настоящие данные из БД проекта: заголовки категорий, `page_description`, пути к изображениям (`/images/categorys/...`) и количество товаров. Для категорий без собственного изображения отображай плейсхолдер с инициалами названия.

## После выбора варианта

1. Обнови React-компонент (`ProductsCard.tsx`) и CSS (`globals.css`).
2. Удали из карточек всё, что не вошло в выбранный вариант (например, перечисление товаров).
3. Собери проект заново: `rm -rf .next && npm run build`.
4. Запусти dev-сервер и проверь визуально — см. `references/nextjs-dev-server-cache-invalidation.md`.

## Sidebar variants

The same workflow applies to navigation components. For `pentajunior-v2` the user picked "Variant 1" (minimalism with accent line) for the production category sidebar. The implementation is captured in `references/category-sidebar-variant1-implementation.md`. When prototyping sidebars:

- Show real category/subcategory data and product counts.
- Prototype active-state colors **and** expand/collapse behavior, not just static layout.
- Make each category clickable in the prototype so the user can feel the accordion mechanics before you write React code.
- Place the prototype in `~/workspace/` and remove it after the user selects a variant.

## Why side-by-side beats Figma here

For developer-driven UI changes, a self-contained HTML file is faster than updating a design tool because:

- It uses the real project palette and fonts.
- It can include real data copied from the SQLite database.
- It runs in any browser without login or exports.
- The chosen CSS can be lifted almost directly into `globals.css`.

## Связь с проектом

Для пентаюниор-v2 этот паттерн применялся при выборе стиля страницы `/blog` (выбран "Dark hero cards") и `/production` (выбран "Clean cards with top image").
