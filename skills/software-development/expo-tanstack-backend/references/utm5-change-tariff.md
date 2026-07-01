# UTM5 Change Tariff — Correct Payload & Common Pitfalls

Endpoint: `POST /customer_api/auth/tariffs`

## Request body (exact)

```json
{
  "tariff_link_id": 10059,
  "account_id": 16590,
  "next_tariff_id": 498
}
```

| Field | Source | Notes |
|-------|--------|-------|
| `tariff_link_id` | `AccountTariff.tariff_link_id` from `/auth/profile` | NOT `tariff.id`. This is the *subscription link* between account and current tariff. |
| `account_id` | `Account.id` | Same as `basic_account` in profile root. |
| `next_tariff_id` | `Tariff.id` from `/auth/tariffs` catalogue | The NEW tariff to switch to. |

## Common errors

### `id=0 не найден` (or similar "not found")
**Cause:** Sending `tariff_id` instead of `tariff_link_id`, or omitting `next_tariff_id`.

**Wrong:**
```json
{ "account_id": 16590, "tariff_id": 498 }
```

**Right:**
```json
{ "tariff_link_id": 10059, "account_id": 16590, "next_tariff_id": 498 }
```

## Profile → modal state mapping

When opening a tariff-change modal, capture **both** `tariff.id` (for UI selection) and `tariff.tariff_link_id` (for API call):

```tsx
const [activeTariffLinkId, setActiveTariffLinkId] = useState<number | null>(null);

const openTariffModal = (currentTariffId?: number) => {
  const current = account?.tariffs?.find((t) => t.id === currentTariffId);
  setSelectedTariff(current || null);
  setActiveTariffLinkId(current?.tariff_link_id ?? null); // ← captured here
  setTariffModalVisible(true);
};

const confirmTariffChange = (tariff: Tariff) => {
  if (!account || activeTariffLinkId == null) return;
  changeTariffMutation.mutate({
    account_id: account.id,
    tariff_link_id: activeTariffLinkId,
    next_tariff_id: tariff.id,
  });
};
```

## GET /auth/tariffs response shape

```json
[
  { "id": 498, "name": "Супер Лайт", "comments": "", "cost": "799", "group_id": 3 }
]
```

**Gotchas:**
- `cost` is a **string** (`"799"`), not a number. Parse with `parseFloat`.
- Field is `comments` (plural), not `comment`. Map to your internal `Tariff.comment` field.

## Test with curl

```bash
# 1. Login
SID=$(curl -s -X POST "https://lk.liga-link.net/customer_api/login" \
  -H "Content-Type: application/json" \
  -d '{"login":"16590","password":"PASS","mobile_telephone":""}' \
  | grep -o '"sid_customer":"[^"]*"' | cut -d'"' -f4)

# 2. Get profile → extract tariff_link_id and account_id
curl -s "https://lk.liga-link.net/customer_api/auth/profile" \
  -H "Cookie: sid_customer=$SID"

# 3. Get tariff list → pick next_tariff_id
curl -s "https://lk.liga-link.net/customer_api/auth/tariffs" \
  -H "Cookie: sid_customer=$SID"

# 4. Change tariff
curl -s -X POST "https://lk.liga-link.net/customer_api/auth/tariffs" \
  -H "Cookie: sid_customer=$SID" \
  -H "Content-Type: application/json" \
  -d '{"tariff_link_id":10059,"account_id":16590,"next_tariff_id":498}'
```

## UI Refresh After Tariff Change — Common Bug

**Symptom:** After `POST /auth/tariffs` succeeds, the service screen still shows the OLD tariff name/price.

**Root cause:** TanStack Query cache holds stale `profile` and `account` data. A simple `invalidateQueries` is often too slow — the UI reads the old cached value before the refetch completes.

## FIX — invalidate broad cache keys immediately

```ts
export function useChangeTariff() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: changeTariff,
    onSuccess: () => {
      // Invalidate every bucket the screen touches
      qc.invalidateQueries({ queryKey: ['auth'] });
      qc.invalidateQueries({ queryKey: ['account'] });
      qc.invalidateQueries({ queryKey: ['catalog'] });
      // Force immediate refetch before the next paint
      qc.refetchQueries({ queryKey: ['auth', 'profile'] });
      qc.refetchQueries({ queryKey: ['account', 'links'] });
    },
  });
}
```

**Why `refetchQueries`:** `invalidateQueries` only *marks* cache stale. The component may repaint once more with old data before the background refetch lands. `refetchQueries` fires the request immediately.

---

## FIX — Server-Side Cache Busting via Auto-Logout+Login (UTM5 / legacy APIs)

**Symptom:** Even after invalidating the client cache and force-refetching, `/auth/profile` still returns the **old tariff**.

**Root cause:** The server itself caches the subscriber profile (sometimes 30–60 seconds). The same `sid_customer` session cookie hits a warm server-side cache.

**Solution:** After a successful mutation, perform an **invisible logout+login cycle** to obtain a fresh `sid_customer`, then re-fetch.

### Architecture changes

**1. Save credentials in the auth store (volatile, RAM only):**

```ts
// lib/auth-store.ts
interface Credentials { login: string; password: string; }

export const useAuthStore = create<AuthState>((set) => ({
  // ... existing state ...
  credentials: null as Credentials | null,
  setCredentials: (creds) => set({ credentials: creds }),
}));
```

**2. Capture credentials on login:**

```ts
// hooks/api/auth.ts
export function useLogin() {
  const setToken = useAuthStore((s) => s.setToken);
  const setCredentials = useAuthStore((s) => s.setCredentials);

  return useMutation({
    mutationFn: login,
    onSuccess: async (data, variables) => {
      setCredentials({
        login: variables.login,
        password: variables.password,
      });
      const sid = data?.sid_customer || data?.token || '';
      if (sid) await setToken(sid);
    },
  });
}
```

**3. Perform logout+login inside `useChangeTariff`:**

```ts
// hooks/api/catalog.ts
import { login as apiLogin, logout as apiLogout } from '@/api/services/auth';

export function useChangeTariff() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: changeTariff,
    onSuccess: async () => {
      // 1. Invalidate client cache
      qc.invalidateQueries({ queryKey: ['auth'] });
      qc.invalidateQueries({ queryKey: ['account'] });
      qc.invalidateQueries({ queryKey: ['catalog'] });

      // 2. 🔧 Server cache busting: new session = fresh data
      const creds = useAuthStore.getState().credentials;
      if (creds) {
        try { await apiLogout(); } catch { /* silent */ }
        try {
          const data = await apiLogin({
            ...creds,
            mobile_telephone: '',
          });
          const sid = data?.sid_customer || data?.token || '';
          if (sid) await useAuthStore.getState().setToken(sid);
        } catch { /* keep old sid if relogin fails */ }
      }

      // 3. Second-round invalidation after new sid
      qc.invalidateQueries({ queryKey: ['auth'] });
      qc.invalidateQueries({ queryKey: ['account'] });
      await qc.refetchQueries({
        queryKey: ['auth', 'profile'],
        type: 'active',
      });
    },
  });
}
```

**3. Second-round invalidation after new sid**

Wait, after the relogin, invalidate the client cache **again** — stale data may have accumulated during the relogin window.

```ts
// 4. Second-round invalidation
qc.invalidateQueries({ queryKey: queryKeys.auth.all });
qc.invalidateQueries({ queryKey: queryKeys.account.all });
await qc.refetchQueries({
  queryKey: queryKeys.auth.profile(),
  type: 'active',
});
```

**Why relogin is invisible to the user:**
- It happens inside `onSuccess`, after the user already saw the "success" state.
- The UI shows the tariff-change confirmation; the background relogin happens 1–2 seconds after the UI update.
- `isPending` stays true during the relogin, so the user sees a loading indicator.

**When NOT to use this:**
- Modern APIs with proper `ETag` / `Cache-Control: no-cache` — relogin is unnecessary overhead.
- APIs that return consistent data immediately after mutations (e.g. returns updated object in response body).
- APIs where logout invalidates unrelated concurrent sessions (e.g. WebSocket connections).

### Diagnostic script (Node.js)

Save as `scripts/test-tariff-change.mjs` and run with real credentials:

```js
#!/usr/bin/env node
const BASE = 'https://lk.liga-link.net/customer_api';
const [login, password] = process.argv.slice(2);

let sid = null;
async function api(method, path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(sid ? { Cookie: `sid_customer=${sid}` } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  const txt = await res.text();
  // extract new sid from Set-Cookie (web) or body JSON (RN mock)
  const sc = res.headers.get('set-cookie');
  if (sc) { const m = sc.match(/sid_customer=([^;]+)/); if (m) sid = m[1]; }
  if (txt && path.includes('/login')) {
    const j = JSON.parse(txt);
    if (j.sid_customer) sid = j.sid_customer;
  }
  return txt ? JSON.parse(txt) : undefined;
}

(async () => {
  if (!login) { console.error('Usage: node test-tariff-change.mjs <login> <password>'); process.exit(1); }

  await api('POST', '/login', { login, password, mobile_telephone: '' });
  const before = await api('GET', '/auth/profile');
  const tariffs = (before.accounts?.[0]?.tariffs || []).map(t => `${t.id}`).join(',');
  console.log('Before:', tariffs);

  // Pick first alternative tariff
  const all = await api('GET', '/auth/tariffs');
  const currentIds = new Set((before.accounts?.[0]?.tariffs || []).map(t => t.id));
  const alt = all.find(t => !currentIds.has(t.id));
  if (!alt) { console.log('No alternative tariff'); process.exit(0); }

  const account = before.accounts[0];
  const linkId = account.tariffs[0]?.tariff_link_id;
  await api('POST', '/auth/tariffs', {
    account_id: account.id,
    tariff_link_id: linkId,
    next_tariff_id: alt.id,
  });

  const afterSameSid = await api('GET', '/auth/profile');
  const t2 = (afterSameSid.accounts?.[0]?.tariffs || []).map(t => `${t.id}`).join(',');
  console.log('After same SID:', t2, t2 === tariffs ? '(STALE!)' : '(ok)');

  // Relogin with same credentials
  sid = null;
  await api('POST', '/login', { login, password, mobile_telephone: '' });
  const afterRelogin = await api('GET', '/auth/profile');
  const t3 = (afterRelogin.accounts?.[0]?.tariffs || []).map(t => `${t.id}`).join(',');
  console.log('After relogin:', t3, t3 === tariffs ? '(STALE!)' : '(ok)');
})();
```

Run with `node scripts/test-tariff-change.mjs LOGIN PASS`.

If `After same SID` shows `(STALE!)` but `After relogin` shows `(ok)`, the fix is confirmed.

---

## Deferred Tariff Change (UTM5 5.5-032) — `next_tariff_name`

### Discovery
After `POST /auth/tariffs` returns `{"result":"OK"}`, `GET /auth/profile` still shows the old tariff. This is **not** a cache bug — UTM5 applies tariff changes **deferred**, at the beginning of the next billing period.

### Profile response shape
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

The field `next_tariff_name` tells the user which tariff will become active next. **Do not implement relogin hacks** to "fix" this — they don't help and only add latency/flakiness.

### TypeScript — add `next_tariff_name`
```ts
export interface ProfileTariff {
  id: number;
  name: string;
  next_tariff_name?: string;   // ← add this
  tariff_link_id: number;
  account_id: number;
}
```

### UI — show planned change
Render the current tariff card and overlay/placement a hint:
```tsx
const current = account?.tariffs?.[0];
// Card shows: "Супер" 629 ₽
// If next_tariff_name exists, show → "Супер Лайт" (starts next period)
```

---

## When simple invalidate works vs when relogin is required

| API behaviour | Client-only fix | Relogin fix |
|---------------|----------------|-------------|
| Mutation returns updated object in body | ✅ read from response | unnecessary |
| `GET /profile` returns latest data after mutation | ✅ invalidate + refetch | unnecessary |
| `GET /profile` returns stale data for 10–60s after mutation | ❌ client fix fails | ✅ relogin |
| Server returns `next_tariff_name` (deferred change) | ✅ show `next_tariff_name` | unnecessary — relogin won't help |

**Golden rule:** Before implementing server cache busting, inspect the raw profile JSON after mutation. If `next_tariff_name` is present, the server is already working correctly — just surface that field in the UI.

---

## staleTime tuning for catalog data

`GET /auth/tariffs` and `GET /auth/services` are reference catalog data — they change once per marketing cycle, not once per minute. Set a longer staleTime to avoid unnecessary refetches:

```ts
export function useTariffs() {
  return useQuery({
    queryKey: queryKeys.catalog.tariffs(),
    queryFn: getTariffs,
    staleTime: 3 * 60_000, // 3 minutes (was 15 seconds)
    initialData: [],
  });
}

export function useServiceLinks() {
  return useQuery({
    queryKey: queryKeys.account.links(),
    queryFn: getServiceLinks,
    staleTime: 30_000, // 30 seconds — links change on connect/disconnect
    initialData: [],
  });
}
```

| Data type | Recommended staleTime | Reason |
|-----------|----------------------|--------|
| User profile | 5 min | Changes on balance update |
| Catalog (tariffs/services) | 3 min | Marketing-driven, rare |
| Service links | 30 sec | Change on connect/disconnect |
| Notifications | 1 min | Frequent updates |
| Billing stats | 5 min | Expensive query |

---

## Full mutation hook pattern (all mutations)

Use a shared `invalidateAll` helper to avoid copy-paste invalidation lists:

```ts
function invalidateAll(qc: ReturnType<typeof useQueryClient>) {
  qc.invalidateQueries({ queryKey: queryKeys.auth.all });
  qc.invalidateQueries({ queryKey: queryKeys.account.all });
  qc.invalidateQueries({ queryKey: queryKeys.catalog.all });
  qc.invalidateQueries({ queryKey: queryKeys.notifications.all });
  qc.invalidateQueries({ queryKey: queryKeys.payments.all });
  qc.invalidateQueries({ queryKey: queryKeys.billing.all });
}

export function useConnectService() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: connectService,
    onSuccess: () => invalidateAll(qc),
  });
}

export function useDisconnectService() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: disconnectService,
    onSuccess: () => invalidateAll(qc),
  });
}
```

This is over-invalidation (some buckets refresh unnecessarily) but avoids stale-data bugs. When performance matters, invalidate only the specific keys the mutation affects.

