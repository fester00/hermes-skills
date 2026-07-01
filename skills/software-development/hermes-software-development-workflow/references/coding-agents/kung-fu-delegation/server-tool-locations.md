# Server Tool Locations Reference — /home/natan

## Critical: nvm hides tools from default PATH

Node-based CLI tools (opencode, npm packages) are installed via nvm and are **NOT** in default system PATH. Always verify with:

### Where tools actually live
| Tool | Actual Path | Default PATH | nvm v24 PATH |
|------|-------------|--------------|--------------|
| `node` (v18) | system: `/usr/bin/node` | ✅ yes | — |
| `node` (v24) | `~/.nvm/versions/node/v24.13.1/bin/node` | ❌ no | ✅ yes |
| `opencode` | `~/.nvm/versions/node/v24.13.1/bin/opencode` | ❌ no | ✅ yes |
| `npm` (global v24) | `~/.nvm/versions/node/v24.13.1/bin/npm` | ❌ no | ✅ yes |

### Safe verification pattern
```bash
# Method 1: find across entire filesystem (slow, never misses)
find / -name "opencode" -type f 2>/dev/null

# Method 2: try common nvm paths
echo ~/.nvm/versions/*/bin/opencode

# Method 3: run with explicit nvm PATH
env -i PATH="/home/natan/.nvm/versions/node/v24.13.1/bin:$PATH" which opencode

# Method 4: source nvm and use normally
source /home/natan/.nvm/nvm.sh
nvm use 24
which opencode  # now works
```

### What gotchas to avoid
1. **Never run `which opencode` alone** — it only checks PATH, nvm tools aren't there
2. **Never conclude "not found" from `which`** — always follow up with `find` or explicit nvm PATH
3. **nvm default alias may be set** — check `cat ~/.nvm/alias/default`

### Other tools on this server
| Tool | Status | Path |
|------|--------|------|
| `gh` (GitHub CLI) | ✅ in PATH | `/usr/bin/gh` |
| `git` | ✅ in PATH | `/usr/bin/git` |
| `curl` | ✅ in PATH | `/usr/bin/curl` |
| `docker` | ❌ not installed | — |
| `claude-code` | ❌ not installed | — |
| `codex` | ❌ not installed | — |
| `aider` | ❌ not installed | — |
