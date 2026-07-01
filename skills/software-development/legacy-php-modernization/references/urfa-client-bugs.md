# Urfa_Client Known Bugs — LigaLink Session Findings

## Bug 1: getUserInfo() skips `locked_in_funds` and `email`

**File:** `library/Urfa/Client.php`  
**Method:** `getUserInfo()` calling `rpcf_user5_get_user_info_new` (id `-0x4052`)

**Root cause:** After reading `$user['passport'] = $this->urfa->get_string()`, the code immediately calls `$this->urfa->finish()`, leaving two fields unread in the socket buffer:

| Field | Type | Position after passport |
|---|---|---|
| `locked_in_funds` | `double` | 1st |
| `email` | `string` | 2nd |

**Impact:**
- Form shows empty email even when UTM5 has a value.
- On save, `editUserInfo()` writes empty string back, **destroying the existing email**.
- User reported: "I tried changing email from admin@liga-link.net to max@liga-link.net" — the form appeared empty because of this bug.

**Fix:**
```php
// After: $user['passport'] = $this->urfa->get_string();
$this->urfa->get_double(); // consume locked_in_funds
$user['email'] = $this->urfa->get_string(); // now reads correctly
$this->urfa->finish();
```

> **Status in deployed source (June 2026):** The production archive `my.ligalink.ru.zip` already contains this fix. Use this reference primarily when auditing older copies or forks where email still loads as empty.

---

## Bug 2: Stale-read after `editUserInfo()`

**File:** `library/Urfa/Client.php`  
**Method:** `editUserInfo()` calling `rpcf_user5_edit_user` (id `-0x4040`)

**Root cause:** After writing user data via `editUserInfo()`, calling `getUserInfo()` on the **same `$urfa` object** may return cached/stale data from the socket buffer, including the old email.

**Impact:**
- Form reloads after POST but still shows the old email.
- User thinks the save failed, when in fact UTM5 accepted the write.

**Fix:** Force a fresh connection:
```php
// In controller POST handler, after $urfa->editUserInfo($data):
unset($urfa); // triggers __destruct chain: Client->Connect->close_session+disconnect
$urfa = $this->reconnect(); // fresh TCP socket + fresh RPC session
$user = $urfa->getUserInfo(); // now reads actual UTM5 state
```

**Warning:** `unset($urfa)` must NOT be placed between GET-read and POST-write. It destroys the object; any later `$urfa->editUserInfo()` call will fatal. Move `unset()` to the very end of the action or rely on PHP's end-of-scope cleanup.

---

## Bug 3: Urfa_Admin needs explicit `close()` for TCP cleanup

**File:** `library/Urfa/Admin.php`

**Root cause:** `Admin.php` has no `close()` method. Calling `$urfaAdmin->close_session()` only closes the RPC session layer, leaving the TCP socket open. In `catch` blocks the socket may leak.

**Fix:** Add to `Admin.php`:
```php
public function close() {
    if (isset($this->urfa)) {
        unset($this->urfa); // triggers Connect::__destruct() -> close_session + disconnect
    }
}
```

In controllers: always use `$urfaAdmin->close()` (not `close_session()`). In catch blocks:
```php
try {
    $urfaAdmin = new Urfa_Admin();
    // ... calls ...
} catch (Exception $e) {
    Zend_Registry::get('Zend_Log')->err('Urfa_Admin error: ' . $e->getMessage());
} finally {
    if (isset($urfaAdmin)) {
        $urfaAdmin->close();
    }
}
```

---

## Verification Steps

1. Before fix: load passport form → email field empty even when UTM5 has value.
2. After fix: email loads correctly.
3. Change email → save → reload page → new email persists.
4. If still stale after save, check that `unset($urfa)` + `reconnect()` is present in POST handler.
