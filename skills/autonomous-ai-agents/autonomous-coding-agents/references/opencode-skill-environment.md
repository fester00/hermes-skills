# Setting up OpenCode agent skills, plugins, and MCP servers

Use this recipe when an OpenCode agent needs its own reusable skills and plugins, independent of Hermes skills.

## What OpenCode v2 can load on its own

| Kind | Location | Format |
|---|---|---|
| Plugins | `plugins` array in `opencode.jsonc` | npm package (`@scope/pkg`), git URL (`pkg@git+https://...`), or local directory path |
| Skills | `~/.config/opencode/skills/<id>/SKILL.md` or `.opencode/skills/<id>/SKILL.md` | Markdown with YAML frontmatter (`name`, `description`) |
| Agents | `~/.config/opencode/agents/<name>.md` or `.opencode/agents/<name>.md` | Markdown with frontmatter (`description`, `mode`, `permissions`) |
| MCP servers | `mcp.servers.<name>` in config | `{ type: "local", command: [...], timeout: { startup, catalog, execution } }` |

Important: OpenCode agents do **not** inherit Hermes skills or memory. Transfer required context in the brief or migrate skills into the OpenCode format.

## Installing a plugin

Add to `~/.config/opencode/opencode.jsonc`:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "plugins": [
    "superpowers@git+https://github.com/obra/superpowers.git",
    ""
  ]
}
```

Verify:

```bash
opencode plugin list
```

Expected output:

```
ID           VERSION  SOURCE
     5.1.0    
superpowers  8ca22db  superpowers@git+...
```

## Installing a skill

Clone the source repo, copy the skill directory into the OpenCode skills tree:

```bash
mkdir -p ~/.config/opencode/skills
cp -R /tmp/andrej-karpathy-skills/skills/karpathy-guidelines ~/.config/opencode/skills/
cp -R /tmp/ECC/skills/tdd-workflow ~/.config/opencode/skills/
cp -R /tmp/ECC/skills/security-review ~/.config/opencode/skills/
cp -R /tmp/ECC/skills/verification-loop ~/.config/opencode/skills/
cp -R /tmp/ECC/skills/api-design ~/.config/opencode/skills/
```

Verify by asking an OpenCode session to list available skills:

```bash
opencode run --standalone --auto /tmp/skills-test \
  "List all available skills and report whether karpathy-guidelines, tdd-workflow, and  are loaded"
```

## Reusable setup steps

1. Pick a target profile or global config file.
2. Install plugins via the `plugins` array.
3. Clone skill repositories into `/tmp/` and copy selected skill directories to `~/.config/opencode/skills/`.
4. Confirm MCP servers are declared under `mcp.servers.<name>` with `type: "local"`.
5. Validate: `opencode debug config`, `opencode plugin list`, `opencode mcp list`.
6. Run a skills test to confirm expected skills are advertised.

## Pitfalls

- **Claude-only skills**: skills that rely on `CLAUDE.md`, `.claude-plugin`, or Claude-specific tools do not load in OpenCode. Use only `SKILL.md`-based skills or those with explicit OpenCode support.
- **V1 plugins in V2**: plugins written for OpenCode CLI v1 (using `plugin`/`agent`/`command` singular keys or v1 hook events) do not run in V2. Only superpowers and  currently provide v2-compatible plugins.
- **MCP at root of `mcp`**: V2 requires `mcp.servers.<name>`. A flat `mcp: { "codebase-memory": { ... } }` block is silently ignored or rejected.
- **Flat `timeout` for MCP**: V2 wants `{ "startup": N, "catalog": N, "execution": N }`; a single number causes schema errors.
- **Path to plugin file**: local plugins must be a directory, not a `.js` file. For , point to `.opencode/plugins/`, not ``.
- **No `--config` flag**: use `OPENCODE_CONFIG=/path/to/profile.json` to switch profiles.
