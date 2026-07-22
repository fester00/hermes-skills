# SEO-таблицы и product spec-таблицы в pentajunior-v2

Конденсированные рецепты для добавления стилизованных таблиц в `seo_text` категорий/подкатегорий и для подключения dedicated `spec_tables` к товарам.

## 1. Таблицы внутри `seo_text` (category / subcategory)

Используем собственные CSS-классы `.rti-range-table` и `.rti-table-wrapper`, уже добавленные в `src/app/globals.css`.

### HTML-шаблон

```html
<section class="mt-5">
  <h2 class="h5 mb-3">Заголовок секции с таблицей</h2>
  <div class="table-responsive">
    <div class="rti-table-wrapper">
      <table class="table table-sm align-middle rti-range-table">
        <thead>
          <tr>
            <th scope="col">Параметр</th>
            <th scope="col">Значение 1</th>
            <th scope="col">Значение 2</th>
          </tr>
        </thead>
        <tbody>
          <tr><td>Параметр 1</td><td>...</td><td>...</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>
```

### Правила

- **Без собственных `<h1>` / `<h2>`** внутри `seo_text` — `SeoTextSection.tsx` уже рендерит обёртку с `<h2>`. Внутри `seo_text` используй `<h3>` для подзаголовков таблиц.
- **Внешняя обёртка** — `table-responsive` снаружи, `rti-table-wrapper` внутри. Это даёт горизонтальный скролл на мобильных без сжатия таблицы.
- **`<thead>` без `table-light`** — Bootstrap-класс `table-light` перебивает оливковый фон заголовка.
- Ширина `.rti-table-wrapper` фиксируется через `min-width` (например, `720px`), чтобы `table-responsive` не сжимал таблицу.
- При обновлении `seo_text` всегда делать backup БД и проходить build gate.

### CSS-ключевые свойства

- Фон заголовка: `var(--olive-green)` (#8fb34f).
- Цвет текста заголовка: `#fff !important`.
- Hover строк: `var(--mint-pale)`.
- Чётные строки: `var(--ash-lighter)`.

## 2. Таблицы характеристик товара (product spec tables)

### Архитектура

- `products.spec_table_id` → `spec_tables.id`.
- `spec_tables.columns_json` — JSON-массив строк (первая колонка — название параметра, остальные — продукты/размеры).
- `spec_tables.rows_json` — массив объектов `{name: "Параметр", values: {"Колонка 2": "значение", ...}}`.
- Компонент `src/components/UI/Tables/TableIncluder.tsx` рендерит таблицу и выделяет колонку текущего товара.

### Рецепт добавления dedicated spec table

1. Создать запись в `spec_tables`:

```sql
INSERT INTO spec_tables (id, columns_json, rows_json)
VALUES (
  'product-slug-specs',
  '["Параметр", "Размер A", "Размер B"]',
  '[{"name": "Параметр 1", "values": {"Размер A": "...", "Размер B": "..."}}]'
);
```

2. Привязать к товару:

```sql
UPDATE products SET spec_table_id = 'product-slug-specs' WHERE id = 'product-slug';
```

3. Обновить `template_data` товара через `UniversalTemplate`, чтобы добавить описание, области применения, свойства, температурный диапазон.

4. Пройти build gate: `npx tsc --noEmit && npm run build`.

### Выделение текущего товара в TableIncluder

`TableIncluder` ищет колонку по:
- последнему сегменту ID товара;
- нормализованному совпадению с `productTitle`;
- числам в названии колонки.

Для товаров с ID без цифр и сложных названий проверяйте, что колонка совпадает с `productTitle` нормализованно, либо обновите логику matching в компоненте.

### Верхний скроллбар для широких таблиц

Чтобы скролл был виден **сверху** таблицы (а не снизу), используется двойной `rotateX(180deg)`:

```css
.spec-table-top-scroll {
  transform: rotateX(180deg);
  margin-bottom: 0.5rem;
}

.spec-table-top-scroll .table-responsive {
  transform: rotateX(180deg);
}
```

Компонент `TableIncluder` оборачивает `.table-responsive` в `.spec-table-top-scroll`.

## 3. Визуальные SEO-блоки

- Загружайте навыки дизайна (`ui-ux-pro-max`, `claude-design`) перед правками карточек/таблиц, когда пользователь просит «сделать посимпатичнее».
- Карточки в `seo_text` используют Bootstrap: `row g-4 my-1`, `col-md-6`, `h-100 p-4 rounded-3 bg-body-tertiary`, `h6 fw-semibold mb-2`, иконки `bi-*`.
- Для структурированного списка размеров используйте `badge text-bg-light border` для групп и `list-unstyled small` с `bi-check2`.

## 4. Проверка после изменений

- Скриншоты через headless Chrome для desktop (1280px) и mobile (375px).
- Проверить, что таблица не сжимается, а скроллится горизонтально.
- Проверить, что заголовок таблицы виден (оливковый/синий фон, белый текст).
- Build gate обязателен перед коммитом.
