# Запись персональных данных в UTM5 из ZF1-кабинета LigaLink

Справочник для случаев, когда форма в личном кабинете должна не просто отправлять письмо оператору, а напрямую писать паспортные данные, телефон, email, дату рождения и адрес регистрации в биллинг UTM5.

## Контекст

- Проект: Zend Framework 1, подписчикский кабинет LigaLink (`my.ligalink.ru`).
- Биллинг: UTM5, взаимодействие через URFA-RPC (бинарный протокол поверх XML-RPC-подобного формата).
- Пользовательская функция редактирования профиля (`rpcf_user5_edit_user`, 0x4040, `Urfa_Client::editUserInfo()`) **не умеет писать дополнительные параметры** (`additional_params`).
- Для записи доп. параметров нужна **админская функция** `rpcf_edit_user_new` (0x2126).

## RPC-функции UTM5, используемые в этом сценарии

| Код | Имя в протоколе | Назначение |
|-----|-----------------|------------|
| 0x2006 | `rpcf_get_userinfo` | Получить полный профиль пользователя (включая `additional_params`). |
| 0x440b | `rpcf_get_uaparam_list` | Получить список пользовательских доп. параметров с их ID и типами. |
| 0x2126 | `rpcf_edit_user_new` | Редактирование пользователя администратором, **с поддержкой доп. параметров**. |

## ID дополнительных параметров

Источник: дамп `uaddparams_desc.sql`.

| ID | Имя | Смысл |
|----|-----|-------|
| 6 | `user_birthdate` | Дата рождения |
| 7 | `user_birthplace` | Место рождения |
| 11 | `passport_registration_address` | Адрес регистрации по паспорту |

> ID специфичны для конкретной инсталляции UTM5. Перед использованием на другом стенде перепроверьте через `rpcf_get_uaparam_list` или SQL-таблицу `uaddparams_desc`.

## Архитектура сохранения: GET-before-SET

Админская функция редактирования опасна: если передать неполный профиль, можно затереть существующие поля. Поэтому перед каждым сохранением:

1. Читаем **полный профиль** текущего пользователя через `rpcf_get_userinfo`.
2. Формируем массив изменённых полей.
3. Передаём обратно **все** текущие поля профиля, заменяя только разрешённые к изменению.
4. Для `additional_params` применяем слияние: **новые значения поверх старых**.

```php
// Правильное слияние: новые значения имеют приоритет
$mergedAdditionalParams = $newAdditionalParams + $fullUserInfo['additional_params'];
```

> Ошибка `$fullUserInfo['additional_params'] + $newAdditionalParams` затирает новые значения, потому что в PHP `+` для массивов сохраняет левый операнд при совпадающих ключах.

## Silent re-login: цепочка из трёх Urfa_Client

Сессия UTM5 иногда протухает между операциями. Надёжный паттерн восстановления:

```php
private function _getFreshUrfa()
{
    // 1. Пытаемся восстановить старую сессию
    $urfa1 = new Urfa_Client();
    if ($urfa1->restore_session($this->view->identity->utm5)) {
        return $urfa1;
    }
    unset($urfa1);

    // 2. Логинимся заново — возвращённый объект уже закрыт внутри login()
    $urfa2 = new Urfa_Client();
    $newKey = $urfa2->login($this->login, $this->password);
    unset($urfa2);

    if (!$newKey) {
        throw new Exception('UTM5 silent re-login failed at login stage');
    }

    // 3. Открываем живое соединение по новому ключу
    $urfa3 = new Urfa_Client();
    if (!$urfa3->restore_session($newKey)) {
        throw new Exception('UTM5 silent re-login failed at fresh restore');
    }

    // Обновляем ключ в сессии/identity для следующих запросов
    $this->view->identity->utm5 = $newKey;

    return $urfa3;
}
```

> Важно: `Urfa_Client::login()` сама делает `close_session()` + `disconnect()`, поэтому объект, который её вызвал, нельзя использовать для дальнейших RPC. Нужен третий клиент для `restore_session($newKey)`.

## Кэширование дополнительных параметров

Доп. параметры редко меняются, но часто читаются. Используйте единый ключ кэша:

```php
$additionalParamsCacheKey = md5($login) . '_additional_params';
```

TTL обычно 120 секунд. При отсутствии в кэше — дозагрузка из UTM5.

```php
private function _loadAdditionalParams($userInfo)
{
    $login = $userInfo['login'];
    $cacheKey = md5($login) . '_additional_params';
    $params = $this->cache->load($cacheKey);

    if ($params === false) {
        $urfa = $this->_getFreshUrfa();
        $params = $urfa->getUserAdditionalParams($userInfo['user_id']);
        $this->cache->save($params, $cacheKey);
        unset($urfa);
    }

    return $params;
}
```

## Поля профиля, разрешённые к изменению через форму

| Поле в UTM5 | Поле формы | Примечание |
|-------------|------------|------------|
| `phone` | `phone` / `home_telephone` | Основной телефон. |
| `email` | `email` | Email. |
| `mobile_telephone` | `phone` | В LigaLink именно `mobile_telephone` считается абонентским телефоном. |
| `additional_params[6]` | `birthday` | Дата рождения (`user_birthdate`). |
| `additional_params[11]` | `reg_address` | Адрес регистрации (`passport_registration_address`). |

Паспортные данные (серия, номер, кем выдан, дата выдачи, код) обычно хранятся в единой строке `passport` и обрабатываются отдельно — см. `references/zf1-passport-form-recipe.md`.

## Пример: `_savePassportData()`

```php
private function _savePassportData(Billing_Form_Passport $form, $userInfo)
{
    $urfa = $this->_getFreshUrfa();

    // 1. Полный профиль
    $fullUserInfo = $urfa->getUserInfo();

    // 2. Читаем текущие доп. параметры
    $addParams = $this->_loadAdditionalParams($fullUserInfo);

    // 3. Обновляем только разрешённые поля
    $fullUserInfo['mobile_telephone'] = $form->getValue('phone');
    $fullUserInfo['email']            = $form->getValue('email');
    $fullUserInfo['passport']           = sprintf(
        'серия %s №%s выдан %s %s %s',
        $form->getValue('passport_series'),
        $form->getValue('passport_number'),
        $form->getValue('passport_issued_by'),
        $form->getValue('passport_date'),
        $form->getValue('passport_code')
    );

    // 4. Новые доп. параметры поверх старых
    $newAddParams = array(
        6  => $form->getValue('birthday'),
        11 => $form->getValue('reg_address'),
    );
    $fullUserInfo['additional_params'] = $newAddParams + $addParams;

    // 5. Отправляем обратно через админскую функцию
    $admin = new Urfa_Admin($urfa);
    $admin->rpcf_edit_user_new($fullUserInfo);

    // 6. Инвалидируем кэш
    $this->cache->remove(md5($userInfo['login']) . '_additional_params');
    $this->cache->remove($this->cache_basic_account);
}
```

## Проверка необходимости алерта на главной

Алерт на главной странице показывается, если не заполнены обязательные ПДн:

```php
private function _isPassportAlertNeeded($userData, $additionalParams)
{
    $passport = isset($userData['passport']) ? trim($userData['passport']) : '';
    $hasPassport = (bool) preg_match(
        '/серия\s+\d{4}\s+№\d{6}\s+выдан\s+.+\s+\d{2}\.\d{2}\.\d{4}\s+\d{3}-\d{3}/ui',
        $passport
    );

    $hasPhone = !empty($userData['mobile_telephone']) || !empty($userData['phone']);
    $hasBirthday = !empty($additionalParams[6]);

    return !($hasPassport && $hasPhone && $hasBirthday);
}
```

## Форма и шаблон

См. основные рецепты:

- `references/zf1-passport-form-recipe.md` — базовая версия с отправкой email.
- `references/zf1-passport-form-v2.md` — стилизованная версия, email опционален.
- Для записи в UTM5 достаточно заменить тело `passportAction` на вызов `_savePassportData()` и добавить поля `birthday`, `reg_address` в форму и шаблон.

## Security и workflow

1. **Не оставляйте отладочное логирование** (`writeLog`, `BEFORE`/`AFTER`, `var_dump`) в продовом коде.
2. **GET-before-SET** обязателен при использовании админских функций.
3. **Не коммитьте продовые credentials**: `application/configs/billing.ini` содержит реальные учётные данные UTM5 и `session.encrypt_key`.
4. **SFTP-синхронизация**: VS Code SFTP extension не выгружает файлы при `git pull`. После получения изменений обязательно выполните `SFTP: Sync Local to Remote` (Ctrl+Shift+P) или сохраните каждый изменённый файл (`Ctrl+S`).
5. **Перед правками делайте `git pull origin master`**, чтобы не перезаписать изменения, сделанные локально через SFTP.

## Связанные файлы

- `library/Urfa/Client.php` — пользовательский URFA-клиент.
- `library/Urfa/Admin.php` — админский URFA-клиент (`rpcf_edit_user_new`).
- `application/modules/billing/controllers/IndexController.php` — действия кабинета.
- `application/modules/billing/forms/Passport.php` — форма персональных данных.
- `application/modules/billing/views/scripts/index/passport.phtml` — шаблон формы.
- `application/modules/billing/views/scripts/index/index.phtml` — главная страница с алертом.
