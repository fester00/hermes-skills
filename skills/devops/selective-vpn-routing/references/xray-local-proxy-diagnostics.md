# Diagnosing a dead host-side Xray proxy (SOCKS5/HTTP → VLESS/Reality)

Use when a local proxy (SOCKS5 on `127.0.0.1:1080`, HTTP on `:1081`) still accepts connections
but every request through it hangs until timeout.

## Decision order — do not skip steps

1. **Which process is actually the proxy?** Two Xray installs coexist easily:
   - the installer's *system* service (`/usr/local/etc/xray/config.json`, frequently just `{}` —
     it starts, binds nothing, and burns memory doing so);
   - the real one, usually a **user** service with its own config (`~/.config/xray/config.json`).
   Confirm the owner of the port and the non-empty config before debugging the wrong PID:
   ```bash
   systemctl status xray | head -5 ; systemctl --user status xray | head -5
   ps -eo pid,user,cmd | grep '[x]ray'
   ss -tlnp | grep -E ':1080|:1081'        # owner PID tells you which instance serves you
   wc -c /usr/local/etc/xray/config.json   # 3 bytes == "{}" == dead weight
   ```
2. **Do the consumers still need the proxy at all?** Test the real endpoints **direct** first
   (`api.telegram.org`, the model-provider API). If a router on the LAN already runs a transparent
   proxy, every device is covered and host-side plumbing is redundant. Also look for a deliberate
   disable marker in `~/.hermes/.env` — a commented
   `# TELEGRAM_PROXY disabled: ... direct works` is a decision, not a bug to "fix".
3. **Is the node TCP-reachable?** `timeout 8 bash -c 'cat < /dev/null > /dev/tcp/<node>/<port>'`
   plus `ping`. Port open and ping fine ⇒ the tunnel, not the network, is what is broken.
4. **Read the proxy's error log** and match the signature table below.
5. **Is the subscription link alive?** Fetch it and read the body — a JSON `errorCode` means the
   link/token is dead and no amount of node tuning will help.

## Error-log signatures

| Signature | Meaning | Action |
|---|---|---|
| `failed to find an available destination > common/retry: [EOF]` | TCP connects, server closes immediately — node credentials are stale/revoked | Take fresh nodes from a live subscription |
| `REALITY: received real certificate (potential MITM or redirection)` | Server did not recognise the client and proxied the handshake to the real SNI site | Wrong `publicKey`/`shortId`/`flow`, or traffic is intercepted upstream. Compare field by field against a config that demonstrably works (e.g. the router's live config) |
| `malformed HTTP request "\x05\x02\x00\x01"` | SOCKS5 bytes arrived at the HTTP inbound — a client points at the wrong port/protocol | Fix the client's port/protocol mapping |
| `common/retry: [EOF]` / `received real certificate` on **every** node of a fresh subscription | Keys in the subscription do not match the deployment, or a second proxy layer intercepts | Verify with the throwaway-instance recipe below before blaming the host |
| endless `dialing TCP to tcp:<node>:<port>` every 20–40 s with no follow-up | A client keeps retrying through the dead tunnel | Fix the tunnel; the retries are a symptom, not the cause |

Keep `loglevel` at `warning` in the live config: `debug` grows the error log without bound
under a retry loop.

## Verify a candidate node on a throwaway instance — never on the live config

```bash
# minimal config: its own inbound port (unprivileged), its own error log
# shape: templates/xray-router-socks5-only.json
~/.local/bin/xray run -c /tmp/xray-test.json &     # socks on 1090
sleep 2.5
curl -x socks5h://127.0.0.1:1090 -sS --max-time 15 -o /dev/null \
     -w '%{http_code} %{time_total}s' https://www.youtube.com ; echo "exit=$?"
kill %1
```

Only after a node returns a real HTTP status do you touch the live config — then change one field
(the outbound) and restart the service, leaving the rest untouched.

## Pitfalls

- **One port per inbound.** Cloning a provider config that ships both a `socks` and an `http`
  inbound onto a single test port makes the second bind collide, so SOCKS5 bytes land in the HTTP
  handler and you get `malformed HTTP request "\x05\x02\x00\x01"`. Remap socks→1090, http→1091.
- **Never combine `-x <proxy>` with `--noproxy ""`.** The pair produces no output at all, so a blank
  `-w` line reads as a dead node when the harness is at fault. Capture stderr and the exit code,
  not just stdout.
- **A subscription comes in two shapes.** Base64/plaintext `vless://` links, or a JSON array of
  complete client configs. Read the first ~200 bytes before choosing how to decode. For the JSON
  shape, copy a whole config and change only the inbound port — hand-rebuilding the outbound
  re-introduces transcription errors in the Reality fields.
- **`flow` must match the deployment.** When every current node carries `flow: xtls-rprx-vision`
  and your config has no `flow` (or the reverse), the handshake fails even with every other field
  identical.
- **A retired node looks identical to a blocked node** from the host side: the IP answers TCP but
  the tunnel never comes up. Always cross-check the node against the *current* subscription before
  spending time on network-layer theories.
