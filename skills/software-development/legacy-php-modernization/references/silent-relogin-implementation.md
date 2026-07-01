# Silent Re-Login Implementation — LigaLink ZF1 Cabinet

## Session

**Date:** 2026-06-14
**User:** LigaLink admin (xfiles)
**Issue:** UTM5 TCP session expires after ~5-7 min idle, kicking users to login

## Root Cause

UTM5 kernel drops TCP session after ~5-7 min inactivity:
```
RPCSessionManager: pop: key not found
Unable to restore Session Key <...> for IP <...>
```

PHP session (`/var/lib/php5/sess_*`) remains alive (size > 0).
Old code in `restore_session()` called `clearIdentity()` → redirect to login.

## Solution: AES-256-CBC + IP-binding

### Architecture

1. **Encrypt password** during `Urfa_Auth_Adapter::authenticate()` with AES-256-CBC
2. **Store encrypted password** in PHP session (`identity->password`)
3. **IP-binding**: format `IP|password`, decrypt only if IP matches
4. **Silent re-login**: `restore_session()` → `login()` with saved creds → update `identity->utm5`

### Key class: `library/Urfa/Session/Crypt.php`

```php
class Urfa_Session_Crypt {
    private static $_cipher = 'AES-256-CBC';
    
    private static function _getKey() {
        $config = new Zend_Config_Ini(APPLICATION_PATH . '/configs/billing.ini', 'app');
        $key = (string) $config->session->encrypt_key;
        return hash('sha256', $key, true); // exactly 32 bytes
    }
    
    public static function encrypt($plaintext, $client_ip = null) {
        if (is_null($client_ip)) $client_ip = $_SERVER['REMOTE_ADDR'];
        $key = self::_getKey();
        $ivlen = openssl_cipher_iv_length(self::$_cipher);
        $iv = openssl_random_pseudo_bytes($ivlen);
        $data = $client_ip . '|' . $plaintext;
        $ciphertext = openssl_encrypt($data, self::$_cipher, $key, OPENSSL_RAW_DATA, $iv);
        return base64_encode($iv . $ciphertext);
    }
    
    public static function decrypt($encoded, $client_ip = null) {
        if (is_null($client_ip)) $client_ip = $_SERVER['REMOTE_ADDR'];
        $key = self::_getKey();
        $data = base64_decode($encoded);
        $ivlen = openssl_cipher_iv_length(self::$_cipher);
        $iv = substr($data, 0, $ivlen);
        $ciphertext = substr($data, $ivlen);
        $plaintext = openssl_decrypt($ciphertext, self::$_cipher, $key, OPENSSL_RAW_DATA, $iv);
        if ($plaintext === false) return false;
        $pos = strpos($plaintext, '|');
        if ($pos === false) return false; // old format — reject
        $stored_ip = substr($plaintext, 0, $pos);
        if ($stored_ip !== $client_ip) return false; // IP mismatch
        return substr($plaintext, $pos + 1);
    }
}
```

### Changes to existing files

**`library/Urfa/Auth/Adapter.php`** (line ~49):
```php
$user_identity['password'] = Urfa_Session_Crypt::encrypt($this->password);
```

**`library/Urfa/Client.php`** — `restore_session()` returns bool only, no `clearIdentity()`:
```php
public function restore_session($session_id, $client_ip = null) {
    // ... restore logic ...
    if (!$restore_session) {
        $this->writeLog('err', "Unable to restore UTM5 session {$session_id}");
        return false; // NO clearIdentity, NO redirect
    }
    $this->writeLog('info', "UTM5 session {$session_id} restored");
    return $restore_session;
}
```

**`application/modules/billing/controllers/IndexController.php`** — `reconnect()`:
```php
private function reconnect() {
    $urfa = new Urfa_Client();
    if ($urfa->restore_session($this->view->identity->utm5)) {
        return $urfa;
    }
    
    $identity = $this->view->identity;
    if (isset($identity->password)) {
        $password = Urfa_Session_Crypt::decrypt($identity->password);
        if ($password !== false) {
            $user = $urfa->login($identity->login, $password, false);
            if ($user && isset($user['utm5'])) {
                $identity->utm5 = $user['utm5'];
                Zend_Auth::getInstance()->getStorage()->write($identity);
                $this->writeLog('info', "Silent re-login succeeded for {$identity->login}");
                return $urfa;
            }
        }
    }
    
    // Complete failure
    Zend_Auth::getInstance()->clearIdentity();
    $this->_helper->flashMessenger->addMessage(
        array('danger' => 'Сессия истекла. Пожалуйста, авторизуйтесь заново.')
    );
    $this->redirect('/?return_uri=' . $this->view->url());
    exit;
}
```

### Debug logging for `login()` failures

When `reconnect()` logs "login() returned false" but decrypt succeeded, add per-step logging:
```php
$open = $this->urfa->open_session($login, $password, $service, $server);
$this->writeLog('info', "login: open_session=" . ($open ? "true" : "false"));
if (!$open) return false;

$call = $this->urfa->call(-0x4052);
$this->writeLog('info', "login: call=" . ($call ? "true" : "false"));
if (!$call) return false;

$send = $this->urfa->send();
$this->writeLog('info', "login: send=" . ($send ? "true" : "false"));
if (!$send) return false;

$data['utm5'] = $this->urfa->get_key();
$this->writeLog('info', "login: get_key={$data['utm5']}");
```

### Config: `application/configs/billing.ini`

```ini
[app]
session.encrypt_key = "ChangeThisToRandom32ByteString!!"
```

**CRITICAL**: Change the key to a random 32+ byte string before production deployment!

## Session Diagnosis Log (from this session)

| Time | Event |
|------|-------|
| 14:50:39 | UTM5 kernel: new Session Key `<8f952e6a...>` assigned |
| 14:50:40 | `restore_session()` fails: `pop: key not found` |
| 14:50:40 | `reconnect()` attempts silent re-login |
| 14:50:40 | `decrypt()` succeeds — password recovered |
| 14:50:40 | `login()` returns false — **this is the failure point** |
| 14:50:40 | Redirect to login with flash message |

## Lessons Learned

1. **UTM5 kernel timeout** — not PHP GC, not cron, not cookie. Kernel drops TCP session.
2. **Silent re-login requires detailed logging** — `login()` has 4 failure points: `open_session`, `call`, `send`, `get_key`.
3. **IP-binding works** — decrypt succeeded only when IP matched. Good security.
4. **Brace balance after patch** — patching `login()` with `patch` tool can swallow `}`. Always verify with `php -l`.
5. **PHP session file** — `stat /var/lib/php5/sess_*` shows session is alive (size > 0) even after UTM5 timeout.
6. **PHP GC not involved** — `gc_probability=0`, `sessionclean` missing. PHP session persists until TTL.

## Verification Steps

After deploying silent re-login:
1. Login to cabinet
2. Wait 10+ minutes without activity
3. Refresh page
4. **Expected**: page loads normally, user sees data, no redirect to login
5. **Log check**: `grep "Silent re-login succeeded" application/logs/app.log`
