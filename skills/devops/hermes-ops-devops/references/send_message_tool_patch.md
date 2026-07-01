# Patch: send_message Tool — Telegram Fallback Transport

## Context
Hermes WebUI's `send_message` tool (`hermes_webui/tools/telegram_tools.py`) creates its own `python-telegram-bot.Bot` instance with `HTTPXRequest`. It does **NOT** use the gateway's `TelegramFallbackTransport`. In regions where `api.telegram.org` is DNS-blocked (e.g. Russia), this causes `send_message` to time out even though the gateway itself is healthy and connected via sticky fallback IP.

## The Patch

Add fallback transport initialization to `build_bot()` or wherever the Bot is constructed.

### Code

```python
# At top of file, add import:
from hermes_cli.gateway.telegram_gateway import TelegramFallbackTransport

# In build_bot() (or equivalent), replace the request construction:
    fallback_ips_env = os.environ.get("TELEGRAM_FALLBACK_IPS", "149.154.167.220,149.154.167.220")
    fallback_ips = [ip.strip() for ip in fallback_ips_env.split(",") if ip.strip()]

    fallback_transport = TelegramFallbackTransport(
        fallback_ips=fallback_ips,
        sticky_ips=True,
    )

    # httpx.HTTPTransport extension for SNI over IP
    fallback_transport_with_sni = httpx.HTTPTransport(
        extensions={"sni_hostname": "api.telegram.org"}
    )

    request = HTTPXRequest(
        connection_pool_size=1,
        proxy=proxy_url,  # existing proxy arg
        http_version="1.1",
    )

    # The key: pass a custom httpx.AsyncClient with our transport
    import httpx as _httpx
    _custom_client = _httpx.AsyncClient(
        transport=fallback_transport_with_sni,
        proxy=proxy_url,
    )
    # Then construct Bot using this client — the exact API depends on PTB version
```

### Simpler Alternative (Tested and Working)

Instead of patching the tool itself, add a **system-level DNS override** so ALL tools (gateway, send_message, curl, anything) resolve `api.telegram.org` correctly:

```bash
# As root (or user with passwordless sudo):
echo "149.154.167.220 api.telegram.org" | sudo tee -a /etc/hosts
```

This is more robust than per-tool patches because:
- It fixes the root cause (DNS resolution)
- It affects all processes, not just the patched one
- It survives tool updates without re-patching
- It requires no code changes

**Trade-off:** Needs `sudo` or passwordless sudo for `/etc/hosts`.

### Alternative Without Sudo: systemd User Override

If sudo is unavailable, add environment variable to gateway's systemd unit via user-level override:

```bash
mkdir -p ~/.config/systemd/user/hermes-gateway.service.d
cat > ~/.config/systemd/user/hermes-gateway.service.d/override.conf <<'EOF'
[Service]
EnvironmentFile=/tmp/hermes-telegram.env
EOF
# Then create /tmp/hermes-telegram.env with:
# TELEGRAM_BOT_TOKEN=...
# TELEGRAM_FALLBACK_IPS=149.154.167.220
systemctl --user daemon-reload
systemctl --user restart hermes-gateway
```

This ensures gateway picks up token and fallback IP on every restart.

## Verification
After applying any fix, verify with:

```bash
# Check what DNS resolves to
resolvectl query api.telegram.org

# Direct API test via fallback IP
BOT_TOKEN="..."
CHAT_ID="..."
curl -s --connect-timeout 15 --max-time 30 \
  --resolve "api.telegram.org:443:149.154.167.220" \
  "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -d "chat_id=${CHAT_ID}" -d "text=Test OK"

# Check if send_message tool works now
send_message target="telegram:CHAT_ID" message="Test after fix"
```

## Related
- Parent skill: `hermes-ops-devops` Section 5
- `references/systemd_user_override.md` — full override template
- `references/telegram-fallback-ip-fix.md` — gateway-level fallback runbook

## Date
2026-06-10 — patched in hermes-webui during Telegram connectivity troubleshooting session.
