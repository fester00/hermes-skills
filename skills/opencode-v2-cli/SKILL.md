---
name: opencode-v2-cli
description: Use when configuring or troubleshooting OpenCode CLI v2 profiles and MCP servers.
version: 1.0.0
author: Master Ugwai
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [opencode, agents, coding-agents, v2, cli, mcp]
    related_skills: [autonomous-coding-agents, opencode]
---

# OpenCode CLI v2

Configure and troubleshoot OpenCode CLI v2 (`@opencode/cli`) as a standalone coding agent.

## Migration from v1

- v1 package: `opencode-ai` (binary `opencode` 1.x)
- v2 package: `@opencode/cli` (binary `opencode` v2.x)
- v2 uses `providers` + `settings`, not legacy `provider` + `options`.
- v2 requires `--standalone` when no background service is running, otherwise it tries deprecated `exo-free` and fails.

## Installation

```bash
npm install -g @opencode/cli@latest --force
opencode --version   # should show v2.x
```

## Profile-based configuration

Store provider-specific configs in `~/.config/opencode/profiles/` and switch with `OPENCODE_CONFIG`:

```bash
OPENCODE_CONFIG=/home/natan/.config/opencode/profiles/opencodeai.json opencode run --standalone --auto /project "task"
```

## Profile 1: OpenCode Go

File `~/.config/opencode/profiles/opencodeai.json` (or `opencodeai-rental.json`):

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode-go/deepseek-v4.1-flash",
  "providers": {
    "opencode-go": {
      "settings": {
        "apiKey": "{env:OPENCODE_GO_API_KEY}"
      }
    }
  },
  "mcp": {
    "servers": {
      "codebase-memory": {
        "type": "local",
        "command": ["/home/natan/.local/bin/codebase-memory-mcp"],
        "timeout": {
          "startup": 30000,
          "catalog": 30000,
          "execution": 30000
        }
      },
      "obsidian": {
        "type": "local",
        "command": [
          "/home/natan/.nvm/versions/node/v24.13.1/bin/node",
          "/home/natan/.nvm/versions/node/v24.13.1/lib/node_modules/obsidian-mcp/build/main.js",
          "/home/natan/obsidian-memory"
        ],
        "timeout": {
          "startup": 30000,
          "catalog": 30000,
          "execution": 30000
        }
      }
    }
  }
}
```

Key points:
- Use `https://opencode.ai/zen/go/v1` — not `https://api.opencode.ai/v1`.
- In V2, MCP servers belong under `mcp.servers` with a mandatory `type` field.
- `timeout` in V2 is an object (`{ startup, catalog, execution }`), not a single number.
- Do not set `enabled: true`; absence means enabled, use `disabled: true` to turn a server off.

## Profile 2: Ollama

File `~/.config/opencode/profiles/ollama.json`:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "ollama/kimi-k2.7-code:cloud",
  "providers": {
    "ollama": {
      "settings": {
        "baseURL": "http://127.0.0.1:11434/v1"
      },
      "models": {
        "kimi-k2.7-code:cloud": {
          "name": "kimi-k2.7-code:cloud",
          "limit": { "context": 256000, "output": 32768 }
        }
      }
    }
  },
  "mcp": { /* same as above */ }
}
```

## Free-tier limitation

OpenCode Free models (`opencode-free/*-free`, endpoint `https://opencode.ai/zen/v1`) return:

```
FreeTierError: OpenCode's free tier can only be used from within OpenCode
```

when called from Hermes or standalone OpenCode CLI. They only work inside the official OpenCode Desktop/Web app. Do not spend time trying to make them work from external agents.

## Gateway models as a general-purpose LLM endpoint

The `opencode-go` provider is not only for coding agents — it is also the way to reach models
the user holds **no direct vendor API key** for. Anthropic models, for example, are reachable as
`opencode-go/claude-haiku-5-5` even with no `ANTHROPIC_API_KEY` anywhere in the Hermes profiles.

Enumerate what the gateway actually serves before telling the user a model is unavailable:

```bash
opencode models | grep -iE 'claude|gemini|gpt'    # exact provider/model IDs
```

One-shot use, no server to start and no `--standalone` needed when the background service is
already up — the cheapest way to run a single prompt against a gateway model:

```bash
opencode run -m opencode-go/claude-haiku-5-5 "$(cat prompt.txt)" > out.txt 2> err.txt
```

Useful when a task needs a model that exists only as a hosted API (comparisons, translation
checks, a second opinion) and starting a full coding session would be overkill. Note the model
runs inside OpenCode's own harness, so output carries OpenCode's agent framing — treat prompt
adherence results from it as close to, but not identical with, a raw API call, and say so if a
comparison depends on it.

## Common mistakes

- Forgetting `--standalone` on a headless server → `Model exo-free has been deprecated`. It is only required when **no background service is running**; if the service is up, plain `opencode run -m <provider>/<model> "prompt"` works as a one-shot.
- Using `api.opencode.ai/v1` for OpenCode Go → auth/balance errors.
- Using `opencode-free` models → `FreeTierError`.
- Expecting OpenCode agents to see Hermes skills/memory — they do not; pass context via the task prompt.
- Putting MCP servers at the root of `mcp` instead of under `mcp.servers` → V2 ignores them or fails schema validation.
- Setting a flat `timeout: 30000` for an MCP server → V2 expects `{ startup, catalog, execution }`.
- Using `--config /path` — OpenCode CLI has no `--config` flag; use `OPENCODE_CONFIG` instead.

## Verification

```bash
OPENCODE_GO_API_KEY=... \
OPENCODE_CONFIG=/home/natan/.config/opencode/profiles/opencodeai.json \
opencode run --standalone --auto /tmp/opencode-smoke "Create file done.txt with text OK"
```

## See also

- `autonomous-coding-agents` skill for agent selection and briefing.
- `references/opencode-skill-environment.md` for installing skills, plugins, and MCP servers on the agent.
- Hermes provider config in `~/.hermes/config.yaml` for available `opencode-go` model IDs.
