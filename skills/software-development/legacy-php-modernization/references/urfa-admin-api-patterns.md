# UTM5 Admin API Patterns — LigaLink ZF1 Cabinet

Technical reference for accessing UTM5 admin-only functions from the ZF1 subscriber cabinet via `Urfa_Admin`.

## Problem

The subscriber-facing URFA API (`Urfa_Client::getUserInfo()`) does **NOT** return `user_additional_params`. Fields like birthdate, birthplace, and registration address are stored in `user_additional_params` + `uaddparams_desc` tables but are only accessible through admin functions.

## Admin functions

| Function | Code | Returns |
|----------|------|---------|
| `rpcf_get_userinfo` | `0x2006` | All standard fields + `parameters_size` block with `parameter_id`/`parameter_value` pairs |
| `rpcf_get_uaparam_list` | `0x440b` | List of all additional parameter descriptors: `id`, `name`, `display_name`, `visible` |

## UTM5 5.3 admin session requirements

Admin sessions require a different SSL handshake than subscriber sessions:

1. **Certificate**: `admin.crt` must exist next to `Socket.php` (passphrase: `netup`)
2. **SSL type**: `RSR_SSL_SSL3_ADMIN` (4) instead of `RSR_SSL_SSL3` (2)
3. **Ciphers**: `SSLv3` (not `ADH-RC4-MD5`)
4. **Crypto method**: `STREAM_CRYPTO_METHOD_SSLv3_CLIENT` in `authorize()`
5. **User type**: `open_session(false)` → `RUT_USER` (0), NOT `RUT_SERVICE` (1)

### Socket.php snippet

```php
if ($this->admin) {
    $context = stream_context_create(array('ssl' => array(
        'local_cert'  => __DIR__ . '/admin.crt',
        'passphrase'  => 'netup',
        'ciphers'     => 'SSLv3',
        'verify_peer' => false,
        'verify_peer_name' => false,
    )));
} else {
    $context = stream_context_create(array('ssl' => array(
        'ciphers' => 'ADH-RC4-MD5',
        'verify_peer' => false,
        'verify_peer_name' => false,
    )));
}
```

### Connect.php snippet

```php
if ($admin) {
    $this->sslType = RSR_SSL_SSL3_ADMIN; // 4
}
// In authorize():
if ($this->admin) {
    stream_socket_enable_crypto($this->socket, true, STREAM_CRYPTO_METHOD_SSLv3_CLIENT);
} else {
    stream_socket_enable_crypto($this->socket, true, STREAM_CRYPTO_METHOD_ANY_CLIENT);
}
```

### Admin.php snippet

```php
public function __construct() {
    $this->open_session(false); // RUT_USER = 0
}
```

## Parameter mapping strategy

**Always map by technical name (`name` field), NOT `display_name`.**

The `display_name` is user-configurable in the UTM5 admin panel and can change. The `name` field is stable.

Typical LigaLink parameters:
- `user_birthdate` (id 6) → Паспорт: Дата рождения
- `user_birthplace` (id 7) → Паспорт: Место рождения
- `passport_registration_address` (id 11) → Паспорт: Адрес регистрации

```php
$paramMap = array();
foreach ($uaparamList as $param) {
    $paramMap[$param['id']] = $param['name']; // Use 'name', not 'display_name'
}
```

## Implementation pattern in controller

```php
try {
    $admin = new Urfa_Admin();
    $userInfo = $admin->rpcf_get_userinfo($user['id']);
    $paramList = $admin->rpcf_get_uaparam_list();

    $paramMap = array();
    foreach ($paramList as $p) {
        $paramMap[$p['id']] = $p['name'];
    }

    $additionalParams = array();
    if (isset($userInfo['additional_params'])) {
        foreach ($userInfo['additional_params'] as $pid => $pval) {
            if (isset($paramMap[$pid])) {
                $additionalParams[$paramMap[$pid]] = $pval;
            }
        }
    }

    $birthdate = isset($additionalParams['user_birthdate']) ? $additionalParams['user_birthdate'] : '';
    $regAddress = isset($additionalParams['passport_registration_address']) ? $additionalParams['passport_registration_address'] : '';

    $admin->close(); // <-- triggers __destruct chain; не используй close_session()
} catch (Exception $e) {
    if (isset($admin)) {
        $admin->close();
    }
    // Log via Zend_Registry::get('Zend_Log') if available
    // Graceful degradation: form works without pre-fill
}
```

## Production passportAction pattern (June 2026)

В развёрнутой версии `my.ligalink.ru` используется кэш + админское API + пользовательское API вместе:

```php
$userInfoCacheKey = $this->cache_basic_account;
$adminUserInfoCacheKey = $this->cache_basic_account . '_admin';
$additionalParamsCacheKey = $this->cache_basic_account . '_additional_params';

if (($userInfo = $this->cache->load($userInfoCacheKey)) === false
    || ($adminUserInfo = $this->cache->load($adminUserInfoCacheKey)) === false
    || ($additionalParams = $this->cache->load($additionalParamsCacheKey)) === false
) {
    try {
        $urfa = $this->reconnect();
        $userInfo = $urfa->getUserInfo();

        $urfaAdmin = new Urfa_Admin();
        $adminUserInfo = $urfaAdmin->rpcf_get_userinfo($userInfo['id']);
        $uaparamList = $urfaAdmin->rpcf_get_uaparam_list();

        foreach ($adminUserInfo['additional_params'] as $paramId => $paramValue) {
            $name = $uaparamList[$paramId]['name']; // <-- stable technical name
            $additionalParams[$name] = $paramValue;
        }

        $this->cache->save($userInfo, $userInfoCacheKey);
        $this->cache->save($adminUserInfo, $adminUserInfoCacheKey);
        $this->cache->save($additionalParams, $additionalParamsCacheKey);

        $urfaAdmin->close();
        $urfa->close();
    } catch (Exception $e) {
        if (isset($urfaAdmin)) {
            $urfaAdmin->close();
        }
        if (Zend_Registry::isRegistered('Zend_Log')) {
            Zend_Registry::get('Zend_Log')->err('Urfa_Admin exception: ' . $e->getMessage());
        }
    }
}
```

## Error handling

`Urfa_Connect::call()` return values:
- `FALSE` (boolean) → socket/connection error, wrong state, or permission denied at SSL level
- `0` (integer) → `RA_END` packet received (normal end-of-response)
- Array → successful response with data

If `rpcf_get_userinfo` returns `FALSE`:
- Check `admin.crt` exists and passphrase is correct
- Check `sslType` is `RSR_SSL_SSL3_ADMIN` (4)
- Check `STREAM_CRYPTO_METHOD_SSLv3_CLIENT` is used
- Check UTM5 account has admin rights for the function

## Logger key

`Zend_Application_Resource_Log` registers the logger under key **`Zend_Log`** in `Zend_Registry`, NOT `logger`.

```php
if (Zend_Registry::isRegistered('Zend_Log')) {
    Zend_Registry::get('Zend_Log')->info('Message');
}
```

## Pitfalls

- **Never search by `display_name`**: administrators can rename fields; `name` is the stable technical identifier.
- **Do NOT use `Billing_Model_Users::getUserInfo()`**: this direct SQL method is dead code (0 callers in the project). All data must flow through URFA-RPC.
- **SSLv3_ADMIN without `admin.crt`**: causes `sslv3 alert handshake failure` in OpenSSL.
- **Admin session ≠ Wheel group**: UTM5 group membership does NOT grant RPC permissions; permissions are configured separately per function.
- **`call()` returns `FALSE` (boolean), not `0` (integer)**: `FALSE` means network/state failure; `0` means `RA_END`. Check with `=== FALSE`.
- **Always close admin with `$urfaAdmin->close()`**: `close_session()` закрывает только RPC-сессию, но оставляет TCP-сокет открытым. `close()` через `unset($this->urfa)` вызывает цепочку `__destruct` и корректно освобождает ресурсы.
