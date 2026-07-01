# Ollama Provider & Profile Auth Troubleshooting

Use this reference when a Hermes profile using an Ollama-hosted model fails with `HTTP 401 Unauthorized`, or when switching cloud models in one profile works while another profile fails.

## Two Ollama providers in Hermes

Hermes has two distinct provider entries for Ollama:

| Provider | Endpoint | Auth mechanism | When to use |
|----------|----------|----------------|-------------|
| `ollama-launch` | `http://127.0.0.1:11434/v1` | Local `ollama` daemon + `ollama signin` cloud session | Local Ollama is running and can pull/run models |
| `ollama-cloud` | `https://ollama.com/v1` | `OLLAMA_API_KEY` from the active profile's `.env` | Direct cloud API; bypasses local daemon |

A cloud model is requested by appending `:cloud` to the model name, e.g. `kimi-k2.7-code:cloud`. The local daemon sees the `:cloud` suffix and proxies the request to `ollama.com` using its own signed-in session.

## Profile `.env` isolation

Each Hermes profile has its own `.env`:

```
~/.hermes/.env                          # default / root profile
~/.hermes/profiles/<name>/.env          # named profile
```

When a profile is active, Hermes reads that profile's `.env`. If the keys differ, switching profiles effectively switches Ollama accounts even though `ollama signin` did not change.

## Common failure pattern

**Symptom:** one profile (e.g. `maximus`) works with `kimi-k2.7-code:cloud`, but another profile (e.g. `shifu`) returns `HTTP 401 Unauthorized` when changing the model to a different cloud model such as `gemma4:cloud`.

**Root cause:** the failing profile's `.env` contains an `OLLAMA_API_KEY` belonging to a different Ollama account than the currently signed-in local session, or the model tag does not exist.

### Diagnosis

1. Compare keys across profiles:
   ```bash
   grep OLLAMA_API_KEY ~/.hermes/.env \
     ~/.hermes/profiles/shifu/.env \
     ~/.hermes/profiles/maximus/.env \
     ~/.hermes/profiles/ugwey/.env 2>/dev/null
   ```

2. Check which account the local Ollama daemon considers active:
   ```bash
   ollama list
   curl -s http://127.0.0.1:11434/v1/models | python3 -m json.tool | head -40
   ```

3. Verify the exact model tag before changing config:
   ```bash
   ollama list | grep -i gemma
   # or pull to see the real error
   ollama pull gemma4:cloud
   ```

### Fixes

**A. Make the profile use the active account**

Copy the working key into the failing profile:

```bash
cp ~/.hermes/.env ~/.hermes/profiles/shifu/.env
```

Or edit only the key:

```bash
# read current active key
grep OLLAMA_API_KEY ~/.hermes/.env
# write it into the target profile
sed -i 's/^OLLAMA_API_KEY=.*/OLLAMA_API_KEY=<active-key>/' ~/.hermes/profiles/shifu/.env
```

Then start a new session (`/new` in CLI or restart the WebUI/gateway session).

**B. Bypass the local daemon entirely**

Switch the profile to direct cloud API so auth depends only on `OLLAMA_API_KEY`:

```yaml
model:
  provider: ollama-cloud
  base_url: https://ollama.com/v1
  default: gemma4:27b   # use the real tag, not :cloud
```

Apply with:

```bash
hermes config set model.provider ollama-cloud
hermes config set model.base_url https://ollama.com/v1
hermes config set model.default gemma4:27b
```

Then `/new` or restart the relevant Hermes process.

### Model-tag pitfall

`:cloud` is not a universal model tag. It works only for models Ollama exposes as cloud-proxied variants. For `gemma4` the correct tags are ordinary ones such as `gemma4`, `gemma4:4b`, `gemma4:9b`, `gemma4:27b`, etc. Verify with:

```bash
ollama list | grep gemma
ollama show gemma4 --modelfile 2>/dev/null | head -20
```

Using a non-existent tag often surfaces as a 401 because the local daemon cannot authorize a model it cannot find in the cloud catalog.

### Quick profile key sync

If all profiles should share one Ollama account:

```bash
for p in shifu maximus ugwey; do
  [ -d ~/.hermes/profiles/$p ] && cp ~/.hermes/.env ~/.hermes/profiles/$p/.env
done
```

If profiles intentionally use different accounts, keep separate keys but remember that switching profile also switches the API key Hermes sees.

## Verification

After any change:

```bash
hermes config get model.default
hermes config get model.provider
grep OLLAMA_API_KEY ~/.hermes/profiles/$(hermes profile list | grep '\*' | awk '{print $2}')/.env 2>/dev/null || grep OLLAMA_API_KEY ~/.hermes/.env
```

Then run a single-turn test:

```bash
hermes chat -q 'say hi'
```

## Notes

- This reference was created from a session where profile `shifu` had a stale `OLLAMA_API_KEY` while `maximus` shared the default profile's key.
- WebUI and gateway sessions read `.env` at startup; config changes and key changes require a new session or restart to take effect.
