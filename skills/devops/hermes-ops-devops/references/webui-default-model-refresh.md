# WebUI Default Model Refresh — Session Notes

Companion to the WebUI restart procedure in the main `hermes-ops-devops` skill.

## What happened

- `~/.hermes/config.yaml` already had `model.default: kimi-k2.7-code:cloud` and `model.provider: ollama-launch`.
- WebUI server-side settings (`load_settings()`) returned `default_model: kimi-k2.7-code:cloud`.
- But the user's browser picker still showed `kimi-k2.6`.

## Diagnosis

The server-side model catalog and default model were correct. The stale value was in the front-end state (likely `localStorage` or cached dropdown selection from the previous session).

## Commands used

```bash
# Invalidate model cache on the server
cd /home/natan/hermes-webui && python3 - <<'PY'
import sys
sys.path.insert(0, '/home/natan/hermes-webui')
from api.config import invalidate_models_cache
invalidate_models_cache()
PY

# Restart WebUI
systemctl --user restart hermes-webui.service
sleep 8
systemctl --user is-active hermes-webui.service
```

## Server-side verification

```bash
cd /home/natan/hermes-webui && python3 - <<'PY'
import sys
sys.path.insert(0, '/home/natan/hermes-webui')
from api.config import load_settings, get_available_models, invalidate_models_cache
invalidate_models_cache()
print('settings default_model:', load_settings().get('default_model'))
print('settings default_model_provider:', load_settings().get('default_model_provider'))
catalog = get_available_models()
print('catalog default_model:', catalog.get('default_model'))
print('catalog active_provider:', catalog.get('active_provider'))
PY
```

Output:
```
settings default_model: kimi-k2.7-code:cloud
settings default_model_provider: ollama-launch
catalog default_model: kimi-k2.7-code:cloud
catalog active_provider: ollama-launch
```

## Client-side fix

After server-side default is confirmed correct, if the browser still shows 2.6:

1. Hard refresh: `Ctrl + Shift + R` (Linux/Windows) / `Cmd + Shift + R` (macOS)
2. If still stale, clear storage and reload:
   ```javascript
   localStorage.clear();
   sessionStorage.clear();
   location.reload(true);
   ```
3. Or open WebUI in an incognito/private window.

## Key takeaway

When a user says "WebUI still shows the old model", first verify the server-side default with `load_settings()` / `get_available_models()`. If the server is correct, the problem is front-end cache, not config. Do not edit `config.yaml` again — clear browser state instead.

## See also

- Main skill: `hermes-ops-devops` → Section 3: WebUI Service Restart & Default Model Refresh
