# ZF1 Session Timeout Fix — PHP-сессия в личном кабинете ЛигаЛинк

## Контекст

В Zend Framework 1-кабинете ЛигаЛинк сессия протухала за ~5 минут простоя. Пользователь открывал "Общая информация", ждал 5 минут, обновлял страницу — и видел желтый баннер "Вам необходимо авторизоваться" с редиректом на логин.

## Диагностика

### Два слоя сессий

| Слой | Механизм | Что хранится | Где проверяется |
|---|---|---|---|
| **PHP/Zend_Auth** | `$_SESSION['Zend_Auth']` | `identity` (login + utm5 session_id) | `Billing_IndexController::init()` строка 22-28 |
| **UTM5** | TCP-соединение + `rpcf_restore_session` | Сессия на ядре биллинга | `reconnect()` строка 65-79 |

### Как отличить по баннеру

| Баннер | Слой | Метод в коде |
|---|---|---|
| **"Вам необходимо авторизоваться"** | PHP-сессия протухла | `Billing_IndexController::init()` |
| **"Сессия истекла. Пожалуйста, авторизуйтесь заново."** | UTM5-сессия не восстановилась | `reconnect()` |

### Почему протухает

По умолчанию `session.gc_maxlifetime` = 1440 сек (24 мин). Но на многих хостингах снижено до 300 сек (5 мин).

Когда пользователь 5 минут бездействует:
1. PHP garbage collector удаляет сессию с диска
2. `Zend_Auth::hasIdentity()` → `false`
3. `Billing_IndexController::init()` → редирект на `/` с баннером

UTM5-сессия при этом может быть жива — но код до неё не доходит.

## Проверка на production

```bash
php -r "echo 'gc_maxlifetime=' . ini_get('session.gc_maxlifetime') . ' сек (' . round(ini_get('session.gc_maxlifetime')/60,1) . ' мин)' . PHP_EOL;"
```

## Решение 1 — Программно в Bootstrap (рекомендуется)

Добавить `_initSession()` в `application/Bootstrap.php` **перед** `_initNavigation()` (~строка 33):

```php
protected function _initSession()
{
    // Увеличиваем время жизни сессии до 8 часов (28800 сек)
    ini_set('session.gc_maxlifetime', 28800);
    ini_set('session.cookie_lifetime', 28800);

    // Явный запуск сессии до того, как Zend_Auth начнёт её использовать
    Zend_Session::start();
}
```

**Почему именно перед `_initNavigation`:** `Navigation` (строка 33-46) обращается к `Zend_Auth::getInstance()->hasIdentity()`. Если сессия ещё не стартована — `Zend_Auth` попытается стартовать её неявно, но уже без наших `ini_set`.

### Патч для Bootstrap.php (полный фрагмент)

```php
    protected function _initSession()
    {
        ini_set('session.gc_maxlifetime', 28800);
        ini_set('session.cookie_lifetime', 28800);
        Zend_Session::start();
    }

    protected function _initNavigation()
    {
        // ... оригинальный код без изменений ...
    }
```

## Решение 2 — Через application.ini

Добавить в `application/configs/application.ini` в секцию `[production]`:

```ini
phpSettings.session.gc_maxlifetime = 28800
phpSettings.session.cookie_lifetime = 28800
```

## Решение 3 — Галочка "Запомнить меня" (30 дней)

В `Default_IndexController::indexAction()` при успешном логине:

```php
if ($form->getValue('remember_me')) {
    ini_set('session.cookie_lifetime', 2592000); // 30 дней
} else {
    ini_set('session.cookie_lifetime', 28800);   // 8 часов
}
```

## Pitfalls

1. **Не добавлять `_initSession()` после `_initNavigation`** — Navigation обращается к `Zend_Auth` раньше, чем применятся настройки сессии.
2. **Не забывать `Zend_Session::start()`** — без явного старта `ini_set` применяется, но сессия стартует неявно при первом `Zend_Auth`-вызове с дефолтными настройками.
3. **Проверять оба слоя независимо** — PHP-сессия и UTM5-сессия имеют разные таймауты. Если баннер "Вам необходимо авторизоваться" — это PHP. Если "Сессия истекла" — это UTM5.
4. **Оригинальный Bootstrap.php ЛигаЛинк не имеет `_initSession()`** — сессия стартует неявно с системными дефолтами.
