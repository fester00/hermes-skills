---
name: zf1-isp-billing
description: Интеграция личных кабинетов ISP-биллингов (UTM5) с Zend Framework 1 через URFA-RPC. Покрывает получение доп. параметров, паспортные формы, graceful degradation, тех. имена vs display_name.
trigger: Личный кабинет ISP, UTM5, URFA-RPC, ZF1, дополнительные параметры пользователя, паспортные данные, ЛигаЛинк.
---

# ZF1 + UTM5 ISP Billing Cabinet

## Технические имена доп. параметров UTM5 (LigaLink)

Из дампа `uaddparams_desc`:

| ID | `name` | `display_name` |
|---|---|---|
| 6 | `user_birthdate` | `Паспорт: Дата рождения` |
| 7 | `user_birthplace` | `Паспорт: Место рождения` |
| 11 | `passport_registration_address` | `Паспорт: Адрес регистрации` |

### Критическое правило: `name` vs `display_name`

- **`name`** (техническое имя) — **стабильное**, не меняется при переименовании в админке UTM5. **Использовать в коде для поиска и условий.**
- **`display_name`** (русская подпись) — **mutable**, админ может переименовать. **Использовать только для UI-подписей.**

### Кодовый паттерн (сопоставление по `name`)

```php
$additionalParams = array();
try {
    $urfaAdmin = new Urfa_Admin();
    $adminUserInfo = $urfaAdmin->rpcf_get_userinfo($user['id']);
    if ($adminUserInfo && !empty($adminUserInfo['additional_params'])) {
        $uaparamList = $urfaAdmin->rpcf_get_uaparam_list();
        $urfaAdmin->close_session();
        if ($uaparamList) {
            foreach ($adminUserInfo['additional_params'] as $paramId => $paramValue) {
                if (isset($uaparamList[$paramId])) {
                    $techName = $uaparamList[$paramId]['name'];
                    $additionalParams[$techName] = $paramValue;
                }
            }
        }
    } else {
        $urfaAdmin->close_session();
    }
} catch (Exception $e) {
    Zend_Registry::get('logger')->err('Urfa_Admin error: ' . $e->getMessage());
}

// Подстановка в форму:
$form->setDefaults(array(
    'birthday'    => isset($additionalParams['user_birthdate']) ? $additionalParams['user_birthdate'] : '',
    'reg_address' => isset($additionalParams['passport_registration_address']) ? $additionalParams['passport_registration_address'] : '',
));
```

## Умный alert дозаполнения

Если есть паспортные данные, но отсутствуют доп. параметры — показать жёлтый alert с перечислением недостающих полей. Склонение: «поле» / «поля».

## Pitfalls

1. **Незакрытые PHP-теги в `.phtml`** — ZF1-view часто содержат `\u003c?php endif; ?` без закрывающего `\u003e`. Браузер отрендерит, но HTML-валидатор сломается. Всегда проверять: `\u003c?php endif; ?\u003e`.
2. **Забыть `close_session()`** — админская сессия Urfa остаётся висеть на ядре биллинга.
3. **ID параметров могут отличаться** в разных установках UTM5. Всегда динамически сопоставлять через `rpcf_get_uaparam_list()`.

## References

- `references/urfa-admin-additional-params.md` — полные реализации `rpcf_get_userinfo` и `rpcf_get_uaparam_list`
- `references/utm5-additional-params-names.md` — таблица технических имён LigaLink
