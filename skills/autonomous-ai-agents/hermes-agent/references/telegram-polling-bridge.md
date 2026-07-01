# Telegram Bridge — Lightweight Two-Way Polling (Fallback)

Use when the user wants to chat with the agent via Telegram but cannot run the full native `hermes gateway`. This is a **DIY lightweight fallback** for environments where `python-telegram-bot` gateway is not possible.

> **Preferred method:** use the built-in `hermes gateway run` (see main Hermes Agent skill under "Telegram Gateway Setup (Native)").

## Architecture

```
User (Telegram)  <── HTTP GET/POST ──>  Python Listener (local)
                                            │
                                            ▼
                                   telegram_queue.json
                                            │
                                            ▼
                                   CLI Agent (Hermes)
```

- **listener** — long-polling Telegram Bot API, saves messages to queue
- **queue** — `~/.hermes/secrets/telegram_queue.json` (newest last)
- **sender** — `telegram-send.py` script for dispatching replies

## Setup

### 1. Store the API key

```bash
mkdir -p ~/.hermes/secrets
chmod 700 ~/.hermes/secrets
echo "YOUR_BOT_TOKEN" > ~/.hermes/secrets/telegram-api-key
chmod 600 ~/.hermes/secrets/telegram-api-key
```

### 2. Create the listener

File: `~/.hermes/secrets/telegram_listener.py`

```python
#!/usr/bin/env python3
import os, json, time, requests
BASE = os.path.expanduser("~/.hermes/secrets")
KEY_FILE = os.path.join(BASE, "telegram-api-key")
QUEUE  = os.path.join(BASE, "telegram_queue.json")
OFFSET = os.path.join(BASE, "telegram_offset.txt")
LOG    = os.path.join(BASE, "telegram_log.txt")

def load_key():
    with open(KEY_FILE) as f: return f.read().strip()

def load_offset():
    try:
        with open(OFFSET) as f: return int(f.read().strip())
    except: return 0

def save_offset(o):
    with open(OFFSET, "w") as f: f.write(str(o))

def load_queue():
    try:
        with open(QUEUE) as f: return json.load(f)
    except: return []

def save_queue(q):
    with open(QUEUE, "w") as f: json.dump(q, f, ensure_ascii=False)

def log(text):
    with open(LOG, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")

def main():
    token = load_key()
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    offset = load_offset()
    queue = load_queue()
    UNREAD = os.path.join(BASE, "telegram_unread")

    while True:
        try:
            r = requests.get(url, params={"offset": offset, "limit": 10}, timeout=30)
            data = r.json()
        except Exception as e:
            log(f"HTTP error: {e}")
            time.sleep(5); continue

        if not data.get("ok"):
            log(f"API error: {data}")
            time.sleep(5); continue

        for upd in data.get("result", []):
            offset = max(offset, upd["update_id"] + 1)
            msg = upd.get("message") or upd.get("edited_message")
            if not msg: continue
            text = msg.get("text", "")
            chat = msg.get("chat", {})
            user = msg.get("from", {})
            entry = {
                "timestamp": int(time.time()),
                "chat_id": chat.get("id"),
                "user_id": user.get("id"),
                "username": user.get("username") or user.get("first_name", "Unknown"),
                "text": text,
            }
            queue.append(entry)
            log(f"@{entry['username']} (chat {entry['chat_id']}): {text}")
            with open(UNREAD, "w") as f: f.write("1")

        save_offset(offset)
        save_queue(queue)
        time.sleep(2)

if __name__ == "__main__":
    main()
```

```bash
chmod +x ~/.hermes/secrets/telegram_listener.py
```

### 3. Create the sender

File: `~/.hermes/secrets/telegram-send.py`

```python
#!/usr/bin/env python3
import sys, os, requests
BASE = os.path.expanduser("~/.hermes/secrets")
with open(os.path.join(BASE, "telegram-api-key")) as f:
    TOKEN = f.read().strip()
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

if len(sys.argv) < 3:
    print("Usage: telegram-send.py <chat_id> <message>")
    sys.exit(1)

resp = requests.post(URL, json={"chat_id": sys.argv[1], "text": sys.argv[2]})
print(resp.json())
```

```bash
chmod +x ~/.hermes/secrets/telegram-send.py
```

### 4. Start the listener (background)

```bash
# Start as Hermes-managed background process via agent terminal(background=true)
cd ~/.hermes/secrets && python3 telegram_listener.py
```

Verify it's running with `process(action="poll", session_id="...")`.

### 5. Read incoming messages

```python
import json, os
with open(os.path.expanduser("~/.hermes/secrets/telegram_queue.json")) as f:
    queue = json.load(f)
for msg in queue[-10:]:
    print(f"[{msg['timestamp']}] @{msg['username']}: {msg['text']}")
```

### 6. Send a reply

```bash
python3 ~/.hermes/secrets/telegram-send.py CHAT_ID "Your reply text"
```

### 7. Auto-poll with cronjob (optional)

Create a cron job that runs every 30 seconds to pull new Telegram messages into the chat:

```yaml
schedule: "*/30 * * * * *"
prompt: "Check ~/.hermes/secrets/telegram_queue.json for new messages since last check. Report any new Telegram messages to the user with [Telegram] prefix."
```

## File Permissions

All files in `~/.hermes/secrets/` must be **user-only readable**:

```bash
chmod 700 ~/.hermes/secrets
chmod 600 ~/.hermes/secrets/telegram-api-key
chmod 600 ~/.hermes/secrets/telegram_queue.json
chmod 600 ~/.hermes/secrets/telegram_offset.txt
chmod 600 ~/.hermes/secrets/telegram_log.txt
```

## Security Notes

- **Never share bot tokens in chat.** If exposed, rotate immediately via @BotFather.
- The listener uses only `getUpdates` and `sendMessage` endpoints.
- No webhook server means no open ports = no inbound attack surface.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Listener not starting | Check `requests` is installed: `pip install requests` |
| No messages in queue | User must send a message to the bot first. Check `telegram_log.txt`. |
| Token invalid | Regenerate via @BotFather, update `telegram-api-key`. |
| Duplicate messages | `offset` file handles deduplication; do not delete it manually. |
| `chat_id` unknown | Read first incoming message from queue -- it contains `chat_id`. |

## Limitations

- Polling has ~2s latency. For instant delivery, webhooks are required (see `webhook-subscriptions` skill).
- Only text messages are supported. For photos/files, extend the listener.
- No built-in group chat filtering -- all messages to the bot are queued.
