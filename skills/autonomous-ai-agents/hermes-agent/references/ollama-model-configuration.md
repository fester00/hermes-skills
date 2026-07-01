# Ollama Local and Cloud Model Configuration for Hermes

Add new Ollama models to the Hermes WebUI/model picker, or fix the case where only one model is available despite many existing in Ollama Cloud.

## Step-by-step

### 1. Understand the two Ollama providers

| Provider | ID | Base URL | Behavior |
|-----------|-----|----------|----------|
| **Ollama Local** | `ollama-launch` | `http://127.0.0.1:11434/v1` | Uses local Ollama server. Models are pulled to disk on first use (slow + takes space). |
| **Ollama Cloud** | `ollama-cloud` | `https://ollama.com/v1` | Pure cloud API, no local downloads. Requires `OLLAMA_API_KEY`. |

> Hermes config uses `provider: ollama-launch` by default. This talks to the local Ollama daemon.

### 2. Check what is currently available

```bash
# List locally pulled Ollama models
ollama list

# Hit the local Ollama API for available tags
curl -s http://localhost:11434/api/tags | jq -r '.models[].name'

# Check current Hermes provider config
grep -A 10 'providers:' ~/.hermes/config.yaml
```

### 3. List all models from Ollama Cloud (no auth required for listing)

```bash
curl -s https://ollama.com/v1/models | jq -r '.data[].id' | head -30
```

> No API key is needed just to *list* models. You only need `OLLAMA_API_KEY` when actually calling a model through the cloud endpoint.

### 4. Add models to ollama-launch (local provider)

Edit `~/.hermes/config.yaml`:

```yaml
providers:
  ollama-launch:
    api: http://127.0.0.1:11434/v1
    default_model: kimi-k2.6:cloud
    models:
      - kimi-k2.6:cloud
      - qwen3.5:397b
      - deepseek-v3.1:671b
      - gemma3:27b
      - minimax-m2
```

> The `:cloud` suffix on model names signals Ollama to pull from cloud rather than local Modelfile.

After editing, restart Hermes or the WebUI. On first request, Ollama will automatically `pull` the model——this may take minutes for large models (e.g. 671b = ~400GB).

### 5. Switch to ollama-cloud (bypass local downloads)

If you prefer cloud inference and faster availability:

1. Get an API key at https://ollama.com/settings
2. Add to `~/.hermes/.env`:
   ```bash
   OLLAMA_API_KEY=your_key_here
   ```
3. Change provider in `config.yaml`:
   ```yaml
   model:
     provider: ollama-cloud
     default: kimi-k2.6
   providers:
     ollama-cloud:
       api: https://ollama.com/v1
       models:
         - kimi-k2.6
         - qwen3.5:397b
   ```

### 6. Use multiple API keys with credential pool (Ollama Pro / multiple accounts)

Hermes supports credential pools — multiple API keys for the same provider with automatic failover and load balancing.

**When to use:** Ollama Pro subscription (allows up to 3 simultaneous models), multiple accounts, or automatic key rotation on 429 rate limits.

**Step 1 — Add keys to pool:**
```bash
hermes auth add ollama-cloud --type api-key --api-key <KEY_1> --label primary
hermes auth add ollama-cloud --type api-key --api-key <KEY_2> --label secondary
hermes auth add ollama-cloud --type api-key --api-key <KEY_3> --label tertiary
```

**Step 2 — Set pool strategy:**
```bash
hermes config set credential_pool_strategies.ollama-cloud least_used
```

Strategies: `least_used` (distributes load evenly — recommended), `round_robin`, `random`, `fill_first`.

**Step 3 — Clean model config** so Hermes uses pool-supplied credentials, not hardcoded key:
```yaml
model:
  api_key: ''
  base_url: ''
  default: kimi-k2.6
  provider: ollama-cloud
```

> Important: set `api_key: ''` and `base_url: ''` in `model:` section. The base URL is picked from `providers.ollama-cloud.api`. If you leave the old `base_url: http://127.0.0.1:11434/v1`, Hermes will try to talk to a local Ollama daemon instead of the cloud.

**Step 4 — Verify:**
```bash
hermes auth list ollama-cloud
# Expected: custom:ollama-cloud (N credentials)
```

**How it works:**
- On every API call, Hermes selects the least-used/exhausted credential from the pool.
- On 429 (rate limit) or 401/402, the exhausted key is cooled down for 1 hour and the next key is tried automatically.
- No manual intervention needed during a session.

### 7. Common issues

| Problem | Fix |
|---------|-----|
| `ollama list` is empty but models configured | No models pulled yet. First call will auto-pull. Or run `ollama pull <model>`. |
| WebUI shows "only 1 model" | The `models:` array in `config.yaml` only has one entry. Add more as shown above. |
| `OLLAMA_API_KEY` not set when using ollama-cloud | Add key to `~/.hermes/.env`. Without it, cloud requests fail. |
| Port 11434 not open | Ensure `ollama serve` is running. Check with `ss -lntp \| grep 11434`. |

## Pitfalls

- **`:cloud` suffix vs bare name**: For `ollama-launch`, use `:cloud` suffix to trigger cloud pulls (e.g. `kimi-k2.6:cloud`). For `ollama-cloud` provider, use bare name (e.g. `kimi-k2.6`).
- **Disk budget**: A 671b parameter model can exceed 400GB. Always check disk space before pulling large models.
- **Restart required after config edit**: Hermes reads `config.yaml` at startup. WebUI sessions may cache the model list.

## Verification

```bash
# Confirm new models appear in config
grep -A 20 'ollama-launch:' ~/.hermes/config.yaml

# Verify Ollama is responsive
curl http://localhost:11434/api/tags

# Check WebUI model dropdown (reload page if needed)
```
