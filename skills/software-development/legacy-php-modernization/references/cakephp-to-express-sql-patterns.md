# CakePHP → Express Raw SQL Migration Patterns

Common SQL patterns from CakePHP 2.x CRMs when migrating to Express + MySQL2.

## Dual-database joins

CakePHP models often join across `ams2` (CRM) and `UTM5` (billing). In Express, split into two queries:

```typescript
// Customer + account (UTM5)
const customer = await db.query('utm5',
  `SELECT c.*, a.balance, a.is_blocked
   FROM users c
   LEFT JOIN accounts a ON c.basic_account = a.id
   WHERE c.id = ? AND c.is_deleted = 0`,
  [uid]
);

// Equipment (CRM)
const equipment = await db.query('crm',
  `SELECT sp.port_num, shl.switch_name
   FROM switch_ports sp
   INNER JOIN switch_house_links shl ON sp.switch_id = shl.switch_id
   WHERE sp.uid = ?`,
  [uid]
);
```

## IP address handling

CakePHP uses MySQL `INET_NTOA()` for storage and `INET_ATON()` for sorting:

```sql
-- Get human-readable IPs
SELECT INET_NTOA(ip) as ip_address FROM ip_groups WHERE ...

-- Sort switches by IP
SELECT * FROM switch_house_links ORDER BY INET_ATON(switch_ip) ASC
```

## Soft-delete pattern

CakePHP uses `deleted` field (NULL = active, timestamp = deleted):

```sql
-- Always add this WHERE clause
WHERE deleted IS NULL

-- Soft delete (don't DELETE)
UPDATE table SET deleted = NOW() WHERE id = ?
```

## Status bit fields

CakePHP CRMs use boolean flags for order status:
- `status_a` = active / visible
- `status_b` = in progress
- `status_c` = completed (repair)
- `status_d` = refused
- `status_e` = done (connection)

```sql
-- Active connection orders
WHERE status_a = 1 AND status_e = 0

-- Completed repair orders
WHERE status_c = 1
```

## Coverage statistics

```sql
-- House coverage percentage
SELECT h.*, hi.num_of_flats,
  (SELECT COUNT(*) FROM users c WHERE c.house_id = h.id AND c.is_deleted = 0) as customers,
  ROUND((
    (SELECT COUNT(*) FROM users c WHERE c.house_id = h.id AND c.is_deleted = 0)
    / hi.num_of_flats
  ) * 100, 2) as coverage_percent
FROM houses h
LEFT JOIN house_infos hi ON h.id = hi.id
```

## JSON response format

Keep CakePHP-style `success` + `data` wrapper for frontend compatibility:

```typescript
res.json({
  success: true,
  data: rows,
  pagination: { page, pageCount, limit, count: total }
});
```

## Dual-DB transactions

When an operation writes to both CRM and billing DBs (rare, but possible for order + account updates), use sequential transactions — MySQL2 does not support cross-database transactions for separate connections:

```typescript
// Write to CRM first
db.transaction('crm', async (conn) => {
  await conn.execute('INSERT INTO orders ...', [params]);
});

// Then write to billing
db.transaction('utm5', async (conn) => {
  await conn.execute('UPDATE accounts SET ...', [params]);
});
```

## Date handling (legacy UNIX timestamps)

CakePHP stores many dates as `create_date` (UNIX timestamp) and uses `date('d.m.Y')` in views. The new backend stores ISO strings and uses `date-fns` on frontend:

```typescript
// Backend: MySQL timestamp fields (stored as INT/UNIX in legacy)
// Use `dateStrings: true` in pool config to avoid Node.js timezone shifts
const pool = mysql.createPool({
  ...config,
  dateStrings: true, // ← always enable for legacy DBs
});

// Frontend: format with date-fns
import { format } from 'date-fns';
format(new Date(customer.create_date * 1000), 'dd.MM.yyyy');
```

## NMS / SNMP queries (node-snmp-native)

Legacy CakePHP uses a custom `NmsComponent` for SNMP v1/v2c switch polling. Port to Node.js with `net-snmp`:

```bash
npm install net-snmp
```

```typescript
import snmp from 'net-snmp';

const session = snmp.createSession(switchIp, 'public', { version: snmp.Version1 });
session.get(['1.3.6.1.2.1.1.1.0'], (error, varbinds) => {
  if (error) { console.error(error); return; }
  console.log(varbinds[0].value.toString());
  session.close();
});
```

ARP records (CRM table `arp_records`): store client IP, MAC, switch IP, port, last seen.
```sql
SELECT client_ip, mac, switch_ip, port_num, last_date
FROM arp_records
WHERE client_ip = ? ORDER BY last_date DESC LIMIT 1
```

## Coverage statistics (advanced)

CakePHP models use complex subqueries for coverage. Always port to raw SQL explicitly:

```sql
-- House coverage percentage
SELECT h.*, hi.num_of_flats,
  (SELECT COUNT(*) FROM users c WHERE c.house_id = h.id AND c.is_deleted = 0) as customers,
  ROUND((
    (SELECT COUNT(*) FROM users c WHERE c.house_id = h.id AND c.is_deleted = 0)
    / hi.num_of_flats
  ) * 100, 2) as coverage_percent,
  (SELECT COUNT(*) FROM switch_house_links WHERE house_id = h.id AND is_deleted = 0) as switch_count,
  (SELECT COUNT(*) FROM users c WHERE c.house_id = h.id AND c.is_deleted = 0 AND c.is_juridical = 1) as juridical_count
FROM houses h
LEFT JOIN house_infos hi ON h.id = hi.id
```
