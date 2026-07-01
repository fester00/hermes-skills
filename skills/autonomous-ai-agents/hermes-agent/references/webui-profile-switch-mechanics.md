# WebUI Profile Switch Mechanics

How the "Switch Profile" button in Hermes WebUI works under the hood, and what it does NOT do.

## Behavior

When a user clicks "Switch Profile" in the WebUI, `switchToProfile(name)` is called (`static/panels.js:2181`). It performs these steps:

1. **Blocks if agent is busy** — checks `STREAMS > 0` (an LLM call is in progress). If busy, the switch is rejected with "Cannot switch while agent is running."
2. **Switches HERMES_HOME** — writes the new profile name to `~/.hermes/active_profile`, then calls `init_profile_state()` which:
   - Sets `HERMES_HOME` env var to `~/.hermes/profiles/<name>/`
   - Clears all env vars loaded from the OLD profile's `.env`
   - Reloads `.env` from the NEW profile's directory
   - Reloads `config.yaml` from the NEW profile's directory
3. **Reloads model list + workspace list** — parallel `populateModelDropdown()` + `loadWorkspaceList()`
4. **Applies defaults** — if the new profile has `model.default` or `workspace` configured, those are applied
5. **Session handling**:
   - If current session has messages → old session is preserved under the old profile, a **new empty session** is created under the new profile
   - If current session is empty (no messages) → workspace/model are updated in-place, no new session created
6. **Refreshes UI panels** — skills, memory, crons, workspaces panels are reloaded from the new profile's state

## What It Does NOT Do

| Expectation | Reality |
|---|---|
| Creates a parallel second agent | No. It is still the **same** `server.py` process, just with a different `HERMES_HOME`. Only ONE profile is active at a time per WebUI process. |
| Gives the agent separate memory / skills / MCP | Partially yes (different `HERMES_HOME` = different `memory.sqlite`, different skill dirs), but the **same gateway and MCP pool** are shared if the gateway is already running. |
| Allows two users/agents to work simultaneously | No. Switch Profile is **exclusive** — switching kicks out the previous profile's context. |
| Provides separate API keys per profile | Only if each profile's `.env` has different keys. But if both profiles route through the same local Ollama proxy, they share the same proxy and its credential pool. |
| Works while a long task is running | **Blocked** until agent finishes. |

## Multi-Agent Parallelism: Right Tool for the Job

| Need | Solution |
|---|---|
| Quick parallel subtask (minutes, shared context) | `delegate_task` — up to 3 subagents within the same session |
| Background scheduled task | `cronjob` tool |
| Long-running independent agent with its own UI and state | **Separate Hermes instance** on a different port: `PORT=18889 python server.py` |
| Code isolation (prevent git conflicts) | `hermes -w` (worktree mode) |

## Pitfalls

### "I switched to profile 'coder' but MCP still shows old vault"

The WebUI `switchToProfile()` reloads config and state, but the **MCP server process** is owned by `hermes-gateway.service`, not by WebUI. If the gateway was started under the old profile, its MCP server config (`mcp_servers:` in `config.yaml`) still points to the old paths.

**Fix:** After WebUI profile switch, also restart the gateway:
```bash
hermes gateway restart       # or systemctl --user restart hermes-gateway
```
Then start a NEW WebUI session (`/new` or refresh) so the MCP client handle is recreated with the new profile's config.

### Credential pool exhaustion across profiles

If profile A and profile B both use `ollama-cloud` with the same `HERMES_OLLAMA_KEY`, they share the SAME credential pool in `~/.hermes/auth.json`. An exhaustion in one profile blocks the other.

**Fix:** Use the local Ollama proxy (`ollama-launch`) as the provider in both profiles, or use physically separate Hermes instances with isolated `HERMES_HOME` (not just WebUI profile switch).

### Workspace confusion after switch

If the new profile has no `workspace` configured, the WebUI falls back to `DEFAULT_WORKSPACE` (usually `~`). The previous session's file tree may suddenly show the home directory instead of the project folder.

**Fix:** Always set `workspace` in each profile's `config.yaml`:
```yaml
workspace: ~/projects/my-project
```

## Reference: Relevant Source Locations

| File | Function | Line |
|---|---|---|
| `api/profiles.py` | `switch_profile()` | ~315 |
| `api/profiles.py` | `init_profile_state()` | ~304 |
| `api/profiles.py` | `_reload_dotenv()` | ~270 |
| `static/panels.js` | `switchToProfile()` | 2181 |
| `static/sessions.js` | `newSession()` | 264 |
| `static/panels.js` | `openProfileCreate()` | 2298 |

## Quick Test

```bash
# List profiles
hermes profile list

# Switch to profile 'shifu' (CLI level — affects both CLI and WebUI sticky default)
hermes profile use shifu

# Check active profile
python3 -c "import os; print(os.environ.get('HERMES_HOME', '~/.hermes'))"
```
