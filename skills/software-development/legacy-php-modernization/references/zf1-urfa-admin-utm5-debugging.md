# Urfa_Admin + UTM5 Debugging Reference

Session-hardened knowledge for debugging permission and SSL issues when calling admin-only Urfa functions from a ZF1 cabinet.

## Context

The LigaLink subscriber cabinet uses `Urfa_Client` for regular user API calls. Admin-only functions (e.g., `rpcf_get_userinfo` 0x2006, `rpcf_get_uaparam_list` 0x440b) require `Urfa_Admin`, which opens a separate privileged session.

## Key admin functions for reading user data

| Function | Opcode | What it returns | User API equivalent |
|----------|--------|-----------------|---------------------|
| `rpcf_get_userinfo` | `0x2006` | Full user info including `user_additional_params` | None — `rpcf_user5_get_user_info` does NOT return additional params |
| `rpcf_get_uaparam_list` | `0x440b` | List of `uaddparams_desc` entries (`id`, `name`, `display_name`) | None |

## The permission-denied trap

**Symptom:** `rpcf_get_userinfo()` returns `FALSE` (boolean) or `0` (integer), and UTM5 `main.log` shows:

```
Access granted to [SSL]<utm5cabinet> ... Request for function <0x2006> not permitted
SSL type requested: SSLv3(2)
```

**Root cause:** The admin session's `userType` determines RPC permissions, NOT the UTM5 group (`Wheel`). Even with full group rights, `RUT_SERVICE` (1) may be denied while `RUT_USER` (0) is allowed.

### How `Urfa_Admin` opens a session

In `library/Urfa/Admin.php`:

```php
public function __construct() {
    parent::__construct(true);  // $admin = true
}
```

In `library/Urfa/Connect.php`, `open_session($isService = true)`:

```php
if ($isService) {
    $this->urfa->put_int(1);   // RUT_SERVICE = 1
} else {
    $this->urfa->put_int(0);   // RUT_USER = 0
}
```

**Fix:** Change `Urfa_Admin` constructor to call `$this->open_session(false)`:

```php
public function __construct() {
    parent::__construct(true);
    $this->open_session(false);  // userType = RUT_USER (0)
}
```

### The SSLv3 admin type dead end

UTM5 supports `RSR_SSL_SSL3_ADMIN` (type 4) for admin connections. Attempting to use it:

```php
// In Urfa/Connect.php __construct($admin)
if ($admin) {
    $this->sslType = 4;  // RSR_SSL_SSL3_ADMIN
}
```

**Result:** `stream_socket_enable_crypto(): SSL operation failed ... sslv3 alert handshake failure`

**Why:** Modern PHP/OpenSSL no longer supports SSLv3. The `RSR_SSL_SSL3_ADMIN` type is non-functional in contemporary environments.

**Resolution:** Keep `sslType = 2` (SSLv3 regular) and instead fix the `userType` via `open_session(false)`.

## Mapping additional parameters by technical name

`rpcf_get_uaparam_list()` returns entries like:

```
id=6,  name='user_birthdate',               display_name='Дата рождения'
id=7,  name='user_birthplace',              display_name='Место рождения'
id=11, name='passport_registration_address', display_name='Адрес регистрации'
```

**Always index by `name`, never by `display_name`.** Admins can rename the display label; the technical name is stable.

```php
$paramMap = array();
foreach ($uaparams as $p) {
    $paramMap[$p['name']] = $p['id'];
}
```

Then `rpcf_get_userinfo()` returns `user_additional_params` as an array keyed by `paramid`:

```php
$birthdate = isset($user['user_additional_params'][$paramMap['user_birthdate']])
    ? $user['user_additional_params'][$paramMap['user_birthdate']]
    : null;
```

## Diagnosing without Zend_Log

If `Zend_Registry::get('Zend_Log')` is unavailable, add `error_log()` directly in `Urfa_Connect::call()`:

```php
public function call($code) {
    // ... existing code ...
    if (!$this->urfa->read()) {
        error_log("Urfa call read() failed for code " . sprintf("0x%x", $code));
        return FALSE;
    }
    $code = $this->urfa->get_int();
    if ($code == 0) {
        error_log("Urfa call returned 0 (RA_END) for code " . sprintf("0x%x", $code) . " — permission denied or function not found?");
        return 0;
    }
    // ...
}
```

Read PHP errors via: `tail -f /var/log/apache2/error.log` or `tail -f application/logs/app.log`.

Read UTM5 kernel logs via: `tail -f /netup/utm5/log/main.log` (exact path varies by installation).

## Graceful degradation pattern

Always wrap `Urfa_Admin` in `try/catch`. If admin API fails (permissions, network, SSL), the form should still render:

```php
$hasBirthdate = false;
$birthdateValue = '';
$hasRegAddress = false;
$regAddressValue = '';

try {
    $admin = new Urfa_Admin();
    $admin->open_session(false);  // RUT_USER
    $userInfo = $admin->rpcf_get_userinfo($userId);
    $paramList = $admin->rpcf_get_uaparam_list();
    // ... map and extract ...
} catch (Exception $e) {
    if (Zend_Registry::isRegistered('Zend_Log')) {
        Zend_Registry::get('Zend_Log')->err('Urfa_Admin failed: ' . $e->getMessage());
    }
    // Leave defaults empty; form still works
}
```

## Checklist for adding admin-data prefill to a form

- [ ] `Urfa_Admin` constructor calls `open_session(false)` (RUT_USER)
- [ ] Admin methods `rpcf_get_userinfo()` and `rpcf_get_uaparam_list()` implemented in `Urfa/Admin.php`
- [ ] Controller maps params by technical `name`, not `display_name`
- [ ] Form fields receive default values from admin API
- [ ] View shows current-data block with conditional display
- [ ] `try/catch` around all admin calls with logging
- [ ] Zend_Log key is `'Zend_Log'` (not `'logger'`) when loaded via `Zend_Application_Resource_Log`
- [ ] If server has custom `_initLog()` in `Bootstrap.php`, sync it to local sources before deploy
