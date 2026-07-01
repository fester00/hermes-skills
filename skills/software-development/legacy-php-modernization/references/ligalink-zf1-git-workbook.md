# LigaLink ZF1 Cabinet — Git Workbook

Working copy of the subscriber web personal cabinet lives at `https://git.liga-link.net/git/lk.git` (ZF1 + URFA/UTM5). Use this reference when the user asks to continue work on `my.ligalink.ru`.

## Repository facts

- **URL:** `https://git.liga-link.net/git/lk.git`
- **Access:** user `ugway`, password from the user's password store
- **Main branch:** `master`
- **Deploy target:** production web server at `my.ligalink.ru` (VS Code SFTP pushes from the user's local machine)
- **Entry point:** `www/index.php`
- **Module route:** `resources.router.routes.users.route = "/user/:action/*"` in `application/configs/application.ini`

## Layout after clone

```
lk/
├── application/
│   ├── modules/billing/
│   │   ├── controllers/IndexController.php   # all /user/* actions
│   │   ├── forms/Passport.php               # passport / personal-data form
│   │   ├── forms/UserEdit.php               # profile edit form
│   │   └── views/scripts/index/
│   │       ├── index.phtml                  # "Общая информация"
│   │       ├── passport.phtml               # personal-data form view
│   │       └── edit.phtml, payment.phtml, ...
│   ├── configs/
│   │   ├── application.ini                  # DB, routes, modules
│   │   └── billing.ini                      # URFA + cache + session.encrypt_key
│   ├── layouts/
│   │   └── _menu.phtml                      # side nav includes /user/passport
│   └── cache/
├── library/
│   └── Urfa/
│       ├── Client.php                       # URFA protocol client
│       ├── Auth/Adapter.php                 # Zend_Auth adapter
│       └── Session/Crypt.php                # AES-256-CBC password storage for silent re-login
├── www/index.php
└── README, LICENSE, .gitignore
```

## What is already implemented (as of repo initial commit)

- `Billing_Form_Passport` with fields: `passport_series`, `passport_number`, `passport_issued_by`, `passport_date`, `passport_code`, plus `birthdate`, `reg_address`, `mobile_telephone`, `email`, and an acceptance checkbox.
- `passportAction()` in `IndexController.php`:
  - Parses existing `$userData['passport']` string.
  - Pre-fills form fields if data exist.
  - Masks sensitive parts when showing existing data.
  - Makes passport fields required only when UTM5 has no passport yet (`!$hasPassport`).
  - On POST sends the collected data via `Zend_Mail` to the configured support address.
- Menu link `/user/passport` labeled "Персональные данные" in `application/layouts/_menu.phtml`.
- `Urfa_Session_Crypt` stores the cabinet password encrypted in the PHP session (`identity->password`) and performs silent re-login when the UTM5 kernel session expires.

## What was in archive v39 but missing / different in the repo

| File | Repo state vs v39 |
|---|---|
| `application/modules/billing/views/scripts/index/index.phtml` | Missing the top alert banner that warns the user to actualize personal data. |
| `library/Urfa/Session/Crypt.php` | Present but not byte-identical to v39 (equivalent logic). |
| `library/Urfa/Client.php` | Minor whitespace/comment differences; equivalent logic. |
| `IndexController.php` | Contains the same `passportAction()` and silent re-login but log levels differ from v39. |
| `application/configs/billing.ini` | Repo already contains production `session.encrypt_key` and URFA credentials; v39 had placeholder key and commented-out credentials. |

Action: if the user wants the exact v39 behavior, add the missing alert block to `index.phtml`.

## Typical next tasks

1. **Add the missing top alert** in `index.phtml` when passport / birthdate / registration address are incomplete.
2. **Improve form UX**: inline validation, better masking, date picker, address hints.
3. **Persist data**: currently the form only sends email. To write back to UTM5, either:
   - extend `Urfa_Client::userEdit()` to accept a new passport string, or
   - create a local table `user_passport_requests` in the UTM5 DB and write there, then notify operator.
4. **Add tests / staging deployment**: prod is deployed via SFTP; coordinate with the user before pushing live.

## Security notes

- `billing.ini` contains real credentials and the session encryption key. Never commit a changed key to a public repo; in this on-premise repo it is acceptable but should still be rotated periodically.
- The session key must be exactly 32 bytes worth of entropy for AES-256-CBC. `Urfa_Session_Crypt` hashes the configured key with SHA-256 to derive 32 bytes, so any string works but strength depends on source entropy.

## How to clone

```bash
git clone https://ugway:<password>@git.liga-link.net/git/lk.git
```

Or set up a credential helper and omit the password from the URL.

## Verification after changes

Before telling the user a change is ready:

- [ ] `git diff` reviewed; no credentials accidentally changed.
- [ ] New action/view/form triple is complete (`IndexController`, `forms/`, `views/scripts/index/`).
- [ ] Route reachable under `/user/<action-name>`.
- [ ] Link added to `_menu.phtml` or relevant page.
- [ ] Form validates required fields and preserves values on error.
- [ ] `$this->view->userData` set in any action whose view includes `_menu.phtml`.
- [ ] Cache invalidated after any UTM5 data mutation.
