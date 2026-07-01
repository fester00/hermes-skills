# UTM5 URFA: дополнительные параметры пользователя

## Контекст
Исследование проводилось для задачи чтения/записи даты рождения из дополнительных параметров UTM5 (`user_additional_params`).

## Вывод

Стандартные пользовательские (user5) URFA-функции НЕ поддерживают дополнительные параметры. Доступен только административный набор.

---

## 1. Пользовательские user5-функции — доступные поля

Функция `rpcf_user5_get_user_info_new` (id `-0x4052`) возвращает только стандартные поля:
```
user_id, login, basic_account, balance, credit, is_blocked,
create_date, last_change_date, who_create, who_change, is_juridical,
full_name, juridical_address, actual_address,
work_telephone, home_telephone, mobile_telephone,
web_page, icq_number, tax_number, kpp_number,
bank_id, bank_account, int_status, vat_rate,
pasport, locked_in_funds, email
```

Функция `rpcf_user5_edit_user` (id `-0x4040`) принимает только:
```
full_name, actual_address, juridical_address,
work_telephone, home_telephone, mobile_telephone,
web_page, icq_number, pasport, bank_id, bank_account, email
```

❌ Доп. параметров там **нет**.

---

## 2. Административные функции — полная поддержка доп. параметров

### Чтение: `rpcf_get_userinfo` (id `0x2006`)

На выходе содержит блок:
```xml
<integer name="parameters_size"/>
<for name="i" from="0" count="parameters_size">
    <integer name="parameter_id"/>
    <string name="parameter_value"/>
</for>
```

**Ключевые поля:**
- `parameter_id` — ID доп. параметра (соответствует `uaddparams_desc.id`)
- `parameter_value` — строковое значение

> Порядок и количество доп. параметров определяются `parameters_size`.

### Запись: `rpcf_edit_user_new` (id `0x2126`)

На вход принимает блок:
```xml
<integer name="parameters_count" default="size(parameter_value)"/>
<for name="i" from="0" count="size(parameter_value)">
    <integer name="parameter_id" array_index="i"/>
    <string name="parameter_value" array_index="i"/>
</for>
```

**Особенности:**
- Чтобы изменить один доп. параметр, нужно передать **все** доп. параметры, иначе те, что не переданы, будут удалены (уточнить поведение в документации NetFlow/Urentcol).
- Формат: массив пар `(parameter_id, parameter_value)`, размер `parameters_count`.

---

## 3. Справочник доп. параметров (uaparam)

Таблицы в БД UTM5:
- `uaddparams_desc` — описания типов доп. параметров (`id`, `name`, `display_name`, `visible`)
- `user_additional_params` — значения (`uid`, `upid`, `value`)

URFA-функции для управления **справочником** (не значениями):

| Функция | ID | Назначение |
|---|---|---|
| `rpcf_get_uaparam_list` | `0x440b` | Список определений (id, name, display_name, visible) |
| `rpcf_add_uaparam` | `0x440c` | Создать определение |
| `rpcf_del_uaparam` | `0x440d` | Удалить определение |
| `rpcf_edit_uaparam` | `0x440e` | Изменить определение |
| `rpcf_del_uaparam_new` | `0x4411` | Удалить определение (новый вариант) |
| `rpcf_is_uaparam_in_use` | `0x4412` | Проверить использование |

---

## 4. Практические выводы для htdata/ZF1

Если нужно работать с доп. параметрами в **пользовательском кабинете** (user5):

1. **Через URFA (админская сессия)** — если у htdata/CRM есть админские креды для URFA, использовать `rpcf_get_userinfo` и `rpcf_edit_user_new`.

2. **Через прямое чтение БД** — htdata уже подключён к БД UTM5 (`useDbConfig = 'UTM5'`), можно использовать модели CakePHP:
   ```php
   // Чтение значения доп. параметра "birthday" для uid=X
   $this->UserAdditionalParam->find('first', [
       'conditions' => ['uid' => $uid, 'upid' => $birthdayParamId]
   ]);
   ```

3. **Через CakePHP → htdata API → frontend** — CakePHP оборачивает прямой SQL, frontend забирает по REST.

---

## 5. Как найти ID параметра по имени

```sql
SELECT id FROM uaddparams_desc WHERE name = 'birthday' OR display_name LIKE '%дата рождения%';
```

> Рекомендуется хранить mapping `uaparam_id` в конфиге htdata (например, `Configure::write('Utm5.BirthdayParamId', 42)`), чтобы не делать SQL-запрос каждый раз.

---

## 6. Альтернатива: хранить в локальной таблице CRM

Если доп. параметры UTM5 недоступны через user5 API, можно сохранять дату рождения в **локальной таблице CRM** (БД `ams2-test`), а синхронизировать с UTM5 через фоновую задачу или админский URFA-вызов.
