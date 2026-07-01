# GitHub Copilot CLI ACP Auth Setup for Hermes

Recipe for making `delegate_task(acp_command="copilot")` work inside Hermes,
especially when Hermes gateway runs as a systemd user service.

## 1. Install GitHub Copilot CLI

```bash
# Requires Node.js (v24+ recommended on this machine)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 24
npm install -g @github/copilot
```

Verify:

```bash
copilot --version
copilot --help | grep -q acp && echo "ACP supported"
```

Typical binary path on this machine:
`/home/natan/.nvm/versions/node/v24.13.1/bin/copilot`

## 2. Create a fine-grained PAT v2 with Copilot Requests

Classic PATs (`ghp_...`) and the GitHub CLI OAuth token are **not sufficient**
for Copilot CLI headless use.

1. Go to https://github.com/settings/personal-access-tokens/new
2. Token name: `hermes-copilot-acp`
3. Expiration: your choice
4. Repository access: `All repositories` (or select repositories)
5. Account permissions → **Copilot Requests** → select **Read**
6. Generate token. Copy the value (`github_pat_...`).

## 3. Store the token for Hermes

Edit `~/.hermes/.env`:

```bash
COPILOT_GITHUB_TOKEN=github_pat_11AAAAA...your_token
COPILOT_CLI_PATH=/home/natan/.nvm/versions/node/v24.13.1/bin/copilot
```

Reload any open shells or restart the gateway.

## 4. Make the token and PATH available to Hermes gateway

Create a systemd drop-in:

```bash
mkdir -p ~/.config/systemd/user/hermes-gateway.service.d
cat > ~/.config/systemd/user/hermes-gateway.service.d/copilot.conf <<'EOF'
[Service]
Environment="COPILOT_CLI_PATH=/home/natan/.nvm/versions/node/v24.13.1/bin/copilot"
Environment="PATH=%h/.nvm/versions/node/v24.13.1/bin:%h/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
EnvironmentFile=%h/.hermes/.env
EOF
```

Reload and restart:

```bash
systemctl --user daemon-reload
systemctl --user restart hermes-gateway.service
```

Verify the running gateway process has the token:

```bash
PID=$(systemctl --user show hermes-gateway.service -p MainPID --value)
tr '\0' '\n' < /proc/$PID/environ | grep -i COPILOT
```

## 5. Pin the ACP subagent model

Edit `~/.hermes/config.yaml`:

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

## 6. Smoke test

```python
delegate_task(
    acp_command="copilot",
    goal="Respond with exactly: ACP_SMOKE_OK",
    context="Smoke test only. Reply with ACP_SMOKE_OK.",
    toolsets=['terminal', 'file']
)
```

Expected result summary:
- `status: completed`
- `model: kimi-k2.7-code:cloud`
- `summary` contains `ACP_SMOKE_OK`

## Troubleshooting

### `Could not start Copilot ACP command 'copilot'`

- PATH not visible to gateway → check systemd drop-in and `daemon-reload`.
- `COPILOT_CLI_PATH` not set → set it in `~/.hermes/.env` and drop-in.
- Binary missing → reinstall `@github/copilot` globally under node v24.

### `Authorization error, you may need to run /login`

- Token missing or wrong → verify `COPILOT_GITHUB_TOKEN`.
- Token is a classic PAT (`ghp_...`) → create fine-grained PAT v2.
- Token is a `gh` CLI OAuth token → it often lacks **Copilot Requests**
  permission; use a dedicated fine-grained PAT.

### `Access denied by policy settings`

- The token is valid but the account/organization policy blocks Copilot CLI.
- Check Copilot subscription and org policy at
  https://github.com/settings/copilot

### ACP starts but uses wrong model

- Make sure `delegation.model` is set explicitly in `~/.hermes/config.yaml`.
- Check the result summary `model` field after a smoke test.

## Fallback

If ACP cannot be made to work, use a native Hermes subagent immediately:

```python
delegate_task(
    goal="Same task",
    context="Full description...",
    toolsets=['terminal', 'file']
)
```

Native subagents do not require Copilot CLI and use the same toolsets.
