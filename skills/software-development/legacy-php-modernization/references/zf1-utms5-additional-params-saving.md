# Saving UTM5 additional user parameters from a ZF1 cabinet

## Context
LigaLink subscriber cabinet (`my.ligalink.ru`) runs Zend Framework 1 and talks to NetUP UTM5 via URFA. Standard user editing (`rpcf_user5_edit_user`, exposed as `Urfa_Client::editUserInfo()`) only updates basic fields. It cannot write user additional parameters such as `user_birthdate`, `user_birthplace`, or `passport_registration_address`.

## Why this matters
152-FZ / Russian telecom rules require the operator to keep subscriber passport data up to date. Birthdate and registration address are stored in UTM5 as user additional parameters, not in the base user record.

## The only safe admin function
`rpcf_edit_user_new` (`0x2126`) accepts the full base user record plus a map of additional parameters. It rewrites the whole record, so the caller must preserve untouched fields.

## LigaLink additional parameter IDs
Derived from `uaddparams_desc` table:

| ID | System name | Display name |
|---|---|---|
| 6 | `user_birthdate` | Паспорт: Дата рождения |
| 7 | `user_birthplace` | Паспорт: Место рождения |
| 11 | `passport_registration_address` | Паспорт: Адрес регистрации |

## Safe controller pattern (PHP)

```php
private function _savePassportData($userInfo, $passportData, $formValues)
{
    if (empty($userInfo['id'])) {
        $this->writeLog('err', '_savePassportData: missing user id');
        return false;
    }

    try {
        $urfaAdmin = new Urfa_Admin();
        $fullUser = $urfaAdmin->rpcf_get_userinfo($userInfo['id']);

        if (empty($fullUser['user_id'])) {
            throw new Exception('rpcf_get_userinfo returned no data');
        }

        $passportStr = 'серия ' . $passportData['series'] . ' №' . $passportData['number']
            . ' выдан ' . $passportData['issued_by'] . ' ' . $passportData['date']
            . ' ' . $passportData['code'];

        $updates = array(
            'passport' => $passportStr,
            'mob_tel'  => $formValues['phone'],
            'email'    => $formValues['email'],
        );

        $addParams = array();
        if (!empty($formValues['birthday']))    $addParams[6]  = $formValues['birthday'];
        if (!empty($formValues['birthplace']))  $addParams[7]  = $formValues['birthplace'];
        if (!empty($formValues['reg_address'])) $addParams[11] = $formValues['reg_address'];

        // Preserve untouched additional params
        if (!empty($fullUser['additional_params']) && is_array($fullUser['additional_params'])) {
            $addParams = $fullUser['additional_params'] + $addParams;
        }

        $result = $urfaAdmin->rpcf_edit_user_new($fullUser, $updates, $addParams);
        unset($urfaAdmin);

        return ($result !== false);
    } catch (Exception $e) {
        $this->writeLog('err', '_savePassportData failed: ' . $e->getMessage());
        return false;
    }
}
```

## URFA admin implementation notes

### Reading errors from `rpcf_edit_user_new`
Do **not** call `finish()` before reading the optional error fields:

```php
$this->urfa->send();
$user_id = $this->urfa->get_int();

if ($user_id == 0) {
    $error_code = $this->urfa->get_int();
    $error_description = $this->urfa->get_string();
    $this->urfa->finish();
    $this->writeLog('err', "rpcf_edit_user_new failed: {$error_code} {$error_description}");
    return false;
}

$this->urfa->finish();
return $user_id;
```

### Field-name mapping
`rpcf_get_userinfo` field → `rpcf_edit_user_new` field:

| Source | Target |
|---|---|
| `full_name` | `full_name` |
| `act_address` | `act_address` |
| `jur_address` | `jur_address` |
| `work_tel` | `work_tel` |
| `home_tel` | `home_tel` |
| `mob_tel` | `mob_tel` |
| `web_page` | `web_page` |
| `icq_number` | `icq_number` |
| `passport` | `passport` |
| `bank_id` | `bank_id` |
| `bank_account` | `bank_account` |
| `email` | `email` |
| `comments` | `comments` |
| `personal_manager` | `personal_manager` |
| `connect_date` | `connect_date` |
| `is_send_invoice` | `is_send_invoice` |
| `advance_payment` | `advance_payment` |
| `house_id` | `house_id` |
| `flat_number` | `flat_number` |
| `entrance` | `entrance` |
| `floor` | `floor` |
| `district` | `district` |
| `building` | `building` |
| `is_juridical` | `is_juridical` |
| `login` | `login` |
| `password` | `password` |

## Testing protocol
1. Pick a test subscriber, note current values in Java admin / UTM5.
2. Submit the form, check `Zend_Log` for `_savePassportData: rpcf_edit_user_new result=...`.
3. If result is numeric user_id but data is missing, the function accepted the packet but ignored part of it (check field order / additional-param IDs).
4. Clear `Zend_Cache` and refresh the cabinet page.
5. Re-check values in Java admin.

## Cache invalidation
After successful save:

```php
$this->cache->remove($this->cache_basic_account);                // base user info
$this->cache->remove($this->cache_basic_account . '_additional_params');
```

## Risk checklist
- [ ] Tested on non-production subscriber.
- [ ] Logged raw `rpcf_edit_user_new` result.
- [ ] Verified base fields (phone, email, passport) were not accidentally cleared.
- [ ] Verified existing additional parameters not in the edited set remain unchanged.
- [ ] Confirmed admin credentials in `billing.ini` have rights to `0x2126`.
