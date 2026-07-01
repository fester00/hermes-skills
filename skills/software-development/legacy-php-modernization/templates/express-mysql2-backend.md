# Express + TypeScript + MySQL2 Backend Scaffold

Quick-start template for CRM/ISP-style backends with dual-database setup.

## Files to create

```
backend/
├── src/
│   ├── server.ts
│   ├── config/index.ts
│   ├── database/DatabaseManager.ts
│   ├── middleware/auth.ts
│   ├── middleware/validate.ts
│   ├── routes/
│   ├── controllers/
│   ├── services/
│   ├── types/index.ts
│   └── utils/
├── .env
├── package.json
└── tsconfig.json
```

## DatabaseManager.ts

```typescript
import mysql from 'mysql2/promise';

export interface PoolConfig {
  host: string; port: number; user: string;
  password: string; database: string;
}

class DatabaseManager {
  private pools = new Map<string, mysql.Pool>();
  register(name: string, config: PoolConfig) {
    this.pools.set(name, mysql.createPool({
      ...config, waitForConnections: true,
      connectionLimit: 10, queueLimit: 0,
      enableKeepAlive: true, keepAliveInitialDelay: 10000,
      dateStrings: true,
    }));
  }
  get(name: string): mysql.Pool {
    const pool = this.pools.get(name);
    if (!pool) throw new Error(`Pool '${name}' not registered`);
    return pool;
  }
  async query(poolName: string, sql: string, values?: unknown[]) {
    const [rows] = await this.get(poolName).execute(sql, values);
    return rows as mysql.RowDataPacket[];
  }
}
export const db = new DatabaseManager();
```

## Auth middleware (JWT + RBAC)

```typescript
// src/middleware/auth.ts
import jwt from 'jsonwebtoken';
import { db } from '../database/DatabaseManager';

export interface AuthRequest extends Request {
  user?: User & { role: UserRole };
}

export async function authMiddleware(req: AuthRequest, res: Response, next: NextFunction) {
  const token = req.cookies?.token ?? req.headers.authorization?.replace('Bearer ', '');
  if (!token) { res.status(401).json({ success: false, error: 'Unauthorized' }); return; }
  const decoded = jwt.verify(token, config.jwt.secret) as { userId: number };
  const rows = await db.query('crm', `SELECT u.*, g.* FROM users u LEFT JOIN groups g ON u.group_id = g.id WHERE u.id = ?`, [decoded.userId]);
  if (!rows.length) { res.status(401).json({ success: false, error: 'User not found' }); return; }
  req.user = { ...rows[0], role: mapRole(rows[0].group_name) };
  next();
}

export function requireRole(...roles: UserRole[]) {
  return (req: AuthRequest, res: Response, next: NextFunction) => {
    if (!req.user || !roles.includes(req.user.role)) {
      res.status(403).json({ success: false, error: 'Forbidden' });
      return;
    }
    next();
  };
}
```

## Package.json scripts

```json
{
  "scripts": {
    "dev": "nodemon --exec ts-node src/server.ts",
    "build": "tsc",
    "start": "node dist/server.js"
  }
}
```

## Notes

- Always use `mysql2/promise` for async/await
- Raw SQL preferred over ORM for dual-DB legacy queries
- Register pools at startup: `db.register('crm', config.dbCrm)`
- `dateStrings: true` avoids timezone issues with legacy UNIX timestamps
- Use `INET_NTOA()` / `INET_ATON()` for MySQL IP handling
