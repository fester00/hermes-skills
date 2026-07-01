# LigaLink Project Ecosystem Map

Condensed reference for the LigaLink ISP projects on this user's home server. Load this before any LigaLink-related task to avoid modifying the wrong codebase.

## Project inventory

| Path | Stack | Purpose | Who uses it |
|------|-------|---------|-------------|
| `~/htdata/` | CakePHP 2.x + dual DB (ams2, UTM5) | Legacy admin CRM for operators | Internal staff (call center, installers, managers) |
| `~/htdata-v2/` | Express + TypeScript + MySQL2 backend + React 19 + Tailwind v4 frontend | Full rewrite of operator CRM | Internal staff (same as above) |
| `~/htdata-frontend/` | React 19 + Vite (separate frontend) | Possibly a dashboard or stripped-down frontend | TBD — check `src/pages/` on arrival |
| **Web personal cabinet** (archive from download) | Zend Framework 1 + URFA/UTM5 | **Subscriber web personal cabinet** at `my.ligalink.ru/user/` | End subscribers (web browser) |
| `~/workspace/ligalink/` | Expo + React Native (iOS/Android) | Subscriber mobile app | End subscribers |
| `~/pentajunior/` | Next.js 15 | Unrelated business website (silicone compounds) | External customers |

## Key endpoints

- **Operator CRM API:** `https://lk.liga-link.net/customer_api` (also used by mobile app)
- **Subscriber mobile API base:** `https://lk.liga-link.net/customer_api`
- **Subscriber web URL:** `my.ligalink.ru/user/` (web version of personal account — source is the ZF1 project)

## What lives where

### CakePHP htdata (`~/htdata/`)
- `app/Model/` — CRM models using `ams2` DB + UTM5 billing models (`useDbConfig='UTM5'`)
- `app/Controller/UsersController.php` — **Operator logins only**, not subscriber accounts
- `app/Controller/AjaxController.php` — JSON-RPC hub for internal tools
- `app/Config/database.php` — credentials for `ams2`, `UTM5`, `UTM5Archive`, `rzs`
- **No subscriber-facing pages here** — `CustomersController` queries UTM5 `users` table but serves internal operators

### htdata-v2 (`~/htdata-v2/`)
- `backend/src/controllers/customerController.ts` — raw SQL to UTM5 `users`/`accounts`/`houses`/`tariffs`
- `backend/src/routes/customers.ts` — REST endpoints for operator searches / detail views
- `frontend/src/pages/Customers/CustomerCardPage.tsx` — operator-facing customer detail card
- **Not a subscriber personal account** — this is the operator CRM replacement

### Web personal cabinet (Zend Framework 1)
- Usually lives in a separate archive or remote server (`my.ligalink.ru`). On this user's environment it arrived as a downloadable tgz archive containing `htdata/` at root.
- `application/modules/billing/controllers/IndexController.php` — all subscriber-facing screens (`/user/`, `/user/edit-user`, `/user/payment`, etc.)
- `application/modules/billing/views/scripts/index/index.phtml` — "Общая информация" (home page of the personal cabinet)
- `application/modules/billing/forms/UserEdit.php` — edit-profile form (home/mobile/email + acceptance checkbox)
- `library/Urfa/Client.php` — URFA client that connects to УТМ5. `getUserInfo()` already returns `$user['passport']` containing a single string with all passport data.
- `application/configs/application.ini` — DB is UTM5 (`host = 172.16.1.1`, DB = `UTM5`)
- `Billing_Model_DbTable_Users` extends `Zend_Db_Table_Abstract` with `$_name = 'users'` — maps directly to the `users` table in the default DB (UTM5)
- `editAction()` currently only sends a message via `urfa->sendMessage()` — does NOT save profile changes to UTM5. The `userEdit($user, $data)` method in `Urfa_Client` exists but uses the old `$user['passport']` value, disallowing user-edited passport updates via URFA.

### Mobile app (`~/workspace/ligalink/`)
- `app/(tabs)/profile.tsx` — subscriber profile with passport fields (`passport_series`, `passport_number`, `passport_date`, `passport_issue`)
- `app/(tabs)/index.tsx` — home screen with balance, address, tariff, notifications
- `api/services/profile.ts` — `getProfile()`, `updateProfile()`, `getBalance()`
- `api/endpoints.ts` — `BASE_URL = 'https://lk.liga-link.net/customer_api'`
- `api/types.ts` — `UserProfile`, `ProfileUpdatePayload` (currently only `full_name`, `email`, `mobile_telephone`)
- **Current API limitation:** `PUT /auth/profile` only accepts `full_name`, `email`, `mobile_telephone`. Passport fields exist in the UI but are **not sent to API on save**.

## Decision tree for new features

When the user asks for changes to "личный кабинет" or "my.ligalink.ru/user":

1. **Is the task about the mobile app?** → modify `~/workspace/ligalink/`
2. **Is the task about the operator CRM?** → modify `~/htdata-v2/` (or `~/htdata/` for legacy)
3. **Is the task about the web version at `my.ligalink.ru`?**
   - If the user provides an archive link or mentions the "web personal cabinet", the source code is almost certainly a **Zend Framework 1** project with URFA/UTM5 integration (not CakePHP, not React).
   - Ask where the deploy target is — the ZF1 cabinet may be served from the VDS (`130.255.9.9`) or another production host; source and deployed code may be separate.
4. **Is the task about the old CakePHP system?** → avoid unless explicitly requested; it is being phased out.

## UTM5 URFA passport field note
- `Urfa_Client.php:getUserInfo()` returns `$user['passport']` as a single string, e.g.:
  `серия 4524 №771388 выдан ГУ МВД России по г.Москве 07.05.2025 770-111`
- This is **read-only** in the existing code — `userEdit()` passes the old value back to the API. To accept user-updated passport data, either:
  a. Save to a local DB table (e.g. `user_passport_requests`) and send email to operator, or
  b. Bypass `userEdit()` and send data via `sendMessage()` as a profile-change request.

## UTM5 billing DB (`UTM5`)

Key tables for subscriber data:
- `users` — customers (full_name, actual_address, mobile_telephone, email, login, password, house_id, basic_account)
- `accounts` — billing accounts (balance, credit, is_blocked, is_deleted)
- `houses` — addresses (street, number, building)
- `tariffs` + `account_tariff_link` + `tariffs_services_link` + `periodic_services_data` — tariff details
- `service_links` + `iptraffic_service_links` + `ip_groups` — IP assignments
- `blocks_info` — block history
- `switch_ports` + `access_switches` + `switch_house_links` — equipment mapping

> Note: `users` table in UTM5 == `Customer` model in CakePHP and == "subscriber" in the mobile app.

## URFA functions discovered
- `getUserInfo()` -> `$user['passport']` is a single string
- `getAdditional()` -> bitflags for promised payments / voluntary block / change tariff flags
- `sendMessage(subject, body)` -> sends an internal message in UTM5 (used by `editAction` and `newMessageAction`)
- `userEdit($user, $data)` -> exists but does NOT allow updating passport from `$data`; it reuses the old `$user['passport']` value
- `getAccountsInfo()` -> returns balances, block_status per account

## Common pitfall

Don't assume "users" in CakePHP `UsersController` are subscribers. In htdata:
- **User** = operator employee (login/password for CRM)
- **Customer** = subscriber from UTM5 `users` table
- In htdata-v2: both are queried as raw SQL from UTM5, but the frontend is operator-only
