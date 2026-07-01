# ACP Delegation Model Configuration

When Hermes spawns an ACP subagent via `delegate_task(acp_command="copilot")`,
the model used by that subagent is **not** the main `model.default` value.
It is governed by the `delegation:` block in `~/.hermes/config.yaml`.

## Example: local proxy for `kimi-k2.7-code:cloud`

```yaml
model:
  default: kimi-k2.7-code:cloud
  provider: ollama-launch
  base_url: http://127.0.0.1:11434/v1

delegation:
  model: kimi-k2.7-code:cloud
  provider: ollama-launch
  base_url: http://127.0.0.1:11434/v1
```

## Verification smoke test

```python
delegate_task(
    acp_command="copilot",
    goal="Respond with exactly: OPENCODE_SMOKE_OK",
    context="Smoke test only. Reply with OPENCODE_SMOKE_OK.",
    toolsets=['terminal', 'file']
)
```

Check the result summary for the `model` field. If it shows the desired model,
the delegation config is active.

## Common mistakes

- **Wrong `acp_command`**: `delegate_task(acp_command="opencode")` fails
  because `opencode` is not the ACP binary. The correct value is `copilot`
  (GitHub Copilot CLI in `--acp --stdio` mode).
- **Empty `delegation.model`**: the subagent falls back to an older or different
  model even after the main model was upgraded. Always set `delegation.model`
  explicitly when using ACP subagents.
- **Using a `gh` token**: the GitHub CLI OAuth token often lacks the **Copilot
  Requests** permission and fails with `Authorization error` or
  `Access denied by policy settings`. Create a fine-grained PAT v2 with the
  **Copilot Requests** permission and set `COPILOT_GITHUB_TOKEN`.

## Hard prerequisites

1. GitHub Copilot CLI installed: `npm install -g @github/copilot`.
2. CLI authenticated for Copilot API (fine-grained PAT v2 with **Copilot Requests**
   permission, or token from `copilot login`).
3. Hermes gateway can see the CLI and token (PATH + `COPILOT_GITHUB_TOKEN` via
   systemd drop-in if gateway runs under systemd).

See `copilot-acp-auth-setup.md` for the full setup recipe.

If the CLI is missing or unauthenticated, fall back to native Hermes
`delegate_task` without `acp_command`.
