# OpenCode JSON-Mode Smoke Test (kimi-k2.7-code:cloud)

Session: 2026-06-13
Environment: Linux, Node v24.13.1 via nvm, Ollama-compatible proxy at `http://127.0.0.1:11434/v1`
Model: `kimi-k2.7-code:cloud`

## Config

`~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "ollama/kimi-k2.7-code:cloud",
  "provider": {
    "ollama": {
      "models": {
        "kimi-k2.7-code:cloud": {
          "_launch": true,
          "limit": { "context": 256000, "output": 32768 },
          "name": "kimi-k2.7-code:cloud"
        }
      },
      "name": "Ollama",
      "npm": "@ai-sdk/openai-compatible",
      "options": { "baseURL": "http://127.0.0.1:11434/v1" }
    }
  }
}
```

## Command

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 24
cd /tmp
opencode run --model ollama/kimi-k2.7-code:cloud --format json \
  "Respond with exactly: OPENCODE_SMOKE_OK"
```

## Expected output (excerpt)

```
bash: /home/natan/.openclaw/completions/openclaw.bash: No such file or directory
{"type":"step_start", ...}
{"type":"text", ... "text":"OPENCODE_SMOKE_OK"}
{"type":"step_finish", "reason":"stop", "tokens":{"total":9104,"input":9079,"output":25,...}, "cost":0}
```

## Notes

- The `bash: ...openclaw.bash: No such file...` line is a harmless shell-completion warning; ignore it.
- `cost: 0` because the model runs through a local Ollama-compatible proxy.
- JSON-mode output is a stream of events; the useful final answer is in the `text` event.
- If `--model` is omitted and `~/.config/opencode/opencode.json` has the model set, the default is used automatically.

## When to run

Run this smoke test after:
- changing OpenCode config or model;
- updating nvm/node version;
- any suspicion that OpenCode lost its model/provider settings.
