# Рецепт: усиление коротких метатегов и оптимизация статических страниц

## Контекст

Помимо категорий/подкатегорий/товаров в `pentajunior.db`, в проекте есть статические страницы Next.js и блог-статьи, у которых метатеги тоже влияют на SEO. Этот рецепт описывает, как находить и усиливать **короткие** title/description, а также проходить сервисные страницы и блог.

## Когда применять

- Пользователь сказал: «пройдись по метатегам» или «допиши короткие title и description».
- После основного прохода по категориям остались статические страницы и блог.
- title ≤50 символов или description ≤120 символов.

## Где живут метатеги

| Тип страницы | Файл | Поля |
|---|---|---|
| Главная | `src/app/layout.tsx` + `src/app/syte-config.ts` | `metadata.title`, `metadata.description`, `CONFIG.description`, `CONFIG.keys` |
| Сервисные страницы | `src/app/<page>/page.tsx` | `metadata.title`, `metadata.description` |
| Блог-список | `src/app/blog/page.tsx` | `metadata.title`, `metadata.description` |
| Блог-статьи | `src/data/blog/article-*.ts` | `metaTitle`, `metaDescription`, `keywords` |

## Пороги длины

| Поле | Минимум полезной длины | Максимум |
|---|---|---|
| `meta_title` / `title` | ≥45–50 символов | ≤70 |
| `meta_description` / `description` | ≥120 символов | ≤160 |

Если title <45 — точно дописываем. Если description <120 — точно дописываем.

## Формула усиления

Для статических страниц и блог-статей применяем ту же логику, что и для каталога:

1. **Марка / тема** — что это за страница.
2. **Целевое применение / выгода** — зачем пользователю эта страница.
3. **Коммерческий сигнал** — `купить`, `цены`, `доставка по России`, `Москва`, `Пента Юниор`.

### Примеры хороших преобразований

| Было | Стало |
|---|---|
| `Силикон для заливки форм — купить RTV-2` (53) | `Силикон для заливки форм — купить RTV-2, платиновый, оловянный` (69) |
| `Каталог продукции — Пента Юниор` (31) | `Каталог силиконовых материалов — купить | Пента Юниор` (62) |
| `Контакты компании Пента Юниор: адрес, телефоны...` (82 desc) | `Контакты Пента Юниор: адрес в Москве, телефоны, e-mail, банковские реквизиты. Региональные партнёры и дилеры по России.` (119) |

## Workflow

1. **Найти все статические страницы**:
   ```bash
   ls /home/natan/pentajunior-v2/src/app/*/page.tsx
   ```
   Исключить `admin`, `api`, `_not-found`, динамические маршруты `[...]`.

2. **Найти все блог-статьи**:
   ```bash
   ls /home/natan/pentajunior-v2/src/data/blog/article-*.ts
   ```

3. **Извлечь метатеги скриптом**:
   ```python
   import re
   from pathlib import Path
   
   # Статические страницы
   for f in Path('/home/natan/pentajunior-v2/src/app').glob('*/page.tsx'):
       text = f.read_text()
       title = re.search(r'title:\s*"([^"]+)"', text)
       title = title.group(1) if title else 'N/A'
       desc = re.search(r'description:\s*\n?\s*"([^"]+)"', text)
       desc = desc.group(1) if desc else 'N/A'
       print(f'{f.parent.name}: title={len(title)}, desc={len(desc)}')
   
   # Блог-статьи
   for f in Path('/home/natan/pentajunior-v2/src/data/blog').glob('article-*.ts'):
       text = f.read_text()
       id = re.search(r'id:\s*"([^"]+)"', text)
       title = re.search(r'metaTitle:\s*"([^"]+)"', text)
       desc = re.search(r'metaDescription:\s*"([^"]+)"', text)
       if id and title and desc:
           print(f'{id.group(1)}: title={len(title.group(1))}, desc={len(desc.group(1))}')
   ```

4. **Составить черновик правок** по формуле выше, показать пользователю, получить «давай».

5. **Применить правки** через `patch` для `.tsx` и `.ts` файлов.

6. **Build gate**:
   ```bash
   export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
   cd /home/natan/pentajunior-v2
   ./node_modules/.bin/tsc --noEmit
   rm -rf .next tsconfig.tsbuildinfo
   npm run build
   ```

7. **Глобальная финальная проверка** по всему сайту:
   - 0 title >70
   - 0 description >160
   - 0 «от производителя» / «производитель» в конце
   - 0 дублирующихся наборов keywords у товаров

8. **git add**, commit, push, deploy по команде пользователя.

## Что не забыть

- Убрать «от производителя» везде, кроме случаев, где это действительно так.
- Убрать «производитель» из description блог-статей — заменить на «Пента Юниор».
- Проверить, что главная `layout.tsx` не дублирует бренд в title.
- Если description превышает 160 — укоротить, не просто обрезать, а сохранить смысл.
