# Hermes Tool Mapping for Superpowers Skills

Superpowers skills describe actions in harness-agnostic language. This reference maps those actions to Hermes tools.

## Action → Hermes tool

| Superpowers action | Hermes tool | Notes |
|---|---|---|
| Read a file | `read_file` | Use instead of `cat`/`head`/`tail` |
| Write / edit / delete a file | `write_file` or `patch` | Prefer `patch` for targeted edits |
| Search file contents | `search_files` with `target='content'` | Ripgrep-backed |
| Find files by name | `search_files` with `target='files'` | |
| Run shell command | `terminal` | Use background mode for long tasks |
| Start background process | `terminal(background=True, notify_on_complete=True)` | |
| Poll background process | `process(action='poll')` | |
| Dispatch subagent | `delegate_task` | Max 3 concurrent; leaf agents only |
| Use OpenCode | `terminal` with `opencode run < brief.md` | Pipe brief via stdin |
| Read Obsidian note | `mcp__obsidian__read_note` or `mcp__obsidian__search_vault` | Use MCP first; terminal fallback on timeout |
| Index/query codebase | `codebase-memory-audit` or `browser_cdp` with codebase-memory MCP | |
| Take screenshot | `browser_vision` or Playwright via `terminal` | For local addresses use Playwright, not `browser_navigate` |
| Upload to Yandex.Disk | `yandex-api` skill or Python script using `YANDEX_DISK_TOKEN` | |
| Manage todos | `todo` | Session-scoped; combine with ledger file for recovery |
| Save durable memory | `memory` | User prefs, env facts, conventions only |
| Ask clarifying question | `clarify` | One question at a time when possible |
| Run tests | `terminal` with project test command | Read full output |
| Build / lint | `terminal` with `npm run build`, `npm run lint`, etc. | |

## Tool-specific rules

### `delegate_task`
- Use for isolated reasoning-heavy subtasks.
- Pass `toolsets` to restrict available tools.
- Never delegate web search or browser navigation.
- Subagents cannot use `clarify`, `memory`, or `delegate_task`.

### `opencode`
- Always pipe the brief via stdin: `opencode run < /tmp/brief.md`.
- Never use `-f /tmp/brief.md 'prompt'`.
- Smoke-test before use.
- Include MCP instructions in the brief.

### `browser_*`
- `browser_navigate` blocks local addresses (`localhost`, `192.168.x.x`).
- For local web verification, use Playwright tests or headless probes via `terminal`.

### `memory`
- Save only durable, cross-session facts (preferences, env, conventions).
- Do NOT save task progress, commit SHAs, or temporary TODO state.
- Use session ledger files for task state.

## Non-git project adaptation

Many projects live in `/mnt/data/natan-storage/` without git history. For these:

1. Skip `using-git-worktrees` worktree creation.
2. State the base directory explicitly.
3. Use `write_file` to save plan/spec to `.hermes/plans/` inside the project or under `~/obsidian-memory/Projects/<project>/`.
4. Use git only if the project is already a repo.
5. For delivery, package with `tar` and upload via `yandex-api` if requested.

## Ledger file convention

To survive Hermes context compaction, maintain a ledger:

```markdown
# Ledger — plan: .hermes/plans/YYYY-MM-DD_HHMMSS-feature.md

- [x] Task 1: setup project skeleton
- [ ] Task 2: implement product catalog
  - fix round 1: address review feedback
- [ ] Task 3: add modal and form
- [ ] Task 4: SEO + SSR prerender
```

Save ledger beside the plan file as `<plan>-ledger.md`.
