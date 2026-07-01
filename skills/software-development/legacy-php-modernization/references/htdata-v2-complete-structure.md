# Reference: htdata-v2 Complete Structure

This document captures the complete file tree and key implementation patterns from the LigaLink CRM v2 full rewrite session (May 2026). Use as a structural reference when scaffolding similar CRM/ISP backends.

## Root layout

```
htdata-v2/
├── backend/
│   ├── src/
│   │   ├── config/index.ts           # dotenv + DB pool registration
│   │   ├── database/DatabaseManager.ts  # Named connection pools (crm, utm5, archive)
│   │   ├── middleware/
│   │   │   ├── auth.ts            # JWT verify + role extraction + requireRole()
│   │   │   └── validate.ts       # express-validation wrapper
│   │   ├── routes/                # Express routers per domain
│   │   ├── controllers/           # Raw SQL controllers with dual-DB queries
│   │   ├── services/              # authService (bcrypt, user lookup)
│   │   ├── types/index.ts         # TypeScript interfaces for all entities
│   │   └── utils/                 # (empty — place for helpers)
│   ├── .env                       # DB creds, JWT secret, CORS, cookie settings
│   ├── .env.example               # Template for new developers
│   ├── package.json               # TypeScript, Nodemon, MySQL2
│   └── tsconfig.json              # CommonJS output, paths: {"@/*": ["src/*"]}
├── frontend/
│   ├── src/
│   │   ├── App.tsx                # Routes + PrivateRoute guard + AuthProvider
│   │   ├── main.tsx               # StrictMode + BrowserRouter + QueryProvider
│   │   ├── components/
│   │   │   ├── layout/Layout.tsx  # Sidebar + nav items filtered by role + mobile overlay
│   │   │   ├── ui/                # (empty — shadcn-style primitives go here)
│   │   │   └── shared/            # (empty)
│   │   ├── pages/
│   │   │   ├── Auth/LoginPage.tsx
│   │   │   ├── Customers/
│   │   │   │   ├── CustomersPage.tsx      # Search + pagination list
│   │   │   │   └── CustomerCardPage.tsx   # Detail: account, equipment, tariffs, IPs
│   │   │   ├── Orders/
│   │   │   │   ├── OrdersPage.tsx         # Tabs: connection vs repair, filters
│   │   │   │   └── OrderCreatePage.tsx    # Form with type toggle
│   │   │   ├── Equipment/
│   │   │   │   └── EquipmentPage.tsx      # Switches list + subscriber stats
│   │   │   └── Brigades/
│   │   │       └── BrigadeStatsPage.tsx   # Cards with completion rate
│   │   ├── hooks/                 # (empty — tanstack-query does most work)
│   │   ├── services/
│   │   │   └── api.ts            # Axios instance: baseURL=/api, withCredentials, 401→redirect
│   │   ├── types/index.ts         # User, Customer, Order, Switch, Brigade, etc.
│   │   ├── context/
│   │   │   └── AuthContext.tsx    # useAuth hook, can(feature) guard, role features map
│   │   └── lib/
│   │       ├── utils.ts           # cn() for Tailwind class merging
│   │       └── QueryProvider.tsx  # TanStack QueryClient wrapper
│   ├── index.html                 # lang=ru, dark theme root
│   ├── vite.config.ts             # Proxy /api to localhost:3001, path alias @/
│   ├── tsconfig.app.json          # ignoreDeprecations: 6.0, paths
│   └── package.json               # Tailwind v4, React 19, TanStack Query, Axios, Recharts, date-fns
├── docs/
│   └── ARCHITECTURE_PLAN.md       # Full legacy audit from earlier session
└── package.json                   # Root: concurrently dev:backend + dev:frontend
```

## Key patterns used

### DatabaseManager (multi-pool)
- `db.register(name, config)` at startup
- `db.query(poolName, sql, values?)` — always returns `RowDataPacket[]`
- `db.transaction(poolName, fn)` — explicit begin/commit/rollback

### Auth flow
- Login → `bcrypt.compare()` → `jwt.sign()` → `res.cookie('token', ...)`
- `authMiddleware` — read cookie, verify JWT, fetch user + group, attach `req.user.role`
- `requireRole('manager', 'call_center_manager')` — route-level guard
- Frontend: `useAuth().can('orders_assign')` — UI-level guard (hides nav items/buttons)

### Role feature map (frontend)
```tsx
const features: Record<UserRole, string[]> = {
  call_center_manager: ['customer_search', 'customer_card', 'diagnostics', ...],
  manager: [...call_center_manager..., 'orders_assign', 'brigades_stats', 'brigades_manage'],
  installer: ['orders_view', 'orders_calendar'],
};
```

### API response wrapper
```json
{ "success": true, "data": [...], "pagination": { "page": 1, "pageCount": 4, "limit": 25, "count": 97 } }
```

### Bulk file generation technique
When `write_file` triggers false TS5112 linter errors (tsconfig present but specified on commandline), switch to `execute_code` with Python `hermes_tools` wrapper for mass file creation.