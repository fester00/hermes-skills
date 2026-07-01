# LigaLink Web Personal Cabinet (Zend Framework 1)

Downloaded archive structure and key findings for the subscriber-facing web personal cabinet.

## Stack
- **Framework:** Zend Framework 1 (legacy)
- **Auth:** `Zend_Auth` with custom `Urfa_Auth_Adapter`
- **Data source:** URFA (custom XML-RPC-like protocol) to УТМ5 billing
- **Frontend:** Bootstrap 3/4 in views (PHP phtml templates), jQuery, jQuery UI
- **DB connection:** PDO_MYSQL to UTM5 (`host=172.16.1.1`, DB=`UTM5`)
- **Cache:** Zend_Cache (File backend, lifetime 120s)

## Directory layout (downloaded archive)

```
htdata/
├── application/
│   ├── Bootstrap.php
│   ├── modules/
│   │   ├── billing/                 # Subscriber module
│   │   │   ├── controllers/
│   │   │   │   └── IndexController.php   # All /user/* actions
│   │   │   ├── forms/
│   │   │   │   ├── UserEdit.php          # Edit profile form (home/mobile/email)
│   │   │   │   ├── Payment.php
│   │   │   │   ├── Card.php
│   │   │   │   ├── TurboMode.php
│   │   │   │   ├── Credit.php
│   │   │   │   ├── Block.php
│   │   │   │   ├── Pay.php
│   │   │   │   ├── ChangePassword.php
│   │   │   │   ├── ChangeServicePassword.php
│   │   │   │   ├── Message.php
│   │   │   │   ├── ByDate.php
│   │   │   │   ├── Traffic.php
│   │   │   │   └── ChangeTariff.php
│   │   │   ├── models/
│   │   │   │   ├── Users.php
│   │   │   │   └── DbTable/Users.php
│   │   │   └── views/scripts/index/
│   │   │       ├── index.phtml             # "Общая информация"
│   │   │       ├── edit.phtml              # Generic form renderer
│   │   │       ├── edit-user.phtml         # (exists but not loaded)
│   │   │       ├── payment.phtml
│   │   │       ├── service.phtml
│   │   │       ├── traffic.phtml
│   │   │       ├── block.phtml
│   │   │       ├── change-tariff.phtml
│   │   │       ├── messages.phtml
│   │   │       ├── new-message.phtml
│   │   │       ├── tariff-history.phtml
│   │   │       ├── invoices.phtml
│   │   │       ├── invoice-document.phtml
│   │   │       ├── blocking-report.phtml
│   │   │       ├── dhs-report.phtml
│   │   │       ├── promise-payment.phtml
│   │   │       ├── service-report.phtml
│   │   │       ├── trafficdate.phtml
│   │   │       ├── trafficip.phtml
│   │   │       ├── telephony-report.phtml
│   │   │       ├── other-charges-report.phtml
│   │   │       ├── turbo-mode.phtml
│   │   │       ├── sent-messages.phtml
│   │   │       └── invoice_document_ind.html / invoice_document_jur.html
│   │   └── default/                      # Login module
│   │       ├── controllers/IndexController.php
│   │       ├── forms/Login.php
│   │       └── views/scripts/index/index.phtml
│   ├── layouts/
│   │   ├── default.phtml                   # Main layout
│   │   ├── login.phtml                     # Login layout
│   │   ├── _menu.phtml
│   │   └── _footer.phtml
│   ├── configs/
│   │   ├── application.ini                 # DB config, routes, modules
│   │   └── billing.ini                     # URFA config + cache settings
│   └── cache/
├── library/
│   ├── Zend/                               # Zend Framework 1 library
│   ├── ZendX/                              # Zend Framework extras
│   ├── Urfa/
│   │   ├── Client.php                      # URFA client (key file)
│   │   ├── Admin.php
│   │   ├── Resolve.php
│   │   ├── Connect.php
│   │   ├── Packet.php
│   │   ├── Socket.php
│   │   ├── Exception.php
│   │   └── ipaddress.php
│   └── DRG/
│       ├── Model.php
│       ├── DatePeriod.php
│       ├── Util.php
│       ├── Mail.php
│       └── Validator/
├── www/
│   ├── index.php                           # Entry point
│   └── assets/
│       ├── bootstrap4/
│       ├── js/
│       ├── images/
│       └── img/
├── tests/
└── cronjobs/
```

## URFA getUserInfo() response

```php
public function getUserInfo()
{
    $user = array();
    $this->urfa->call(-0x4052);
    $this->urfa->send();
    $user['id'] = $this->urfa->get_int();
    $user['login'] = $this->urfa->get_string();
    $user['basic_account'] = $this->urfa->get_int();
    $user['balance'] = Urfa_Resolve::roundDouble($this->urfa->get_double());
    $user['credit'] = Urfa_Resolve::roundDouble($this->urfa->get_double());
    $user['is_blocked_int'] = $this->urfa->get_int();
    $user['is_blocked'] = Urfa_Resolve::resolveBlockState($user['is_blocked_int']);
    $user['create_date'] = Urfa_Resolve::getDateFromTimestamp($this->urfa->get_int());
    $user['last_change_date'] = Urfa_Resolve::getDateFromTimestamp($this->urfa->get_int());
    $user['who_create'] = Urfa_Resolve::resolveUserName($this->urfa->get_int());
    $user['who_change'] = Urfa_Resolve::resolveUserName($this->urfa->get_int());
    $user['is_juridical'] = $this->urfa->get_int();
    $user['full_name'] = $this->urfa->get_string();
    $user['juridical_address'] = $this->urfa->get_string();
    $user['actual_address'] = $this->urfa->get_string();
    $user['work_telephone'] = $this->urfa->get_string();
    $user['home_telephone'] = $this->urfa->get_string();
    $user['mobile_telephone'] = $this->urfa->get_string();
    $user['web_page'] = $this->urfa->get_string();
    $user['icq'] = $this->urfa->get_string();
    $user['tax'] = $this->urfa->get_string();
    $user['kpp'] = $this->urfa->get_string();
    $user['bank_id'] = $this->urfa->get_int();
    $user['user_bank_account'] = $this->urfa->get_string();
    $user['int_status'] = Urfa_Resolve::resolveIntStatus($this->urfa->get_int());
    $user['vat_rate'] = Urfa_Resolve::roundDouble($this->urfa->get_double());
    $user['passport'] = $this->urfa->get_string();   // <-- Single string, e.g.:
    // "серия 4524 №771388 выдан ГУ МВД России по г.Москве 07.05.2025 770-111"
    $this->urfa->finish();
    return $user;
}
```

## URFA userEdit() — read-only passport

```php
public function userEdit($user, $data)
{
    $this->urfa->call(-0x4040);
    $this->urfa->put_string($user['full_name']);
    $this->urfa->put_string($user['actual_address']);
    $this->urfa->put_string($user['juridical_address']);
    $this->urfa->put_string($user['work_telephone']);
    $this->urfa->put_string($data['home_telephone']);
    $this->urfa->put_string($data['mobile_telephone']);
    $this->urfa->put_string($user['web_page']);
    $this->urfa->put_string($user['icq']);
    $this->urfa->put_string($user['passport']);    // <-- PASSPORT IS NOT FROM $data, FROM $user!
    $this->urfa->put_int($user['bank_id']);
    $this->urfa->put_string($user['user_bank_account']);
    $this->urfa->put_string($data['email']);
    $this->urfa->send();
    $this->urfa->finish();
    return true;
}
```

**Key finding:** `userEdit()` exists but it uses the OLD `$user['passport']` value, NOT from `$data`. So updating passport through URFA is **not supported** by the current protocol implementation. Options:
1. Save passport data to a local table in the UTM5 DB (e.g. `user_passport_requests`)
2. Send data via email (using `Zend_Mail` / `DRG_Mail`)
3. Send data via `sendMessage()` as a profile change request to operator

## Routes (from application.ini)

```ini
resources.router.routes.users.route = "/user/:action/*"
resources.router.routes.users.defaults.module= "billing"
resources.router.routes.users.defaults.controller= "index"
resources.router.routes.users.defaults.action= "index"
```

So `/user/` -> `billing/index/index` ("Общая информация")
And `/user/edit-user` -> `billing/index/edit` (edit profile — currently uses sendMessage)

## Existing editAction behavior

```php
public function editAction()
{
    $this->setTitle('Редактирование профиля');
    $message = null;
    $this->view->form = new Billing_Form_UserEdit();
    if ($this->getRequest()->isPost()) {
        if ($this->view->form->isValid($this->getRequest()->getPost())) {
            $urfa = $this->reconnect();
            $messages = $data = $this->view->form->getValues();
            foreach ($messages as $name => $value) {
                $message .= $name.' '.$value.'. ';
            }
            $urfa->sendMessage('Редактирование профиля', $message);   // <-- Not saving to DB!
            $this->_helper->flashMessenger->addMessage(array('success' => 'Сообщение отправлено'));
            $this->_helper->redirector('index', 'index', 'billing');
        }
    }
}
```

## How to add passport form page

1. Create new action `passportAction()` in `IndexController.php`
2. Create new form `Billing_Form_Passport` with fields:
   - `passport_series` (text, required)
   - `passport_number` (text, required)
   - `passport_issued_by` (text, required)
   - `passport_date` (date, required)
   - `passport_code` (text, required)
3. Create new view `passport.phtml` with masked display and edit/submit buttons
4. Parse `$userData['passport']` string with regex to pre-fill fields
5. On submit: either save to UTM5 `users` table local column, or send email, or sendMessage
6. Add link in `index.phtml` next to "Общая информация"

## Masking logic for passport display

Input string: `серия 4524 №771388 выдан ГУ МВД России по г.Москве 07.05.2025 770-111`

Masked display: `серия 45** №77**** выдан ГУ МВД России по г.Москве **.**.2025 ***-***`

Regex to parse:
```php
$pattern = '/серия\s+(\d{4})\s+№(\d{6})\s+выдан\s+(.+?)\s+(\d{2}\.\d{2}\.\d{4})\s+(\d{3}-\d{3})/ui';
```

## Known DB credentials (application.ini)

```ini
resources.db.adapter = PDO_MYSQL
resources.db.params.host = 172.16.1.1
resources.db.params.username = utm5cabinet
resources.db.params.password = JlHaUlgRxxn0n9mYDH
resources.db.params.dbname = UTM5
```

## Useful URFA methods

- `getUserInfo()` -> array with `passport` string
- `getAdditional()` -> bitflags: 1=promised_payments, 2=voluntary_block, 8=change_tariff
- `getAccountsInfo()` -> array of account balances and statuses
- `getServices()` -> array of user services
- `getTarrifs()` -> array of tariffs
- `sendMessage(subject, body)` -> send internal message (used by editAction)
- `changePasswordForCabinet()` -> change user password
- `getMessages(start, end)` -> get message history
- `setBlock(start, end, aid)` -> voluntary block
- `getInvoices(start, end)` -> get invoices
- `getBlockingReport(start, end)` -> blocking report
- `getDHSReport(start, end)` -> session report
- `userEdit($user, $data)` -> edit profile (but NOT passport)
- `getPromisePaymentInfo($aid)` -> promise payment info
- `addPromisePayment($aid, $sum)` -> add promise payment
- `getTurboMode()` -> turbo mode info
- `getCardPaymentInfo()` -> card payment info
- `cardPayment()` -> pay with access card
- `getTelephonyReport(start, end)` -> telephony report
