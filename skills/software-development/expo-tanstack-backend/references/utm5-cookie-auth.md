# UTM5 /customer_api Cookie-Based Auth

## Context

UTM5 subscriber REST API uses **cookie auth**:
- `POST /login` → server returns `Set-Cookie: sid_customer=...
- All subsequent requests must send `Cookie: sid_customer=...`

## CORS and platform trap

**Expo Web** (`localhost:8081`) will **never** work if the backend does not send
`Access-Control-Allow-Origin` + `Access-Control-Allow-Credentials: true`.
Browsers block the response before JavaScript can read `Set-Cookie`.

**Python `httpx`** works because it operates at TCP level without CORS enforcement.

**Rule:** Always test cookie-based login on a **real device or emulator**:

```bash
npx expo start --android   # or --ios
```

On real devices, `fetch` talks directly to the server — no CORS mediation.

## Session storage: persistent vs volatile

Typical apps want **persistent** login across restarts — save `sid_customer` to `AsyncStorage` or `expo-secure-store`. Some apps (e.g. customer portals with shared devices) require **volatile** sessions that die when the app closes.

### Persistent (default)
```ts
import AsyncStorage from '@react-native-async-storage/async-storage';
export async function setSessionId(sid: string) { AsyncStorage.setItem('sid', sid); }
export async function getSessionId() { return AsyncStorage.getItem('sid'); }
```

### Volatile (in-memory only)
```ts
let inMemorySid: string | null = null;
export async function setSessionId(sid: string) { inMemorySid = sid; }
export async function getSessionId() { return inMemorySid; }
// Closing the app wipes the session; user must re-login.
```

```ts
import { Platform } from 'react-native';
const isWeb = Platform.OS === 'web';

async function request(method: string, url: string, body?: Record<string, unknown>) {
  const sid = await getSessionId(); // AsyncStorage

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (!isWeb && sid) {
    headers['Cookie'] = `sid_customer=${sid}`;
  }

  const response = await fetch(`${BASE_URL}${url}`, {
    method,
    headers,
    credentials: 'include', // ignored on RN, needed on Web
    ...(body ? { body: JSON.stringify(body) } : {}),
  });

  // --- Extract session after login ---
  if (url.includes('/login') && !url.includes('/logout')) {
    if (!isWeb) {
      // RN fetch may hide Set-Cookie header → parse JSON body as fallback
      const cloned = response.clone();
      try {
        const bodyJson = await cloned.json();
        if (bodyJson?.sid_customer) {
          await setSessionId(bodyJson.sid_customer);
        } else if (bodyJson?.token) {
          await setSessionId(bodyJson.token);
        }
      } catch { /* body not JSON */ }
    } else {
      // Web: browser handles cookies automatically
      const setCookie = response.headers.get('set-cookie');
      if (setCookie) {
        const match = setCookie.match(/sid_customer=([^;]+)/);
        if (match) await setSessionId(match[1]);
      }
    }
  }

  // --- Clear on auth errors ---
  if (response.status === 401 || response.status === 403) {
    await removeSessionId();
  }

  // ... error handling + return
}
```

## Login endpoint variants

UTM5 has multiple login endpoints:
- `POST /customer_api/login` — standard subscriber login
- `POST /customer_api/login_hotspot` — hotspot portal (may return empty body)

**Payload:** Always include `mobile_telephone: ""` even if not used:

```ts
client.post('/login', {
  login: '16590',
  password: '5f7d1356',
  mobile_telephone: '',
});
```

## Testing checklist

1. Run on **real device / emulator**, not Expo Web
2. Check Metro logs for `[API] sid_customer из body: ...`
3. If missing, the server doesn't return `sid_customer` in body — check `Set-Cookie` via proxy (Charles Proxy, mitmproxy)
4. Next authenticated request should succeed (e.g. `GET /auth/profile`)

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| `HTTP 401` on `/auth/profile` after login | `sid_customer` not saved or not sent | Verify `getSessionId()` returns value; check `Cookie` header in request |
| `CORS` preflight `OPTIONS` fails in Web | Server lacks `Access-Control-Allow-Origin` | Test on real device |
| `Query data cannot be undefined` | Server returns empty body `204` | Add `|| []` fallback in service functions |
| Metro warning persists after fix | Old bundle cached | `npx expo start --clear` |
