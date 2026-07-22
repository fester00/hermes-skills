# Telegram gateway: proxy works for GitHub but breaks Telegram API

Session reference: 2026-07-16 — `TELEGRAM_PROXY=socks5://127.0.0.1:10808` (xray) was set for GitHub access, but the Telegram gateway could not connect because xray did not route `api.telegram.org` / Telegram fallback IPs.

## Symptom

- `hermes gateway status` shows the service running.
- `~/.hermes/logs/gateway.log` repeats:
  ```
  [Telegram] Connect attempt N/8 failed: httpx.ConnectError: All connection attempts failed
  Reconnect telegram error: telegram connect timed out after 30s
  ```
- Telegram bot does not respond.

## Key observation

In many regions `api.telegram.org` is reachable directly, while GitHub is blocked. A single SOCKS5 proxy set for GitHub may not carry Telegram traffic. Forcing Telegram through it will break the bot.

## Diagnostic sequence

1. **Check current proxy setting**
   ```bash
   grep -iE "TELEGRAM_PROXY|SOCKS" ~/.hermes/.env
   ```

2. **Test Telegram API with and without proxy**
   ```bash
   # Direct
   curl -s -o /dev/null -w "%{http_code} %{time_total}s\n" --max-time 10 https://api.telegram.org/botFAKE/getMe
   # Via the configured proxy
   curl -s -o /dev/null -w "%{http_code} %{time_total}s\n" --max-time 10 -x socks5h://127.0.0.1:10808 https://api.telegram.org/botFAKE/getMe
   ```
   - `200/404` direct + `000` through proxy → proxy does not route Telegram.
   - `000` direct + `200/404` through proxy → direct Telegram is blocked; proxy needed.

3. **Confirm in gateway log**
   ```bash
   tail -n 50 ~/.hermes/logs/gateway.log
   ```
   Look for:
   - `Proxy detected; passing explicitly to HTTPXRequest: socks5://...`
   - Repeated `ConnectError` right after.

## Fixes

### A. Telegram works directly — remove the proxy

```bash
# Edit ~/.hermes/.env
sed -i.bak 's/^TELEGRAM_PROXY=.*/# TELEGRAM_PROXY removed: direct connection works/' ~/.hermes/.env

# Restart gateway
systemctl --user restart hermes-gateway
```

Then verify:
```bash
hermes gateway status
tail -n 30 ~/.hermes/logs/gateway.log
```

### B. Telegram is blocked and proxy is required

Make sure the proxy actually routes Telegram destinations:

- For xray/V2Ray: check routing rules include `geosite:telegram`, `geoip:telegram`, or explicit `149.154.0.0/16`.
- For a generic SOCKS5 tunnel: confirm it forwards arbitrary destinations, not only a whitelist.

After changing proxy config, rerun the curl test above until both direct and proxied paths behave as expected.

### C. Use Telegram fallback IPs

When `api.telegram.org` DNS is poisoned but Telegram IPs are reachable, the Hermes gateway already auto-discovers fallback IPs via DNS-over-HTTPS (see log line `Auto-discovered Telegram fallback IPs: ...`). If proxy removal makes it work, this auto-fallback is usually sufficient.

## Pitfalls

- The gateway reads `.env` only at startup. Any change to `TELEGRAM_PROXY` needs a gateway restart.
- `hermes gateway status` showing `active (running)` does **not** mean Telegram is connected; it only means the service process is alive. Read `gateway.log` for platform connection state.
- A proxy configured for one blocked service (e.g. GitHub) is not automatically suitable for another (Telegram).
- Do not assume Telegram is blocked just because GitHub is. Test directly first.

## Related

- `hermes-agent` skill, section "Telegram Gateway Setup (Native)" — for token and allowed-user setup.
- `references/webui-provider-error-silent-chat.md` — the same "health check passes but actual traffic fails" pattern in WebUI.
