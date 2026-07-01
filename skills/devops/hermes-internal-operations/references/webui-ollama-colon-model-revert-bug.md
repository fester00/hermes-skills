# WebUI Cross-Provider Model Reverts to Default — Ollama `:` Tags

Use this reference when a Hermes WebUI session silently switches the selected model back to the profile default after the first assistant response, especially with Ollama-family models.

## Symptom

1. User opens Hermes WebUI (separate `~/hermes-webui` install).
2. Switches to a profile whose `model.provider` is `ollama-launch` (local daemon) and `model.default` is some cloud model, e.g. `kimi-k2.7-code:cloud`.
3. From the model picker, selects a model from a *different* provider group, e.g. `gemma4:31b` under **Ollama Cloud**.
4. First request goes out and returns an answer.
5. Immediately after, the composer chip/dropdown snaps back to `kimi-k2.7-code:cloud`.

## Root cause

Ollama model IDs contain a colon (`gemma4:31b`, `qwen3.5:397b`, `kimi-k2.6:cloud`).

The WebUI stores an explicit cross-provider pick as an internal `@provider:model` string:

```text
@ollama-cloud:gemma4:31b
```

On subsequent turns the server re-resolves the session model. The resolver `_split_provider_qualified_model()` in `api/routes.py` uses `rsplit(":", 1)` to split provider from model. Because the model itself contains `:`, it mis-parses the string:

| Input | Parsed provider | Parsed model |
|-------|-----------------|--------------|
| `@ollama-cloud:gemma4:31b` | `ollama-cloud:gemma4` | `31b` |

`ollama-cloud:gemma4` is not a known provider, so the "repair stale models" path concludes the selection is invalid and reverts the session to the profile's `default_model`.

A direct Python reproduction:

```python
import os, sys
sys.path.insert(0, '/home/natan/hermes-webui')
os.environ['HERMES_HOME'] = '/home/natan/.hermes/profiles/shifu'
from api.routes import _resolve_compatible_session_model_state

model, provider, normalized = _resolve_compatible_session_model_state(
    '@ollama-cloud:gemma4:31b',
    'ollama-launch',
    profile_provider='ollama-launch',
    profile_default_model='kimi-k2.7-code:cloud',
    explicit_model_pick=False,
    prefer_cached_catalog=True,
)
print(model, provider, normalized)
# -> kimi-k2.7-code:cloud None True
```

The bug fires on non-explicit resolves (second turn, session reload, dropdown refresh), not on the first explicit user pick.

## Affected code

| File | Function | Problem |
|------|----------|---------|
| `api/routes.py` | `_split_provider_qualified_model()` | `rsplit(":", 1)` cannot distinguish provider separator from model-tag colon |
| `api/config.py` | `resolve_model_provider()` | Has a fallback for the same issue but only for runtime routing, not session normalization |
| `static/ui.js` | `_providerFromModelValue()`, `_modelStateForSelect()` | Same naive `:` split; can mis-attribute provider context |

## Immediate workarounds

### 1. Stay on the active provider's own models

If the profile is `ollama-launch`, pick only models from the **Ollama Launch** group (the local daemon's cloud-proxied list). Those IDs are usually already prefixed so the provider matches `model.provider`.

### 2. Switch the profile to the provider you actually want

If you intend to use `ollama-cloud` models, set the profile default provider to `ollama-cloud`:

```bash
hermes profile use shifu
hermes config set model.provider ollama-cloud
hermes config set model.base_url https://ollama.com/v1
hermes config set model.default gemma4:31b
```

Then restart the WebUI session. Now the active provider matches the picker group and the repair path is not triggered.

### 3. Use a model alias without the colon

Add a `model.aliases` entry that maps a clean local name to the real Ollama tag:

```yaml
model:
  provider: ollama-cloud
  base_url: https://ollama.com/v1
  default: gemma4-31b
  aliases:
    gemma4-31b: gemma4:31b
```

The alias key has no `:`, so the WebUI's provider-qualified parser handles it correctly, while the real model ID is sent to the API.

### 4. Bypass WebUI picker for this model

Use the CLI for models that contain `:` when the WebUI picker is misbehaving:

```bash
hermes chat -m gemma4:31b --provider ollama-cloud -q "your prompt"
```

## Permanent fix

The parser needs to treat the first `:` after `@provider:` as the provider/model boundary when the provider part is a known Hermes provider slug, and fall back only when the candidate provider is unrecognized.

Conceptual patch outline (server side):

```python
def _split_provider_qualified_model(model: str) -> tuple[str, str | None]:
    model = str(model or "").strip()
    if not (model.startswith("@") and ":" in model):
        return model, None
    inner = model[1:]
    # Try the first segment as the provider.
    provider_hint, bare_model = inner.split(":", 1)
    if _provider_is_known_or_configured(provider_hint):
        return bare_model.strip(), _clean_session_model_provider(provider_hint)
    # If the first segment is not a known provider, fall back to rsplit
    # for legacy/custom providers whose names may contain ':'.
    provider_hint, bare_model = inner.rsplit(":", 1)
    provider = _clean_session_model_provider(provider_hint)
    bare = bare_model.strip()
    if provider and bare:
        return bare, provider
    return model, None
```

A matching change is needed in `static/ui.js` (`_providerFromModelValue`, `_modelStateForSelect`) and in `api/config.py` (`_norm_model_id`) so the client and server agree on the boundary.

## How to verify before patching

Run the reproduction snippet above against the target profile. If it returns the default model instead of `@ollama-cloud:gemma4:31b`, the bug is present.

After a candidate fix, the same snippet should return:

```text
@ollama-cloud:gemma4:31b ollama-cloud False
```

and the WebUI dropdown should remain on `gemma4:31b` after the first assistant response.

## Related notes

- This is a server-side normalization bug, not an auth/key bug. Key-related 401s are covered in `ollama-provider-profile-auth.md`.
- The issue is most visible with Ollama because Ollama tags almost always contain `:`. Other providers with colon-bearing model IDs (e.g. some HuggingFace-style local-server IDs) may trigger the same class of bug.
- First-turn explicit picks survive because `explicit_model_pick=True` short-circuits the repair path. The revert happens on the second turn or on any session reload that re-runs `_resolve_compatible_session_model_state` with `explicit_model_pick=False`.
