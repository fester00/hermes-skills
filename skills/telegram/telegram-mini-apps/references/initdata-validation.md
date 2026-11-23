# Validating `initData`

The client hands the raw `Telegram.WebApp.initData` query string to the page. Send **that string** to the
backend as-is; parse it there. `initDataUnsafe` is display data only.

## Algorithm (official form)

```
data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()) if k != "hash")
secret_key       = HMAC_SHA256(key="WebAppData", msg=<bot_token>)
valid            = hex(HMAC_SHA256(key=secret_key, msg=data_check_string)) == hash
```

Notes that decide success or failure:

- The **key** of the first HMAC is the literal string `WebAppData`; the **message** is the bot token. Swapping
  them is the most common reason for a hash mismatch.
- Hash the field values **exactly as received** (JSON is still a JSON string). Decoding + re-serialising `user`
  changes key order and whitespace and breaks the signature.
- Values are URL-encoded in `initData`; decode per-field **once** (`urllib.parse.unquote_plus`), not with a
  `parse_qs` that silently drops the `hash` field or normalises `+`.
- `hash` is the only excluded field.
- Compare in constant time (`hmac.compare_digest`).

## Python, stdlib only

```python
import hashlib, hmac
from urllib.parse import unquote_plus

def validate(init_data: str, bot_token: str) -> dict:
    pairs = [p.split("=", 1) for p in init_data.split("&") if "=" in p]
    fields = {k: unquote_plus(v) for k, v in pairs}
    received = fields.pop("hash", "")
    check = "\n".join(f"{k}={fields[k]}" for k in sorted(fields))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, received):
        raise ValueError("bad signature")
    return fields   # auth_date, user (JSON), query_id, start_param, chat_type, ...
```

`fields["user"]` is a JSON string — `json.loads` it after validation. `auth_date` is a unix timestamp: reject
anything older than your session window (5–15 minutes is a sane default for a fresh launch token).

## FastAPI

```python
from fastapi import Header, HTTPException
import os

@app.post("/api/auth")
async def auth(x_init_data: str = Header(alias="X-Init-Data")):
    try:
        fields = validate(x_init_data, os.environ["BOT_TOKEN"])
    except ValueError:
        raise HTTPException(401, "invalid init data")
    user = json.loads(fields["user"])
    token = issue_session(user["id"], user.get("language_code"))
    return {"token": token, "user": user}
```

Header is safer than a body field: it cannot be lost by a form re-serialisation and it is easy to forward
through a reverse proxy.

## Node / Express

```js
const crypto = require('crypto');

function validate(initData, botToken) {
  const params = new URLSearchParams(initData);
  const hash = params.get('hash');
  params.delete('hash');
  const check = [...params.entries()].sort(([a], [b]) => a.localeCompare(b))
    .map(([k, v]) => `${k}=${v}`).join('\n');
  const secret = crypto.createHmac('sha256', 'WebAppData').update(botToken).digest();
  const expected = crypto.createHmac('sha256', secret).update(check).digest('hex');
  return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(hash || ''))
    ? Object.fromEntries(params) : null;
}
```

`URLSearchParams` already percent-decodes; do not decode again.

## Third-party validation (no bot token)

When a service must trust the data without holding the token, Telegram provides an **Ed25519** signature variant:

```
data_check_string = "<bot_id>:WebAppData\n" + sorted fields (excluding hash and signature), "key=value" joined by \n
verify Ed25519(public_key, data_check_string, base64url_decode(signature))
```

Public keys are published in the docs (separate key for the test environment) — fetch them from
`https://core.telegram.org/bots/webapps`, do not hardcode a stale copy.

## Session exchange, not session storage

- `initData` is re-issued on **every** launch and is a launch credential, not a session: verify it, then mint your
  own cookie/JWT with your own TTL, and treat that as the session.
- Re-validate on sensitive endpoints (payments, writes) or at least require the session token; never let a
  `user_id` from the request body be authoritative.
- Rate-limit the auth endpoint per IP and per Telegram `user.id`.
- Multi-instance backends: the bot token is the signing key everywhere, so any instance can validate; keep the
  token in a secret store, not in the repo.

## Debugging a mismatch

1. Print the raw `initData` (server log) and the computed `data_check_string`. If the string has reordered or
   re-encoded values, the fix is in parsing, not in the crypto.
2. Confirm the token: a token with a stray newline/space, or a token of the *test* bot used against production
   data, gives a clean mismatch.
3. Confirm the fields you exclude: only `hash`.
4. Replay the exact string in a 5-line script against the same token — if that passes, the bug is in the
   request layer (proxy stripping headers, body parser mangling `+`).
