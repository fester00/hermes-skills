# WebUI: chat is silent but `/health` returns 200

Session reference: 2026-07-16 — WebUI process and nginx were healthy, yet the UI produced no answers.

## Symptom

- `curl http://127.0.0.1:<port>/health` → `200`
- WebUI loads, sessions list works, you can type a message.
- No assistant response appears; the composer stays spinning or empty.
- Browser network tab shows the chat request may even return, but the SSE/data stream contains no answer.

## Root cause to check first

The WebUI server is fine. The failure is in the **agent/model layer** behind it. The most common offender is provider throttling or auth failure returned as an HTTP error to the agent, which the UI does not surface prominently.

## Diagnostic sequence

1. **Confirm the server is alive**
   ```bash
   pgrep -f "hermes-webui/server.py"
   ss -tlnp | grep 18789          # or HERMES_WEBUI_PORT
   curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:18789/health
   ```

2. **Read the server log for model/provider errors**
   ```bash
   tail -n 200 ~/.hermes/webui/server-18789.log
   ```
   Look for:
   - `HTTP 429` / `rate limit` / `you have reached your session usage limit`
   - `HTTP 401` / `Unauthorized`
   - `HTTP 402` / `Payment required`
   - `ConnectError`, `TimeoutError`, certificate errors
   - Provider names like `ollama-cloud`, `openrouter`, `anthropic`

3. **Check the active model/provider for the failing session**
   - In WebUI: look at the model chip in the composer.
   - On disk:
     ```bash
     grep -A 5 "^model:" ~/.hermes/config.yaml
     cat ~/.hermes/webui/settings.json | python3 -m json.tool | grep -i "model\|provider" | head -20
     ```

4. **Verify provider access from the host itself**
   ```bash
   # Example for Ollama cloud
   curl -s -o /dev/null -w "%{http_code}\n" https://ollama.com/v1/models
   # Example for a custom endpoint behind a proxy
   curl -s -o /dev/null -w "%{http_code}\n" -x socks5h://127.0.0.1:10808 <endpoint>/models
   ```

5. **If a proxy is configured, test with and without it**
   See `references/telegram-proxy-direct-vs-fallback.md` for the same pattern applied to Telegram.

## Common fixes

### Ollama Cloud 429 — session usage limit

Symptom in log:
```
HTTP 429: you (natanfes) have reached your session usage limit
```

This means the account has exhausted its cloud inference quota, not that the WebUI is broken.

Options:
- Switch the profile to another provider with an active API key.
- Use a local Ollama model if one is pulled (`ollama list`).
- Wait for the quota window or add credits via Ollama settings.

To switch provider for the whole profile:
```bash
hermes config set model.provider openrouter   # or custom, anthropic, etc.
hermes config set model.default <model-name>
# Restart WebUI so new sessions pick up the default
systemctl --user restart hermes-webui.service
```

To switch only in WebUI without changing the CLI default, use the model picker in the composer. If the picker reverts after the first response, see `references/webui-ollama-colon-model-revert-bug.md`.

### Proxy misconfiguration

If `.env` sets `*_PROXY` or the provider uses a SOCKS5 proxy that does not route the provider endpoint, requests will fail with `ConnectError` or timeout even though the WebUI `/health` works.

Fix: remove the proxy for that endpoint, or configure the proxy routing to include it.

## Pitfalls

- Do not assume WebUI is down just because chat is silent. Always check `server-*.log` first.
- `/health` only proves the HTTP server is up; it does not prove the model provider is answering.
- Errors may be buried in the middle of a long log file, not at the very end. Use `grep -i` for `429|401|timeout|connecterror`.
- A restart of WebUI alone will not fix provider-side throttling or auth errors.
