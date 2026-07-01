# UTM5 REST API — Subscriber Portal Endpoints

Extracted from Netup UTM5 5.5-031 REST API documentation.
Full API has 553 endpoints in 17 groups. This subset covers the endpoints actually useful for a mobile subscriber self-service portal.

## Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/login` | Universal login |
| POST   | `/login_hotspot` | Hotspot login (LigaLink uses this) |

## User (core data)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/users` | Basic user data |
| GET    | `/users/full_info` | Full info including accounts, tariffs, service links, blocks, bonuses |
| GET    | `/users/accounts` | Accounts with balances |
| GET    | `/users/contacts` | User contacts |
| GET    | `/users/blocks_info` | Blocking history |
| GET    | `/users/invoices` | Invoices |
| GET    | `/users/servicelinks` | Active service links |
| GET    | `/users/notification_messages` | All notification messages |
| GET    | `/users/notification_messages_paged` | Paged notifications |
| GET    | `/users/web_settings` | Web settings |
| GET    | `/users/total_bonus` | Total bonus amount |

## Customer (self-service actions)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/customer/required_payment` | How much is needed to pay |
| PUT    | `/customer/profile` | Update own profile |
| POST   | `/customer/tarifflinks` | Change tariff |
| POST   | `/customer/connect_service` | Connect a service |
| DELETE | `/customer/servicelinks` | Disconnect a service (pass slink_id) |
| POST   | `/customer/card_payment` | Pay by card |
| POST   | `/customer/promised_payments` | Create promised payment |
| POST   | `/customer/move_funds` | Move funds between accounts |
| POST   | `/customer/enable_turbo_mode` | Enable turbo mode |
| POST   | `/customer/enable_voluntary_blocking` | Voluntary block on |
| POST   | `/customer/disable_voluntary_blocking` | Voluntary block off |
| POST   | `/customer/connect_24tv_service` | Connect 24TV |
| DELETE | `/customer/24tv_service` | Disconnect 24TV |

## Tariffication (reference data)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/tariffing/tariffs` | All tariffs |
| GET    | `/tariffing/services` | All services |
| GET    | `/tariffing/suppliers` | Suppliers |

## Reports (history)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/reports/payments` | Payment history |
| GET    | `/reports/blocks` | Blocking report |
| GET    | `/reports/services` | Services report |
| GET    | `/reports/invoices_doc_list` | Invoice documents |

## Notes

- All endpoints live under `/customer_api` base path (e.g. `https://lk.liga-link.net/customer_api/users`).
- **Authentication is cookie-based**: `POST /login` returns `Set-Cookie: sid_customer=...`. All subsequent requests must send `Cookie: sid_customer=...` in headers. React Native `fetch` does **not** auto-persist cookies — save `sid_customer` manually (AsyncStorage or SecureStore) and inject it as a `Cookie` header on every request.
- If `/login_hotspot` returns empty body, use `/login` with `mobile_telephone: ""` in the payload.
- Call `POST /logout` to invalidate the server session before clearing local state.
- The full API at `https://www.netup.ru/ru/utm5/utm5docs/5.5-031-release-rest/` has `api_data.json` and `api_project.json` available for programmatic inspection.
- Response shapes vary between installations; treat types as guidance, not contracts.
