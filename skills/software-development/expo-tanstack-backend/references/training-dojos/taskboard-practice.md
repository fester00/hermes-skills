# TaskBoard Practice Scaffold — Three-Layer Dojo

A self-contained mini-project for hands-on practice after the socratic course.
Fill in the blanks to wire `api/` → `services/` → `hooks/` correctly.

## Files

### `src/api/client.ts`

```typescript
const BASE_URL = 'https://api.taskboard.example.com';

async function request<T>(url: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('accessToken');

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${url}`, {
    ...options,
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (response.status === 401) {
    localStorage.removeItem('accessToken');
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export const client = {
  get: <T>(url: string) => request<T>(url, { method: 'GET' }),
  post: <T>(url: string, body?: unknown) => request<T>(url, { method: 'POST', body }),
  put: <T>(url: string, body?: unknown) => request<T>(url, { method: 'PUT', body }),
  del: <T>(url: string) => request<T>(url, { method: 'DELETE' }),
};
```

### `src/services/auth.service.ts`

```typescript
import { client } from '../api/client';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  token: string;
  user: {
    id: number;
    email: string;
    name: string;
  };
}

export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  const data = await client.post<AuthResponse>('/auth/login', credentials);
  localStorage.setItem('accessToken', data.token);
  return data;
}

export async function logout(): Promise<void> {
  await client.post<void>('/auth/logout');
  localStorage.removeItem('accessToken');
}

export async function getMe(): Promise<AuthResponse['user']> {
  const data = await client.get<AuthResponse['user']>('/auth/me');
  return data;
}
```

### `src/hooks/useAuth.ts`

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as authService from '../services/auth.service';

export function useAuth() {
  const queryClient = useQueryClient();

  const { data: user, isLoading } = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: authService.getMe,
    enabled: !!localStorage.getItem('accessToken'),
    retry: false,
  });

  const loginMutation = useMutation({
    mutationFn: authService.login,
    onSuccess: (data) => {
      queryClient.setQueryData(['auth', 'me'], data.user);
    },
  });

  const logoutMutation = useMutation({
    mutationFn: authService.logout,
    onSuccess: () => {
      queryClient.removeQueries({ queryKey: ['auth', 'me'] });
    },
  });

  return {
    user: user ?? undefined,
    isLoading,
    isAuthenticated: !!user,
    login: loginMutation.mutateAsync,
    logout: logoutMutation.mutateAsync,
    isLoginPending: loginMutation.isPending,
    isLogoutPending: logoutMutation.isPending,
  };
}
```

### Extension exercises

After completing the scaffold above, the learner should implement:

1. `services/tasks.service.ts` with `Task`, `CreateTaskInput`, `getTasks(userId)`, `getTask(id)`, `createTask(input)`, `updateTask(id, changes)`, `deleteTask(id)`.
2. `hooks/useTasks.ts` with `useQuery({ queryKey: ['tasks', userId], enabled: !!userId })`.
3. `hooks/useCreateTask.ts` with `useMutation` + `invalidateQueries(['tasks'])`.
4. `features/tasks/TaskList.tsx` guarded by `useAuth().isAuthenticated`.

## Rules enforced by this scaffold
- No `fetch` outside `api/client.ts`.
- No `useQuery` / `useMutation` inside `services/`.
- No business types (`Task`, `User`) inside `api/`.
- `localStorage` is the single source of truth for the access token; React Context is not used for auth state persistence.
