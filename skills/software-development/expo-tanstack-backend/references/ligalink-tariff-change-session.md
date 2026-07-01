# LigaLink Tariff Change Investigation — 2025-05-14 Session Notes

## Observation: UTM5 returns `next_tariff_name` after POST /auth/tariffs

After calling `POST /auth/tariffs` (payload: `account_id`, `tariff_link_id`, `next_tariff_id`) for subscriber account `16590`, the server responds with `{"result":"OK"}`. However, `GET /auth/profile` still lists the OLD tariff as active. Crucially, the `ProfileTariff` object inside `profile.tariffs[0]` now includes a field `next_tariff_name`:

```json
{
  "tariffs": [{
    "id": 427,
    "name": "(архив) Супер (месяц)",
    "next_tariff_name": "Супер Лайт",
    "tariff_link_id": 10059
  }]
}
```

## Root cause
UTM5 applies tariff changes **deferred** — at the start of the next billing period. The `POST` merely queues the change for the next cycle.

Therefore:
- There is **no server-side stale profile cache bug** (hypothesis `h_server_cache` was rejected).
- A **relogin hack is dead code** — changing `sid_customer` by logout/login will not update the active tariff either, because the change is deferred by the billing engine, not a caching layer.

## Practical lesson
In a React Native / Expo app, the correct UX after `changeTariffMutation` is:
1. Call `invalidateAll()` (invalidate auth, account, catalog, notifications, payments, billing) so the client refreshes the profile.
2. Surface `next_tariff_name` in the UI — show a small indicator such as `→ Супер Лайт` beneath the current tariff name, making it clear the change has been queued.

## Code delta
- **Removed:** `credentials` state from `lib/auth-store.ts` (used only for relogin hack).
- **Removed:** credential saving in `hooks/api/auth.ts` `useLogin.onSuccess`.
- **Removed:** relogin logic inside `hooks/api/catalog.ts` `useChangeTariff.onSuccess`.
- **Added:** `next_tariff_name?: string` to `api/types.ts` `ProfileTariff` interface.
- **Added:** `nextTariffName` prop to `TariffRow` component in `app/(tabs)/service.tsx`.

## Verification script
`scripts/test-api-change.mjs` was created to DRY-RUN and execute the full flow (login → tariff list → change → profile poll with relogin). It confirmed that the active tariff stayed old even after relogin, proving deferred application.
