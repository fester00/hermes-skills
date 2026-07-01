---
name: urfa-admin-additional-params
description: Полная реализация админских URFA-методов для получения дополнительных параметров пользователя UTM5.
---

# Urfa_Admin: Получение дополнительных параметров UTM5

## Контекст

Дополнительные параметры пользователя в UTM5 (дата рождения, адрес регистрации и т.д.) хранятся в `user_additional_params` и описываются в `uaddparams_desc`. Они **не возвращаются** пользовательским API `rpcf_user5_get_user_info`.

Для их получения нужны **админские** функции URFA:
- `rpcf_get_userinfo` (id `0x2006`) — возвращает стандартные поля + блок `additional_params`
- `rpcf_get_uaparam_list` (id `0x440b`) — возвращает справочник доп. параметров

## Реализация в `library/Urfa/Admin.php`

### `rpcf_get_userinfo($user_id)`

```php
public function rpcf_get_userinfo($user_id)
{
    $this->call(0x2006);
    $this->put_int($user_id);
    $this->send();

    $data = array();
    $data['user_id']              = $this->get_int();
    $data['login']                = $this->get_string();
    $data['balance']              = $this->get_double();
    $data['create_date']          = $this->get_date();
    $data['last_change_date']     = $this->get_date();
    $data['who_create']           = $this->get_int();
    $data['who_change']           = $this->get_int();
    $data['is_juridical']         = $this->get_int();
    $data['full_name']            = $this->get_string();
    $data['juridical_address']    = $this->get_string();
    $data['actual_address']       = $this->get_string();
    $data['work_telephone']       = $this->get_string();
    $data['home_telephone']       = $this->get_string();
    $data['mobile_telephone']     = $this->get_string();
    $data['email']                = $this->get_string();
    $data['bank_account']         = $this->get_string();
    $data['bank_name']            = $this->get_string();
    $data['bank_bik']             = $this->get_string();
    $data['bank_cor_account']     = $this->get_string();
    $data['inn']                  = $this->get_string();
    $data['kpp']                  = $this->get_string();
    $data['ogrn']                 = $this->get_string();
    $data['okpo']                 = $this->get_string();
    $data['comments']             = $this->get_string();
    $data['personal_manager']      = $this->get_string();
    $data['connect_date']          = $this->get_date();
    $data['discount_period_id']     = $this->get_int();
    $data['discount_period_date']   = $this->get_date();
    $data['block_after_date']       = $this->get_date();
    $data['block_after_balance']    = $this->get_double();
    $data['password']               = $this->get_string();
    $data['always_online']          = $this->get_int();
    $data['amount_of_payments']     = $this->get_double();
    $data['amount_of_charges']      = $this->get_double();
    $data['last_charges_date']      = $this->get_date();
    $data['last_payment_date']      = $this->get_date();
    $data['is_dealer']              = $this->get_int();
    $data['dealer_id']              = $this->get_int();
    $data['comp_state']             = $this->get_int();
    $data['comp_state_date']        = $this->get_date();
    $data['org_structure_id']       = $this->get_int();
    $data['is_send_sms']            = $this->get_int();

    // Блок дополнительных параметров
    $data['parameters_size']        = $this->get_int();
    $data['additional_params']      = array();
    for ($i = 0; $i < $data['parameters_size']; $i++) {
        $paramId    = $this->get_int();
        $paramValue = $this->get_string();
        $data['additional_params'][$paramId] = $paramValue;
    }

    $this->finish();
    return $data;
}
```

### `rpcf_get_uaparam_list()`

```php
public function rpcf_get_uaparam_list()
{
    $this->call(0x440b);
    $this->send();

    $data = array();
    $count = $this->get_int();
    for ($i = 0; $i < $count; $i++) {
        $id           = $this->get_int();
        $name         = $this->get_string();
        $display_name = $this->get_string();
        $visible      = $this->get_int();

        $data[$id] = array(
            'name'         => $name,         // <-- stable technical ID
            'display_name' => $display_name, // <-- mutable UI label
            'visible'      => $visible,
        );
    }

    $this->finish();
    return $data;
}
```

## Использование в контроллере (сопоставление по `name`)

```php
$additionalParams = array();
try {
    $urfaAdmin = new Urfa_Admin();
    $adminUserInfo = $urfaAdmin->rpcf_get_userinfo($user['id']);
    if ($adminUserInfo && !empty($adminUserInfo['additional_params'])) {
        $uaparamList = $urfaAdmin->rpcf_get_uaparam_list();
        $urfaAdmin->close_session(); // <-- обязательно!

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

// Подстановка в форму по техническим именам:
$form->setDefaults(array(
    'birthday'    => isset($additionalParams['user_birthdate']) ? $additionalParams['user_birthdate'] : '',
    'reg_address' => isset($additionalParams['passport_registration_address']) ? $additionalParams['passport_registration_address'] : '',
));
```

## Проверенные технические имена (LigaLink UTM5)

Получены из дампа таблицы `uaddparams_desc`:

| ID | `name` | `display_name` |
|---|---|---|
| 6 | `user_birthdate` | `Паспорт: Дата рождения` |
| 7 | `user_birthplace` | `Паспорт: Место рождения` |
| 11 | `passport_registration_address` | `Паспорт: Адрес регистрации` |

> ⚠️ Эти `display_name` — **mutable**. Админ может их переименовать в UTM5. **В коде всегда использовать `name`.**

## Pitfalls

1. **Незакрытые PHP-теги в `.phtml`** — ZF1-view часто содержат `<?php endif; ?` без закрывающего `>`. Браузер отрендерит, но HTML-валидатор сломается. Всегда проверять закрытие.
2. **Поиск по `display_name`** — при переименовании полей в UTM5 код перестанет работать. Только `name`.
3. **Забыть `close_session()`** — админская сессия остаётся висеть на ядре биллинга.
4. **ID параметров могут отличаться** в разных установках UTM5. Всегда использовать `rpcf_get_uaparam_list()` для динамического сопоставления.
