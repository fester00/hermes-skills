# OpenCode provider configuration patterns

## CLI versions and packages

OpenCode has two incompatible CLI generations in npm:

- **V1:** package `opencode-ai` (binary `opencode --version` reports something like `1.18.x`).
- **V2:** package `@opencode/cli` (binary `opencode --version` reports `opencode v2.x.x`).

`opencode.ai` cloud providers (`opencode-go`, `opencode-zen`, etc.) and the V2 config schema require **V2 CLI**. If the installed CLI is V1, V2 provider blocks will be silently downgraded (`Omitted native setting that cannot be represented in V1`) or fail with provider/model not found.

Install or switch to V2 with `--force`, because V1 and V2 share the `opencode` binary name:

```bash
npm install -g @opencode/cli@latest --force
opencode --version   # expect "opencode v2.x.x"
```

If V1 must remain for legacy profiles, avoid mixing them under the same `opencode` binary; V2 replaces V1 in `$PATH` after `--force`.

## Built-in providers

OpenCode V2 ships with built-in provider definitions. Prefer them over hand-rolled provider blocks.

| Provider | Config key | Credential env var |
|---|---|---|
| OpenCode AI / opencode.ai | `opencode` | `OPENCODE_API_KEY` or `apiKey` in config |
| Ollama | `ollama` | none (local) |

Do not invent an npm package name for the OpenCode AI provider. The correct V2 config uses the built-in provider key with just `apiKey`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode-go/claude-sonnet-4",
  "providers": {
    "opencode-go": {
      "settings": {
        "apiKey": "oc_sk_..."
      }
    }
  }
}
```

For the base `opencode` provider (not `opencode-go`), the same pattern applies with provider key `opencode`.

## Hermes / OpenCode WebUI provider endpoints

The Hermes WebUI and the official OpenCode cloud providers use a `/zen` routing layer, not the raw `api.opencode.ai` endpoint. When configuring a custom OpenAI-compatible provider for `opencode-go` or `opencode-zen`, set the base URL that matches the Hermes provider definition:

| Provider | Hermes `api` value | Use in custom V2 config |
|---|---|---|
| `opencode-go` | `https://opencode.ai/zen/go/v1` | `settings.baseURL` |
| `opencode-zen` | `https://opencode.ai/zen/v1` | `settings.baseURL` |

When using the **built-in** V2 provider, you do not need `baseURL`; the CLI resolves the endpoint from the provider catalog. If you see `Insufficient account funds` or `Model is unavailable` with the default `api.opencode.ai/v1` endpoint, switch to the `/zen/go/v1` URL instead.

## Known opencode-go model IDs

The models available under `opencode-go` match the catalog in the Hermes `providers.opencode-go.models` list. Common working IDs include:

```text
deepseek-v4.1-flash
deepseek-v4-pro
deepseek-v4-flash
deepseek-flash
kimi-k2.6
kimi-k2.7-code
kimi-k3
glm-5.1, glm-5.2, glm-5.3, glm-5.3-flash
mimo-v2.5, mimo-v2.6-flash, mimo-v2.5-pro, mimo-v2.6-pro
qwen3.6-plus, qwen3.7-plus, qwen3.7-max, qwen3.8-max, qwen3.8-flash
minimax-m2.5, minimax-m2.7, minimax-m3
grok-4.6, grok-4.7
hy3, hy4-preview, space-bunny
```

There is no `ling-3.1-flash` in `opencode-go`; do not request it. The free-tier names such as `opencode/ling-3.1-flash-free` are part of the separate `opencode` free provider and are not guaranteed to be available for API keys tied to a paid Go subscription.

## Built-in vs free providers

OpenCode V2 includes both paid cloud providers (e.g. `opencode-go`) and a default free provider (`exo-free`). The free provider has been deprecated; a V2 install that has not selected a model will fail with `Model exo-free has been deprecated`. Always set an explicit `model` in the active config, or pass `--model provider/model` on the command line.

## Avoiding the deprecated free default

V2 `opencode run` without `--standalone` connects to the background service, which may default to the deprecated `exo-free` provider and fail with `Model exo-free has been deprecated`. For headless, one-shot tasks, always pass `--standalone` and either set `model` in the active config or pass `--model provider/model`:

```bash
OPENCODE_CONFIG=/home/natan/.config/opencode/profiles/opencodeai.json \
opencode run --standalone --auto /path/to/project "prompt"
```

## Selecting a configuration file

OpenCode does not support a `--config` CLI flag. Override the active config with the environment variable `OPENCODE_CONFIG`:

```bash
OPENCODE_CONFIG=/home/natan/.config/opencode/profiles/opencodeai.json \
opencode run --auto /path/to/project "prompt"
```

Keep profile configs under `~/.config/opencode/profiles/<name>.json`. The default config stays at `~/.config/opencode/opencode.json`.

## MCP servers in profile configs

Attach `codebase-memory` and `obsidian` MCP servers directly to a profile so every `opencode run` invocation inherits them:

```json
{
  "mcp": {
    "codebase-memory": {
      "type": "local",
      "enabled": true,
      "command": ["/home/natan/.local/bin/codebase-memory-mcp"],
      "timeout": 30000
    },
    "obsidian": {
      "type": "local",
      "enabled": true,
      "command": [
        "/home/natan/.nvm/versions/node/v24.13.1/bin/node",
        "/home/natan/.nvm/versions/node/v24.13.1/lib/node_modules/obsidian-mcp/build/main.js",
        "/home/natan/obsidian-memory"
      ],
      "timeout": 30000
    }
  }
}
```

Verify that both binaries exist before running; `opencode` will fail to initialize the provider session if an enabled MCP command is missing.

## Verifying a profile

1. Inspect the resolved config:
   ```bash
   OPENCODE_CONFIG=/path/to/profile.json opencode debug config
   ```

2. List available models for a provider:
   ```bash
   OPENCODE_API_KEY=... opencode models opencode
   ```

3. Run a tiny smoke test that writes one file:
   ```bash
   mkdir -p /tmp/opencode-smoke
   cd /tmp/opencode-smoke
   OPENCODE_CONFIG=/path/to/profile.json opencode run --standalone --auto . \
     "Create file smoke.txt with content OPENCODE_SMOKE_OK"
   cat smoke.txt
   ```

V2 `run` syntax is `opencode run [flags] <directory> "prompt"`, not `opencode --dir <dir> run "prompt"`. The `--dir` flag does not exist in V2.

## Common API errors from the provider

| Error | Meaning | Action |
|---|---|---|
| `Failed to initialize provider: opencode` | Built-in provider not selected or wrong `npm`/`package` field in config | Use provider key `opencode` / `opencode-go`, no `npm` or `package` field |
| `Omitted native setting that cannot be represented in V1` | Installed CLI is V1 (`opencode-ai`) but config uses V2 `providers` schema | Upgrade to V2 CLI: `npm install -g @opencode/cli@latest --force` |
| `ProviderModelNotFoundError` | Model ID does not exist in the connected provider's catalog | List models with `opencode models <provider>` and pick an existing one |
| `D.languageModel is not a function` | Config references an external SDK provider package that is incompatible with the installed CLI version | Switch to the built-in `opencode` provider; do not use third-party SDK packages for CLI |
| `Model exo-free has been deprecated` | No model selected; V2 defaulted to the deprecated free provider | Set explicit `model` in config or pass `--model provider/model`; use `--standalone` for headless |
| `Model access is disabled` | The API key does not have permission for this model | Pick a different model or check account entitlements |
| `Insufficient account funds` | Account balance is zero/negative, or wrong endpoint (e.g. `api.opencode.ai/v1`) | Switch to `https://opencode.ai/zen/go/v1` for `opencode-go`; otherwise add funds |
| `Model is unavailable` | Model is temporarily unavailable, not provisioned, or ID is wrong | Try a different model or verify the exact ID in Hermes `providers.opencode-go.models` |
| `Endpoint is unavailable` | The requested free-tier endpoint is down or blocked for the key | Use a paid Go model instead |

## Free-tier restriction

`opencode-free` models (e.g. `ling-3.1-flash-free`, `mimo-v2.6-flash-free`) return:

```
FreeTierError: OpenCode's free tier can only be used from within OpenCode
```

The free tier is **only usable from the official OpenCode desktop or web app**. It does not work through the OpenCode CLI, Hermes, or any third-party client, because the API enforces client-origin validation. Do not attempt to make `opencode-free` work in `opencode run` or in Hermes WebUI; switch to a paid `opencode-go` model, an Ollama local model, or a custom provider with your own API key.

## `opencode serve` flags

V2 `opencode serve` does **not** accept `--standalone`. The supported flags are `--hostname`, `--port`, `--cors`, `--service`, and `--stdio`. Passing `--standalone` produces `Unrecognized flag: --standalone` and the server exits.

```bash
# Correct
opencode serve --port 14124

# Wrong
opencode serve --standalone --port 14124
```

## Avoid installing the wrong provider package

The package `ai-sdk-provider-opencode-sdk` is a third-party Vercel AI SDK adapter, not the official OpenCode CLI provider. Installing it globally does not make `opencode` CLI work with `opencode.ai`; it can cause `D.languageModel is not a function` errors if referenced in config. Remove it if it was installed while debugging:

```bash
npm uninstall -g ai-sdk-provider-opencode-sdk
```

The official CLI communicates with opencode.ai via its built-in provider. Third-party SDK packages are for use inside other AI SDK applications, not inside the OpenCode CLI.
