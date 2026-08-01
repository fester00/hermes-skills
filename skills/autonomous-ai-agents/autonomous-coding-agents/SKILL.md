---
name: autonomous-coding-agents
description: "Choose, brief, and orchestrate autonomous coding agents (OpenCode, Hermes subagents, Codex, Claude Code). Includes fallbacks when agents fail."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [agents, coding-agents, opencode, subagents, delegation, orchestration]
    related_skills: [opencode, claude-code, codex, superpowers-workflow, subagent-driven-development, dispatching-parallel-agents, code-quality-gates]
---

# Autonomous Coding Agents

Use this skill when you need to delegate implementation work to an autonomous coding agent and want to pick the right tool, write a bulletproof brief, and recover gracefully when the agent fails.

## When to use which agent

| Situation | Preferred agent |
|---|---|
| User explicitly asked for OpenCode | OpenCode |
| User explicitly asked for Codex / Claude Code | That tool |
| 1–3 files, ≤15 min | Hermes `delegate_task` |
| 3–5 files, isolated | Hermes `delegate_task` |
| >5 files, refactoring, site/project from scratch | OpenCode or 2 parallel agents |
| OpenCode fails on `todowrite` or permissions | Hermes `delegate_task` |
| Need iteration and user feedback | Interactive TUI (OpenCode / Claude Code) |

## Brief template

Every autonomous agent brief must include:

1. **Goal** — one sentence.
2. **Project path** — absolute path.
3. **Files to create/modify** — exact list.
4. **Files NOT to touch** — guardrails.
5. **Tech stack & constraints** — versions, lint rules, semantic HTML, etc.
6. **Design tokens / colors / fonts** — if UI work.
7. **Verification commands** — `npx tsc --noEmit`, `npm run build`, test command.
8. **Expected output format** — file list + verification results.

## OpenCode headless pitfalls

See `references/opencode-headless-failure-fallback.md` for the full
investigation and reproduction.

### `todowrite` schema error

**Symptom:**
```
✗ Todos failed
Error: The todowrite tool was called with invalid arguments:
SchemaError(Missing key at ["todos"][0]["content"])
```

**Cause:** OpenCode's built-in todo tool breaks in headless `opencode run < brief.md` mode on multi-step tasks.

**Fix:** Add an anti-todo instruction at the top of the brief:
```markdown
Do not use todo, planning, or task-tracking tools. Do not call todowrite
or similar tools. Execute the work directly.
```
If it still fails after a retry, **immediately switch to Hermes `delegate_task`**.

### External directory permission denied

**Symptom:** `permission requested: external_directory` → auto-reject.

**Fix:** Use `--auto --dir /absolute/path/to/project`. If still rejected, use `delegate_task`.

### Partial files / empty directory

**Symptom:** Agent reports success but directory is empty or only config files exist.

**Fix:** Agent crashed silently or the prompt was too large. Read full log, reduce scope to 1–3 files per dispatch, or switch to `delegate_task`.

## Hermes subagent best practices

- Use `role="leaf"` for implementation workers.
- Pass absolute project path and exact file list in `context`.
- Do NOT assume subagents can read your conversation history.
- Run `npx tsc --noEmit` inside each subagent task when possible.
- For parallel tasks, ensure they don't edit the same files.

## Post-agent verification (mandatory)

After any agent reports completion:

1. Inspect file tree: `find . -maxdepth 3 -type f | sort`
2. Check for duplicates / wrong locations.
3. Run TypeScript check: `npx tsc --noEmit`
4. Run build: `npm run build`
5. Start production server and smoke test:
   - `npm run start` (or `npm run start:standalone` if configured)
   - `curl -s http://localhost:PORT | grep -E "<title|<h1"`
6. If using `output: 'standalone'` in Next.js:
   - Verify `.next/static/` is copied to `.next/standalone/.next/static/`, otherwise production will 404 on JS chunks.
   - Safer default: use `next start` without standalone unless you explicitly need Docker.
7. Run Playwright / e2e smoke if available.
8. Manually review screenshots if visual work.

## Recovery decision tree

```
Agent failed?
├── OpenCode todowrite error
│   └── Switch to Hermes delegate_task
├── OpenCode permission denied
│   └── Try --auto --dir, else delegate_task
├── Agent created wrong structure
│   └── Take over directly; don't redispatch blindly
├── Build / tsc fails after agent
│   └── Fix manually or redispatch with exact error
└── Tests / e2e fail
    └── Redispatch with failing command and expected behavior
```

## Rules

1. Never trust an agent's self-report of success without fresh verification.
2. If OpenCode headless fails twice with the same error, stop retrying and switch tool.
3. Always scope agents to a single workdir; never share directories across parallel agents unless designed for it.
4. Capture agent failures in the appropriate skill or support file, not just memory.
5. After visual/UI agent work, always inspect screenshots.

## Verification

Smoke test any agent setup before heavy tasks:

```bash
opencode run --auto --dir /tmp/agent-smoke 'Create a file /tmp/agent-smoke/hello.txt with text OPENCODE_SMOKE_OK'
```

```python
delegate_task(
    goal="Create /tmp/hermes-smoke/hello.txt containing HERMES_SMOKE_OK",
    context="Project path: /tmp/hermes-smoke. Only create hello.txt.",
    role="leaf"
)
```

Both should result in the expected file and content.

## See also

- `references/opencode-todowrite-fallback.md`
- `opencode` skill for OpenCode-specific commands
- `superpowers-workflow` for project lifecycle
- `dispatching-parallel-agents` for parallel workstreams
