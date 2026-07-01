---
name: opencode
description: "Delegate coding to OpenCode CLI (features, PR review)."
version: 1.3.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, OpenCode, Autonomous, Refactoring, Code-Review]
    related_skills: [claude-code, codex, hermes-agent]
---

# OpenCode CLI

Use [OpenCode](https://opencode.ai) as an autonomous coding worker orchestrated by Hermes terminal/process tools. OpenCode is a provider-agnostic, open-source AI coding agent with a TUI and CLI.

## When to Use

- User explicitly asks to use OpenCode
- You want an external coding agent to implement/refactor/review code
- You need long-running coding sessions with progress checks
- You want parallel task execution in isolated workdirs/worktrees

## Prerequisites

- OpenCode installed: `npm i -g opencode-ai@latest` or `brew install anomalyco/tap/opencode`
- Auth configured: `opencode auth login` or set provider env vars (OPENROUTER_API_KEY, etc.)
- Verify: `opencode auth list` should show at least one provider
- Git repository for code tasks (recommended)
- `pty=true` for interactive TUI sessions

## Binary Resolution (Important)

Shell environments may resolve different OpenCode binaries. If behavior differs between your terminal and Hermes, check:

```
terminal(command="which -a opencode")
terminal(command="opencode --version")
```

If needed, pin an explicit binary path (nvm node 24 on this machine):

```
terminal(command="/home/natan/.nvm/versions/node/v24.13.1/bin/opencode run '...'", workdir="~/project")
```

## Standalone Configuration File

OpenCode CLI reads global defaults from `~/.config/opencode/opencode.json`. This is the cleanest way to pin the model and provider so you don't have to pass `--model` every time. Example for a local Ollama-compatible proxy:

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

With this file in place, `opencode run` and `opencode` (TUI) default to the configured model.

## One-Shot Tasks

Use `opencode run` for bounded, non-interactive tasks:

```
terminal(command="opencode run 'Add retry logic to API calls and update tests'", workdir="~/project")
```

Attach context files with `-f`:

```
terminal(command="opencode run 'Review this config for security issues' -f config.yaml -f .env.example", workdir="~/project")
```

Show model thinking with `--thinking`:

```
terminal(command="opencode run 'Debug why tests fail in CI' --thinking", workdir="~/project")
```

Force a specific model:

```
terminal(command="opencode run 'Refactor auth module' --model openrouter/anthropic/claude-sonnet-4", workdir="~/project")
```

Get machine-readable output (good for parsing results programmatically):

```
terminal(command="opencode run 'Refactor auth module' --format json", workdir="~/project")
```

**Background one-shot with JSON logging** (does not block Telegram):

```
terminal(command="cd ~/project && nohup opencode run --format json 'TASK DESCRIPTION' > /tmp/opencode-$(date +%s).log 2>&1 & echo $! > /tmp/opencode.pid", background=true)

# Later, collect results
process(action="list")
cat /tmp/opencode-*.log
```

## Interactive Sessions (Background)

For iterative work requiring multiple exchanges, start the TUI in background:

```
terminal(command="opencode", workdir="~/project", background=true, pty=true)
# Returns session_id

# Send a prompt
process(action="submit", session_id="<id>", data="Implement OAuth refresh flow and add tests")

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send follow-up input
process(action="submit", session_id="<id>", data="Now add error handling for token expiry")

# Exit cleanly — Ctrl+C
process(action="write", session_id="<id>", data="\x03")
# Or just kill the process
process(action="kill", session_id="<id>")
```

**Important:** Do NOT use `/exit` — it is not a valid OpenCode command and will open an agent selector dialog instead. Use Ctrl+C (`\x03`) or `process(action="kill")` to exit.

### TUI Keybindings

| Key | Action |
|-----|--------|
| `Enter` | Submit message (press twice if needed) |
| `Tab` | Switch between agents (build/plan) |
| `Ctrl+P` | Open command palette |
| `Ctrl+X L` | Switch session |
| `Ctrl+X M` | Switch model |
| `Ctrl+X N` | New session |
| `Ctrl+X E` | Open editor |
| `Ctrl+C` | Exit OpenCode |

### Resuming Sessions

After exiting, OpenCode prints a session ID. Resume with:

```
terminal(command="opencode -c", workdir="~/project", background=true, pty=true)  # Continue last session
terminal(command="opencode -s ses_abc123", workdir="~/project", background=true, pty=true)  # Specific session
```

## Common Flags

| Flag | Use |
|------|-----|
| `run 'prompt'` | One-shot execution and exit |
| `--continue` / `-c` | Continue the last OpenCode session |
| `--session <id>` / `-s` | Continue a specific session |
| `--agent <name>` | Choose OpenCode agent (build or plan) |
| `--model provider/model` | Force specific model |
| `--format json` | Machine-readable output/events |
| `--file <path>` / `-f` | Attach file(s) to the message |
| `--thinking` | Show model thinking blocks |
| `--variant <level>` | Reasoning effort (high, max, minimal) |
| `--title <name>` | Name the session |
| `--attach <url>` | Connect to a running opencode server |

## ACP Delegation via Hermes (Experimental)

Hermes can spawn the **GitHub Copilot CLI in ACP mode** as an external subagent. That CLI behaves as an autonomous coding worker (the underlying agent is OpenCode/Copilot). Use `delegate_task(acp_command="copilot")` — **not** `acp_command="opencode"`:

```python
delegate_task(
    acp_command="copilot",
    goal="Implement feature X",
    context="Full task description...",
    toolsets=['terminal', 'file']
)
```

**Hard prerequisites:**
1. The **GitHub Copilot CLI with ACP support** must be installed (`npm install -g @github/copilot`, binary is usually called `copilot`).
2. The CLI must be able to reach PATH, or you must set `COPILOT_CLI_PATH` / `HERMES_COPILOT_ACP_COMMAND`.
3. The CLI must be **authenticated with a valid Copilot token** (fine-grained PAT v2 with the **Copilot Requests** permission, or an OAuth token from `copilot login`). The `gh` CLI token is often **not enough** — it may fail with `Authorization error` or `Access denied by policy settings`.

Without any of the above, the call fails. Do not try to fix this by changing the model or retrying — satisfy the prerequisites first, or fall back to native Hermes `delegate_task`.

See `references/copilot-acp-auth-setup.md` for a complete setup recipe, including a systemd drop-in for `hermes-gateway.service`.

### Controlling the model for ACP subagent

The ACP subagent does **not** read `model.default` directly. It uses the Hermes **delegation** config. To pin the subagent model (e.g. `kimi-k2.7-code:cloud` through a local proxy), set in `~/.hermes/config.yaml`:

```yaml
delegation:
  model: kimi-k2.7-code:cloud
  provider: ollama-launch
  base_url: http://127.0.0.1:11434/v1
```

Then verify with a smoke test:

```python
delegate_task(
    acp_command="copilot",
    goal="Respond with exactly: OPENCODE_SMOKE_OK",
    context="This is a smoke test. Reply only with OPENCODE_SMOKE_OK.",
    toolsets=['terminal', 'file']
)
```

If the result summary shows `model: kimi-k2.7-code:cloud`, the configuration is active. See also `references/acp-delegation-model-config.md`.

### Fallback to Native Hermes Subagent

If ACP delegation fails (no Copilot CLI, wrong binary, auth issues), **immediately fall back to a regular Hermes `delegate_task`** without `acp_command`:

```python
delegate_task(
    goal="Same task: implement feature X",
    context="Full task description... Include file paths, expected output, verification steps.",
    toolsets=['terminal', 'file']
)
```

The Hermes native subagent uses the same model/provider and has full access to terminal/file tools. It cannot call `clarify`, `memory`, or `delegate_task` recursively, but it can read files, run commands, and make edits.

**Rule:** Always verify ACP readiness with a smoke test before relying on it for production tasks. If unsure, default to native `delegate_task`.

## Procedure

1. Verify tool readiness:
   - `terminal(command="opencode --version")`
   - `terminal(command="opencode auth list")`
2. For bounded tasks, use `opencode run '...'` (no pty needed).
3. For iterative tasks, start `opencode` with `background=true, pty=true`.
4. Monitor long tasks with `process(action="poll"|"log")`.
5. If OpenCode asks for input, respond via `process(action="submit", ...)`.
6. Exit with `process(action="write", data="\x03")` or `process(action="kill")`.
7. Summarize file changes, test results, and next steps back to user.

## PR Review Workflow

OpenCode has a built-in PR command:

```
terminal(command="opencode pr 42", workdir="~/project", pty=true)
```

Or review in a temporary clone for isolation:

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && opencode run 'Review this PR vs main. Report bugs, security risks, test gaps, and style issues.' -f $(git diff origin/main --name-only | head -20 | tr '\n' ' ')", pty=true)
```

## Parallel Work Pattern

Use separate workdirs/worktrees to avoid collisions:

```
terminal(command="opencode run 'Fix issue #101 and commit'", workdir="/tmp/issue-101", background=true, pty=true)
terminal(command="opencode run 'Add parser regression tests and commit'", workdir="/tmp/issue-102", background=true, pty=true)
process(action="list")
```

## Session & Cost Management

List past sessions:

```
terminal(command="opencode session list")
```

Check token usage and costs:

```
terminal(command="opencode stats")
terminal(command="opencode stats --days 7 --models anthropic/claude-sonnet-4")
```

## Pitfalls

- Interactive `opencode` (TUI) sessions require `pty=true`. The `opencode run` command does NOT need pty.
- `/exit` is NOT a valid command — it opens an agent selector. Use Ctrl+C to exit the TUI.
- PATH mismatch can select the wrong OpenCode binary/model config. Pin absolute path when in doubt.
- If OpenCode appears stuck, inspect logs before killing:
  - `process(action="log", session_id="<id>")`
- Avoid sharing one working directory across parallel OpenCode sessions.
- Enter may need to be pressed twice to submit in the TUI (once to finalize text, once to send).
- **ACP delegation via `delegate_task(acp_command="copilot")` requires GitHub Copilot CLI with a valid Copilot token. If it fails, immediately fall back to native Hermes `delegate_task` without `acp_command`. Do NOT use `acp_command="opencode"` — `opencode` is not a valid ACP binary name.**
- **A `gh` OAuth token is often not sufficient for Copilot CLI.** If you see `Authorization error` or `Access denied by policy settings`, create a fine-grained PAT v2 with the **Copilot Requests** permission and set `COPILOT_GITHUB_TOKEN`.
- **Classic GitHub PATs (`ghp_...`) are not supported by Copilot CLI.**
- **For Hermes gateway to see the token and PATH**, use a systemd drop-in (`~/.config/systemd/user/hermes-gateway.service.d/copilot.conf`) with `EnvironmentFile=%h/.hermes/.env` and the correct PATH, then `daemon-reload` + `restart hermes-gateway.service`.
- **First `opencode` run may print `bash: /home/natan/.openclaw/completions/openclaw.bash: No such file or directory`.** This is a harmless shell-completion warning, not an error; ignore it.
- **`opencode run --format json` emits JSON-RPC-like events per line.** Parse them as a stream (`step_start`, `text`, `step_finish`). The final `step_finish` contains `tokens`, `cost`, and `reason`.

## Verification

Standalone OpenCode smoke test:

```
terminal(command="opencode run 'Respond with exactly: OPENCODE_SMOKE_OK'")
```

ACP smoke test (after Copilot CLI is installed and authenticated):

```python
delegate_task(
    acp_command="copilot",
    goal="Respond with exactly: OPENCODE_SMOKE_OK",
    context="Smoke test only. Reply with OPENCODE_SMOKE_OK.",
    toolsets=['terminal', 'file']
)
```

Success criteria:
- Output includes `OPENCODE_SMOKE_OK`
- Command exits without provider/model/auth errors
- For ACP: result summary shows the expected `model` (set via `delegation:` config)
- For code tasks: expected files changed and tests pass

See also: `references/opencode-json-mode-smoke.md` for a concrete `kimi-k2.7-code:cloud` JSON-mode smoke test.

## Rules

1. Prefer `opencode run` for one-shot automation — it's simpler and doesn't need pty.
2. Use interactive background mode only when iteration is needed.
3. Always scope OpenCode sessions to a single repo/workdir.
4. For long tasks, provide progress updates from `process` logs.
5. Report concrete outcomes (files changed, tests, remaining risks).
6. Exit interactive sessions with Ctrl+C or kill, never `/exit`.
7. If ACP delegation fails, fall back to native Hermes `delegate_task` without `acp_command`.