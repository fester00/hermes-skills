---
name: hermes-internal-operations
description: Class-level runbook for operating, auditing, and troubleshooting the Hermes Agent instance itself — state reconciliation, token-usage diagnosis, and WebUI service maintenance.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, operations, audit, state, tokens, webui, troubleshooting, devops]
triggers:
  - "audit hermes skills"
  - "reconcile skills"
  - "profile has more skills"
  - "skills count mismatch"
  - "how many skills do I have"
  - "sync skills with obsidian"
  - "why does X profile have more skills"
  - "check hermes state"
  - "token usage too high"
  - "tokens disappeared"
  - "unexpected token consumption"
  - "restart webui"
  - "hermes webui down"
  - "webui not responding"
  - "webui slow"
---

# Hermes Internal Operations

Use this skill when the task is about Hermes itself rather than an external project: skill counts look wrong, token usage seems unexplained, or the Hermes WebUI needs a restart or health check.

## 1. State Audit: Reconciling Skills & Profiles

Hermes skills live in multiple layers that often diverge:

| Layer | Location | Mutable |
|-------|----------|---------|
| Built-in | Shipped with Hermes core | No |
| Root profile | `~/.hermes/skills/` | Yes |
| Named profiles | `~/.hermes/profiles/<name>/skills/` | Yes |
| External docs | Obsidian vaults, runbooks | Yes, but can be stale |

### Three-layer inventory

1. **Merged API view** — what the active session sees:
   ```python
   skills_list()  # built-in + active-profile physical
   ```
2. **Physical files on disk**:
   ```bash
   # Default (root) profile
   find ~/.hermes/skills -maxdepth 2 -name "SKILL.md" | wc -l

   # Named profiles
   for p in ~/.hermes/profiles/*/; do
     echo "$(basename $p): $(find $p/skills -name 'SKILL.md' | wc -l)"
   done
   ```
3. **External documentation** — read vault skill indices and cross-check links.

### Reconciliation workflow

```
skills_list()  → merged count and names
      ↓
find physical SKILL.md → per-profile counts
      ↓
Compare: built-ins = merged - physical
      ↓
If Obsidian involved:
      ├─ Try MCP: mcp_obsidian_search_vault / read_note
      ├─ On MCP timeout (3 failures): filesystem fallback
      └─ Cross-check Obsidian links against disk paths
      ↓
Report table with all three layers
```

### Obsidian fallback pattern

When `mcp_obsidian_*` times out after 3 failures, read the vault directly:

```bash
read_file ~/obsidian-memory/<path>/<note>.md
# or
read_file ~/obsidian/<path>/<note>.md
```

Always verify that Obsidian references still point to existing disk paths.

### Reporting format

| Profile | Merged (API) | Physical (Disk) | Built-in | Obsidian Docs |
|---------|-------------|-----------------|----------|---------------|
| default | 79 | 2 | 77 | references 3 deleted skills |
| shifu | — | 95 | 0 | — |

*Inactive profiles do not appear in `skills_list`; use `find` only for them.*

### Pitfalls

- Never assume merged count == physical count. Built-ins inflate the API count.
- Profile isolation is real: named-profile skill directories are invisible to the default session.
- Obsidian documentation decays; cross-check links before quoting.
- MCP timeouts are environmental; capture the filesystem fallback recipe.

See `references/session-2026-06-03-skills-reconciliation.md` for a concrete case study.

## 2. Token Audit: Diagnosing Unexpected Usage

Use this section when the user reports token usage that seems too high relative to visible activity, e.g. “10% of my quota disappeared in 30 minutes but nobody was doing anything.”

### Goal

1. Did Hermes actually consume the tokens in that window?
2. If not, where should the user look next (provider billing lag, shared API key, WebUI keep-alive, compression, etc.)?

### Diagnostic sequence

Run in order. Each step adds evidence; stop when the picture is clear.

1. **High-level usage picture**
   ```bash
   hermes insights --days 1
   ```
   Look at sessions/messages/tool calls, platform split (WebUI often dominates), and top tools.
2. **Recent sessions**
   ```bash
   hermes sessions list --limit 30
   ```
   Identify any session active in the suspect window. Long or untitled sessions may be WebUI background tabs.
3. **Gateway activity**
   ```bash
   grep -E 'inbound|response ready|api_calls|token|cost|compression|curator' \
     ~/.hermes/logs/gateway.log | tail -n 80
   ```
   If no `inbound` and no `response ready` with high `api_calls`, the gateway did not spend tokens.
4. **Active autonomous agents**
   ```bash
   hermes cron list
   ps aux | grep -iE 'hermes chat|opencode|codex|claude' | grep -v grep
   ```
5. **WebUI state**
   ```bash
   pgrep -f "hermes-webui/server.py"
   ss -tlnp | grep 18789   # or HERMES_WEBUI_PORT
   ```
   Warm browser tabs may flush/compress context in the background.
6. **Provider-side lag**
   Many providers report usage minutes to hours later. Check the provider dashboard for the *timestamp of the billed request*, not just the debit time.

### Common explanations

| Observation | Likely cause | Action |
|-------------|--------------|--------|
| `insights` shows huge WebUI token count; gateway quiet | WebUI session + compression/context growth | Restart WebUI, close idle tabs |
| `insights` shows many `delegate_task` / browser calls | Prior heavy subagent work | Normal; confirm with user |
| Gateway has many `compression` lines | Context compression triggered | Expected near token limit; check model context length |
| No Hermes activity in logs, but provider debited | Provider billing lag or shared key | Check provider dashboard / rotate key |
| `hermes cron list` shows jobs | Scheduled agent is running | Inspect job prompt and schedule |

### Pitfalls

- Don't trust wall-clock alone. A quiet window can be followed by a delayed charge for an earlier long session.
- Don't blame a specific tool without counts. `terminal` is often #1 by call count but not by tokens.
- Compression is not free; it fires near context limits.

If Hermes logs show no matching activity but the provider keeps debiting:
1. Rotate the API key (shared key suspected).
2. Set `HERMES_WEBUI_PASSWORD` so public WebUI cannot be used by crawlers.
3. Check for other applications using the same provider key.

See `references/token-audit-checklist.md` for a copy-paste checklist.

## 3. WebUI Maintenance: Restart & Health Check

Use this section when the Hermes WebUI is slow, unresponsive, needs a restart, or shows stale state (e.g. an old model name still displayed after config change).

### Current command: `hermes dashboard`

Modern Hermes ships a single CLI subcommand for the WebUI dashboard:

```bash
hermes dashboard --help          # options: --port, --host, --no-open, --stop, --status
hermes dashboard --port 9119 --no-open   # run in background / server context
hermes dashboard --status
hermes dashboard --stop
```

Default bind is `127.0.0.1:9119`. Verify listening:

```bash
ss -tlnp | grep 9119
```

### Quick restart recipe

```bash
# 1. Stop any existing dashboard
hermes dashboard --stop

# 2. Verify port is free
ss -tlnp | grep 9119

# 3. Start fresh (use no-open when running remotely / via agent)
hermes dashboard --port 9119 --no-open

# 4. Verify health
ss -tlnp | grep 9119
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9119/
# Expected: 302 or 200
```

### After a power outage (separate `~/hermes-webui` install)

If the server lost power and the WebUI no longer answers after boot:

1. Check status:
   ```bash
   cd ~/hermes-webui && ./ctl.sh status
   ```
2. If it is stopped or `Health: unreachable`, start it:
   ```bash
   cd ~/hermes-webui && ./ctl.sh start
   ```
3. Wait 5–10 seconds, then verify:
   ```bash
   ./ctl.sh status
   curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:18789/health
   ```
4. If the reverse proxy still returns 502, verify nginx can reach `127.0.0.1:18789` and restart nginx if needed.

The `ctl.sh` script does **not** auto-start after reboot. If power outages are frequent, consider a systemd user unit or cron `@reboot` entry.

See `references/webui-separate-repo-power-outage-recovery.md` for a concise command runbook from a real recovery on this server.

If the dashboard process is running but the port is not listening, check logs for a build or runtime error. The dashboard command builds the web UI on first start; set `--skip-build` only if `web/dist` already exists.

### Legacy `~/hermes-webui` install

Older Hermes used a separate `hermes-webui` repository with `start.sh` / `server.py` on port 18789. If `hermes dashboard` is not available, fall back to the legacy path:

```bash
cd ~/hermes-webui
./ctl.sh status                 # daemon-style PID/log management
./ctl.sh start 18789            # persistent background run
./ctl.sh stop
./ctl.sh restart 18789
```

Equivalent manual path (when `ctl.sh` is unavailable):
```bash
cd ~/hermes-webui && ./start.sh --no-browser > /tmp/hermes-webui-restart.log 2>&1 &
ss -ltnp | grep 18789
```

### Restarting the gateway itself

The gateway process (`hermes_cli.main gateway run`) is the runtime that owns this agent session. A restart **cannot** be issued from inside the session — Hermes blocks `hermes gateway restart` and `ctl.sh restart gateway` when called by an agent process to prevent self-termination loops.

If the user asks the agent to restart the gateway, explain the constraint and give them the exact manual command to run in a separate shell:

```bash
hermes gateway restart
# or directly:
/home/natan/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway restart
```

Pitfalls:
- `kill <gateway_PID>` from the agent session may appear to work, but the command will be killed by SIGTERM propagation before it can complete.
- `nohup`, `setsid`, or background wrappers launched from the agent still inherit enough session context that Hermes detects and blocks the restart.
- The only reliable path is a shell outside the gateway process (SSH session, another terminal, or the user running it directly).


**Auto-restart trap:** If a system-wide unit has `Restart=always` and a stale process survived a manual kill, `systemctl stop` may appear to succeed while systemd immediately respawns a new process. The restart counter can climb into the hundreds while the port stays occupied. After stopping/disabling, always verify the port is actually free:
```bash
ss -tlnp | grep :18789
pgrep -f "hermes-webui/server.py"
```
If the port is still occupied, identify the surviving PID with `ps -eo pid,lstart,cmd | grep hermes-webui/server.py`, kill it manually (`kill -9 <PID>`), then restart the desired unit.

### Common pitfalls

- **Duplicate systemd scopes:** WebUI may be installed both as `systemctl --user hermes-webui.service` and as `sudo systemctl hermes-webui.service`. Both can run simultaneously and fight for the same port. Always check both scopes; stop the system-wide unit with `sudo` if needed.
- **Stale process after stop:** `systemctl stop` may leave a `server.py` process or an `obsidian-mcp` child still holding the port. Verify with `pgrep` and `ss -tlnp`, then `pkill -9 -f 'hermes-webui/server.py'` if necessary.
- **Port race condition:** `start.sh` may complain about another server right after a kill. Wait 3–5 seconds and retry, or verify the port is free first.
- **Separate `.env` files:** WebUI reads `~/hermes-webui/.env`; gateway reads `~/.hermes/.env`.
- **nginx reverse proxy:** for SSE chat behind nginx, use:
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
- **No password = public access:** set `HERMES_WEBUI_PASSWORD` in `~/hermes-webui/.env` if exposed to the internet.
- **Missing modules:** if logs show `ModuleNotFoundError: No module named 'dotenv'`, install `python-dotenv` in the WebUI venv.

If the WebUI still shows stale data after restart:
1. Clear browser cache / hard-refresh.
2. Check `~/.hermes/webui/` for a stale `settings.json`.
3. Confirm the browser is hitting the right origin.
4. If the restart command reports `invalid choice: 'webui'` (Hermes CLI has no `hermes webui` subcommand), start or restart the WebUI server directly from the `~/hermes-webui` repository using `ctl.sh`, `start.sh`, or `server.py`.

### Recognizing which WebUI install is active

| Check | Built-in dashboard | Separate `~/hermes-webui` |
|-------|--------------------|---------------------------|
| Help command | `hermes dashboard --help` works | `hermes dashboard` is unknown command |
| Source dir | `~/.hermes/hermes-agent/gateway/dashboard` or similar | `~/hermes-webui` |
| Typical port | 9119 | 18789 (configurable via `.env`) |
| Launcher | `hermes dashboard` | `start.sh`, `ctl.sh`, or `server.py` |

When in doubt, list both ports and processes:
```bash
ss -tlnp | grep -E '9119|18789'
pgrep -af "hermes-webui/server.py|hermes_cli.main dashboard"
```

A separate `~/hermes-webui` repository is a common real-world install even when `hermes dashboard` is available. The user's link (e.g. `https://github.com/nesquena/hermes-webui`) is a strong signal that they are using the separate repository. In that case prefer `~/hermes-webui/ctl.sh` or `~/hermes-webui/start.sh` over the built-in dashboard.

See `references/webui-restart-recipe.md` for a concise command runbook.
- `references/webui-update-and-port-cleanup.md` — full recovery after a WebUI update when duplicate systemd scopes or `Restart=always` stale processes fight for the port

## 4. Core Runtime Import Failures

Use this section when Hermes tools fail with an internal Python `ImportError` that mentions files inside `hermes-agent/agent/` (e.g. `cannot import name 'agent_runtime_owns_post_tool_hook' from 'agent.agent_runtime_helpers'`). The symptom looks like a tool or provider failure, but the root cause is a stale/mismatched source file in the Hermes runtime.

### Recognizing the pattern

A tool call returns an error that looks provider-related but originates from Hermes' own imports:

```
Error during OpenAI-compatible API call #1:
cannot import name 'agent_runtime_owns_post_tool_hook'
from 'agent.agent_runtime_helpers' (/home/natan/.hermes/hermes-agent/agent/agent_runtime_helpers.py)
```

Key signs:
- Error references a file under `~/.hermes/hermes-agent/agent/`
- The symbol (`agent_runtime_owns_post_tool_hook`) was recently introduced
- Tool fails identically every call; retrying does not help
- Other unrelated tools may still work, or the same tool fails consistently

### Root causes

1. **Partial update.** A `git pull` or manual edit added a call site that imports a new helper, but `agent/agent_runtime_helpers.py` was not updated (merge conflict, untracked local change, or update script skipped it).
2. **Mixed versions.** The active Python process loaded an old cached `.pyc` or an old checkout while another file references a newer symbol.
3. **Runtime live-patched.** A previous fix or experiment edited one module but left a sibling module stale.

### Recovery recipe

1. **Inspect the failing file and the missing symbol**
   ```bash
   cd /home/natan/.hermes/hermes-agent
   grep -n "agent_runtime_owns_post_tool_hook" agent/*.py
   grep -n "def agent_runtime_owns_post_tool_hook\|agent_runtime_owns_post_tool_hook" agent/agent_runtime_helpers.py
   ```

2. **Check repository state**
   ```bash
   git status
   git diff -- agent/agent_runtime_helpers.py
   git log --oneline -5 -- agent/agent_runtime_helpers.py
   ```

3. **Resolve the mismatch**
   - If `git status` shows a local modification → review and revert if it is stale:
     ```bash
     git checkout -- agent/agent_runtime_helpers.py
     ```
   - If `git status` shows unmerged / conflict markers → resolve the conflict and commit.
   - If the file is simply behind remote → pull the latest matching checkout:
     ```bash
     git pull
     ```

4. **Clear stale bytecode**
   ```bash
   find /home/natan/.hermes/hermes-agent -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
   find /home/natan/.hermes/hermes-agent -name "*.pyc" -delete
   ```

5. **Restart the gateway (and any background Hermes processes)**
   ```bash
   systemctl --user restart hermes-gateway
   # If WebUI was running separately:
   hermes dashboard --stop
   hermes dashboard --port 9119 --no-open
   ```

6. **Verify the tool works again**
   Run a simple command through the affected tool:
   ```bash
   whoami && pwd
   ```

### Pitfalls

- **Do not blame the provider or the tool backend.** The error message may say "OpenAI-compatible API call", but the failure is local.
- **Do not restart only the chat/WebUI session.** The stale module is loaded in the gateway/runtime process; restart the service that owns the Python process.
- **Check `git status` before editing.** A manual fix may be overwritten by the next `git pull` or conflict with upstream changes.
- **Verify the symbol actually exists after the fix.** A missing helper may also indicate a deeper structural mismatch requiring a full update.

### When to escalate

If `git status` is clean, `git log` shows the symbol was never added to `agent_runtime_helpers.py`, and pulling does not help, the checkout may be in an inconsistent state. Options:
- Reinstall Hermes Agent (`hermes update` or manual reinstall)
- Ask the user whether they manually patched the source
- Preserve `git diff` output before touching anything

See `references/runtime-import-failure-recovery.md` for the concrete case study from this session.

## 5. Ollama Provider & Profile Auth Failures

Use this section when a Hermes profile using an Ollama-hosted model fails with `HTTP 401 Unauthorized`, or when switching models works in one profile but fails in another.

### Key facts

- Hermes has **two** Ollama providers:
  - `ollama-launch` → local daemon at `127.0.0.1:11434/v1`; auth comes from `ollama signin`
  - `ollama-cloud` → direct `https://ollama.com/v1`; auth comes from `OLLAMA_API_KEY` in the active profile's `.env`
- Each profile has an isolated `.env`. Switching profiles can switch `OLLAMA_API_KEY` even if `ollama signin` did not change.
- The `:cloud` suffix works only for models Ollama exposes as cloud variants. For `gemma4` use ordinary tags like `gemma4:27b`, not `gemma4:cloud`.

### Diagnosis

```bash
# Compare keys across profiles
grep OLLAMA_API_KEY ~/.hermes/.env \
  ~/.hermes/profiles/shifu/.env \
  ~/.hermes/profiles/maximus/.env \
  ~/.hermes/profiles/ugwey/.env 2>/dev/null

# Check local Ollama state
ollama list
curl -s http://127.0.0.1:11434/v1/models | python3 -m json.tool | head -40

# Verify the real model tag
ollama list | grep -i gemma
```

### Common fixes

**Sync the failing profile to the active Ollama account:**
```bash
cp ~/.hermes/.env ~/.hermes/profiles/shifu/.env
# then start a new session
```

**Use direct cloud API instead of local daemon:**
```bash
hermes config set model.provider ollama-cloud
hermes config set model.base_url https://ollama.com/v1
hermes config set model.default gemma4:27b
# then start a new session
```

### Pitfalls

- Don't assume `ollama-launch` ignores `OLLAMA_API_KEY`; Hermes may use it for fallbacks or model-list calls.
- Don't use `:cloud` as a generic suffix. Verify the tag with `ollama list` first.
- WebUI/gateway sessions read `.env` at startup; key changes need a new session or restart.

See `references/ollama-provider-profile-auth.md` for the full case study and command recipes.

## 6. WebUI Model Selection Reverts to Default (Ollama `:` Tags)

Use this section when the Hermes WebUI silently switches the selected model back to the profile default **after the first assistant response**, especially after picking an Ollama model from a different provider group than the active profile provider.

### Symptom chain

1. Profile `model.provider` is `ollama-launch` and `model.default` is `kimi-k2.7-code:cloud`.
2. In the WebUI picker, select `gemma4:31b` from the **Ollama Cloud** group.
3. First request succeeds.
4. After the response, the composer chip snaps back to `kimi-k2.7-code:cloud`.

### Why it happens

Ollama model IDs contain colons (`gemma4:31b`). The WebUI encodes a cross-provider pick as `@ollama-cloud:gemma4:31b`. On later turns the session resolver re-parses that string with `rsplit(":", 1)`, splitting at the **last** colon instead of the provider boundary. It sees provider `ollama-cloud:gemma4` (unknown) and model `31b`, decides the selection is stale, and repairs it to the profile default.

This is a **server-side parser bug** in `_split_provider_qualified_model()` / `_resolve_compatible_session_model_state()`, not an auth problem. First-turn explicit picks survive; the revert happens on the second turn or any non-explicit resolve.

### Quick workarounds

**A. Match the picker group to the active profile provider**

If the profile uses `ollama-launch`, pick only from the **Ollama Launch** group. If you want **Ollama Cloud**, switch the profile provider:

```bash
hermes profile use shifu
hermes config set model.provider ollama-cloud
hermes config set model.base_url https://ollama.com/v1
hermes config set model.default gemma4:31b
```

Then restart the WebUI session.

**B. Use a model alias without the colon**

```yaml
model:
  provider: ollama-cloud
  base_url: https://ollama.com/v1
  default: gemma4-31b
  aliases:
    gemma4-31b: gemma4:31b
```

The alias key has no `:`, so the picker/resolver handle it correctly; the real tag is sent to the API.

**C. Use the CLI for colon-bearing models**

```bash
hermes chat -m gemma4:31b --provider ollama-cloud -q "your prompt"
```

### Permanent fix

The parser needs to try the **first** `:` segment as a known provider before falling back to `rsplit`. A conceptual patch is documented in `references/webui-ollama-colon-model-revert-bug.md`. Verify any fix with a direct reproduction:

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
# Before fix: kimi-k2.7-code:cloud None True
# After fix:  @ollama-cloud:gemma4:31b ollama-cloud False
```

See `references/webui-ollama-colon-model-revert-bug.md` for the full case study, reproduction recipe, and patch outline.

## References

- `references/session-2026-06-03-skills-reconciliation.md` — concrete state-reconciliation case study
- `references/token-audit-checklist.md` — copy-paste token-diagnostic checklist
- `references/webui-restart-recipe.md` — concise WebUI restart runbook
- `references/webui-update-and-port-cleanup.md` — full recovery after a WebUI update when stale processes fight for the port
- `references/runtime-import-failure-recovery.md` — recovering from a core Hermes runtime ImportError that breaks tool calls
- `references/ollama-provider-profile-auth.md` — diagnosing `HTTP 401` and model-tag mistakes when switching Ollama cloud models across Hermes profiles
- `references/webui-ollama-colon-model-revert-bug.md` — WebUI model selection reverts to default after first response when Ollama model IDs contain `:`
