# Рецепт миграции контента категории из pentajunior → pentajunior-v2

Пошаговый рецепт, отработанный на 9 категориях проекта `pentajunior-v2`. Используется, когда в v2 уже есть товары с `intro`/`body`/`bullets`, но не хватает секции «Применение» / «Области применения» / «Способ применения», а таблицы характеристик уже перенесены.

## 1. Подготовка

- Рабочая директория: `/home/natan/pentajunior-v2`.
- Эталонный проект: `/home/natan/workspace/pentajunior`.
- Проверить slug категории в v2 и соответствующий `categoryId` в v1 (`src/data/products.tsx`).

## 2. Извлечь v1 данные

Из `workspace/pentajunior/src/data/products.tsx` извлекаем для каждого товара категории:
- `description` (JSX)
- `application` (JSX)
- `metaDescription` (только если в v2 пуст)

Парсинг JSX-файла делается через баланс скобок `{}` и регулярные выражения. См. `scripts/extract_v1_application.py`.

## 3. Определить, чего не хватает в v2

```sql
SELECT id, name, template_data FROM products WHERE category_id = ?;
```

Смотрим наполненность:
- `intro`, `body`, `bullets` — обычно уже есть
- `application` — может быть пустым или содержать plain-text
- `applications`, `application_industrial`, `application_domestic` — обычно отсутствуют
- `recommendations`, `method`, `important_note`, `surface_prep`, `mixing_steps`, `degassing`, `safety` — обычно отсутствуют

## 4. Распределить v1 application по полям v2

### 4.1 Общий алгоритм

Конвертируем JSX в Markdown (удаляем `<>`, `className`, экранируем):

```python
def jsx_to_html(js):
    s = js.replace('<>', '').replace('</>', '')
    s = re.sub(r'className="([^"]*)"', r'class="\1"', s)
    return s

def html_to_md(html):
    # через html.parser.HTMLParser
    # <p> → \n\n, <strong> → **, <li> → \n- , <h3> → \n\n###
    ...
```

Разбиваем по жирным заголовкам:

```python
parts = re.split(r'\n\n\*\*([^*]+)\*\*[:：]?\s*', md)
```

### 4.2 Семантическое распределение

| Заголовок v1 | Поле v2 | Примечание |
|---|---|---|
| Область применения / Промышленное применение / Бытовое применение | `applications` / `application_industrial` / `application_domestic` | Только список применений |
| Способ применения / Способы применения | `recommendations` или `method` | Если пошаговая инструкция — `recommendations`; если общий способ — `method` |
| Рекомендация | `method` или `recommendations` | Дополнительный совет |
| Важно / Внимание | `important_note` | Блок «Важно» |
| Подготовка поверхности | `surface_prep` | Для силиконовых компаундов |
| Приготовление смеси | `mixing_steps` | Нумерованный список |
| Дегазация и заливка | `degassing` | Инструкция |
| Меры безопасности | `safety` | Блок безопасности |

### 4.3 Разделение смешанного списка

Если `application` содержит и области, и инструкцию в одном списке (как у средств защиты рук), разделяем по ключевым глаголам:

```python
for item in items:
    lower = item.lower()
    if any(v in lower for v in ['нанесите', 'разотрите', 'смойте', 'удалите', 'распределите', 'дайте', 'обновляйте']):
        recommendations.append(item)
    else:
        applications.append(item)
```

## 5. Очистить дубли и артефакты

### 5.1 Удалить дублирующие поля

- Если `application_industrial` == `applications` — удалить `application_industrial`, иначе UniversalTemplate отрендерит список дважды.
- Если `surfaces` == `applications` — удалить `surfaces`, иначе DescriptionSection отрендерит тот же список как «Применимые поверхности».
- Очистить legacy `application` после переноса.

### 5.2 Очистить body/intro

Убрать из `body`/`intro` trailing-заголовки:

```python
body = re.sub(r'\s*Область применения [^:]+:.*$', '', body, flags=re.DOTALL)
body = re.sub(r'\s*Способ применения [^:]+:.*$', '', body, flags=re.DOTALL)
body = re.sub(r'\s*Способы применения [^:]+:.*$', '', body, flags=re.DOTALL)
```

## 6. Обновить БД v2

```python
import sqlite3, json
conn = sqlite3.connect('pentajunior.db')
cur = conn.cursor()
cur.execute("UPDATE products SET template_data=? WHERE id=?", (json.dumps(data, ensure_ascii=False), pid))
conn.commit()
```

## 7. Проверки

1. `npx tsc --noEmit`
2. `npm run build`
3. `git add pentajunior.db`
4. `git commit -m "data(products): ..."`
5. `git pull --rebase origin master && git push origin master`
6. Убить dev-сервер: `pkill -f 'next start --port 3001'`
7. Перезапустить: `npx next start --port 3001`
8. Проверить страницу: `curl -I http://localhost:3001/production/<slug>/<product-id>`
9. Визуальная проверка через `browser_navigate` + `browser_vision` — искать пустые списки, дублирование секций, сырой HTML.

## 8. Примеры категорий

| Категория v2 | category_id v2 | categoryId v1 | Что добавлялось |
|---|---|---|---|
| Силикон для форм | 1 | 1 | `surface_prep`, `mixing_steps`, `degassing`, `safety`, `important_note` (общая инструкция для всех) |
| Разделительные смазки | 2 | 2 | `applications`, `method`, `important_note` |
| Масла ПМС | 3 | 3 | `applications` |
| Высокотемпературные смазки | 4 | 4 | `applications`, убрано дублирующее `application_industrial` |
| Силиконовые герметики | 5 | 5 | `applications`, убрано дублирующее `surfaces` |
| Силиконовые коврики ТСМ-1 | 6 | 6 | `application_industrial`, `application_domestic` |
| Изделия из силиконовых резин | 7 | 7 | `applications` (из plain-text `application`) |
| Гидрофобизаторы | 8 | 8 | `recommendations`, `method`, `important_note` |
| Средства защиты рук | 9 | 9 | `applications` + `recommendations` (разделение смешанного списка) |

## 9. Частые ловушки

- **Сырой HTML в `application`**: если поле `application` содержит HTML, `MarkdownParagraph` его экранирует и пользователь видит теги. Конвертировать в Markdown или разбить на массивы строк.
- **Пустые списки в snapshot**: accessibility tree не всегда показывает текст рядом с иконками Bootstrap. Проверять визуально через `browser_vision`.
- **Дублирование секций**: появляется, когда `applications` + `application_industrial` + `application_domestic` совпадают, или `applications` + `surfaces`.
- **Пропущенная перезапуск сервера**: `next start` отдаёт старую сборку из `.next`. После `npm run build` обязательно перезапускать.
