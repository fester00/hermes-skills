# SEO-структура карточек категорий в каталоге

Карточка категории на странице `/production` — это не просто визуальный блок. Она должна быть семантически корректной и полезной для поисковых систем.

## Что не работает для SEO

- **Перечисление названий товаров внутри карточки без ссылок** почти не даёт SEO-веса. Это просто текст, похожий на keyword stuffing.
- **Длинные перечни свойств** внутри карточки отвлекают пользователя и удлиняют карточку неравномерно.
- **Скрытые или визуально неразличимые заголовки** ухудшают доступность.

## Что работает

1. **Чистая иерархия заголовков**
   - `h1` — заголовок страницы ("Каталог продукции").
   - `h2` — название каждой категории в карточке.
   - `p` — уникальное описание категории.

2. **Уникальное описание категории**
   - 1–3 предложения.
   - Содержит ключевые слова естественным образом.
   - Не дублирует `meta_description` дословно.

3. **Изображение категории с осмысленным `alt`**
   - `alt={title}` — лучше, чем "image" или пустой alt.
   - Изображение относится к категории, а не к случайному товару.

4. **Кликабельная карточка**
   - Вся карточка обёрнута в `<a>` или содержит явную ссылку.
   - Ссылка ведёт на страницу категории `/production/[slug]`.

5. **JSON-LD ItemList**
   - Страница `/production` экспортирует `CollectionPage` + `ItemList` с категориями.
   - Каждый элемент `itemListElement` содержит `name`, `description`, `url`.

6. **Одинаковая высота карточек**
   - Используй `display: flex` + `flex-grow-1` для описания и ссылки.
   - Это улучшает визуальное восприятие и снижает layout shift.

## Рекомендуемая структура карточки

```tsx
<article className="col-12 col-sm-6 col-lg-4 col-xl-3 mb-4 d-flex">
  <Link href={href} className="service-card category-card-v1 d-flex flex-column w-100">
    <div className="service-card-media mb-3">
      {imageSrc ? (
        <Image src={imageSrc} alt={title} fill className="object-fit-contain p-3" />
      ) : (
        <ProductImagePlaceholder title={title} />
      )}
    </div>

    <div className="d-flex flex-column flex-grow-1 px-1">
      <span className="badge category-count-badge">{productCount} товаров</span>
      <h2 className="card-title mb-2">{title}</h2>
      <p className="card-desc flex-grow-1">{page_description || meta_description}</p>

      <footer className="category-card-footer mt-auto pt-3">
        <span className="category-card-link">
          Перейти в раздел <i className="bi bi-arrow-right" />
        </span>
      </footer>
    </div>
  </Link>
</article>
```

### Стили бейджа

Бейдж должен быть в брендовой палитре, а не тёмным Bootstrap `bg-secondary`:

```css
.category-count-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  background: var(--mint-pale);     /* светло-мятный фон */
  color: var(--olive-dark);           /* оливковый текст */
  border: 1px solid rgba(143, 179, 79, 0.25);
}
```

## Практический вывод для пентаюниор

В карточках категорий на `/production` было решено:
- убрать список товаров из карточки (перечисление названий без ссылок не даёт SEO-веса);
- оставить превью категории, бейдж количества товаров в брендовом цвете, заголовок `h2`, описание и ссылку;
- использовать единый размер карточек в сетке (`d-flex` + `flex-grow-1`);
- для категорий без изображения показывать плейсхолдер с инициалами названия.

Это упрощает страницу, делает карточки ровными и не пытается "прокачать" SEO через переспам ключевыми словами.
