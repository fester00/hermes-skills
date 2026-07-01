# React Query / TanStack Query — Beginner Pitfalls

> Captured from a live socratic teaching session (TaskBoard, auth+tasks).
> These are the exact mistakes a learner made when asked to write `api/client.ts`,
> `services/auth.service.ts`, and `hooks/useAuth.ts` from scratch.

## 1. Calling `fetch` directly inside a service

**Wrong:** `fetch('/api/tasks')` inside `services/tasks.service.ts`.
**Why it fails:** Bypasses the `api/client.ts` interceptor that attaches `Authorization` tokens and uniform error handling. The service layer must only know business parameters (e.g. `userId: number`), never HTTP plumbing.
**Fix:** Always route through the shared `client.get/post/put/del` wrapper.

## 2. Loosely typed URL parameters

**Wrong:** `userID: Record<string, unknown>` for a route segment.
**Why it fails:** Passing an object interpolates as `"[object Object]"` into the URL.
**Fix:** Use concrete types: `userId: number | string` and template-literal it: `` `/users/${userId}/tasks` ``.

## 3. Returning an "OK/error" object instead of throwing

**Wrong:**
```ts
type ApiResponse = { success: 'OK', status: number } | { error: 'error', status: number };
// ...
return res.ok ? { success: 'OK', status: res.status } : { error: 'error', status: res.status };
```
**Why it fails:** TanStack Query treats any resolved promise as **success**. The UI will see `isError === false` even though the HTTP status was 500.
**Fix:** Let the shared `client.ts` wrapper check `response.ok` and `throw new Error(...)`. The service function should return the typed entity (`Task`, `Task[]`, `void`), and TanStack Query will naturally populate `isError` when the promise rejects.

## 4. Requiring the full entity (with `id`) for a create call

**Wrong:** `createTask(task: Task)` where `Task.id` is required.
**Why it fails:** The client doesn't know the id yet; the server generates it.
**Fix:** Use `Omit<Task, 'id'>` or a dedicated `CreateTaskInput` type.

## 5. Returning HTTP status codes from a service

**Wrong:** `deleteTask` returns `Promise<number>` (the HTTP status).
**Why it fails:** Components and hooks expect business entities or `void`. A `204` status is an implementation detail.
**Fix:** Return `Promise<void>` (or `Promise<Task>` if the API echoes the deleted item). Let `client.ts` handle status-checking.

## 6. Accepting `RequestInit` in a service function

**Wrong:** `createTask(task: Task, options: RequestInit = {})`.
**Why it fails:** The service layer should not accept raw `headers`, `method`, `signal`. That leaks HTTP concerns into business logic.
**Fix:** Business parameters only. If you need special headers, the `api/client.ts` interceptor or a dedicated wrapper is the right place.

## 7. Passing a called function instead of a function reference to `mutationFn`

**Wrong:** `useMutation({ mutationFn: client.post('/login', data) })`.
**Why it fails:** This executes the request **immediately** during render and passes a `Promise` where `useMutation` expects a **callable function**.
**Fix:** Pass the reference: `mutationFn: authService.login`. TanStack Query calls it later with whatever you pass to `.mutate(...)`.

## 8. Confusing `mutate()` with `mutateAsync()`

- `mutate(data)` → fire-and-forget. Returns `void`. Good for simple button handlers where UI already watches `mutation.isPending`.
- `mutateAsync(data)` → returns `Promise<Result>`. Use when the caller needs to `await`, run code **after** success (e.g. `navigate('/dashboard')`, `toast.success`), or wrap in `try/catch`.

## 9. Forgetting `enabled` on dependent / auth-gated queries

**Wrong:** `useQuery({ queryKey: ['auth', 'me'], queryFn: authService.getMe })` with no `enabled`.
**Why it fails:** A guest opening the page triggers a request without a token, gets `401`, and sees an error state.
**Fix:** `enabled: !!localStorage.getItem('accessToken')` (or derived from an auth atom). This makes the query idle rather than loading/errored.

## 10. `await` without `return` in an async service function

**Wrong:**
```ts
export async function getMe(): Promise<User> {
  await client.get<User>('/auth/me');
}
```
**Why it fails:** The function implicitly returns `undefined`.
**Fix:** `return await client.get<User>('/auth/me');` or `const data = await ...; return data;`.

## 11. Storing token in React Context / useState instead of `localStorage`

**Why it fails:** Context/state is wiped on page refresh. The `api/client.ts` interceptor reads `localStorage` synchronously on every request and survives reloads without a Provider tree dance.
**Fix:** `localStorage.setItem('accessToken', token)` after login; read it inside the interceptor.

## 12. Forgetting `removeQueries` or `clear()` on logout

**Why it fails:** The UI still shows the old `user` object from cache for up to `cacheTime` even though the token is gone. Any subsequent request will fail with 401, but the user sees an authenticated-looking screen.
**Fix:** On logout success:
1. `localStorage.removeItem('accessToken')`
2. `queryClient.removeQueries({ queryKey: ['auth', 'me'] })` (or `queryClient.clear()`)
3. Then navigate.
