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

`@opencode/cli` declares **two** bins, both pointing at the same binary: `opencode` and `opencode2`.

### Removing the legacy v1 package (done 2026-10-13)

The old `opencode-ai` (v1) package was uninstalled; globally only `@opencode/cli` (and the unrelated
`ai-sdk-provider-opencode-sdk`) remain. Delete v1 rather than updating it: both packages claim the bin
name `opencode`, so keeping both leaves a competing claim on PATH while the v1 binary is already unreachable.
`opencode-ai` pulls no dependencies, and nothing referenced it (npm deps, systemd units, crontab, profile
configs all clean). Rollback if ever needed: `npm install -g opencode-ai@1.18.35`.

> ⚠️ **npm uninstall trap — it removes the surviving bin link too.** Because npm tracks the bin *name*
> `opencode` against the removed package, `npm uninstall -g opencode-ai` deletes the shared symlink and
> leaves you with `opencode: command not found`, even though `@opencode/cli` is still installed. Re-run
> `npm install -g @opencode/cli@latest --force` to recreate both bins, then prove it with `opencode --version`
> and check every symlink (`ls -l $(dirname $(command -v node))/opencode*`). Any `npm uninstall -g` of a
> package that ever shared a bin name needs this re-link step.

## Profile-based configuration

Store provider-specific configs in `~/.config/opencode/profiles/` and switch with `OPENCODE_CONFIG`:

```bash
cd /path/to/project      # каталог проекта — это cwd; позиционного аргумента у `run` нет
OPENCODE_CONFIG=/home/natan/.config/opencode/profiles/opencodeai.json opencode run --standalone --auto "task"
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
- MCP servers may be declared either **flat** (`"mcp": { "<name>": {…} }`, the shape the docs use) or
  **nested** (`"mcp": { "servers": {…} }`). Both are accepted — what matters is the mandatory `type`
  (`local`/`remote`). Our profiles use the flat form and their servers connect.
- `timeout` in V2 is an object (`{ startup, catalog, execution }`), not a single number.
- `"enabled": true` is valid (the docs examples set it); absence also means enabled, and
  `"disabled": true` turns a server off.

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

## Provider `package` is mandatory in v2 — the Ollama trap

In v2 a `providers.<id>` block must resolve to a provider **package**; a block with only
`settings.baseURL` fails at model init with a confusing, near-empty error:

```
Error: Unsupported package for ollama/kimi-k2.7-code:cloud:
```

(`SessionRunnerModel.UnsupportedPackageError` — the trailing value after the colon is the package, empty
because none was resolved.) Verified 2026-10-13 on `profiles/ollama.json`: adding the block below made the
profile work again (`opencode run --standalone --auto -m ollama/kimi-k2.7-code:cloud "Reply with exactly: OLLAMA-OK"` → `OLLAMA-OK`).

```jsonc
{
  "providers": {
    "ollama": {
      "name": "Ollama (local proxy)",
      "package": "@opencode/ai/providers/openai-compatible",   // ← without this the model never initializes
      "env": ["OLLAMA_API_KEY"],
      "settings": { "baseURL": "http://127.0.0.1:11434/v1" },
      "models": { "kimi-k2.7-code:cloud": { "name": "kimi-k2.7-code:cloud", "limit": { "context": 256000, "output": 32768 } } }
    }
  }
}
```

`opencode-go` profiles need no package (built-in provider, `settings.apiKey` alone works), which is why
`opencodeai.json` / `opencodeai-rental.json` function while the Ollama one silently rotted.

Enumerate the package ids the installed binary actually supports (no docs needed):

```bash
BIN=$(readlink -f "$(command -v opencode)")
strings -n 6 "$BIN" | grep -oE '@opencode/ai/providers/[a-z0-9-]+' | sort -u
```

## Common mistakes

- Provider block with only `settings.baseURL` → `Unsupported package for <provider>/<model>:` — add `package` (see the section above).
- Running bare `opencode` (no `OPENCODE_CONFIG`) on this machine: the root configs are not a working entry point — `~/.config/opencode/opencode.jsonc` has the same package-less ollama provider and the run dies with `AI.Error.Authentication: Upstream request failed: Endpoint is unavailable.` Always pass a profile.
- Forgetting `--standalone` on a headless server → `Model exo-free has been deprecated`. It is only required when **no background service is running**; if the service is up, plain `opencode run -m <provider>/<model> "prompt"` works as a one-shot.
- Omitting `OPENCODE_CONFIG` when using a gateway model → `Error: Model unavailable: opencode-go/<model>`. The provider only exists inside a profile file; `opencode models` then shows built-ins only.
- Passing a project directory as an argument to `opencode run` → no such argument (`opencode run [flags] [<message...>]`); the working directory is the cwd, so `cd` into the project first. A positional path is silently swallowed into the message.
- Assuming the background service is up: check `ss -tlnp | grep 49374` and pass `--standalone` when it is not listening.
- Using `api.opencode.ai/v1` for OpenCode Go → auth/balance errors.
- Using `opencode-free` models → `FreeTierError`.
- Expecting OpenCode agents to see Hermes skills/memory — they do not; pass context via the task prompt.
- Forgetting the mandatory `type` (`local`/`remote`) on an MCP server, or misspelling the wrapper key →
  the server silently does not load. The nesting itself is never the problem: flat `mcp` and `mcp.servers`
  both work.
- Setting a flat `timeout: 30000` for an MCP server → V2 expects `{ startup, catalog, execution }`.
- Using `--config /path` — OpenCode CLI has no `--config` flag; use `OPENCODE_CONFIG` instead.

## Verification

```bash
cd /tmp/opencode-smoke
OPENCODE_GO_API_KEY=... \
OPENCODE_CONFIG=/home/natan/.config/opencode/profiles/opencodeai.json \
opencode run --standalone --auto "Create file done.txt with text OK"
```

## See also

- `autonomous-coding-agents` skill for agent selection and briefing.
- `references/opencode-skill-environment.md` for installing skills, plugins, and MCP servers on the agent.
- Hermes provider config in `~/.hermes/config.yaml` for available `opencode-go` model IDs.

## MCP profile check — do this FIRST

**Check the profile before promising vault/graph work, and never run without `OPENCODE_CONFIG`.**
The gateway provider (`opencode-go`) is defined *inside* a profile file: `opencode run -m opencode-go/<model>`
without `OPENCODE_CONFIG` fails with `Error: Model unavailable: opencode-go/<model>`, and plain
`opencode models` lists only built-in providers (ollama + the free tier).

Verified map (2026-10-13, after the 2.0.28 update) — MCP servers are declared by almost every profile:

| Config | model | MCP servers |
|---|---|---|
| `profile/opencodeai.json` | `opencode-go/deepseek-v4.1-flash` | codebase-memory, obsidian |
| `profiles/opencodeai-rental.json` | `opencode-go/deepseek-v4.1-flash` | codebase-memory, obsidian |
| `profiles/opencodeai-test.json` | `opencode-go/deepseek-v4-flash` | codebase-memory, obsidian |
| `profiles/opencodeai-ling.json` | `opencode-go/gemini-3.7-flash` | codebase-memory, obsidian |
| `profiles/ollama.json` | `ollama/kimi-k2.7-code:cloud` | codebase-memory, obsidian |
| `opencode.jsonc` (root) | `ollama/kimi-k2.7-code:cloud` | codebase-memory, obsidian |
| `opencode.json` (root) | — | codebase-memory-mcp |
| `profiles/opencode-free.json` | `opencode-free/ling-3.1-flash-free` | **none** |

Re-derive this map instead of trusting the table (profiles drift):

```bash
for f in ~/.config/opencode/profiles/*.json ~/.config/opencode/opencode.json*; do
  python3 -c "import json,re,sys;p=sys.argv[1];t=open(p,encoding='utf-8').read();\
 t='\n'.join(re.sub(r'^\s*//.*$','',l) for l in t.splitlines());d=json.loads(t);\
 m=d.get('mcp') or {};s=m.get('servers') if 'servers' in m else m;\
 print(p.split('/')[-1], d.get('model'), list(s) if isinstance(s,dict) else None)" "$f"
done
```

Strip **line-level** comments only — a naive `re.sub(r'//.*','',text)` eats the `//` inside `https://…`
and every profile then reports a parse error.

Before promising an agent any vault/graph work:

```bash
OPENCODE_CONFIG=<profile with mcp.servers> opencode run --auto -m opencode-go/claude-haiku-5-5 \
  "Call the obsidian MCP tool that lists vaults, then codebase-memory list_projects. Report results."
```

Verified 2026-10-11 on `opencode-go/claude-haiku-5-5`: obsidian → `list-available-vaults` →
`obsidian-memory`; codebase-memory → `list_projects` → 4 projects. Tool names in OpenCode are
kebab-case (`list-available-vaults`), and agents can call them in one `execute` block via `tools.<server>[...]`.

Also note: the background service (`opencode.exe serve --service`, `127.0.0.1:49374`) is usually up, so
`--standalone` is not needed for one-shot runs.

## OPENCODE_CONFIG does not isolate — root configs silently wipe a profile's `providers`

Verified 2026-10-13 on 2.0.28. A profile passed via `OPENCODE_CONFIG` is **merged with** `~/.config/opencode/opencode.json`
and `opencode.jsonc`, not substituted for them. Merge is deep for `mcp` but the `providers` object behaves
as last-document-wins, so a profile's `providers` block disappears when a root config also defines `providers`:

```bash
OPENCODE_CONFIG=~/.config/opencode/profiles/opencodeai.json opencode models   # → no opencode-go/* at all
OPENCODE_CONFIG=~/.config/opencode/profiles/opencodeai.json opencode run --auto -m opencode-go/deepseek-v4.1-flash "hi"
# → Error: Model unavailable: opencode-go/deepseek-v4.1-flash
OPENCODE_CONFIG=~/.config/opencode/profiles/opencodeai.json opencode debug config | grep -A3 providers
# → the merged doc shows only providers.ollama from the root opencode.jsonc
```

Proof the profile itself is fine — run it with an isolated HOME (`--standalone` is required there, because
the real background service already owns 49374):

```bash
HOME=/tmp/oc-home OPENCODE_CONFIG=~/.config/opencode/profiles/opencodeai.json opencode models --standalone
# → opencode-go/claude-haiku-5-5, opencode-go/deepseek-v4.1-flash, opencode-go/glm-5.3, …
```

Fixes, in order of preference: state the provider in the root `opencode.json` (chain-wide), remove the
conflicting `providers` block from root `opencode.jsonc`, or isolate the environment
(`HOME`/`XDG_CONFIG_HOME`) per profile. Do not "fix" the profile file — it is not the broken part.

## v2 schema and CLI details that differ from the docs

- Both shapes are accepted for MCP: flat `"mcp": { "<name>": {…} }` (as in the docs and in our profiles) and
  nested `"mcp": { "servers": { … } }`. `"enabled": true` is valid and used in the docs examples.
- `opencode mcp debug <server>` is documented but **absent** in 2.0.28 (`Unknown subcommand "debug"`).
  Useful replacements: `opencode mcp list`, `opencode debug agents` (agent ids, modes, resolved permissions),
  `opencode debug paths` (data/config/cache/state/db locations), `opencode debug config` (merged documents).
- Commands documented but missing in 2.0.28: `agent`, `attach`, `export`, `import`, `github`, `tui`, `web`.
  Present but absent from `docs/cli`: `api`, `debug`, `mini`, `pair`, `plugin`, `reload`, `service`, `update`.
  The docs describe the whole product (TUI + web + desktop), the CLI is narrower — check `opencode <cmd> --help`
  before promising a command exists.
- A first `opencode mcp list` may print `No MCP servers configured` while servers are configured; repeated
  calls show them as `connected`. Never conclude MCP is missing from a single call.
- Docs mirror for offline reading (Russian + English, refreshed by `regen.sh`):
  `/mnt/data/natan-storage/docs/opencode-v2/`; consolidated Russian digest:
  `~/obsidian-memory/Knowledge/OpenCode v2 — устройство, CLI, отличия от субагентов.md`.

## Documentation — read the source, do not scrape it

The docs site serves every page as **raw Markdown**, so no HTML stripping, no browser, no proxy tricks:

```bash
curl -sL --noproxy '*' https://opencode.ai/docs/cli.md        # English original
curl -sL --noproxy '*' https://opencode.ai/docs/ru/agents.md  # official Russian translation
```

- Enumerate the page list from `https://opencode.ai/docs/sitemap-index.xml` → `sitemap-0.xml`.
  The canonical set (~33 pages): `index, cli, config, agents, mcp-servers, rules, permissions, skills,
  plugins, tools, custom-tools, commands, tui, server, sdk, models, providers, acp, troubleshooting,
  share, policies, network, ide, ecosystem, formatters, keybinds, lsp, web, enterprise, gitlab, github,
  references, windows-wsl, themes`.
- **Almost every page has an official Russian translation** under `/docs/ru/<page>.md`; only
  `providers`, `policies`, `references` and the root `index` are English-only. Config keys, flags and
  tool names stay Latin in the translation, so `search_files` with the exact key matches the Russian file too.
- Local mirror: `/mnt/data/natan-storage/docs/opencode-v2/` — `ru/` (30 pages), `en/` (34), plus a
  `README.md` mapping question → page. Refresh it with `scripts/regen-docs.sh` (packaged with this skill;
  a copy sits in the mirror directory).
- Cite the mirror path rather than a URL when a fact comes from the docs — it stays readable offline and
  survives link rot (search it with `search_files`, path `/mnt/data/natan-storage/docs/opencode-v2`).

Two fetch-script traps that cost a re-download (`scripts/regen-docs.sh` encodes both):

- `local url="$1" dest="$2" tmp="$TMP/$(basename "$dest")"` fails with `dest: unbound variable` under
  `set -u` on bash 5 — expand each variable in its own `local` line.
- Never `rm` the destination when a fetch fails: download to a temp file, validate it (`http 200`,
  size > 500, body is not a `{"status"...}` 404 payload), then `mv` it into place. A bare
  `curl -o dest` + `rm -f dest` on failure deletes pages that were already mirrored.

## Service, sessions, and what lives where

- Background server: `opencode service status|start|stop|restart|get`. When up it listens on
  `127.0.0.1:49374` (process shows as `opencode.exe`), and a one-shot `opencode run` then needs no
  `--standalone`. Prove it with `ss -tlnp | grep 49374`.
- Sessions: `opencode session list|delete|export|import` — `list` shows the current project's top-level
  sessions newest-first; `delete` also removes their child sessions.
- Other subcommands worth knowing: `api` (request against the running server), `debug`, `stats`, `mini`,
  `pair` (one-time links for browser/app), `serve [--hostname --port --cors --service --stdio]`,
  `plugin list|add|check|update|remove`, `mcp list|add|auth|logout`,
  `auth list|login|logout|export|import|switch`, `upgrade|update`, `uninstall`, `reload`, `acp`.
- Install map — what an OpenCode agent can see on this machine:
  - `~/.config/opencode/AGENTS.md` — global rules file, injected into every session (here it carries the
    codebase-memory "prefer graph tools over grep" policy).
  - `~/.config/opencode/skills/<name>/SKILL.md` — OpenCode's own skills. `opencode plugin list` printing
    "No plugins found" says nothing about this directory: plugins and skills are separate mechanisms.
  - `~/.config/opencode/agents/*.md` — agent definitions; project-level ones go in `.opencode/agents/`.
  - `~/.local/share/opencode/` — `opencode.db` (sessions), `storage/`, `tool-output/`, `shell/`, and
    `snapshot/` (file snapshots, hundreds of MB — check it before blaming npm for a full root).
- What an agent can see versus a Hermes subagent, and which engine to run:
  `superpowers-workflow/references/opencode-vs-subagents.md`.
