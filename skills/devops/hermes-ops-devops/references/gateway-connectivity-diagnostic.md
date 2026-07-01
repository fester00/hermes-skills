# Gateway Connectivity Diagnostic

## Problem
Gateway (or any outbound service) reports "Timed out" on HTTPS connections, but ICMP ping works and DNS resolves.

## Diagnostic Signal
- `ping <ip>` works fine
- `curl -s --max-time 8 https://<host>/` returns `000 8.00s` (TCP timeout on TLS)
- Gateway logs show: `Connect attempt 1/8 failed: Timed out` followed by retry loops
- DNS returns correct IP, but HTTPS never completes

## Root Cause
HTTPS (port 443) may be blocked by ISP/government while ICMP remains open. Common in regions with Telegram/RuNet blocks.

## Diagnostic Commands

```bash
# Step 1: Check if TLS handshake reaches host
curl -s --max-time 8 -o /dev/null -w "%{http_code} %{time_total}s\n" https://api.telegram.org/
# 000 with time =~ max-time = TLS/HTTPS blocked (or MTU issue)

# Step 2: Verify ICMP only
echo "=== PING ==="
ping -c 2 149.154.166.110 | tail -2
echo "=== DNS ==="
dig +short api.telegram.org

# Step 3: Check gateway logs for specific failure pattern
tail -50 ~/.hermes/logs/gateway.log | grep -i -E "(timeout|telegram|connect attempt)" | tail -10

# Step 4: If using a proxy, check env vars
env | grep -i "proxy"
grep -i "proxy" ~/.hermes/.env ~/.hermes/config.yaml 2>/dev/null
```

## Fix: Configure Proxy in Config

Edit `~/.hermes/config.yaml`:

```yaml
telegram:
  proxy:
    type: socks5
    url: socks5://127.0.0.1:1080   # or socks5h:// for DNS through proxy
```

If proxy requires auth:
```yaml
telegram:
  proxy:
    type: socks5
    url: socks5://user:pass@proxy_host:port
```

## Fix: Environment-Level Proxy (fallback)
If Hermes gateway does not pick up config.yaml proxy, set env before starting gateway:

```bash
export ALL_PROXY=socks5://127.0.0.1:1080
hermes gateway run --replace
```

## After Proxy Setup
1. Kill old gateway: `pkill -f "hermes_cli.main gateway run"`
2. Start new gateway (or let systemd restart it)
3. Wait 30s, then: `send_message action=list` in agent session
4. If `telegram:...` target appears — connection restored

## Pitfalls
- Do NOT restart gateway without proxy if HTTPS is blocked — it will time out again.
- Do NOT use `proxy` env var alone — test with `curl -x socks5://...` first.
- `socks5h://` vs `socks5://`: `socks5h` sends DNS through proxy; use if raw IPs also fail.
- `http_proxy` may break websocket connections in some gateway backends — prefer `socks5`.
