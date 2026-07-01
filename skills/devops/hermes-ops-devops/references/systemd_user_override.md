# systemd User-Level Service Override — No Sudo Required

When a systemd service runs at user level (`--user`), its unit file lives in
`~/.config/systemd/user/`. You can add environment variables, change
`ExecStart`, or add `EnvironmentFile` **without root** by creating a drop-in
override.

## Use Case: Load .env for Hermes Gateway

Gateway's `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ALLOWED_USERS` live in
`~/.hermes/profiles/<profile>/.env` but systemd does **not** read `.env`
automatically. This leads to `send_message` timeouts because the gateway
can't authenticate.

## Step-by-Step

```bash
# 1. Create a sanitized .env file (no comments, no inline values)
#    systemd EnvironmentFile rejects inline comments and spaces around '='
cat > /tmp/hermes-telegram.env <<'EOF'
TELEGRAM_BOT_TOKEN=853159...zB_M
TELEGRAM_HOME_CHANNEL=942051327
TELEGRAM_ALLOWED_USERS=942051327,120954006,535814521
TELEGRAM_WEBHOOK_PORT=8443
EOF

# 2. Create the override directory
mkdir -p ~/.config/systemd/user/hermes-gateway.service.d

# 3. Write the override
cat > ~/.config/systemd/user/hermes-gateway.service.d/override.conf <<'EOF'
[Service]
EnvironmentFile=/tmp/hermes-telegram.env
EOF

# 4. Reload daemon and restart
systemctl --user daemon-reload
systemctl --user restart hermes-gateway

# 5. Verify the env is loaded
systemctl --user show hermes-gateway --property=Environment
# Should include: TELEGRAM_BOT_TOKEN=853159...zB_M
```

## Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| `Failed to parse environment file` | Comments or spaces around `=` in .env | Strip comments, remove spaces: `KEY=value` |
| `Failed to set up mount namespacing` | Using `EnvironmentFile=` with `DynamicUser=yes` | Remove `DynamicUser` or move env to `Environment=` lines |
| Override not applied | Forgot `daemon-reload` | Always `systemctl --user daemon-reload` after editing |
| Override lost after reboot | File in `/tmp/` | Move `.env` to `~/.hermes/hermes-telegram.env` (persistent) |
| `systemctl --user` not available | No user systemd instance | Start with `systemd --user` or use `export XDG_RUNTIME_DIR=/run/user/$(id -u)` |

## EnvironmentFile Format Rules (systemd is strict)

```
# VALID
KEY=value
KEY="value with spaces"
KEY='single quoted'

# INVALID — systemd will reject the entire file
KEY = value        # spaces around =
KEY=value # comment  # inline comment
export KEY=value   # 'export' keyword not supported
```

## Alternative: Environment= lines (no file needed)

If the token is short enough, inline in the override:

```ini
[Service]
Environment="TELEGRAM_BOT_TOKEN=853159...zB_M"
Environment="TELEGRAM_ALLOWED_USERS=942051327,120954006,535814521"
```

Pro: No separate file to manage.
Con: Secrets visible in `systemctl show` output; harder to rotate.

## One-Liner Verification

```bash
systemctl --user show hermes-gateway --property=Environment | grep TELEGRAM_BOT_TOKEN
```

If empty → env not loaded. Check `override.conf` syntax and `daemon-reload`.
