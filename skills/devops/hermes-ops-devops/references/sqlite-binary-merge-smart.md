# Smart-merge для бинарной SQLite-базы в git

Сценарий: файл `pentajunior.db` отслеживается в git, является бинарным, и при `git pull` возникает конфликт (HEAD vs origin/master). Нужно сохранить лучшее из двух версий, а не слепо выбрать "ours" или "theirs".

## Когда применять

- Бинарный файл — SQLite `.db`.
- В обеих ветках есть ценные изменения (например, локальные — заполненные данные из старого проекта; удалённые — ручные правки от другого разработчика).
- `git merge` не может автоматически объединить бинарный файл.

## Пошаговый рецепт

```bash
# 1. Сохранить обе версии БД во время конфликта
cp pentajunior.db pentajunior.db.LOCAL   # наша версия (HEAD)
git show origin/master:pentajunior.db > pentajunior.db.REMOTE

# 2. Отменить неудачный merge, чтобы работать в чистом рабочем дереве
git merge --abort

# 3. Сравнить template_data в обеих версиях скриптом на Python
#    (см. пример ниже) и выбрать лучшее для каждого товара.

# 4. Применить smart-merge — взять LOCAL как основу, перенести
#    нужные поля из REMOTE программно через Python + sqlite3.

# 5. Завершить merge, принудительно оставив нашу (уже smart-merged) версию
git commit --amend --no-edit
git pull -s recursive -X ours origin master --no-rebase

# 6. Удалить временные файлы
rm pentajunior.db.LOCAL pentajunior.db.REMOTE
```

## Пример скрипта сравнения

```python
import sqlite3, json

conn_local = sqlite3.connect('pentajunior.db.LOCAL')
conn_remote = sqlite3.connect('pentajunior.db.REMOTE')

c_local = conn_local.cursor()
c_remote = conn_remote.cursor()

c_local.execute("SELECT id, template_data FROM products WHERE category_id=2")
for pid, td_local in c_local.fetchall():
    c_remote.execute(
        "SELECT template_data FROM products WHERE id=? AND category_id=2",
        (pid,)
    )
    row = c_remote.fetchone()
    if not row:
        print(f"{pid}: only in LOCAL")
        continue
    td_remote = json.loads(row[0])
    local = json.loads(td_local)

    for key in set(local) | set(td_remote):
        lv = local.get(key)
        rv = td_remote.get(key)
        if lv != rv:
            print(f"{pid}.{key}")
            print("  LOCAL:", lv)
            print("  REMOTE:", rv)

conn_local.close()
conn_remote.close()
```

## Ключевые принципы

1. **Не делайте `git checkout --ours` или `--theirs` вслепую** — вы потеряете данные одной из сторон.
2. **Бинарный файл != неразрешимый конфликт** — если внутри него структурированные данные, их можно merge вручную через SQL.
3. **После smart-merge используйте `-X ours`** — это гарантирует, что в окончательном коммите останется именно smart-merged файл, а не версия с сервера.
4. **Сохраняйте ручные правки**, если они точнее/актуальнее, чем сгенерированные.
5. **Убирайте заглушки** вроде `"Не указан"` — они появляются, когда поля не заполнены.

## Риски

- Smart-merge требует понимания схемы таблиц и значения полей.
- Если обе версии меняли одно и то же поле, нужно вручную решить, какое значение правильное.
- Всегда делайте резервную копию (`cp file.db file.db.backup`) перед массовым UPDATE.
