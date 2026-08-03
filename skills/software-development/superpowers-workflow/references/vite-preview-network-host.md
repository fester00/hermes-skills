# Running Vite preview/dev server on local IP

Use when the user wants to access a Vite project from another device on the same network.

## Problem

`npm run preview -- --port 3002` binds to `localhost` only. External devices cannot reach it.

## Solution

Add `--host 0.0.0.0`:

```bash
cd /path/to/project
npm run preview -- --port 3002 --host 0.0.0.0
```

Output will show:
```
➜  Local:   http://localhost:3002/
➜  Network: http://192.168.0.98:3002/
```

The project is then reachable from other devices on the LAN at the Network URL.

## Cleanup

Before switching projects or restarting, kill any processes on the port:

```bash
ss -ltnp | grep -E '3002|3003|3004' | grep -oP 'pid=\\K[0-9]+' | sort -u | xargs -r kill -9
```

When using `background=True` Hermes terminal processes with `watch_patterns`, a stale process may hold the port. Always verify with `ss -ltnp | grep PORT` before launching a new server. If the port is in use, kill the existing process first rather than letting Vite auto-pick another port, which breaks the URL shared with the user.

## Provenance

- 2026-08-01: used for `silicone-landing-v2` preview so the user could review the landing page from another device.
