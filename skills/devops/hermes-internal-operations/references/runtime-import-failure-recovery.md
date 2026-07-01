---
date: 2026-06-23
skill: hermes-internal-operations
topic: core-runtime-import-failure
---

# Recovering from a Hermes core runtime ImportError

Real case: terminal tool calls failed with an error that looked API-related but was purely a local import mismatch.

## Symptom

Every `terminal` tool call returned:

```
Error executing tool: Error during OpenAI-compatible API call #1:
cannot import name 'agent_runtime_owns_post_tool_hook'
from 'agent.agent_runtime_helpers' (/home/natan/.hermes/hermes-agent/agent/agent_runtime_helpers.py)
```

Retrying produced the same error. Other tools may or may not be affected depending on which code path imports the missing helper.

## Diagnosis

```bash
cd /home/natan/.hermes/hermes-agent
git status
git diff -- agent/agent_runtime_helpers.py
grep -n "agent_runtime_owns_post_tool_hook" agent/*.py
```

In this case the file was stale relative to the rest of the checkout: the rest of the code referenced a newly-added helper, but `agent_runtime_helpers.py` did not contain it.

## Fix

The user resolved the mismatch outside the agent (likely a `git pull` or manual patch). Once the source files were consistent again:

```bash
find /home/natan/.hermes/hermes-agent -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find /home/natan/.hermes/hermes-agent -name "*.pyc" -delete
systemctl --user restart hermes-gateway
```

If no system-level user unit exists, find and restart the gateway process directly:
```bash
pgrep -af "hermes_cli.main gateway run"
kill -HUP <PID>   # or kill <PID>, then relaunch via the user's normal start path
```

After restart the same `terminal` command (`whoami && pwd && uname -a`) succeeded.

## Verification

```bash
whoami && pwd && uname -a
ss -tlnp | grep 9119   # if dashboard was also restarted
```

## Lessons

1. Error text mentioning `OpenAI-compatible API call` is misleading — the failure is in Hermes' own module loading, not the remote API.
2. An `ImportError` inside `hermes-agent/agent/` almost always means the checkout is inconsistent.
3. Restarting the chat/WebUI session is not enough; restart the gateway/runtime process after fixing the source.
4. Always check `git status` before editing core files, otherwise the next update may reintroduce the mismatch.
