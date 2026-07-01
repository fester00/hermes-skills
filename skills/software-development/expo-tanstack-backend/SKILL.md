---
name: expo-tanstack-backend
title: Expo + TanStack Query Backend Integration
description: |
  Complete architecture pattern for React Native Expo apps that consume a REST API
  via TanStack Query (React Query). Covers HTTP client with auth interceptors,
  service-layer organization, Zustand auth store, QueryProvider setup, custom hooks
  for queries and mutations, and AuthGuard routing with protected tabs.
trigger: |
  When building or refactoring a React Native Expo app that needs to fetch data
  from a REST API, uses or should use TanStack Query, requires login or auth
  flow, or needs a service-layer architecture to organize API calls.
prerequisites:
  - "Expo SDK 50+"
  - "@tanstack/react-query installed"
  - "Zustand (optional, for auth state)"
  - "@react-native-async-storage/async-storage or expo-secure-store"
---

# Expo + TanStack Query Backend Integration

## When to use this skill

Any Expo React Native project that:
- Calls a REST API (not just GraphQL)
- Needs auth tokens sent on requests
- Benefits from caching and stale-while-revalidate
- Has multiple screens sharing server data
- Needs login to main app flow

## Project structure

```
├── api/
│   ├── client.ts              # HTTP client: fetch + interceptors + error class
│   ├── endpoints.ts           # URL constants only
│   ├── types.ts               # All API DTOs / interfaces
│   ├── query-keys.ts          # Centralised query-key factory (prevents stale bugs)
│   └── services/
│       ├── index.ts           # Barrel export: export * from './auth', './user' ...
│       ├── auth.ts            # login(credentials)
│       ├── profile.ts         # getProfile, updateProfile
│       ├── account.ts         # getAccounts, getBalance
│       ├── catalog.ts         # getTariffs, getServices
│       ├── user-services.ts   # connect/disconnect/changeTariff (actions on user data)
│       ├── payment.ts         # getPaymentHistory, makePayment
│       └── notification.ts    # getNotifications, updatePolicy
├── lib/
│   ├── storage.ts             # getToken / setToken / removeToken
│   └── auth-store.ts          # Zustand store: token, isAuthenticated, logout
├── providers/
│   └── QueryProvider.tsx      # QueryClientProvider + session restore + global 401 handler
├── hooks/
│   └── api/                   # OR queries.ts — split by domain when >200 lines
│       ├── auth.ts
│       ├── profile.ts
│       ├── catalog.ts
│       ├── notifications.ts
│       └── payments.ts
├── app/
│   ├── _layout.tsx            # AuthGuard wraps Stack; redirects login <-> tabs
│   ├── login.tsx              # Login screen
│   └── (tabs)/
│       ├── index.tsx
│       ├── profile.tsx
│       └── other screens
```

> **Organise by domain, not by auth flag.** All files under `api/services/` are authorised — the client injects the session cookie/token automatically. Split by domain (`profile`, `payment`, `catalog`) so that each file owns one bounded context.
>

## 1. HTTP Client (api/client.ts)

```ts
import { getToken } from '@/lib/storage';

export const BASE_URL = 'https://api.example.com/v1';

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request<T>(
  method: string,
  url: string,
  body?: Record<string, unknown>,
) {
  const token = await getToken();
  const response = await fetch(`${BASE_URL}${url}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });

  if (!response.ok) {
    let msg = `HTTP ${response.status}`;
    try { msg = (await response.json())?.message || msg; } catch { /* not JSON */ }
    throw new ApiError(msg, response.status);
  }

  const text = await response.text();
  return text ? JSON.parse(text) : undefined;
}

export const client = {
  get: <T>(url: string) => request<T>('GET', url),
  post: <T>(url: string, body?: Record<string, unknown>) =>
    request<T>('POST', url, body),
  put: <T>(url: string, body?: Record<string, unknown>) =>
    request<T>('PUT', url, body),
  delete: <T>(url: string) => request<T>('DELETE', url),
};
```

### Pitfall: payload casts
TypeScript rejects `credentials as Record<string, unknown>` when the interface lacks an index signature. Use `as unknown as Record<string, unknown>` in service functions that wrap `client.post`.

---

## 1a. Query-key factory (api/query-keys.ts)

Instead of scattering raw strings (`'profile'`, `'balance'`) across 20 hooks, use a single factory:

```ts
export const queryKeys = {
  auth: {
    all: ['auth'] as const,
    profile: () => [...queryKeys.auth.all, 'profile'] as const,
    v2:    () => [...queryKeys.auth.all, 'v2'] as const,
  },
  account: {
    all: ['account'] as const,
    balance: () => [...queryKeys.account.all, 'balance'] as const,
    services: (accountId?: number) =>
      [...queryKeys.account.all, 'services', accountId] as const,
  },
  catalog: {
    all: ['catalog'] as const,
    services: () => [...queryKeys.catalog.all, 'services'] as const,
    tariffs:  () => [...queryKeys.catalog.all, 'tariffs'] as const,
  },
  billing: {
    all: ['billing'] as const,
    stats: () => [...queryKeys.billing.all, 'stats'] as const,
    full:  () => [...queryKeys.billing.all, 'full'] as const,
  },
  notifications: {
    all: ['notifications'] as const,
    list:   () => [...queryKeys.notifications.all, 'list'] as const,
    policy: () => [...queryKeys.notifications.all, 'policy'] as const,
  },
  payments: {
    all: ['payments'] as const,
    required: () => [...queryKeys.payments.all, 'required'] as const,
    min:      () => [...queryKeys.payments.all, 'min'] as const,
  },
} as const;
```

**Why:** When you need to invalidate the entire account slice, call `qc.invalidateQueries({ queryKey: queryKeys.account.all })` and every balance, service and child query refreshes automatically. No orphaned stale data.

### Pitfall: circular imports
Keep `query-keys.ts` free of runtime imports (export only const objects). Do NOT import functions from `api/services/` or `hooks/` into this file or you will create circular dependencies.

## 2. Endpoints (api/endpoints.ts)

Keep URL strings only, no logic. Use `as const` for strict typing:

```ts
export const ENDPOINTS = {
  auth: { login: '/login' },
  user: { getUser: '/users', getAccounts: '/users/accounts' },
  customer: { changeTariff: '/customer/tarifflinks' },
} as const;
```

## 3. Services (api/services/*.ts)

One domain per file. Each exports async functions that call `client.get/post/put/delete`.

```ts
import { ENDPOINTS } from '../endpoints';
import { client } from '../client';
import type { User, Account } from '../types';

export async function getUser(): Promise<User> {
  return client.get<User>(ENDPOINTS.user.getUser);
}
```

### Barrel export (api/services/index.ts)

Add an `index.ts` so screens can import from a single entry:

```ts
export * from './auth';
export * from './profile';
export * from './account';
export * from './catalog';
export * from './user-services';
export * from './notifications';
export * from './payments';
```

Usage in hooks or screens:

```ts
import { getProfile, getBalance, getServices } from '@/api/services';
```


## 4. Token Storage (lib/storage.ts)

Try `expo-secure-store` first, fallback to `@react-native-async-storage/async-storage`:

```ts
let secureStore: typeof import('expo-secure-store') | null = null;
try { secureStore = require('expo-secure-store'); } catch { /* no-op */ }

export async function getToken(): Promise<string | null> { /* ... */ }
export async function setToken(token: string): Promise<void> { /* ... */ }
export async function removeToken(): Promise<void> { /* ... */ }
```

## 5. Auth Store (lib/auth-store.ts)

Use Zustand for global auth state; persist token to storage.

```ts
import { create } from 'zustand';
import { setToken, removeToken, getToken } from './storage';

interface AuthState {
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  setToken: (t: string) => Promise<void>;
  logout: () => Promise<void>;
  restoreSession: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null, isLoading: true, isAuthenticated: false,
  setToken: async (token) => { await setToken(token); set({ token, isAuthenticated: true, isLoading: false }); },
  logout: async () => { await removeToken(); set({ token: null, isAuthenticated: false }); },
  restoreSession: async () => {
    const token = await getToken();
    set({ token, isAuthenticated: !!token, isLoading: false });
  },
}));
```

## 6. QueryProvider (providers/QueryProvider.tsx)

```ts
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from '@/lib/auth-store';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 1000 * 60 * 2, refetchOnWindowFocus: false, retry: 1 },
    mutations: { retry: 0 },
  },
});

export default function QueryProvider({ children }: { children: React.ReactNode }) {
  const restoreSession = useAuthStore((s) => s.restoreSession);
  useEffect(() => { restoreSession(); }, [restoreSession]);
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
```

## 7. Hooks — split by domain when >200 lines

If the app has ≤6 queries, keep them in one `hooks/queries.ts`. Once the file passes ~200 lines, split by domain into `hooks/api/*.ts`:

```
hooks/
├── api/
│   ├── auth.ts           # useLogin, useLogout
│   ├── profile.ts        # useProfile, useUpdateProfile
│   ├── catalog.ts        # useServices, useServiceLinks, useConnectService
│   ├── billing.ts        # useStatistics, useFullStatistics
│   ├── notifications.ts  # useNotifications, useUpdatePolicy
│   └── payments.ts       # useMakePayment, usePromisedPayment
```

Each hook file imports from `@/api/services` and `@/api/query-keys` only.

**Example** — `hooks/api/profile.ts`:

```ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getProfile, updateProfile } from '@/api/services';
import { queryKeys } from '@/api/query-keys';

export function useProfile() {
  return useQuery({
    queryKey: queryKeys.auth.profile(),
    queryFn: getProfile,
    staleTime: 1000 * 60 * 2,
  });
}

export function useUpdateProfile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: updateProfile,
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.auth.all }),
  });
}
```

### Mutation pattern
Always attach `onSuccess` invalidation so stale local data gets refetched:

```ts
onSuccess: () => {
  queryClient.invalidateQueries({ queryKey: ['balance'] });
}
```

### Global 401 / logout handler

Configure `QueryClient` once in the provider so every query and mutation shares the same 401 logic:

```tsx
// providers/QueryProvider.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from '@/lib/auth-store';

function createQueryClient() {
  const logout = useAuthStore.getState().logout;

  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 30,
        retry: (failureCount, error: any) => {
          if (error?.status === 401) return false;
          return failureCount < 2;
        },
      },
      mutations: {
        retry: 0,
        onError: (error: any) => {
          if (error?.status === 401) logout();
        },
      },
    },
  });
}

export default function QueryProvider({ children }: { children: React.ReactNode }) {
  const [client] = useState(() => createQueryClient());
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
```

### Why split hooks by domain
- Single `queries.ts` with 15+ hooks becomes a merge-conflict magnet in teams.
- `useQuery` keys are scattered → easy to mismatch invalidate keys.
- Import size matters for lazy-loaded tabs.
- Aligns with `api/services/*` split: one domain, one service file, one hook file.


## 8. AuthGuard (app/_layout.tsx)

Wrap the Stack with a component that redirects based on auth state:

```ts
function AuthGuard({ children }: { children: React.ReactNode }) {
  const segments = useSegments();
  const router = useRouter();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);

  useEffect(() => {
    if (isLoading) return;
    const atLogin = segments[0] === 'login';
    if (!isAuthenticated && !atLogin) router.replace('/login');
    else if (isAuthenticated && atLogin) router.replace('/(tabs)');
  }, [isAuthenticated, isLoading, segments, router]);

  return <>{children}</>;
}
```

Wrap the expo-router Stack:

```tsx
<QueryProvider>
  <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
    <AuthGuard>
      <Stack>
        <Stack.Screen name="login" options={{ headerShown: false }} />
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      </Stack>
    </AuthGuard>
  </ThemeProvider>
</QueryProvider>
```

## 9. Scroll Components (User Preference)

Do NOT create one shared Scroll component for all screens. Each screen gets its own scroll container optimized for its layout.

| Screen layout | Scroll strategy |
|---------------|-----------------|
| Static blocks plus 1 FlatList | FlatList as root or ScrollView wrapping the FlatList |
| Long form (profile) | ScrollView with contentContainerStyle |
| List of items | FlatList (not ScrollView with .map) |
| Calendar plus modal | ScrollView for screen, modal has its own container |

**Rule**: Never nest a ScrollView inside another ScrollView or FlatList unless one has `scrollEnabled={false}`.

### VirtualizedList nesting warning

React Native throws: `VirtualizedLists should never be nested inside plain ScrollViews with the same orientation`. This happens whenever a `FlatList` (or any `VirtualizedList`) is placed inside a parent `ScrollView`.

**Fix — use plain `View` + `.map()` (no ScrollView at all):**

When the parent `ScrollView` already handles scrolling, never wrap a list in a child `ScrollView` — even with `scrollEnabled={false}` some RN versions still warn. Simply use a `View` and render items with `.map()`.

```tsx
<View style={{ paddingHorizontal: 4 }}>
  {notices.map((item, index) => (
    <View key={`notice-${index}`} style={{ marginBottom: 10 }}>
      <Text>{item.date}</Text>
      <Text>{item.text}</Text>
    </View>
  ))}
</View>
```

> This is acceptable for lists under ~30 items. For longer lists, make the `FlatList` the root scroll container of the screen (use `ListHeaderComponent` for static content above the list).

## 10. Query functions must never return `undefined`

TanStack Query throws `Query data cannot be undefined` if the `queryFn` returns `undefined`. This often happens when:
- The API returns an empty body (`204 No Content`)
- The `client.get` helper returns `undefined` for an empty response
- The server responds with `null` but TypeScript types declare an array

### CRITICAL PITFALL: `await` before the fallback

`client.get()` returns a `Promise`. A `Promise` is always truthy, so `client.get() || []` **never falls through** — it returns the Promise itself, not the resolved array.

**Wrong (will still throw `undefined`):**
```ts
export async function getNotifications(): Promise<NotificationMessage[]> {
  return client.get<NotificationMessage[]>(ENDPOINTS.notifications.list) || [];
}
```

**Correct:**
```ts
export async function getNotifications(): Promise<NotificationMessage[]> {
  return (await client.get<NotificationMessage[]>(ENDPOINTS.notifications.list)) || [];
}
```

Apply `await` + `|| []` to every service function whose return type is an array. Use `??` (nullish coalescing) instead of `||` if empty arrays `""` or `0` could be valid responses.

### Secondary defence: `initialData` in hooks

Even with the fix above, stale TanStack Query cache might contain `undefined` from an earlier broken version of the service. Add `initialData` to array-returning `useQuery` hooks:

```ts
export function useNotifications() {
  return useQuery({
    queryKey: queryKeys.notifications.list(),
    queryFn: getNotifications,
    staleTime: 1000 * 60 * 3,
    initialData: [],          // ← prevents undefined flash on first render
  });
}
```

For non-array types, return a minimal valid object, `null` wrapped in a discriminated union, or set `initialData` to a sensible default.

`useColorScheme()` can return `'unspecified'`. Add an index signature to `Colors`:

```ts
export const Colors: Record<string, { text: string; /* ... */ }> = {
  light: { /* ... */ },
  dark: { /* ... */ },
};
```

Then use `Colors[colorScheme ?? 'light']` safely everywhere.

## 13. Keyboard + Tab-Bar Overlap (Text-Input Screens)

When a screen contains many text inputs (e.g. profile editing), the system keyboard slides up and two things break:
1. **Tab bar floats on top of the keyboard** — covers the focused input
2. **Input sits behind the keyboard** — user can't see what they're typing

### Fix: `tabBarHideOnKeyboard` + `KeyboardAvoidingView`

In `app/(tabs)/_layout.tsx` — hide the tab bar when any text input is focused:

```tsx
<Tabs
  screenOptions={{
    tabBarHideOnKeyboard: true,  // ← hides tab bar when keyboard opens
    tabBarActiveTintColor: '#fff',
    tabBarInactiveTintColor: 'rgba(255,255,255,0.7)',
    tabBarStyle: { backgroundColor: 'transparent', borderTopWidth: 0, height: 64 },
  }}
>
```

In the text-input screen (`profile.tsx`) — wrap content in `KeyboardAvoidingView`:

```tsx
import { KeyboardAvoidingView, Platform, ScrollView } from 'react-native';

<KeyboardAvoidingView
  behavior={Platform.OS === 'ios' ? 'padding' : undefined}
  style={{ flex: 1, backgroundColor: colors.background }}
  keyboardVerticalOffset={Platform.OS === 'ios' ? 64 : 0}
>
  <ScrollView
    contentContainerStyle={styles.scrollContent}
    keyboardShouldPersistTaps="handled"
  >
    {/* all TextInputs */}
  </ScrollView>
</KeyboardAvoidingView>
```

**Why both are needed:**
- `tabBarHideOnKeyboard` removes the 64px tab bar that would otherwise cover the bottom half of the screen
- `KeyboardAvoidingView` pushes the ScrollView content up so the focused input stays visible above the keyboard
- `keyboardShouldPersistTaps="handled"` lets the user tap "Save" or other buttons without dismissing the keyboard first

On Android, `KeyboardAvoidingView` behavior is less reliable than on iOS. If inputs are still hidden, add `android:windowSoftInputMode="adjustPan"` in `AndroidManifest.xml` (or use `expo-build-properties` plugin).

---

## 14. Dynamic Theme Colors: StyleSheet vs Inline

A common bug: hard-coding a background color in `StyleSheet.create()` that doesn't adapt to light/dark theme:

**Wrong:**
```ts
const styles = StyleSheet.create({
  baseInput: {
    paddingVertical: 8,
    paddingHorizontal: 10,
    borderRadius: 8,
    fontSize: 15,
    backgroundColor: '#ededed',  // ← never changes for dark mode
  },
});
```

**Correct:** Move the dynamic color into the inline style applied at render time:

```ts
function BInput({ style, editMode, ...rest }: BInputProps) {
  const colors = Colors[useColorScheme() ?? 'light'];

  return (
    <TextInput
      style={[
        styles.baseInput,               // static styles (padding, borderRadius)
        { color: colors.text, backgroundColor: colors.subBackground },  // dynamic
        editMode && { borderColor: colors.accent, borderWidth: 2 },
        style,
      ]}
      {...rest}
    />
  );
}

const styles = StyleSheet.create({
  baseInput: {
    paddingVertical: 8,
    paddingHorizontal: 10,
    borderRadius: 8,
    fontSize: 15,
    // NO backgroundColor here — it is applied inline
  },
});
```

**Rule:** Anything that changes with `colorScheme` must be in the inline `style={[]}` array, never in `StyleSheet.create()`. Static layout values (padding, margin, flex, borderRadius) stay in StyleSheet for performance.

---

## 15. Useful staleTime defaults

| Data | staleTime |
|------|-----------|
| User profile | 5 min |
| Account balance | 1 min |
| Notifications | 3 min |
| Payment history | 3 min |
| Tariffs list | 60 min |
| Services list | 30 min |

---

## 16. Type-mismatch debugging checklist

When the TypeScript compiler or runtime throws `undefined is not an object` on API data, walk through:

1. **Does `api/types.ts` match the actual response?**
   - Open the real JSON response in browser DevTools or a curl call.
   - Compare field names: API may return `service_name` while types say `name`.
   - Capitalisation matters: `user_id` vs `userId`.

2. **Does the hook use the right query key?**
   - Mismatch: `queryKey: ['profile']` in hook but `invalidateQueries({ queryKey: ['user'] })` in mutation.
   - Fix: use `queryKeys.auth.profile()` everywhere.

3. **Does the UI guard against `undefined`?**
   - `mainAccount?.balance` is safe; `mainAccount.balance` crashes if `accounts` is empty.
   - Always default: `balance = mainAccount?.balance ?? profile?.balance ?? 0`.

4. **Does the service function return the right shape?**
   - Some endpoints wrap the payload in an object: `{ data: { user: { ... } } }`.
   - Add intermediate type or unwrap in the service function before returning.

5. **Is there a stale cache from an old `queries.ts`?**
   - Run `npx expo start --clear` or reset the QueryClient cache during dev.

**Frequent field mismatches** (UTM5 / custom REST APIs):
- `name` ↔ `service_name`, `title`, `tariff_name`
- `cost` ↔ `price`, `amount`
- `id` ↔ `service_id`, `slink_id`, `tariff_link_id`
- `balance` in root ↔ nested inside `accounts[0].balance`
- Timestamps: seconds vs milliseconds vs ISO strings

When in doubt, log the full response first, then model the type.

---

## 16. Cookie-based Authentication (when API uses `sid_customer`)

Some APIs (e.g. UTM5 /customer_api) use **cookie auth** — `POST /login` returns `Set-Cookie: sid_customer=...` and all subsequent requests must send `Cookie: sid_customer=...`. React Native `fetch` does **not** persist cookies automatically, unlike a browser.

### CORS and platform differences: Expo Web vs. real device

**Critical pitfall:** Testing cookie auth in **Expo Web** (`localhost:8081`) will fail if the backend does not send `Access-Control-Allow-Origin` and `Access-Control-Allow-Credentials: true`. The browser blocks the response before JavaScript can read `Set-Cookie`.

Python `httpx` or `requests` work because they operate at the TCP level and do not enforce CORS. Expo Web does not.

**Rule:** Always test cookie-based login on a **real device or emulator** (`npx expo start --android` / `--ios`), where `fetch` talks directly to the server without CORS mediation. Expo Web is fine only when the backend explicitly allows the dev origin.

### Cookie-aware client pattern (works on all platforms)

```ts
import { Platform } from 'react-native';
const isWeb = Platform.OS === 'web';

async function request<T>(method: string, url: string, body?: Record<string, unknown>) {
  const sid = await getSessionId(); // AsyncStorage-backed

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  // In RN we must send the cookie manually because fetch has no cookie jar.
  // In Web the browser handles cookies automatically (if CORS allows).
  if (!isWeb && sid) {
    headers['Cookie'] = `sid_customer=${sid}`;
  }

  const response = await fetch(`${BASE_URL}${url}`, {
    method,
    headers,
    credentials: 'include',               // ignored on RN, required on Web
    ...(body ? { body: JSON.stringify(body) } : {}),
  });

  // After login: extract the session id.
  // RN fetch may hide the Set-Cookie header, so parse the JSON body as fallback.
  if (url.includes('/login') && !url.includes('/logout')) {
    if (!isWeb) {
      const cloned = response.clone();
      try {
        const bodyJson = await cloned.json();
        if (bodyJson?.sid_customer) await setSessionId(bodyJson.sid_customer);
        else if (bodyJson?.token)    await setSessionId(bodyJson.token);
      } catch { /* body not JSON */ }
    } else {
      const setCookie = response.headers.get('set-cookie');
      if (setCookie) {
        const match = setCookie.match(/sid_customer=([^;]+)/);
        if (match) await setSessionId(match[1]);
      }
    }
  }

  // Clear local session on auth errors
  if (response.status === 401 || response.status === 403) {
    await removeSessionId();
  }
  // ... error handling and return JSON
}
```

### Why the fallback body-parsing matters
React Native implementations of `fetch` (via `whatwg-fetch` or the native networking layer) do **not** expose the `Set-Cookie` response header to JavaScript. The server may still return the session token inside the JSON payload. Always support both paths so the same client works in dev (Web) and production (RN).

### Login endpoint gotcha
UTM5 has both `/login` (universal) and `/login_hotspot`. If `/login_hotspot` returns empty body, try `/login` with `mobile_telephone: ""` in the payload:

```ts
client.post('/login', { login, password, mobile_telephone: '' });
```

### Storage for cookie mode

```ts
export async function getSessionId(): Promise<string | null> { /* AsyncStorage */ }
export async function setSessionId(sid: string): Promise<void> { /* AsyncStorage */ }
export async function removeSessionId(): Promise<void> { /* AsyncStorage */ }
```

### Session restoration and the "skip login" bug

A common bug: when the app restarts, `restoreSession()` finds `sid_customer` in AsyncStorage and sets `isAuthenticated = true` immediately. But if the server session has expired (e.g. after 10 minutes of inactivity), the user lands on the profile screen and all API calls return 401.

**Fix — validate the token on restore:**

```ts
// In QueryProvider or an initialisation hook
async function restoreAndValidate() {
  const sid = await getSessionId();
  if (!sid) { set({ isAuthenticated: false, isLoading: false }); return; }

  try {
    // Hit a lightweight endpoint (e.g. /v3/auth or /auth/accounts)
    await client.post('/v3/auth');
    set({ token: sid, isAuthenticated: true, isLoading: false });
  } catch {
    await removeSessionId();
    set({ token: null, isAuthenticated: false, isLoading: false });
  }
}
```

**Alternative — 401 global handler in QueryClient:**

```ts
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error: any) => {
        if (error?.status === 401) {
          // Trigger logout and redirect
          useAuthStore.getState().logout();
          return false;
        }
        return failureCount < 2;
      },
    },
  },
});
```

Both approaches work; the first prevents the flash-of-unauthorized-screen, the second catches it gracefully.

### Server logout

Call `POST /logout` before clearing local state to invalidate the server-side session:

```ts
export async function logout(): Promise<unknown> {
  const result = await client.post('/logout');
  await removeSessionId();
  return result;
}
```

---

## 17. Pure Component + Parent-Level Filtering Pattern

When the same list component (e.g. notice list, payment history, transaction log) is reused across multiple screens with different filters, **keep the component pure** and let each parent manage its own filter state.

### Anti-pattern (don't do this)

```tsx
// NoticeList.tsx — component manages its own filter state
export default function NoticeList() {
  const [filter, setFilter] = useState('all');
  const { data } = useNotifications(); // fetches inside component
  const filtered = data?.filter(n => filter === 'all' || n.type === filter);
  return (
    <>
      <FilterBar selected={filter} onChange={setFilter} />
      <FlatList data={filtered} ... />
    </>
  );
}
```

Problems:
- Same component used on 3 screens → 3 identical filter UIs, can't customize per screen
- Hard to pre-filter data differently per screen (e.g. "last 5" vs "30 days")
- Component fetches its own data → can't share fetched data between screens without duplicate requests or complex props drilling

### Correct pattern

**1. Keep the list component pure — only render logic:**

```tsx
// components/NoticeList.tsx
interface Props {
  notices: Notice[];
  emptyText?: string;
}

export default function NoticeList({ notices, emptyText = 'Нет данных' }: Props) {
  if (!notices.length) return <EmptyState text={emptyText} />;

  return (
    <View style={{ paddingHorizontal: 4 }}>
      {notices.map((item, index) => (
        <NoticeCard key={`notice-${index}`} notice={item} />
      ))}
    </View>
  );
}
```

**2. Filter components are separate and reusable:**

```tsx
// components/NoticeFilterBar.tsx
interface Props {
  selected: NoticeCategory;
  onChange: (cat: NoticeCategory) => void;
}

export default function NoticeFilterBar({ selected, onChange }: Props) {
  const categories: { key: NoticeCategory; label: string }[] = [
    { key: 'all',     label: 'Все' },
    { key: 'payment', label: 'Платежи' },
    { key: 'block',   label: 'Блокировки' },
    { key: 'service', label: 'Услуги' },
    { key: 'system',  label: 'Системные' },
  ];

  return (
    <View style={{ flexDirection: 'row', gap: 8, marginBottom: 12 }}>
      {categories.map(cat => (
        <Chip
          key={cat.key}
          label={cat.label}
          selected={selected === cat.key}
          onPress={() => onChange(cat.key)}
        />
      ))}
    </View>
  );
}
```

**3. Each screen fetches and filters independently:**

```tsx
// app/(tabs)/index.tsx — home: last 5, no filter
export default function HomeScreen() {
  const { data: notices = [] } = useNotifications(last30DaysStart, today);
  const lastFive = notices.slice(0, 5);
  return <NoticeList notices={lastFive} emptyText="Нет уведомлений" />;
}

// app/(tabs)/phinance.tsx — payments + charges from statistics API
export default function FinanceScreen() {
  const { data: stats = [] } = useFullStatistics();
  const payments = stats.filter(s => s.paymentAmount > 0);
  const charges  = stats.filter(s => s.amount > 0);
  return (
    <ScrollView>
      <Section title="Пополнения">
        <NoticeList notices={payments.map(mapStatsToNotice)} />
      </Section>
      <Section title="Списания">
        <NoticeList notices={charges.map(mapStatsToNotice)} />
      </Section>
    </ScrollView>
  );
}

// app/(tabs)/notice.tsx — all notices with category filter + date range
export default function NoticeScreen() {
  const [period, setPeriod] = useState({ start: subDays(new Date(), 30), end: new Date() });
  const [category, setCategory] = useState<NoticeCategory>('all');
  const { data: notices = [] } = useNotifications(period.start, period.end);

  const filtered = category === 'all'
    ? notices
    : notices.filter(n => categorizeNotice(n) === category);

  return (
    <ScrollView>
      <NoticeFilterBar selected={category} onChange={setCategory} />
      <DateRangePicker value={period} onChange={setPeriod} />
      <NoticeList notices={filtered} emptyText="Уведомлений за период нет" />
    </ScrollView>
  );
}
```

**4. Mapping helpers live in `lib/`, not inside components:**

```ts
// lib/notices.ts
export function categorizeNotice(n: Notice): NoticeCategory {
  const t = n.text.toLowerCase();
  if (/платеж|оплат|пополн|коррекц|ревок/.test(t)) return 'payment';
  if (/блок|заблок|приост/.test(t))            return 'block';
  if (/тариф|услуг|интернет|подключ/.test(t))    return 'service';
  return 'system';
}

export function mapStatsEntryToNotice(entry: StatisticsEntry): Notice {
  return {
    id: String(entry.id),
    date: entry.paymentDate ?? entry.date ?? '',
    text: entry.comments?.[0] ?? entry.comment ?? '',
    category: entry.paymentAmount > 0 ? 'payment' : entry.amount > 0 ? 'block' : 'system',
    amount: entry.paymentAmount ?? entry.amount ?? 0,
  };
}
```

### Why this pattern wins

| Concern | Pure component | Self-contained component |
|---------|----------------|--------------------------|
| Reuse across screens | Easy — different data/filter per screen | Hard — same filter UI everywhere |
| Testability | High — pass array, assert render | Low — must mock API + user events |
| Cache efficiency | Parent chooses data source, TanStack Query dedupes | Each instance fetches independently |
| Screen-specific behaviour | Natural — slice, map, filter per screen | Props explosion or internal conditions |
**Related reference files:**
- `references/utm5-change-tariff.md` — ChangeTariff payload, server-cache-busting pattern (relogin hack vs deferred change), test script
- `references/tanstack-initialdata-modals.md` — **CRITICAL**: `initialData: []` + `staleTime` prevents real fetches, causing empty modals. Also covers `useMemo` inside `useCallback` hook violation.
- `references/utm5-cookie-auth.md` — Cookie-based auth, CORS traps, RN fetch injection
- `references/rn-flatlist-nested-scroll-warning.md` — VirtualizedList nesting, nested ScrollView fixes
- `scripts/test-tariff-change.mjs` — Reproduction script: run with credentials to verify server-side cache

## 18. UTM5 / Netup REST API pitfalls

### 18.1 Server cache after mutation — relogin fix

Some UTM5 installations cache the subscriber profile on the server per `sid_customer`. After a tariff change (`POST /auth/tariffs`), subsequent `GET /auth/profile` with the same session cookie may return the old data for 30–120s.

**Test before building:**
```sh
node scripts/test-tariff-change.mjs LOGIN PASS
```

If the test shows `(STALE!)` after change but correct after relogin, implement the auto-logout+login fix described in `references/utm5-change-tariff.md`.

However, first verify whether the server is returning `next_tariff_name` in the profile JSON. If present, the change is **deferred** (applied next billing period) — a relogin hack will not help. Surface `next_tariff_name` in the UI instead.

### 18.1a Deferred Tariff Change (UTM5 5.5-032) — `next_tariff_name`

**Discovery**
After `POST /auth/tariffs` returns `{"result":"OK"}`, `GET /auth/profile` still shows the old tariff. This is **not** a cache bug — UTM5 applies tariff changes **deferred**, at the beginning of the next billing period.

**Profile response shape**
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

**TypeScript — add `next_tariff_name`**
```ts
export interface ProfileTariff {
  id: number;
  name: string;
  next_tariff_name?: string;   // ← add this
  tariff_link_id: number;
  account_id: number;
}
```

**UI — show planned change**
Render the current tariff card and overlay/placement a hint:
```tsx
const current = account?.tariffs?.[0];
// Card shows: "Супер" 629 ₽
// If next_tariff_name exists, show → "Супер Лайт" (starts next period)
```

### 18.2 Empty notification array is normal

UTM5 `/auth/notifications` returns `[]` for subscribers with no notification history. This is **not** a bug — verify by checking the same subscriber in the UTM5 admin panel.

### 18.2 Date range restriction: max 1 year

`GET /auth/full_statistics` and related billing endpoints reject `startDate` older than 1 year with an explicit error: `startDate less than year ago`. Always compute the default range dynamically:

```ts
const defaultStart = subYears(new Date(), 1);   // date-fns
const defaultEnd   = new Date();
```

If the user requests a custom period, clamp to `max(1 year ago, userStart)` before sending.

### 18.3 Login endpoint variants

| Endpoint | Behaviour | Use when |
|----------|-----------|----------|
| `POST /login` | Returns `{ sid_customer, ... }` or `Set-Cookie` | Standard mobile app login |
| `POST /login_hotspot` | Often returns empty body; session may not persist | Hotspot captive-portal flows |

If `/login_hotspot` returns empty body, fallback to `/login` with an empty `mobile_telephone` field:

```ts
client.post('/login', { login, password, mobile_telephone: '' });
```

- `references/rn-flatlist-nested-scroll-warning.md` — Full reproduction recipe: nested FlatList/ScrollView warning, fix strategies, Metro cache clearing
- `references/utm5-cookie-auth.md` — UTM5 /customer_api cookie-based auth: CORS platform trap, RN fetch cookie injection, login endpoint variants, persistent vs volatile session storage
- `references/utm5-change-tariff.md` — Correct `POST /auth/tariffs` payload (`tariff_link_id` vs `tariff_id`), response shape mapping (`cost` string, `comments` plural), test curl recipe
- `references/utm5-api-subscriber-endpoints.md` -- UTM5 REST API endpoints relevant to subscriber portals (from Netup docs)
- `references/pdf-to-design-colors.md` -- Extracting hex color palettes from PDF mockups via PNG conversion + vision analysis
- `references/tanstack-initialdata-modals.md` — **CRITICAL**: `initialData: []` + `staleTime` blocks real fetches, causing empty modals. Also covers `useMemo` inside `useCallback` hook violation.

## 19. TanStack Query `initialData` + `staleTime` — The Empty Modal Bug

When a modal that displays a server-fetched list opens **blank** on first visit then populates after a mutation, the cause is `initialData: []` combined with a long `staleTime`.

### How it happens

```ts
export function useTariffs() {
  return useQuery({
    queryKey: queryKeys.catalog.tariffs(),
    queryFn: getTariffs,
    staleTime: 3 * 60_000,
    initialData: [],  // ← treated as "already valid data"
  });
}
```

TanStack Query sees `initialData` + `staleTime` and decides: "data is present and fresh — no need to call `queryFn`". The list stays `[]` until `invalidateQueries` marks it stale.

### Fix: remove `initialData` for server-fetched lists

```ts
export function useTariffs() {
  return useQuery({
    queryKey: queryKeys.catalog.tariffs(),
    queryFn: getTariffs,
    staleTime: 3 * 60_000,
    // initialData REMOVED
  });
}
```

Result:
- First mount: `status === 'pending'` → show spinner
- Fetch completes → list populates
- Within `staleTime`: cached data reused
- After `staleTime`: next mount triggers refetch

### When `initialData` IS correct

Use it only when data is pre-populated (SSR, `setQueryData`) or has a sensible default (form state). **Never** for server lists the user expects to see populated.

## 20. `useMemo` inside `useCallback` — Hook rule violation

`useMemo` must be at the **top level** of a component or custom hook. Inside a `useCallback` it executes conditionally, violating React's Rules of Hooks.

```tsx
// ❌ WRONG
const TariffModal = useCallback(() => {
  const currentIds = useMemo(() => new Set(...), [account?.tariffs]);
  return <Modal>...</Modal>;
}, [...]);

// ✅ CORRECT: hoist useMemo to component level
const currentTariffIds = useMemo(() => new Set(...), [account?.tariffs]);
const TariffModal = useCallback(() => {
  return <Modal>{allTariffs?.map(t => <Item isActive={currentTariffIds.has(t.id)} />)}</Modal>;
}, [allTariffs, currentTariffIds, ...]);
```

**Why it matters with modals:** A hidden modal means 0 hooks; a visible modal means 1 hook. React tracks hook count per component, so toggling visibility corrupts the hook order and crashes.

---
