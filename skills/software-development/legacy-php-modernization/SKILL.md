---
name: legacy-php-modernization
description: |
  Legacy PHP modernization for CakePHP, Laravel, Yii, CodeIgniter, and Zend Framework 1. Covers full-rewrite vs hybrid vs strangler-fig strategy, React 19 + Tailwind v4 + Radix UI scaffolds, TanStack Query for legacy REST, RBAC migration, and day-to-day maintenance of un-migrated ZF1 subscriber cabinets (URFA/UTM5, passport forms, caching, mail).
version: 1.1
updated: 2026-06-15
---

# Legacy PHP Modernization

## When to use

User asks to:
- Rewrite / modernize / redesign an old PHP project
- Build a new frontend for an existing PHP CRM/admin panel
- Replace CakePHP 2.x/3.x views with React
- Add a React layer to a legacy billing or subscriber management system
- Maintain or extend a Zend Framework 1 subscriber cabinet (personal account)
- Modify ZF1 forms, URFA/UTM5 integration, or passport handling

## Architecture Strategy (choose one)

| Strategy | When | Pros | Cons |
|---|---|---|---|
| **Strangler Fig** | Gradual rewrite over months | Zero downtime, incremental value | Two codebases in parallel |
| **Hybrid** | Large data, can't risk billing | MVP in 4–6 weeks, safe billing | Two backends initially |
| **Full Rewrite** | User explicitly wants clean slate, OR audit shows PHP is thin proxy over stable DB | Clean architecture, full control, no legacy debt | 2–3 months to MVP, migration risk |

> **Note:** Full Rewrite is viable far more often than it first appears. Do not default to Hybrid just because the legacy app is "big." Full Rewrite works when:
> - The legacy codebase is audit-able in one session (under 40 controllers, under 60 models)
> - Database schemas are well-understood and stable (dual DB: CRM + billing, no business logic in stored procedures)
> - User wants to learn modern patterns (Express + TypeScript + raw SQL) — hands-on practice accelerates adoption
> - No critical billing logic lives in PHP (e.g., billing is in external system like UTM5, PHP just queries it)
> - No complex file uploads, no legacy session state that must be preserved across deploy
>
> If user says "переписать с нуля" or "full rewrite" → **do not push back with Hybrid.** Scaffold both backend and frontend in the same session: backend API first, frontend pages second. Use `execute_code` (Python) for bulk file generation when `write_file` triggers false linter positives at scale.

For **ISP/CRM-style systems** with a billing DB (UTM5) + CRM DB (ams2), both Hybrid and Full Rewrite are valid:
- **Hybrid:** Keep CakePHP as a **proxy API** to UTM5. Build new React frontend that talks to both old CakePHP endpoints and new CRM endpoints.
- **Full Rewrite:** Replace CakePHP entirely with Express + TypeScript + MySQL2. New backend queries both DBs directly via raw SQL. Cleanest architecture, but requires rebuilding all controllers.

## Phase 1: Audit the old code (delegate in parallel)

1. **Models audit** — list all models, belongsTo/hasMany/hasOne links, dual-database configs (`database.php`), soft-delete fields (`deleted`), raw SQL reports.
2. **Controllers audit** — list all public actions, AJAX JSON-RPC endpoints, `beforeFilter` auth checks, role checks (`Group.limited_privileges`).
3. **Views audit** — note which screens map to which React pages.

> Pro tip: Send two leaf agents simultaneously — one for models, one for controllers.

## Phase 2: Scaffold the new frontend

### Stack (CRM-optimized)

- **Vite** + React 19 + TypeScript
- **Tailwind CSS v4** (warn: no `tailwind.config.js`, use `@theme` in CSS)
- **Radix UI primitives** (Dialog, Tabs, Select, Popover, etc.)
- **TanStack Query** (server state, caching, mutations)
- **react-router-dom** (BrowserRouter)
- **Axios** with `withCredentials: true` for legacy cookie auth
- **Recharts** for simple stats dashboards
- **date-fns** for date formatting

## Tailwind v4 pitfalls

⚠️ `@apply` in `@layer base` breaks the build — see [`references/tailwind-v4-apply-pitfall.md`](references/tailwind-v4-apply-pitfall.md) for the exact error and fix.

```css
/* src/index.css — Tailwind v4 way */
@import "tailwindcss";

@theme {
  --color-background: hsl(0 0% 100%);
  --color-foreground: hsl(222.2 84% 4.9%);
  --color-primary: hsl(222.2 47.4% 11.2%);
  --radius: 0.5rem;
}

@layer base {
  body {
    background-color: var(--color-background);
    color: var(--color-foreground);
  }
}
```

### Path aliases (required)

```json
// tsconfig.app.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "ignoreDeprecations": "6.0",
    "paths": { "@/*": ["src/*"] }
  }
}
```

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: { alias: { '@': path.resolve(__dirname, './src') } },
});
```

## Phase 2.5: CakePHP CRM-specific audit checklist

When auditing an ISP/CRM-style CakePHP project, look for these patterns:

### Dual-database setup
Check `app/Config/database.php` for multiple configs:
- `default` / `test` — CRM tables (orders, employees, equipment)
- `UTM5` — billing (customers, accounts, tariffs, payments)
- `UTM5Archive` — historical billing data
- `rzs` — regulatory logs (Russia-specific)

### Role model
CakePHP 2.x CRMs typically use `Group.limited_privileges`:
- `0` = admin / full access
- `1` = partial (can't edit brigades/settings/houses)
- `2+` = restricted (read-only, can't access switches/tariffs)

Check `beforeFilter()` in each controller for:
```php
if ($this->Session->read('Auth.User.Group.limited_privileges') != 0) {
  throw new UnauthorizedException('Доступ запрещен');
}
```

Also check `AjaxController` for `$accessDeny` arrays restricting models/methods by privilege level.

### API patterns
CakePHP CRMs expose three API styles simultaneously:
1. **Standard CRUD** — `GET /customers`, `POST /orders/edit/:id` — returns JSON via `beforeRender()` + `_serialize`
2. **JSON-RPC hub** — `POST /ajax` with body `{model, method, params}` — universal model/method proxy via `AjaxController::index()`
3. **NMS wrapper** — `POST /diag` with body `{method, params, required: [...]}` — SNMP operations via `DiagController`

### Soft-delete pattern
Almost all tables use `deleted` field:
- `NULL` = active record
- `YYYY-MM-DD HH:ii:ss` = soft-deleted
Filter with `'deleted' => NULL` in queries.

### Equipment models
ISP CRMs track physical infrastructure:
- `AccessSwitch` + `SwitchPort` + `SwitchHouseLink` — wired switches and ports
- `Wireless` + `WirelessPort` + `WirelessHouseLink` — WiFi equipment
- `Iptvbox` + `IptvboxAccountLink` — IPTV set-top boxes
- `Hive` + `HivesHouse` — network nodes / POPs

### Order system
Two separate order types:
- `Order` — connection/installation orders (status_a/b/c/d/e)
- `RepairOrder` — repair/maintenance tickets (type='int')
Both have `executor` (employee name or brigade), `connect_date`/`connect_time`, soft-delete via `deleted`.

### Statistics queries
CakePHP models often contain raw SQL for billing reports (ARPU, coverage, credit customers). Look for `harpu()`, `countCreated()`, `getExecutorStats()` methods.

## Phase 3: Map roles from legacy to React

Typical CakePHP 2.x CRM uses `Group.limited_privileges`:
- `0` = admin / full access
- `1` = partial (can't edit brigades/settings)
- `2+` = restricted (read-only, can't access switches/tariffs)

When defining new roles (e.g., call-center manager, field manager, installer), map them against:
1. The old `limited_privileges` numeric levels
2. The actual `beforeFilter` checks in each controller
3. The `AjaxController::$accessDeny` whitelist/blacklist

Auth context pattern:

```tsx
// hooks/useAuth.tsx
function canAccess(feature: string, user: User): boolean {
  const priv = user.Group?.limited_privileges ?? 999;
  if (priv === 0) return true;
  const isManager = user.Group.name.toLowerCase().includes('менеджер');
  const isCallCenter = user.Group.name.toLowerCase().includes('колл');
  const isInstaller = user.Group.name.toLowerCase().includes('монтаж');

  switch (feature) {
    case 'customer_search': case 'customer_card': case 'diagnostics':
    case 'equipment_search': case 'equipment_view':
    case 'orders_calendar': case 'orders_create': case 'orders_view':
      return isManager || isCallCenter || isInstaller;
    case 'orders_assign':
      return isManager;
    default:
      return false;
  }
}
```

## Phase 4: API integration with CakePHP

Legacy CakePHP exposes:
1. **Standard CRUD** — `GET /customers`, `POST /orders/edit/:id`
2. **AJAX JSON-RPC** — `POST /ajax` with body `{model, method, params}`
3. **Public endpoints** — `GET /ajax/getCustomerDetails/:uid`

Axios setup:

```ts
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true,
  headers: { 'X-Requested-With': 'XMLHttpRequest' },
});
```

## Phase 5: Directory structure for CRM

```
src/
  components/ui/       # shadcn-style primitives
  components/layout/   # Sidebar, Header, MainLayout
  hooks/               # useAuth, useCustomers, useOrders, useEquipment, useBrigades
  pages/               # All screens organized by domain
  services/            # Axios instance
  types/               # TypeScript interfaces
  lib/                 # cn() helper
  App.tsx              # Routing + ProtectedRoute
```

## Verification checklist

- [ ] Build passes (`vite build`) with zero TS errors
- [ ] Login redirects to dashboard, 401 redirects to login
- [ ] Role gating: restricted user cannot see admin routes
- [ ] Lists support pagination / search / filtering
- [ ] Detail pages load sub-resources (tabs)
- [ ] Mutations invalidate query cache

## References (Migration phase)

- `templates/crm-vite-scaffold/` — copy-ready Vite + Tailwind v4 + Radix templates
- `templates/express-mysql2-backend.md` — Express + TypeScript + MySQL2 scaffold (DatabaseManager, JWT auth, RBAC)
- `references/tailwind-v4-apply-pitfall.md` — Tailwind v4 `@apply` in `@layer base` build error
- `references/cakephp-crm-controllers-audit.md` — Quick-reference for CakePHP 2.x CRM controller patterns
- `references/cakephp-to-express-sql-patterns.md` — Raw SQL migration patterns (dual DB, soft-delete, IP handling, status bits, coverage stats)
- `references/ligalink-ecosystem-map.md` — LigaLink project map (all codebases: htdata + htdata-v2 + mobile + ZF1 cabinet)

---

# Legacy ZF1 Cabinet Maintenance

## When to use

User asks to modify the **subscriber-facing web personal cabinet** at `my.ligalink.ru/user/` (or similar URLs). This is the **un-migrated** Zend Framework 1 codebase that lives in its own archive (not the CakePHP operator CRM, not htdata-v2, not the mobile app).

> Always check `references/ligalink-ecosystem-map.md` first to avoid editing the wrong project.

## ZF1 Stack

- **Framework:** Zend Framework 1 (legacy PHP)
- **Auth:** `Zend_Auth` with custom `Urfa_Auth_Adapter` (connects to УТМ5)
- **Data source:** URFA (XML-RPC-like binary protocol) to УТМ5 billing server
- **Frontend:** Bootstrap 3/4 in PHP phtml templates, jQuery, jQuery UI
- **DB connection:** PDO_MYSQL to UTM5 (`host=172.16.1.1` typical)
- **Cache:** Zend_Cache (File backend, short lifetime)
- **Mail:** `Zend_Mail('utf-8')` or `DRG_Mail()`; server requires working MTA/sendmail/SMTP

## jQuery / ZendX JQuery pitfall (no external CDN)

The subscriber cabinet must work even when the client has no internet access except `ligalink.ru` / `liga-link.net`. Never load jQuery or jQuery UI from Google CDN.

**Problem:** `application/layouts/default.phtml` may contain:
```php
<?php echo $this->jQuery()->setCdnSsl(true)->uiEnable(); ?>
```
This causes ZendX to inject `https://ajax.googleapis.com/ajax/libs/jquery/...`, which can override the local jQuery and break plugins/methods such as `.on()` if the CDN version is older or loads after local scripts.

**Fix:** Force ZendX to use local files and remove duplicate UI includes:
```php
<?php echo $this->headScript()
    ->appendFile('/assets/js/jquery/jquery.min.js')
    ->appendFile('/assets/js/jquery/jquery.timeago.js')
    ->appendFile('/assets/js/jquery/jquery.timeago.ru.js')
?->

<?php echo $this->jQuery()
    ->setLocalPath('/assets/js/jquery/jquery.min.js')
    ->setUiLocalPath('/assets/js/jquery/jquery-ui.custom.min.js')
    ->uiEnable(); ?>
```
And at the bottom of the layout do **not** add `jquery-ui.custom.min.js` again via `headScript()` — ZendX already injects it.

### Verification
- Open browser DevTools → Network, reload the page.
- Confirm no requests to `ajax.googleapis.com`.
- Confirm `jQuery.fn.jquery` matches the expected local version (e.g. `1.11.0`).

## URFA client patterns

| File | Purpose |
|------|---------|
| `application/modules/billing/controllers/IndexController.php` | All `/user/*` actions (index, edit, payment, service, traffic, block, tariff-change, etc.) |
| `application/modules/billing/forms/UserEdit.php` | Edit profile form (home/mobile/email fields) |
| `application/modules/billing/views/scripts/index/index.phtml` | "Общая информация" — home page |
| `application/modules/billing/views/scripts/index/edit.phtml` | Generic form renderer |
| `library/Urfa/Client.php` | URFA client — all УТМ5 communication |
| `application/configs/application.ini` | DB config, routes, modules |
| `application/configs/billing.ini` | URFA connection config, cache settings |
| `application/layouts/_menu.phtml` | Side navigation menu |

## URFA client patterns

### Reconnect pattern used in every action
```php
private function reconnect() {
    $urfa = new Urfa_Client();
    $urfa->restore_session($this->view->identity->utm5);
    return $urfa;
}
```

### Getting user data with caching
```php
$userData = $this->cache->load($this->cache_basic_account);
if ($userData === false) {
    $urfa = $this->reconnect();
    $userData = $urfa->getUserInfo();
    $this->cache->save($userData, $this->cache_basic_account);
    unset($urfa);
}
$this->view->userData = $userData;
```

### Existing URFA methods
- `getUserInfo()` → `$user['passport']` single string, e.g. "серия 4524 №771388 выдан ГУ МВД России по г.Москве 07.05.2025 770-111"
- `getAdditional()` → bitflags: 1=promised_payments, 2=voluntary_block, 8=change_tariff
- `getAccountsInfo()` → balances, block_status per account
- `getServices()` → user services list
- `getTarrifs()` → tariff list
- `getTurboMode()` → turbo mode info
- `sendMessage(subject, body)` → internal UTM5 message (current method used by editAction)
- `userEdit($user, $data)` → edit profile BUT passport is NOT updatable (uses old `$user['passport']`)
- `changePasswordForCabinet()` → change cabinet password
- `setBlock(start, end, aid)` / `delBlock(aid)` → voluntary block
- `getPromisePaymentInfo($aid)` / `addPromisePayment($aid, $sum)` → promise payment
- `getInvoices(start, end)` → invoices
- `getBlockingReport(start, end)` → blocking report
- `getDHSReport(start, end)` → session report
- `getTelephonyReport(start, end)` → telephony report
- `cardPayment(account, card, pin)` → pay with access card

## Passport data handling

### Current behavior
`$userData['passport']` is a single string from УТМ5. It cannot be updated via `userEdit()` (the method reuses the old value).

### Options for user-supplied passport updates
1. **Admin API `rpcf_edit_user_new` (0x2126)** — preferred. Lets you update passport string, phone, email and additional params in one call. Always GET full profile first (`rpcf_get_userinfo`) and merge additional params with new values on the left of the `+` operator.
2. **Email to operator** — use `Zend_Mail` or `DRG_Mail` to send passport data to support@ email. Non-persistent but simple.
3. **Local DB table** — create table in UTM5 DB (e.g. `user_passport_requests`) and save there. Requires DB schema change.
4. **sendMessage()** — send internal УТМ5 message to operator with new passport data. Operator manually updates in УТМ5 admin panel.

### Passport string format
```
серия 4524 №771388 выдан ГУ МВД России по г.Москве 07.05.2025 770-111
```

Parsing regex:
```php
$pattern = '/серия\s+(\d{4})\s+№(\d{6})\s+выдан\s+(.+?)\s+(\d{2}\.\d{2}\.\d{4})\s+(\d{3}-\d{3})/ui';
```

Masked display:
```
серия 45** №77**** выдан ГУ МВД России по г.Москве **.**.2025 ***-***
```

### Additional params IDs for LigaLink

Known UTM5 additional parameter IDs for passport flow:
- `6` — `user_birthdate`
- `7` — `user_birthplace`
- `11` — `passport_registration_address`

Use `rpcf_get_uaparam_list` (0x440b) to resolve names at runtime; never hard-code IDs from dumps longer than necessary.

### Storing registration address

When the form asks for address in separate fields (street, city, zip), store them as a single comma-separated string:

```php
$address = $zip . ', ' . $city . ', ' . $street;
```

And read back by extracting the leading 6-digit zip and splitting on the first comma:

```php
if (preg_match('/^(\d{6})\s*,?\s*(.*)$/u', $address, $m)) {
    $zip = $m[1];
    $rest = $m[2];
    list($city, $street) = array_map('trim', explode(',', $rest, 2));
}
```


## jQuery / ZendX JQuery pitfall (no external CDN)

The subscriber cabinet must work even when the client has no internet access except `ligalink.ru` / `liga-link.net`. Never load jQuery or jQuery UI from Google CDN.

**Problem:** `application/layouts/default.phtml` may contain:
```php
<?php echo $this->jQuery()->setCdnSsl(true)->uiEnable(); ?>
```
This causes ZendX to inject `https://ajax.googleapis.com/ajax/libs/jquery/...`, which can override the local jQuery and break plugins/methods such as `.on()` if the CDN version is older or loads after local scripts.

**Fix:** Force ZendX to use local files and remove duplicate UI includes:
```php
<?php echo $this->headScript()
    ->appendFile('/assets/js/jquery/jquery.min.js')
    ->appendFile('/assets/js/jquery/jquery.timeago.js')
    ->appendFile('/assets/js/jquery/jquery.timeago.ru.js')
?->

<?php echo $this->jQuery()
    ->setLocalPath('/assets/js/jquery/jquery.min.js')
    ->setUiLocalPath('/assets/js/jquery/jquery-ui.custom.min.js')
    ->uiEnable(); ?>
```

And at the bottom of the layout do **not** add `jquery-ui.custom.min.js` again via `headScript()` — ZendX already injects it.

### Verification
- Open browser DevTools → Network, reload the page.
- Confirm no requests to `ajax.googleapis.com`.
- Confirm `jQuery.fn.jquery` matches the expected local version (e.g. `1.11.0`).

See `references/zf1-jquery-cdn-pitfall.md` for the exact error transcript and patch.

## Adding new pages to the cabinet

### Step 1: Create new action in IndexController
```php
public function myNewPageAction() {
    $this->setTitle('Название страницы');
    // ... logic ...
    $this->view->myData = $data;
}
```

> **Compatibility note**: if your menu/nav layout (`_menu.phtml`) reads `$this->userData`, always set `$this->view->userData = $userData` in the action even if you also pass it under a different key.

### Step 2: Create view template
File: `application/modules/billing/views/scripts/index/my-new-page.phtml`
Use existing views as templates (Bootstrap classes, `$this->bootAlert()`, `$this->form`, etc.)

### Step 3: Optionally create a Zend Form
File: `application/modules/billing/forms/MyNewPage.php`
Extend `Zend_Form`. Use existing forms for decorator patterns.
>
> **Form data persistence on validation errors**: set field values explicitly in the template, or call `$form->populate($formData)` in the controller when re-rendering. For example, in phtml:
> ```html
> <input value="<?= htmlspecialchars($this->form->getValue('field_name')) ?>" ...>
> ```

### Client-side: enable submit only when consent checkbox is checked

```js
jQuery(document).ready(function ($) {
    var $consent = $('[name="pd_consent"]');
    var $submitBtn = $('.passport-form button[type="submit"]');

    function updateConsentState() {
        var checked = $consent.is(':checked');
        var $group = $consent.closest('.pd-consent-group');
        if (checked) {
            $consent.removeClass('is-required');
            $group.find('.required-hint').remove();
            $submitBtn.prop('disabled', false);
        } else {
            $consent.addClass('is-required');
            if (!$group.find('.required-hint').length) {
                $group.append('<div class="field-hint required-hint">Обязательно к заполнению</div>');
            }
            $submitBtn.prop('disabled', true);
        }
    }

    $consent.on('change', updateConsentState);
    updateConsentState();
});
```

### Server-side: refuse to save if consent missing

```php
$pdConsent = $form->getValue('pd_consent');
if (empty($pdConsent)) {
    $form->getElement('pd_consent')->markAsError();
    $form->getElement('pd_consent')->addError('Необходимо согласие на обработку персональных данных');
    $this->view->error = 'Для сохранения данных необходимо согласие на обработку персональных данных.';
} else {
    // ... save to UTM5 ...
}
```

### Checkbox decorator (label after box)

```php
$element->setDecorators(array(
    'ViewHelper',
    'Errors',
    array('Label', array('placement' => 'APPEND', 'class' => 'form-check-label')),
    array('HtmlTag', array('tag' => 'div', 'class' => 'form-group form-check pd-consent-group')),
));
```

## Adding new pages to the cabinet
Edit `application/modules/billing/views/scripts/index/index.phtml` or `application/layouts/_menu.phtml`

## Form decorator pattern (Bootstrap 3/4 compatible)

Typical ZF1 form with Bootstrap CSS:
```php
class Billing_Form_MyForm extends Zend_Form {
    public function __construct() {
        $this->setName('form_name');
        parent::__construct();

        $this->addElement('text', 'field_name', array(
            'label' => 'Field Label',
            'class' => 'form-control mb-3',
            'required' => TRUE,
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array('NotEmpty')
        ));

        $this->addElement('checkbox', 'accepted', array(
            'label' => 'Подтверждаю',
            'required' => TRUE,
            'validators' => array(
                array(new Zend_Validate_InArray(array(1)), FALSE)
            ),
            'ErrorMessages' => array('Подтвердите правильность информации'),
        ));

        // Чекбокс согласия на обработку ПДн — submit disabled until checked
        $this->addElement('checkbox', 'pd_consent', array(
            'label' => 'Я согласен на обработку персональных данных и ознакомлен с политикой конфиденциальности',
            'class' => 'form-check-input',
            'required' => false,
            'value' => '1',
            'uncheckedValue' => '',
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                array('NotEmpty', true, array('messages' => array('isEmpty' => 'Необходимо согласие на обработку персональных данных'))),
            ),
        ));

        $this->addElement('button', 'send', array(
            'label' => 'Сохранить',
            'class' => 'btn btn-primary btn-block',
            'type' => 'submit',
            'disabled' => 'disabled',
        ));
            'value' => '1',
            'uncheckedValue' => '',
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                array('NotEmpty', true, array('messages' => array('isEmpty' => 'Необходимо согласие на обработку персональных данных'))),
            ),
        ));

        $this->addElement('button', 'send', array(
            'label' => 'Сохранить',
            'class' => 'btn btn-primary btn-block',
            'type' => 'submit',
            'disabled' => 'disabled',
        ));
    }
}
```

## Flash messages

```php
$this->_helper->flashMessenger->addMessage(
    array('success' => 'Операция успешна')
);
$this->_helper->flashMessenger->addMessage(
    array('danger' => 'Произошла ошибка')
);
```

## Cache invalidation

After data mutation, invalidate relevant cache keys:
```php
$this->cache->remove($this->cache_basic_account);          // user info
$this->cache->remove($this->cache_basic_account . '_additional_params');
$this->cache->remove($this->cache_basic_account . '_accounts');
$this->cache->remove($this->cache_basic_account . '_services');
$this->cache->remove($this->cache_basic_account . '_tarrifs');
```

⚠️ Use the **same cache key** for additional params everywhere. If `indexAction()` uses `_additional_params` and `passportAction()` uses `_passport_additional_params`, the homepage alert may stay stale after the user updates data.

## Typical database credentials (application.ini)

```ini
resources.db.adapter = PDO_MYSQL
resources.db.params.host = 172.16.1.1
resources.db.params.username = utm5cabinet
resources.db.params.password = ...
resources.db.params.dbname = UTM5
resources.db.params.charset = "utf8"
```

## Email handling (Zend_Mail)

Standard `Zend_Mail` with UTF-8:
```php
$mail = new Zend_Mail('utf-8');
$mail->setSubject('Паспортные данные абонента (' . $account . ')')
     ->setBodyText($body)
     ->addTo($toEmail)
     ->setFrom($fromEmail)
     ->send();
```

Pitfall: `Zend_Mail` relies on local sendmail by default. If the production host uses an external SMTP relay, configure `Zend_Mail_Transport_Smtp` in `application.ini` or bootstrap.

## Typical workflow with the LigaLink ZF1 cabinet

The ZF1 cabinet lives in `git.liga-link.net/git/lk.git`. The user (and the repository owner) deploys manually via SFTP/VS Code. The agent's job is code only.

1. `git pull origin master` before any edits.
2. Edit PHP/JS/CSS files, run `php -l` on changed files.
3. `git commit` and `git push origin master`.
4. Tell the user to deploy. **Do not assume the server is updated automatically.**
5. After the user confirms deployment, open the live page in the browser, log in with the provided test account, and verify layout, masks, validation, and POST behavior.

## Conditional required fields

Fields should only be required when the corresponding data is missing in UTM5. For users who already have a passport, address, or birthdate, leave those fields optional (they see masked placeholders). For missing data, add `NotEmpty` validators dynamically in the POST branch:

```php
$hasPassport = !empty($existing['series']);
if (!$hasPassport) {
    $form->getElement('passport_series_number')->addValidator('NotEmpty', true, ...);
    $form->getElement('passport_issued_by')->addValidator('NotEmpty', true, ...);
    $form->getElement('passport_date')->addValidator('NotEmpty', true, ...);
    $form->getElement('passport_code')->addValidator('NotEmpty', true, ...);
}

$hasRegAddress = !empty($additionalParams['passport_registration_address']);
if (!$hasRegAddress) {
    $form->getElement('reg_address')->addValidator('NotEmpty', true, ...);
    $form->getElement('reg_index')->addValidator('NotEmpty', true, ...);
    $form->getElement('reg_city')->addValidator('NotEmpty', true, ...);
}
```

Mirror the same logic in the client-side JS by passing flags from the view:

```php
var hasPassportInUtm5 = <?= json_encode(!empty($parsed['series'])) ?>;
var hasBirthdayInUtm5 = <?= json_encode(!empty($this->additionalParams['user_birthdate'])) ?>;
var hasRegAddressInUtm5 = <?= json_encode(!empty($this->additionalParams['passport_registration_address'])) ?>;
```

## Verification checklist for new pages

- [ ] New action added to `IndexController.php`
- [ ] New view template created in `views/scripts/index/`
- [ ] Form class created (if needed) in `forms/`
- [ ] Route accessible via `/user/action-name`
- [ ] Menu/link added to existing pages (index.phtml or _menu.phtml)
- [ ] Flash messages shown on success/error
- [ ] Cache invalidated after data mutation
- [ ] Form validates required fields and preserves values on error
- [ ] Non-POST requests handled gracefully (display form, not error)
- [ ] `$this->view->userData` set for `_menu.phtml` compatibility
- [ ] **All JS/CSS loaded locally** — no googleapis CDN. jQuery via `setLocalPath()`, jQuery UI via `setUiLocalPath()`. jQuery loaded exactly once. No jQuery version-fallback hacks.

## References (ZF1 maintenance)

- `references/zf1-passport-form-recipe.md` — Complete passport form implementation v1 (ZF1 form + controller action + view + masks + email pattern)
- `references/zf1-passport-form-v2.md` — Styled V2: optional email, inline CSS, pure jQuery masks (no external CDN)
- `references/zf1-passport-form-v3.md` — Compact single-form that writes to UTM5 via `rpcf_edit_user_new`: combined series/number, address split into street/city/zip, custom form row renderer
- `references/zf1-passport-form-v4.md` — Production V4: `Zend_Form_DisplayGroup` rows, Bootstrap-safe CSS with `!important`, direct `<link>/<script>` inclusion because `headLink/inlineScript` does not output, no duplicate JS placeholders
- `references/zf1-passport-form-v5.md` — Mandatory PD consent checkbox + strict local jQuery: consent toggles submit button, server-side guard blocks UTM5 writes without consent, removes CDN and old-jQuery fallback hacks.
- `references/ligalink-ecosystem-map.md` — LigaLink project map (which codebase handles which feature)
1. `git pull origin master` before editing.
2. `git add -A && git commit -m "..."`.
3. **`git push origin master`** — mandatory. Confirm the push succeeded before telling the user it is done.

The user handles deployment to the production host themselves (SFTP sync or server-side `git pull`). The agent's responsibility ends after a successful push.

**Common mistake:** stopping after `git commit` and assuming the work is "done". It is not done until `git push origin master` succeeds.
### When CSS classes are not enough: inline style on inputs

In legacy ZF1 + Bootstrap cabinets, the production CSS may be stale, overridden, or simply not loaded. If you add width classes like `.field-short` to the wrapper `<div class="form-group">`, the inner `<input class="form-control">` can still render at 100% because Bootstrap's `.form-control { width: 100%; }` wins.

**Fallsafe recipe:** set `style="width: ...;"` directly on the input element from the form class:

```php
$fieldWidths = array(
    'passport_serial_number' => '160px',
    'passport_date'          => '140px',
    'passport_code'          => '140px',
    'birthday'               => '140px',
    'reg_zip'                => '110px',
    'phone'                  => '180px',
);
foreach ($this->getElements() as $element) {
    $name = $element->getName();
    if ($name === 'send' || empty($fieldWidths[$name])) continue;
    $currentStyle = $element->getAttrib('style');
    $element->setAttrib('style', trim($currentStyle . ' width: ' . $fieldWidths[$name] . ';'));
}
```

See [`references/zf1-passport-form-v3.md`](references/zf1-passport-form-v3.md) for the full compact form recipe including this inline-width fallback and the multi-field row renderer.

## References (ZF1 maintenance)

- `references/zf1-passport-form-recipe.md` — Complete passport form implementation v1 (ZF1 form + controller action + view + masks + email pattern)
- `references/zf1-passport-form-v2.md` — Styled V2: optional email, inline CSS, pure jQuery masks (no external CDN)
- `references/zf1-passport-form-v3.md` — Compact single-form that writes to UTM5 via `rpcf_edit_user_new`: combined series/number, address split into street/city/zip, custom form row renderer, **inline width fallback for Bootstrap conflicts**
- `references/ligalink-ecosystem-map.md` — LigaLink project map (which codebase handles which feature)
