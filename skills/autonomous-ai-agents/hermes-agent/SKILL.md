---
name: hermes-agent
description: Complete guide to using and extending Hermes Agent — CLI usage, setup, configuration, spawning additional agents, gateway platforms, skills, voice, tools, profiles, and a concise contributor reference. Load this skill when helping users configure Hermes, troubleshoot issues, spawn agent instances, or make code contributions.
version: 2.0.0
author: Hermes Agent + Teknium
license: MIT
metadata:
  hermes:
    tags: [hermes, setup, configuration, multi-agent, spawning, cli, gateway, development]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [claude-code, codex, opencode]
---

# Hermes Agent

Hermes Agent is an open-source AI agent framework by Nous Research that runs in your terminal, messaging platforms, and IDEs. It belongs to the same category as Claude Code (Anthropic), Codex (OpenAI), and OpenClaw — autonomous coding and task-execution agents that use tool calling to interact with your system. Hermes works with any LLM provider (OpenRouter, Anthropic, OpenAI, DeepSeek, local models, and 15+ others) and runs on Linux, macOS, and WSL.

What makes Hermes different:

- **Self-improving through skills** — Hermes learns from experience by saving reusable procedures as skills. When it solves a complex problem, discovers a workflow, or gets corrected, it can persist that knowledge as a skill document that loads into future sessions. Skills accumulate over time, making the agent better at your specific tasks and environment.
- **Persistent memory across sessions** — remembers who you are, your preferences, environment details, and lessons learned. Pluggable memory backends (built-in, Honcho, Mem0, and more) let you choose how memory works.
- **Multi-platform gateway** — the same agent runs on Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, and 10+ other platforms with full tool access, not just chat.
- **Provider-agnostic** — swap models and providers mid-workflow without changing anything else. Credential pools rotate across multiple API keys automatically.
- **Profiles** — run multiple independent Hermes instances with isolated configs, sessions, skills, and memory.
- **Extensible** — plugins, MCP servers, custom tools, webhook triggers, cron scheduling, and the full Python ecosystem.

People use Hermes for software development, research, system administration, data analysis, content creation, home automation, and anything else that benefits from an AI agent with persistent context and full system access.

**This skill helps you work with Hermes Agent effectively** — setting it up, configuring features, spawning additional agent instances, troubleshooting issues, finding the right commands and settings, and understanding how the system works when you need to extend or contribute to it.

**Docs:** https://hermes-agent.nousresearch.com/docs/

## Quick Start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Interactive chat (default)
hermes

# Single query
hermes chat -q "What is the capital of France?"

# Setup wizard
hermes setup

# Change model/provider
hermes model

# Check health
hermes doctor
```

---

## CLI Reference

### Global Flags

```
hermes [flags] [command]

  --version, -V             Show version
  --resume, -r SESSION      Resume session by ID or title
  --continue, -c [NAME]     Resume by name, or most recent session
  --worktree, -w            Isolated git worktree mode (parallel agents)
  --skills, -s SKILL        Preload skills (comma-separate or repeat)
  --profile, -p NAME        Use a named profile
  --yolo                    Skip dangerous command approval
  --pass-session-id         Include session ID in system prompt
```

No subcommand defaults to `chat`.

### Chat

```
hermes chat [flags]
  -q, --query TEXT          Single query, non-interactive
  -m, --model MODEL         Model (e.g. anthropic/claude-sonnet-4)
  -t, --toolsets LIST       Comma-separated toolsets
  --provider PROVIDER       Force provider (openrouter, anthropic, nous, etc.)
  -v, --verbose             Verbose output
  -Q, --quiet               Suppress banner, spinner, tool previews
  --checkpoints             Enable filesystem checkpoints (/rollback)
  --source TAG              Session source tag (default: cli)
```

### Configuration

```
hermes setup [section]      Interactive wizard (model|terminal|gateway|tools|agent)
hermes model                Interactive model/provider picker
hermes config               View current config
hermes config edit          Open config.yaml in $EDITOR
hermes config set KEY VAL   Set a config value
hermes config path          Print config.yaml path
hermes config env-path      Print .env path
hermes config check         Check for missing/outdated config
hermes config migrate       Update config with new options
hermes login [--provider P] OAuth login (nous, openai-codex)
hermes logout               Clear stored auth
hermes doctor [--fix]       Check dependencies and config
hermes status [--all]       Show component status
```

### Tools & Skills

```
hermes tools                Interactive tool enable/disable (curses UI)
hermes tools list           Show all tools and status
hermes tools enable NAME    Enable a toolset
hermes tools disable NAME   Disable a toolset

hermes skills list          List installed skills
hermes skills search QUERY  Search the skills hub
hermes skills install ID    Install a skill (or direct URL: hermes skills install https://...)
hermes skills inspect ID    Preview without installing
hermes skills config        Enable/disable skills per platform
hermes skills check         Check for updates
hermes skills update        Update outdated skills
hermes skills uninstall N   Remove a hub skill
hermes skills publish PATH  Publish to registry
hermes skills browse        Browse all available skills
hermes skills tap add REPO  Add a GitHub repo as skill source
```

### MCP Servers

```
hermes mcp serve            Run Hermes as an MCP server
hermes mcp add NAME         Add an MCP server (--url or --command)
hermes mcp remove NAME      Remove an MCP server
hermes mcp list             List configured servers
hermes mcp test NAME        Test connection
hermes mcp configure NAME   Toggle tool selection
```

### Gateway (Messaging Platforms)

```
hermes gateway run          Start gateway foreground
hermes gateway install      Install as background service
hermes gateway start/stop   Control the service
hermes gateway restart      Restart the service
hermes gateway status       Check status
hermes gateway setup        Configure platforms
```

Supported platforms: Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix, Mattermost, Home Assistant, DingTalk, Feishu, WeCom, BlueBubbles (iMessage), Weixin (WeChat), API Server, Webhooks. Open WebUI connects via the API Server adapter.

Platform docs: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/

### Sessions

```
hermes sessions list        List recent sessions
hermes sessions browse      Interactive picker
hermes sessions export OUT  Export to JSONL
hermes sessions rename ID T Rename a session
hermes sessions delete ID   Delete a session
hermes sessions prune       Clean up old sessions (--older-than N days)
hermes sessions stats       Session store statistics
```

### Cron Jobs

```
hermes cron list            List jobs (--all for disabled)
hermes cron create SCHED    Create: '30m', 'every 2h', '0 9 * * *'
hermes cron edit ID         Edit schedule, prompt, delivery
hermes cron pause/resume ID Control job state
hermes cron run ID          Trigger on next tick
hermes cron remove ID       Delete a job
hermes cron status          Scheduler status
```

### Webhooks

```
hermes webhook subscribe N  Create route at /webhooks/<name>
hermes webhook list         List subscriptions
hermes webhook remove NAME  Remove a subscription
hermes webhook test NAME    Send a test POST
```

### Profiles

```
hermes profile list         List all profiles
hermes profile create NAME  Create (--clone, --clone-all, --clone-from)
hermes profile use NAME     Set sticky default
hermes profile delete NAME  Delete a profile
hermes profile show NAME    Show details
hermes profile alias NAME   Manage wrapper scripts
hermes profile rename A B   Rename a profile
hermes profile export NAME  Export to tar.gz
hermes profile import FILE  Import from archive
```

**Reference:** `references/webui-profile-switch-mechanics.md` — how Switch Profile works in WebUI, what it does and does not do, MCP/gateway interaction pitfalls, and real multi-agent parallelism options.

**Reference:** `references/webui-systemd-service.md` — WebUI deployed as systemd user service (`hermes-webui.service`). Covers `Restart=always` behavior, managing via `systemctl --user`, and the common pitfall where a manual `server.py` process conflicts with the service.

### Credential Pools

```
hermes auth add             Interactive credential wizard
hermes auth list [PROVIDER] List pooled credentials
hermes auth remove P INDEX  Remove by provider + index
hermes auth reset PROVIDER  Clear exhaustion status
```

### Other

```
hermes curator              Autonomous skill maintenance agent
hermes curator status       Rank skills by usage (most/least used)
hermes insights [--days N]  Usage analytics
hermes update               Update to latest version
hermes update --check       Preflight check before updating
hermes -z <prompt>          One-shot non-interactive mode (--model/--provider)
hermes pairing list/approve/revoke  DM authorization
hermes plugins list/install/remove  Plugin management
hermes honcho setup/status  Honcho memory integration (requires honcho plugin)
hermes memory setup/status/off  Memory provider config
hermes completion bash|zsh  Shell completions
hermes acp                  ACP server (IDE integration)
hermes claw migrate         Migrate from OpenClaw
hermes uninstall            Uninstall Hermes
```

---

## Slash Commands (In-Session)

Type these during an interactive chat session.

### Session Control
```
/new (/reset)        Fresh session
/clear               Clear screen + new session (CLI)
/retry               Resend last message
/undo                Remove last exchange
/title [name]        Name the session
/compress            Manually compress context
/stop                Kill background processes
/rollback [N]        Restore filesystem checkpoint
/background <prompt> Run prompt in background
/queue <prompt>      Queue for next turn
/resume [name]       Resume a named session
```

### Configuration
```
/config              Show config (CLI)
/model [name]        Show or change model
/personality [name]  Set personality
/reasoning [level]   Set reasoning (none|minimal|low|medium|high|xhigh|show|hide)
/verbose             Cycle: off → new → all → verbose
/voice [on|off|tts]  Voice mode
/yolo                Toggle approval bypass
/skin [name]         Change theme (CLI)
/statusbar           Toggle status bar (CLI)
```

### Tools & Skills
```
/tools               Manage tools (CLI)
/toolsets            List toolsets (CLI)
/skills              Search/install skills (CLI)
/skill <name>        Load a skill into session
/cron                Manage cron jobs (CLI)
/reload-mcp          Reload MCP servers
/plugins             List plugins (CLI)
```

### Gateway
```
/approve             Approve a pending command (gateway)
/deny                Deny a pending command (gateway)
/restart             Restart gateway (gateway)
/sethome             Set current chat as home channel (gateway)
/update              Update Hermes to latest (gateway)
/curator             Check curator status (gateway)
/platforms (/gateway) Show platform connection status (gateway)
```

### Utility
```
/branch (/fork)      Branch the current session
/fast                Toggle priority/fast processing
/browser             Open CDP browser connection
/history             Show conversation history (CLI)
/save                Save conversation to file (CLI)
/paste               Attach clipboard image (CLI)
/image               Attach local image file (CLI)
/mouse               Toggle mouse injection (CLI) — kills ConPTY phantom clicks
/reload              Reload .env hot-reload (CLI TUI)
/reload-skills       Reload installed skills without restart
```

### Info
```
/help                Show commands
/commands [page]     Browse all commands (gateway)
/usage               Token usage
/insights [days]     Usage analytics
/status              Session info (gateway)
/profile             Active profile info
```

### Exit
```
/quit (/exit, /q)    Exit CLI
```

---

## Key Paths & Config

```
~/.hermes/config.yaml       Main configuration
~/.hermes/.env              API keys and secrets
$HERMES_HOME/skills/        Installed skills
~/.hermes/sessions/         Session transcripts
~/.hermes/logs/             Gateway and error logs
~/.hermes/auth.json         OAuth tokens and credential pools
~/.hermes/hermes-agent/     Source code (if git-installed)
```

Profiles use `~/.hermes/profiles/<name>/` with the same layout.

### Config Sections

Edit with `hermes config edit` or `hermes config set section.key value`.

| Section | Key options |
|---------|-------------|
| `model` | `default`, `provider`, `base_url`, `api_key`, `context_length` |
| `agent` | `max_turns` (90), `tool_use_enforcement` |
| `terminal` | `backend` (local/docker/ssh/modal/vercel), `cwd`, `timeout` (180) |
| `compression` | `enabled`, `threshold` (0.50), `target_ratio` (0.20) |
| `display` | `skin`, `tool_progress`, `show_reasoning`, `show_cost` |
| `stt` | `enabled`, `provider` (local/groq/openai/mistral) |
| `tts` | `provider` (edge/elevenlabs/openai/minimax/mistral/neutts/piper) |
| `memory` | `memory_enabled`, `user_profile_enabled`, `provider` |
| `security` | `tirith_enabled`, `website_blocklist` |
| `delegation` | `model`, `provider`, `base_url`, `api_key`, `max_iterations` (50), `reasoning_effort` |
| `checkpoints` | `enabled`, `max_snapshots` (50) |
| `prompt_caching` | `cache_ttl` (300s default, 3600s opt-in) |
| `auxiliary` | `vision`, `compression`, `session_search`, `curator` model/provider overrides |
| `redaction` | `enabled` (false by default since v0.12.0) |

Full config reference: https://hermes-agent.nousresearch.com/docs/user-guide/configuration

### Providers

20+ providers supported. Set via `hermes model` or `hermes setup`.

| Provider | Auth | Key env var |
|----------|------|-------------|
| OpenRouter | API key | `OPENROUTER_API_KEY` |
| Anthropic | API key | `ANTHROPIC_API_KEY` |
| Nous Portal | OAuth | `hermes auth` |
| OpenAI Codex | OAuth | `hermes auth` |
| GitHub Copilot | Token | `COPILOT_GITHUB_TOKEN` |
| Google Gemini | API key | `GOOGLE_API_KEY` or `GEMINI_API_KEY` |
| DeepSeek | API key | `DEEPSEEK_API_KEY` |
| xAI / Grok | API key | `XAI_API_KEY` |
| Hugging Face | Token | `HF_TOKEN` |
| Z.AI / GLM | API key | `GLM_API_KEY` |
| MiniMax | API key | `MINIMAX_API_KEY` |
| MiniMax CN | API key | `MINIMAX_CN_API_KEY` |
| Kimi / Moonshot | API key | `KIMI_API_KEY` |
| Alibaba / DashScope | API key | `DASHSCOPE_API_KEY` |
| Xiaomi MiMo | API key | `XIAOMI_API_KEY` |
| Kilo Code | API key | `KILOCODE_API_KEY` |
| AI Gateway (Vercel) | API key | `AI_GATEWAY_API_KEY` |
| OpenCode Zen | API key | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | API key | `OPENCODE_GO_API_KEY` |
| Qwen OAuth | OAuth | `hermes login --provider qwen-oauth` |
| LM Studio | Config | `LM_STUDIO_API_KEY` (optional) |
| GMI Cloud | API key | `GMI_CLOUD_API_KEY` |
| Azure AI Foundry | Config | `AZURE_API_KEY` / `AZURE_BASE_URL` |
| MiniMax OAuth | OAuth | `hermes login --provider minimax-oauth` |
| Tencent Tokenhub | API key | `TENCENT_TOKENHUB_API_KEY` |
| Custom endpoint | Config | `model.base_url` + `model.api_key` in config.yaml |
| GitHub Copilot ACP | External | `COPILOT_CLI_PATH` or Copilot CLI |

Full provider docs: https://hermes-agent.nousresearch.com/docs/integrations/providers

### Toolsets

Enable/disable via `hermes tools` (interactive) or `hermes tools enable/disable NAME`.

| Toolset | What it provides |
|---------|-----------------|
| `web` | Web search and content extraction |
| `browser` | Browser automation (Browserbase, Camofox, or local Chromium) |
| `terminal` | Shell commands and process management |
| `file` | File read/write/search/patch |
| `code_execution` | Sandboxed Python execution |
| `vision` | Image analysis |
| `image_gen` | AI image generation |
| `tts` | Text-to-speech |
| `skills` | Skill browsing and management |
| `memory` | Persistent cross-session memory |
| `session_search` | Search past conversations |
| `delegation` | Subagent task delegation |
| `cronjob` | Scheduled task management |
| `clarify` | Ask user clarifying questions |
| `messaging` | Cross-platform message sending |
| `search` | Web search only (subset of `web`) |
| `todo` | In-session task planning and tracking |
| `rl` | Reinforcement learning tools (off by default) |
| `moa` | Mixture of Agents (off by default) |
| `homeassistant` | Smart home control (off by default) |
| `spotify` | Spotify playback control (OAuth, off by default) |
| `openhue` | Philips Hue lights control (bundled, off by default) |
```
Tool changes take effect on `/reset` (new session). They do NOT apply mid-conversation to preserve prompt caching.

---

## Voice & Transcription

### STT (Voice → Text)

Voice messages from messaging platforms are auto-transcribed.

Provider priority (auto-detected):
1. **Local faster-whisper** — free, no API key: `pip install faster-whisper`
2. **Groq Whisper** — free tier: set `GROQ_API_KEY`
3. **OpenAI Whisper** — paid: set `VOICE_TOOLS_OPENAI_KEY`
4. **Mistral Voxtral** — set `MISTRAL_API_KEY`

Config:
```yaml
stt:
  enabled: true
  provider: local        # local, groq, openai, mistral
  local:
    model: base          # tiny, base, small, medium, large-v3
```

### TTS (Text → Voice)

| Provider | Env var | Free? |
|----------|---------|-------|
| Edge TTS | None | Yes (default) |
| ElevenLabs | `ELEVENLABS_API_KEY` | Free tier |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | Paid |
| MiniMax | `MINIMAX_API_KEY` | Paid |
| Mistral (Voxtral) | `MISTRAL_API_KEY` | Paid |
| NeuTTS (local) | None (`pip install neutts[all]` + `espeak-ng`) | Free |

Voice commands: `/voice on` (voice-to-voice), `/voice tts` (always voice), `/voice off`.

---

## Spawning Additional Hermes Instances

Run additional Hermes processes as fully independent subprocesses — separate sessions, tools, and environments.

### When to Use This vs delegate_task

| | `delegate_task` | Spawning `hermes` process |
|-|-----------------|--------------------------|
| Isolation | Separate conversation, shared process | Fully independent process |
| Duration | Minutes (bounded by parent loop) | Hours/days |
| Tool access | Subset of parent's tools | Full tool access |
| Interactive | No | Yes (PTY mode) |
| Use case | Quick parallel subtasks | Long autonomous missions |

### One-Shot Mode

```
terminal(command="hermes chat -q 'Research GRPO papers and write summary to ~/research/grpo.md'", timeout=300)

# Background for long tasks:
terminal(command="hermes chat -q 'Set up CI/CD for ~/myapp'", background=true)
```

### Interactive PTY Mode (via tmux)

Hermes uses prompt_toolkit, which requires a real terminal. Use tmux for interactive spawning:

```
# Start
terminal(command="tmux new-session -d -s agent1 -x 120 -y 40 'hermes'", timeout=10)

# Wait for startup, then send a message
terminal(command="sleep 8 && tmux send-keys -t agent1 'Build a FastAPI auth service' Enter", timeout=15)

# Read output
terminal(command="sleep 20 && tmux capture-pane -t agent1 -p", timeout=5)

# Send follow-up
terminal(command="tmux send-keys -t agent1 'Add rate limiting middleware' Enter", timeout=5)

# Exit
terminal(command="tmux send-keys -t agent1 '/exit' Enter && sleep 2 && tmux kill-session -t agent1", timeout=10)
```

### Multi-Agent Coordination

```
# Agent A: backend
terminal(command="tmux new-session -d -s backend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t backend 'Build REST API for user management' Enter", timeout=15)

# Agent B: frontend
terminal(command="tmux new-session -d -s frontend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t frontend 'Build React dashboard for user management' Enter", timeout=15)

# Check progress, relay context between them
terminal(command="tmux capture-pane -t backend -p | tail -30", timeout=5)
terminal(command="tmux send-keys -t frontend 'Here is the API schema from the backend agent: ...' Enter", timeout=5)
```

### Session Resume

```
# Resume most recent session
terminal(command="tmux new-session -d -s resumed 'hermes --continue'", timeout=10)

# Resume specific session
terminal(command="tmux new-session -d -s resumed 'hermes --resume 20260225_143052_a1b2c3'", timeout=10)
```

### Tips

- **Prefer `delegate_task` for quick subtasks** — less overhead than spawning a full process
- **Use `-w` (worktree mode)** when spawning agents that edit code — prevents git conflicts
- **Set timeouts** for one-shot mode — complex tasks can take 5-10 minutes
- **Use `hermes chat -q` for fire-and-forget** — no PTY needed
- **Use tmux for interactive sessions** — raw PTY mode has `\r` vs `\n` issues with prompt_toolkit
- **For scheduled tasks**, use the `cronjob` tool instead of spawning — handles delivery and retry

---

## Deployment & Integration Workflows

### Full-Stack Setup: WebUI + Telegram Gateway + Custom Personalities

End-to-end checklist for deploying the complete Hermes stack on a single server (WebUI behind nginx reverse proxy with SSL, Telegram gateway polling, and custom agent personalities).

**1. Clone and bootstrap WebUI**
```bash
cd ~
git clone https://github.com/nesquena/hermes-webui.git
cd hermes-webui
python3 bootstrap.py --no-browser
```
- Change port in `.env` if needed (e.g., `HERMES_WEBUI_PORT=18789`).
- Add `HERMES_WEBUI_ALLOWED_ORIGINS=https://<your-domain>:<port>` for reverse-proxy CSRF compliance.

**2. Configure nginx reverse proxy**
```nginx
server {
    listen 8443 ssl;
    server_name _;
    ssl_certificate /etc/nginx/ssl/cert.crt;
    ssl_certificate_key /etc/nginx/ssl/cert.key;

    location / {
        proxy_pass http://127.0.0.1:18789;
        proxy_http_version 1.1;
        proxy_set_header Host $host:$server_port;
        proxy_set_header X-Forwarded-Host $host:$server_port;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400;
    }
}
```
- **Critical:** `proxy_set_header Host $host:$server_port;` fixes CSRF origin mismatch (the WebUI checks Origin against Host).
- **Critical:** `proxy_buffering off; proxy_cache off;` prevents SSE (chat streaming) from hanging behind nginx.

**3. Set up Telegram gateway (native)**
Write to `~/.hermes/.env` (the gateway reads **only** this file, never repo-level `.env`):
```bash
TELEGRAM_BOT_TOKEN=<real_token>
TELEGRAM_ALLOWED_USERS=<your_chat_id>
TELEGRAM_HOME_CHANNEL=<your_chat_id>
TELEGRAM_HOME_CHANNEL_NAME=myhome
```
- Remove any stale placeholder tokens (e.g., `sdfsdfsdfsdf`) — they cause `InvalidToken` even if a real token is present later in the file. Verify raw bytes with:
  ```python
  python3 -c "import os; print(open(os.path.expanduser('~/.hermes/.env'),'rb').read().decode('utf-8',errors='replace'))"
  ```
- If `api.telegram.org` is unreachable from your network, the gateway automatically falls back to `149.154.167.220`. Check `~/.hermes/logs/gateway.log` to confirm the active endpoint.

Start the gateway:
```bash
hermes gateway run      # foreground
hermes gateway install  # systemd background service
```

**4. Configure custom personalities**
Add to `~/.hermes/config.yaml`:
```yaml
personalities:
  mypersona:
    system_prompt: "You are a helpful assistant..."
    temperature: 0.7
display:
  personality: mypersona
```
- Restart the gateway to apply personality changes (`/restart` in chat or `kill` + `hermes gateway run`).

**5. Create role-delegation skill (optional)**
If you route tasks by role (e.g., code tasks → coder personality, content tasks → expert personality), save a delegation skill to `~/.hermes/skills/<name>/SKILL.md`. Load it in sessions with `/skill <name>` or `--skills <name>`.

**Key integration notes**
- **Session isolation:** WebUI sessions use the key prefix `agent:main:web:*`, while Telegram uses `agent:main:telegram:*` (or `agent:main:telegram:dm:<id>`). Contexts are isolated by design.
- **Environment files:** WebUI reads `~/hermes-webui/.env`. Gateway reads `~/.hermes/.env`. Do not confuse the two.
- **Process management:** WebUI runs via `python3 bootstrap.py --no-browser`. Gateway runs via `hermes gateway run`. They are separate long-lived processes.

---

## Autonomous Curator (v0.12.0+)

The Curator is a background agent that maintains your skill library automatically.

### How it works
- Runs on the gateway cron ticker, default 7-day cycle
- Grades skills by rubric (not free-form), ranks by usage
- Consolidates related skills, prunes dead ones
- Writes reports to `~/.hermes/logs/curator/run.json` + `REPORT.md`
- Bundled/hub skills are protected from mutation (pinned)

### Commands
```bash
hermes curator status       # Rank skills: most-used / least-used
hermes curator run          # Trigger a curator cycle manually
```
Config: `hermes model` → pick auxiliary.curator model, or `hermes config set auxiliary.curator.model <name>`.

**Reference:** `references/hermes-admin-and-skill-maintenance.md` — runbook for auditing skills, cleaning ghost references, restructuring persistent memory, and sizing subagent batches against `max_concurrent_children` (cloud model: cap only; local Ollama: also check `num_parallel`).

**Reference:** `references/v0.12.0-changelog.md` — condensed changelog for all v0.12.0 changes.

**Compression settings reference:** `references/compression-settings.md` — detailed guide on `target_ratio`, `hygiene_hard_message_limit`, `memory_char_limit`, and `user_char_limit` tuning.

---

## Troubleshooting

### Voice not working
1. Check `stt.enabled: true` in config.yaml
2. Verify provider: `pip install faster-whisper` or set API key
3. In gateway: `/restart`. In CLI: exit and relaunch.

### Tool not available
1. `hermes tools` — check if toolset is enabled for your platform
2. Some tools need env vars (check `.env`)
3. `/reset` after enabling tools

### Model/provider issues
1. `hermes doctor` — check config and dependencies
2. `hermes login` — re-authenticate OAuth providers
3. Check `.env` has the right API key
4. **Copilot 403**: `gh auth login` tokens do NOT work for Copilot API. You must use the Copilot-specific OAuth device code flow via `hermes model` → GitHub Copilot.

### Credential pool exhaustion & persistent 401 errors
If you see `Non-retryable client error (HTTP 401)` repeatedly even though your API key is valid, the credential pool may have permanently marked the key as `exhausted` after a single failed request. This is recoverable.

**Symptoms**
- `hermes chat` fails with `HTTP 401: unauthorized` on every attempt.
- The same key works fine when used outside Hermes (e.g., `curl` or `ollama launch`).
- `hermes auth list ollama-cloud` shows `last_status: exhausted` and `last_error_code: 401`.

**Diagnosis**
Check `~/.hermes/auth.json` for exhausted entries:
```bash
python3 -c "import json, os; a=json.load(open(os.path.expanduser('~/.hermes/auth.json'))); [print(p,[(e['label'],e.get('last_status'),e.get('last_error_code')) for e in s]) for p,s in a.get('credential_pool',{}).items() if any(e.get('last_status')=='exhausted' for e in s)]" 2>/dev/null
```

**Fix**
```bash
# Reset exhaustion status for the provider
hermes auth reset ollama-cloud

# Or reset all providers at once if unsure
hermes auth reset --all
```

**Ollama-specific routing caveat**
Hermes has two Ollama providers:
- `ollama-launch` — local Ollama server (`http://127.0.0.1:11434/v1`) which can proxy cloud models if you append `:cloud` to the model name (e.g., `kimi-k2.6:cloud`).
- `ollama-cloud` — direct HTTPS API to `ollama.com/v1`.

If your local Ollama is running but empty (no local models), setting `provider: ollama-launch` with `default: kimi-k2.6` (without `:cloud`) will cause a fallback to `ollama-cloud`, which may hit an exhausted key. Use `:cloud` suffix explicitly when routing through the local Ollama proxy:
```yaml
model:
  provider: ollama-launch
  base_url: http://127.0.0.1:11434/v1
  default: kimi-k2.6:cloud
```

### Gateway service not starting / not surviving logout
- **Foreground vs. service**: `hermes gateway run` runs in your terminal and dies when you disconnect. For a persistent background service, use:
  ```bash
  hermes gateway install   # creates systemd/launchd user service
  hermes gateway start     # enables and starts it
  ```
- **Check status**: `hermes gateway status`
- **View logs**: `journalctl --user -u hermes-gateway -f` (Linux) or `log show --predicate 'process == "hermes-gateway"' --info --debug --last 1h` (macOS)
- **Crash loop**: If the service keeps restarting, clear the failed state:
  ```bash
  systemctl --user reset-failed hermes-gateway
  hermes gateway restart
  ```
- **SSH logout kills gateway**: Ensure systemd user linger is enabled:
  ```bash
  sudo loginctl enable-linger $USER
  ```

### Changes not taking effect
- **Tools/skills:** `/reset` starts a new session with updated toolset
- **Config changes:** In gateway: `/restart`. In CLI: exit and relaunch.
- **Code changes:** Restart the CLI or gateway process

### Skills not showing
1. `hermes skills list` — verify installed
2. `hermes skills config` — check platform enablement
3. Load explicitly: `/skill name` or `hermes -s name`

### Gateway issues
Check logs first:
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

Common gateway problems:
**Gateway crash loop from blocked Telegram + MCP zombie pattern**
If `api.telegram.org` is unreachable (blocked ISP, firewall, captive portal), the gateway may crash-loop with `telegram.error.TimedOut`. The obsidian-mcp child can survive the SIGKILL and block new MCP connections in the same CLI session. See full diagnosis and recovery in `references/telegram-gateway-crash-loop.md`.

Quick recovery:
```bash
# Kill stale MCP children
pkill -9 -f 'obsidian-mcp'
# Restart gateway
systemctl --user restart hermes-gateway
# Start a new CLI session (stale MCP handle lives in the old session)
hermes  # or /new inside CLI
```

**Prevention:** disable Telegram via `~/.hermes/.env` (comment out `TELEGRAM_BOT_TOKEN`) or configure `TELEGRAM_PROXY`.

**Gateway dies on SSH logout**: Ensure systemd user linger is enabled: `sudo loginctl enable-linger $USER`
- **Gateway dies on WSL2 close**: WSL2 requires `systemd=true` in `/etc/wsl.conf` for systemd services to work. Without it, gateway falls back to `nohup` (dies when session closes).
- **Gateway crash loop**: Reset the failed state: `systemctl --user reset-failed hermes-gateway`

### Hermes WebUI behind nginx reverse proxy
When running the WebUI behind nginx (e.g. `https://my-server:8443` → `http://127.0.0.1:18789`), two extra settings are required:

1. **CSRF origin match** — The WebUI checks `Origin` vs `Host`. If nginx strips the port, all POST requests get 403.
   ```nginx
   location / {
       proxy_pass http://127.0.0.1:18789;
       proxy_http_version 1.1;
       proxy_set_header Host $host:$server_port;
       proxy_set_header X-Forwarded-Host $host:$server_port;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
       proxy_buffering off;
       proxy_cache off;
       proxy_read_timeout 86400;
   }
   ```
2. **Allow the external origin** in `~/hermes-webui/.env` (or wherever bootstrap reads from):
   ```bash
   HERMES_WEBUI_ALLOWED_ORIGINS=https://130.255.9.9:8443
   ```
3. **SSE streaming** — `proxy_buffering off; proxy_cache off;` are required or chat responses will hang.

### WebUI runtime errors (Python exceptions during chat)

**Symptom: "Failed to load session. Try switching sessions or refreshing."**
This usually means the WebUI **server process has died** (not just a slow response). Always check process liveness first.

**Diagnosis**
1. Check the server process is alive and listening on its port:
   ```bash
   pgrep -f "hermes-webui/server.py"
   ss -tlnp | grep 18789     # or whatever HERMES_WEBUI_PORT is set to
   ```
2. Read the most recent server output or log files:
   ```bash
   tail -n 50 ~/hermes-webui/*.log 2>/dev/null
   tail -n 50 ~/.hermes/webui/bootstrap-*.log 2>/dev/null
   tail -n 50 ~/.hermes/webui/server-*.log 2>/dev/null
   ```
3. If the process is gone, restart it (background):
   ```bash
   cd ~/hermes-webui && ./start.sh --no-browser
   ```
3. Trace the offending symbol by grepping the source tree:
   ```bash
   grep -rn "<symbol>" ~/hermes-webui --include="*.py"
   ```

**Power-outage recovery**
After a power outage or kernel reboot, the WebUI process does not restart automatically if it was started manually with `ctl.sh start`. nginx will return 502 until the WebUI is restarted. Quick recovery:
```bash
cd ~/hermes-webui && ./ctl.sh status   # check if running
cd ~/hermes-webui && ./ctl.sh start    # if stopped
```
For a permanent fix, deploy WebUI as a systemd user service: `references/webui-systemd-service.md`.

**Common pattern: duplicate keyword argument in `_set_thread_env()`**
When `terminal.cwd` is set in a profile's `config.yaml`, the profile runtime env dict already contains `TERMINAL_CWD`. If `streaming.py` also passes `TERMINAL_CWD=...` explicitly, Python crashes with:
```
TypeError: _set_thread_env() got multiple values for keyword argument 'TERMINAL_CWD'
```

Fix: remove the conflicting key from the unpacked dict before calling the setter:
```python
# In api/streaming.py before _set_thread_env(...)
_profile_runtime_env.pop('TERMINAL_CWD', None)
```
Then restart the WebUI process.

### WebUI Authentication & Security

**Critical: password authentication is OFF by default.** If you expose the WebUI behind a reverse proxy with a public IP, anyone on the internet can access it and use your agent, API keys, and tools.

**How to check current auth status:**
```bash
# Inspect env and running config
grep -i "HERMES_WEBUI_PASSWORD" ~/hermes-webui/.env 2>/dev/null
grep "password_hash" ~/.hermes/webui/settings.json 2>/dev/null
```
If neither returns a value, auth is disabled.

**Three ways to enable password protection:**

| Method | Where | Scope |
|---|---|---|
| **A. Env var** (recommended) | `~/hermes-webui/.env` | Global for the process |
| **B. Settings panel** | WebUI → Settings | Stored in `settings.json` |
| **C. nginx basic auth** | nginx config | Extra layer independent of WebUI |

**Method A — env var (fastest):**
```bash
echo 'HERMES_WEBUI_PASSWORD=your-strong-password' >> ~/hermes-webui/.env
# Restart WebUI (e.g. kill the python server.py process and re-run start.sh)
```
- Priority: env var overrides settings.json.
- The password is hashed with PBKDF2-HMAC-SHA256 + a random per-installation salt (600k iterations, OWASP recommendation).

**Method B — via WebUI Settings:**
1. Open WebUI → Settings
2. Fill the password field (this internally writes `_set_password` into settings, which gets hashed and stored as `password_hash`)
3. To disable later, use `_clear_password: true` in settings or remove the env var.

**Method C — nginx basic auth (defense in depth):**
```bash
sudo apt-get install apache2-utils
sudo htpasswd -c /etc/nginx/.htpasswd hermes
```
Then in the nginx `location /` block add:
```nginx
auth_basic "Hermes WebUI";
auth_basic_user_file /etc/nginx/.htpasswd;
```

**Auth behavior details:**
- Sessions last **24 hours** (`SESSION_TTL = 86400`), signed with HMAC-SHA256, stored in `~/.hermes/webui/.sessions.json`.
- Cookies are **HttpOnly**, **SameSite=Lax**, and **Secure** when HTTPS is detected.
- Rate limiting: **5 login attempts per 60 seconds** per IP address.
- Public paths that skip auth: `/login`, `/health`, `/favicon.ico`, `/api/auth/login`, `/api/auth/status`, and everything under `/static/`.

**Security checklist when exposing WebUI to the internet:**
1. ✅ Enable password auth (method A or B)
2. ✅ Use HTTPS via nginx reverse proxy (self-signed or Let's Encrypt)
3. ✅ Set `HERMES_WEBUI_ALLOWED_ORIGINS` to your exact external origin
4. ✅ (Optional) Add nginx basic auth as second layer
5. ✅ (Optional) Restrict access by source IP in nginx (`allow 1.2.3.4; deny all;`)

### Browser Automation (CDP Chrome) in Containers / WSL / Docker

When running Hermes in a containerized or restricted Linux environment (Docker, WSL, cloud VMs), the `browser` toolset may fail because Chrome cannot start its sandbox. Symptoms: `browser_navigate` times out or throws `No usable sandbox! If you are running on a Linux distribution...`.

**Diagnosis**
1. Check if Chrome is installed: `which google-chrome-stable` or `which chromium`.
2. Try launching Chrome manually to see the exact error:
   ```bash
   google-chrome-stable --headless --disable-gpu --remote-debugging-port=9222 about:blank
   ```
3. If the error is `No usable sandbox`, the kernel or container lacks the required namespaces / AppArmor policies.

**Workaround: run Chrome without sandbox (CDP mode)**
```bash
/usr/bin/google-chrome-stable \
  --no-sandbox \
  --headless \
  --disable-gpu \
  --remote-debugging-port=9222 \
  --remote-debugging-address=0.0.0.0 \
  --disable-dev-shm-usage \
  --disable-setuid-sandbox \
  about:blank
```
- `--no-sandbox` is **required** in Docker/WSL/VMs without user namespaces.
- `--remote-debugging-address=0.0.0.0` lets Hermes connect from localhost.
- `--disable-dev-shm-usage` prevents `/dev/shm` exhaustion in small containers.

**Connect Hermes to the running Chrome instance**
1. After Chrome starts, read the CDP WebSocket URL:
   ```bash
   curl -s http://localhost:9222/json/version | grep webSocketDebuggerUrl
   ```
   Example output:
   ```json
   "webSocketDebuggerUrl": "ws://localhost:9222/devtools/browser/bca7c818-b76d-417a-849f-b4ad903e8917"
   ```
2. Write this URL into `~/.hermes/config.yaml`:
   ```yaml
   browser:
     cdp_url: 'ws://localhost:9222/devtools/browser/bca7c818-b76d-417a-849f-b4ad903e8917'
   ```
3. Reload or start a new session (`/reset` in CLI, or restart gateway). Test with `browser_navigate` to `https://ya.ru`.

**Important caveats**
- Every time Chrome restarts, its CDP UUID changes. You must update `cdp_url` in `config.yaml` again.
- Do NOT use this mode for browsing untrusted sites — `--no-sandbox` reduces security isolation.
- For persistent sessions (cookies, logins, saved state), add `--user-data-dir=/path/to/profile` to the Chrome launch flags and reuse the same directory across restarts.

**Persistent profile for logins**
```bash
/usr/bin/google-chrome-stable \
  --no-sandbox \
  --headless \
  --disable-gpu \
  --remote-debugging-port=9222 \
  --remote-debugging-address=0.0.0.0 \
  --disable-dev-shm-usage \
  --disable-setuid-sandbox \
  --user-data-dir=/home/youruser/chrome-profile \
  about:blank
```
- Cookies, localStorage, and authenticated sessions survive as long as you keep `--user-data-dir` the same.
- If you need to capture a visual screenshot with `browser_vision`, keep the headless process running; `browser_vision` takes a snapshot of the active CDP tab.

### Telegram Gateway Setup (Native)

The built-in gateway (`hermes gateway run`) is the recommended method. It uses `python-telegram-bot` with full feature support (commands, buttons, media, voice, groups).

Quick setup:
```bash
# 1. Write these to ~/.hermes/.env  (gateway reads ONLY this file — not repo .env!)
TELEGRAM_BOT_TOKEN=123456:ABC-...
TELEGRAM_ALLOWED_USERS=12345678        # Your numeric chat_id (find it in gateway logs after first message)
TELEGRAM_HOME_CHANNEL=12345678         # Default chat for cron delivery
TELEGRAM_HOME_CHANNEL_NAME=myhome      # Display name for home channel

# 2. Start the gateway
hermes gateway run          # foreground
hermes gateway install      # systemd/launchd background service

# 3. Check status & logs
hermes gateway status
tail -f ~/.hermes/logs/gateway.log
```

#### Adding a new allowed user (workflow)

When a new user messages the bot but gets `Unauthorized user` in logs, add them to `TELEGRAM_ALLOWED_USERS`:

```bash
# Read current value first
grep "TELEGRAM_ALLOWED_USERS" ~/.hermes/.env

# Append new chat_id (use sed, NOT patch — .env is credential-protected)
sed -i 's/TELEGRAM_ALLOWED_USERS=OLD_IDS/TELEGRAM_ALLOWED_USERS=OLD_IDS,NEW_ID/' ~/.hermes/.env

# Verify
grep "TELEGRAM_ALLOWED_USERS" ~/.hermes/.env

# Restart gateway to pick up changes (reads .env only at startup)
systemctl --user restart hermes-gateway
sleep 3
systemctl --user status hermes-gateway --no-pager | head -5
```

**Critical:** The gateway reads `.env` only at process startup. Adding a user without restarting the gateway leaves them blocked. Always restart after editing `TELEGRAM_ALLOWED_USERS`.

**Finding a user's chat_id:** When an unauthorized user sends `/start`, the gateway logs show:
```
WARNING gateway.run: Unauthorized user: 535814521 (Alexander) on telegram
```
Grab the numeric ID and append it to `TELEGRAM_ALLOWED_USERS`.

**Note:** `TELEGRAM_HOME_CHANNEL` controls where cron/unsolicited messages are delivered. It does NOT need to list every allowed user — only the primary admin channel.

**Token masking pitfall:** Terminal output and `grep` often mask tokens as `***` even when the real value is present. The gateway may also fail with `InvalidToken` if an old placeholder (e.g. `sdfsdfsdfsdf`) is still in the file. Verify the raw bytes:
```python
python3 -c "
import os
with open(os.path.expanduser('~/.hermes/.env'), 'rb') as f:
    print(f.read().decode('utf-8', errors='replace'))
"
```
**Note:** The gateway ignores `~/hermes-webui/.env` or any repo-level `.env`. It only loads `~/.hermes/.env`.

### Platform-specific issues
- **Discord bot silent**: Must enable **Message Content Intent** in Bot → Privileged Gateway Intents.
- **Slack bot only works in DMs**: Must subscribe to `message.channels` event. Without it, the bot ignores public channels.
- **Windows HTTP 400 "No models provided"**: Config file encoding issue (BOM). Ensure `config.yaml` is saved as UTF-8 without BOM.
- **Telegram gateway InvalidToken**: The `~/.hermes/.env` file may contain a stale placeholder (e.g. `sdfsdfsdfsdf` or `***`). Terminal output often masks real tokens, so verify with raw Python: `python3 -c "print(open(os.path.expanduser('~/.hermes/.env'),'rb').read())"`. The gateway reads only `~/.hermes/.env`, not the repo-level `.env`.
- **Telegram gateway token works but bot silent**: Make sure `TELEGRAM_ALLOWED_USERS` includes your numeric `chat_id`. The first message to the bot reveals it — check `~/.hermes/logs/gateway.log`.
- **Telegram attachments not received in session**: When a user attaches a file (image, archive, document) via Telegram, it may NOT be passed to the agent session. The agent sees the message text but not the attachment. **Symptom**: user says "I sent you a file" but the agent receives only text. **Workaround**: ask the user to upload the file to a shared location (FTP, cloud, or accessible path), or use the `/image` slash command to load local files into the session if the user can confirm the file path.

### Auxiliary models not working
If `auxiliary` tasks (vision, compression, session_search) fail silently, the `auto` provider can't find a backend. Either set `OPENROUTER_API_KEY` or `GOOGLE_API_KEY`, or explicitly configure each auxiliary task's provider:
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

---

## Where to Find Things

| Looking for... | Location |
|----------------|----------|
| Skill maintenance | `references/hermes-admin-and-skill-maintenance.md` |
| Config options | `hermes config edit` or [Configuration docs](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) |
| Available tools | `hermes tools list` or [Tools reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference) |
| Slash commands | `/help` in session or [Slash commands reference](https://hermes-agent.nousresearch.com/docs/reference/slash-commands) |
| Skills catalog | `hermes skills browse` or [Skills catalog](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog) |
| Provider setup | `hermes model` or [Providers guide](https://hermes-agent.nousresearch.com/docs/integrations/providers) |
| Platform setup | `hermes gateway setup` or [Messaging docs](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/) |
| MCP servers | `hermes mcp list` or [MCP guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) |
| Profiles | `hermes profile list` or [Profiles docs](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) |
| Cron jobs | `hermes cron list` or [Cron docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) |
| Memory | `hermes memory status` or [Memory docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) |
| Env variables | `hermes config env-path` or [Env vars reference](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) |
| CLI commands | `hermes --help` or [CLI reference](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) |
| Gateway logs | `~/.hermes/logs/gateway.log` |
| Telegram user mgmt | `references/telegram-user-management.md` |
| Session files | `~/.hermes/sessions/` or `hermes sessions browse` |
| Source code | `~/.hermes/hermes-agent/` |

---

## Contributor Quick Reference

For occasional contributors and PR authors. Full developer docs: https://hermes-agent.nousresearch.com/docs/developer-guide/

### Project Layout

```
hermes-agent/
├── run_agent.py          # AIAgent — core conversation loop
├── model_tools.py        # Tool discovery and dispatch
├── toolsets.py           # Toolset definitions
├── cli.py                # Interactive CLI (HermesCLI)
├── hermes_state.py       # SQLite session store
├── agent/                # Prompt builder, context compression, memory, model routing, credential pooling, skill dispatch
├── hermes_cli/           # CLI subcommands, config, setup, commands
│   ├── commands.py       # Slash command registry (CommandDef)
│   ├── config.py         # DEFAULT_CONFIG, env var definitions
│   └── main.py           # CLI entry point and argparse
├── tools/                # One file per tool
│   └── registry.py       # Central tool registry
├── gateway/              # Messaging gateway
│   └── platforms/        # Platform adapters (telegram, discord, etc.)
├── cron/                 # Job scheduler
├── tests/                # ~3000 pytest tests
└── website/              # Docusaurus docs site
```

Config: `~/.hermes/config.yaml` (settings), `~/.hermes/.env` (API keys).

### Adding a Tool (3 files)

**1. Create `tools/your_tool.py`:**
```python
import json, os
from tools.registry import registry

def check_requirements() -> bool:
    return bool(os.getenv("EXAMPLE_API_KEY"))

def example_tool(param: str, task_id: str = None) -> str:
    return json.dumps({"success": True, "data": "..."})

registry.register(
    name="example_tool",
    toolset="example",
    schema={"name": "example_tool", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: example_tool(
        param=args.get("param", ""), task_id=kw.get("task_id")),
    check_fn=check_requirements,
    requires_env=["EXAMPLE_API_KEY"],
)
```

**2. Add to `toolsets.py`** → `_HERMES_CORE_TOOLS` list.

Auto-discovery: any `tools/*.py` file with a top-level `registry.register()` call is imported automatically — no manual list needed.

All handlers must return JSON strings. Use `get_hermes_home()` for paths, never hardcode `~/.hermes`.

### Adding a Slash Command

1. Add `CommandDef` to `COMMAND_REGISTRY` in `hermes_cli/commands.py`
2. Add handler in `cli.py` → `process_command()`
3. (Optional) Add gateway handler in `gateway/run.py`

All consumers (help text, autocomplete, Telegram menu, Slack mapping) derive from the central registry automatically.

### Agent Loop (High Level)

```
run_conversation():
  1. Build system prompt
  2. Loop while iterations < max:
     a. Call LLM (OpenAI-format messages + tool schemas)
     b. If tool_calls → dispatch each via handle_function_call() → append results → continue
     c. If text response → return
  3. Context compression triggers automatically near token limit
```

### Testing

```bash
python -m pytest tests/ -o 'addopts=' -q   # Full suite
python -m pytest tests/tools/ -q            # Specific area
```

- Tests auto-redirect `HERMES_HOME` to temp dirs — never touch real `~/.hermes/`
- Run full suite before pushing any change
- Use `-o 'addopts='` to clear any baked-in pytest flags

### Commit Conventions

```
type: concise subject line

Optional body.
```

Types: `fix:`, `feat:`, `refactor:`, `docs:`, `chore:`

### Key Rules

- **Never break prompt caching** — don't change context, tools, or system prompt mid-conversation
- **Message role alternation** — never two assistant or two user messages in a row
- Use `get_hermes_home()` from `hermes_constants` for all paths (profile-safe)
- Config values go in `config.yaml`, secrets go in `.env`
- New tools need a `check_fn` so they only appear when requirements are met
