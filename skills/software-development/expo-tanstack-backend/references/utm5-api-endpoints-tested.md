# UTM5 / Netup REST API — subscriber endpoints reference

Reference extracted from https://www.netup.ru/ru/utm5/utm5docs/5.5-031-release-customer-rest/
and verified through live testing against a real UTM5 5.5.031 instance.

## Tested endpoints (working)

| Method | Endpoint | Auth | Behaviour |
|--------|----------|------|-----------|
| POST | `/login` | no | Returns `{ sid_customer, ... }` — extract and store manually in RN. |
| POST | `/logout` | cookie | Invalidates server session. Call before clearing local state. |
| POST | `/v3/auth` | cookie | Returns `{ id, login, full_name, balance, accounts: [...], slists: [...], abonements: [...] }`. Main profile data. |
| POST | `/auth/accounts` | cookie | Returns list of accounts (may be empty array). |
| POST | `/auth/services/{accountId}` | cookie | Returns `{ slists: [...], services: [...], tariffs: [...] }`. |
| POST | `/auth/slist` | cookie | Returns service-link details including `cost`. |
| GET  | `/auth/notifications?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD` | cookie | Returns `NotificationMessage[]`. May be `[]` for test users. |
| GET  | `/auth/full_statistics?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD` | cookie | Returns `StatisticsEntry[]`. Max date range = 1 year. |
| GET  | `/auth/statistics?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD` | cookie | Returns `StatisticsEntry[]`. Same format as full_statistics. |
| POST | `/auth/block_statistics` | cookie | Returns `{ slink_id: number }[]` with `comments`, `user_date_block`, `next_date_block`. |
| GET  | `/auth/tariffs` | cookie | Returns `Tariff[]` (all available tariffs). |
| POST | `/auth/tariffs` | cookie | **Change tariff**: payload `{ tariff_link_id: number, comments: string }`. |
| POST | `/auth/promised_payment` | cookie | Returns promise-payment details. |
| POST | `/auth/min_payment` | cookie | Returns minimum payment amount. |

## Deprecated / do not use (v2)

| Endpoint | Status | Replacement |
|----------|--------|-------------|
| `/v2/auth` | **DEPRECATED** | `/v3/auth` |
| `/block_statistics` (root) | **DEPRECATED** | `/auth/block_statistics` |

## Field mapping gotchas

- `cost` is returned as **string** (`"450.00"`) not number. Parse with `Number(cost)` or `parseFloat`.
- `comments` is an array `string[]` on block_statistics but may be single `string` on other endpoints. Always normalize: `Array.isArray(x) ? x[0] : x`.
- `service_name` vs `name` — UTM5 uses `service_name` in tariff objects; map to `name` in UI types.
- `paymentDate` / `date` / `user_date_block` — different date field names per endpoint. Always map to a unified `date: string` in the hook/onSuccess handler.

## Change tariff payload (POST /auth/tariffs)

```json
{
  "tariff_link_id": 123,
  "comments": "Желание клиента"
}
```

**Critical**: send `tariff_link_id` (the ID from `services[].tariffs[]`), NOT `tariff_id`.
The `tariff_id` is the generic tariff definition; `tariff_link_id` is the account-specific link.

## Date parameter format

All `startDate` / `endDate` parameters use `YYYY-MM-DD`:

```ts
import { format } from 'date-fns';
const startDate = format(subYears(new Date(), 1), 'yyyy-MM-dd');
const endDate   = format(new Date(), 'yyyy-MM-dd');
```

**Error if startDate > 1 year ago**: `startDate less than year ago`.
**Error if startDate omitted for some endpoints**: returns `[]` or `400`.
