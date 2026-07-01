# UTM5 user additional parameter IDs — LigaLink

Extracted from `uaddparams_desc` table in the LigaLink UTM5 database.

| paramid | name | display_name | visible |
|---|---|---|---|
| 1 | `Номер порта` | Номер порта | 0 |
| 2 | `Номер договора` | Номер договора (для юрлица) | 1 |
| 3 | `Номер заявки` | Номер заявки | 0 |
| 4 | `Абонент - Пол` | Абонент - Пол | 0 |
| 5 | `Абонент - Подписка` | Абонента - Подписка | 1 |
| 6 | `user_birthdate` | Паспорт: Дата рождения | 1 |
| 7 | `user_birthplace` | Паспорт: Место рождения | 1 |
| 8 | `Паспорт: Кем выдан` | Паспорт: Кем выдан | 0 |
| 9 | `passport_notrf` | Паспорт: Не российский | 1 |
| 10 | `passport_no_middlename` | Паспорт: Нет отчества | 1 |
| 11 | `passport_registration_address` | Паспорт: Адрес регистрации | 1 |

## Personal-cabinet relevant IDs

- **6** — `user_birthdate` (used to check completeness of personal data)
- **7** — `user_birthplace`
- **11** — `passport_registration_address`

## Reading values

Values are returned by `Urfa_Admin::rpcf_get_userinfo($userId)` under `additional_params[$paramId]`.
The parameter names are resolved via `Urfa_Admin::rpcf_get_uaparam_list()`.

## Writing values

There is no dedicated `set_user_additional_param` function in the provided `api.xml`.
Options:

1. Send a request to the operator (email / ticket / CRM).
2. Use `rpcf_edit_user_new` (0x2126), which accepts an array of `(parameter_id, parameter_value)` pairs, but requires passing back all user fields — high risk of overwriting unrelated data.
3. Do **not** reuse standard fields such as `web_page` or `icq_number` as storage for birthdate/address; that creates semantic debt and risks data loss.
