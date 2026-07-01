# React + TypeScript + TanStack Query — Project Starter (TaskFlow Pattern)

Condensed project scaffold used in the Socratic React course. Built during a live session with a student, covers the full modern React stack as a single runnable project.

## Tech Stack

- **Build tool**: Vite (react-ts template)
- **Styling**: Tailwind CSS
- **API**: json-server (local REST)
- **Server state**: TanStack Query (`@tanstack/react-query`)
- **Routing**: React Router DOM v6
- **Forms + validation**: React Hook Form + Zod (`@hookform/resolvers`)
- **Testing**: Vitest + React Testing Library (not wired in session, but listed for next step)

## Directory Layout

```
taskflow/
├── db.json                       # json-server data
├── package.json                  # scripts: dev, server, build
├── src/
│   ├── main.tsx                  # QueryClientProvider + BrowserRouter
│   ├── App.tsx                   # Route dispatcher (Routes / Route)
│   ├── index.css                 # Tailwind directives
│   ├── types/
│   │   └── Task.ts               # Task interface + CreateTaskDto / UpdateTaskDto
│   ├── api/
│   │   └── client.ts             # fetch wrappers: fetchTasks, fetchTask, createTask, updateTask, deleteTask
│   ├── hooks/
│   │   └── useTasks.ts           # useQuery / useMutation custom hooks + TASKS_KEY
│   ├── components/
│   │   ├── TaskCard.tsx          # single task card with toggle + Link to detail
│   │   ├── TaskFilter.tsx        # all / active / completed filter buttons
│   │   └── List.tsx              # generic List<T> component with keyExtractor/renderItem
│   ├── features/
│   │   └── TaskList.tsx          # consumes List<Task>, handles empty state
│   └── pages/
│       ├── HomePage.tsx          # tasks query + filter + TaskList
│       ├── AddTaskPage.tsx       # React Hook Form + Zod + useCreateTask + navigate('/')
│       └── TaskDetailPage.tsx    # useTask(id) + update + delete + navigate
```

## Key Patterns

### 1. Query Key Design
- Root list key: `const TASKS_KEY = ['tasks'] as const`
- Single item key: `[...TASKS_KEY, id]` — enables `invalidateQueries` to cascade correctly when list is invalidated.

### 2. Type-Driven DTOs with Utility Types
```ts
export interface Task {
  id: number;
  title: string;
  priority: 'low' | 'medium' | 'high';
  completed: boolean;
}

export type CreateTaskDto = Omit<Task, 'id' | 'completed'>;
export type UpdateTaskDto = Partial<Task>;
```

### 3. Generic List Component
```tsx
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => ReactNode;
  keyExtractor: (item: T) => string | number;
  emptyMessage?: ReactNode;
}
```

### 4. Form with Zod + React Hook Form
```tsx
const schema = z.object({
  title: z.string().min(1).max(100),
  priority: z.enum(['low', 'medium', 'high']),
});

type FormData = z.infer<typeof schema>;

const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
  resolver: zodResolver(schema),
});
```

### 5. Mutation + Navigation Pattern
```tsx
const navigate = useNavigate();
const mutation = useCreateTask();

const onSubmit = (data: FormData) => {
  mutation.mutate(data, { onSuccess: () => navigate('/') });
};
```

## Quick Start Commands

```bash
# 1. Scaffold
npm create vite@latest taskflow -- --template react-ts

# 2. Dependencies
npm install -D tailwindcss postcss autoprefixer json-server
npm install @tanstack/react-query @tanstack/react-query-devtools react-router-dom react-hook-form zod @hookform/resolvers

# 3. Init Tailwind
npx tailwindcss init -p

# 4. Run
npm run server     # json-server --watch db.json --port 3001
npm run dev        # vite
```

## Pitfalls Hit During Session

- **Arrow function without return in `renderItem`**: `task => { <Component /> }` returns `undefined`. Must be `task => ( <Component /> )` or with explicit `return`.
- **`{count && <span>}` renders "0"**: When `count` is `0`, React renders literal `0`. Guard with `count > 0`.
- **Missing `key` in list renders**: Without `key`, state/animations stick to wrong DOM nodes after reorder/delete.
- **Forgetting `useEffect` deps array**: Causes infinite `setState` -> re-render loops.
- **Utility Types confusion**: Students often think `Partial`/`Omit` are basic types like `number`. Clarify they are "type templates".
