# OpenCode Briefing Pattern for Hermes

Canonical way to hand off large coding tasks to OpenCode from a Hermes session.

## 1. Smoke test (before writing the brief)

```bash
opencode --version
opencode auth list
opencode run 'List MCP servers you can access, then respond exactly: OPENCODE_SMOKE_OK'
```

Success means: CLI starts, model answers, and `obsidian`/`codebase-memory` MCP servers are reachable. If any step fails, stop and report to the user instead of launching OpenCode.

Also verify the CLI and plugin are up to date before a large headless run:

```bash
npm install -g opencode-ai@latest
cd ~/.config/opencode && npm install @opencode-ai/plugin@latest
```

## 2. Brief delivery

Always pipe the brief via stdin:

```bash
opencode run --auto --dir /path/to/project --title 'brief task' < /tmp/brief.md
```

Use `--auto` to auto-approve filesystem permissions and `--dir` to set the
working directory. Bad forms to avoid:

```bash
# WRONG — positional prompt is unreliable and may be treated as a file
opencode run -f /tmp/brief.md 'implement this'

# WRONG — brief is not piped
opencode run 'implement /tmp/brief.md'
```

## 3. Prompt guard against the todo schema bug

At the very top of every headless brief, add:

```markdown
Do not use todo, planning, or task-tracking tools. Do not call todowrite or
similar tools. Execute the work directly.
```

Without this guard, OpenCode may invoke its internal `todowrite` tool with a
schema that fails in headless mode and abort before creating files.

## 4. Required brief sections

1. **Goal** — one sentence.
2. **Plan** — copy-pasteable tasks from the written plan. Keep headless briefs
   small (1–3 files per run). For large work, use Hermes `delegate_task` subagents
   instead of one giant OpenCode brief.
3. **Project context** — tech stack, file structure, conventions, existing file paths.
4. **External context sources** — verbatim block below (only if MCP servers are enabled).
5. **Coding principles** — verbatim block below.
6. **Files to touch / not touch**.
7. **Verification commands** per task.
8. **Output format** — git status, test/lint/build output, concerns.

## 5. Verbatim "External context sources" block

Skip this block if MCP servers are disabled in `~/.config/opencode/opencode.json`
and the context is inlined in the brief.

```markdown
## External context sources

Use the configured MCP servers for all research outside this project directory:
- **obsidian** — query the `obsidian-memory` vault for design references, project notes, templates, runbooks.
- **codebase-memory** — index and query relevant repositories for architecture, file structure, data paths, and reusable code.

Do NOT read, copy, or list files outside the current project directory via direct terminal commands. If MCP servers are unavailable, stop and report.
```

## 6. Verbatim coding principles block

```markdown
## Coding principles

1. TDD: write the failing test first, watch it fail, write minimal code, watch it pass, refactor.
2. No production code without a failing test first.
3. One behavior per test; clear descriptive names; test real code, not mocks when possible.
4. Run the exact verification command after every task and report the result.
5. No hardcoded secrets, SQL injection, shell injection, eval/exec with user input, or path traversal.
6. Validate user inputs; handle errors for I/O, network, DB calls.
7. Keep changes surgical — only touch files required by the task.
8. DRY and YAGNI: reuse existing helpers, prefer stdlib, no speculative abstractions.
9. Commit after every task.
10. If a task is unclear, stop and state what is missing. Do not guess.
11. No web search or browser navigation. Use only project files and tools.
12. Use MCP servers (obsidian, codebase-memory) for external context; never read files outside the workdir directly.
```

## 7. Monitoring

Run OpenCode in background with `notify_on_complete=True` so you can keep working:

```python
terminal(
    command="cd /tmp && opencode run --auto --dir /path/to/project --title 'task' < /tmp/brief.md",
    background=True,
    notify_on_complete=True
)
```

Then poll:

```python
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>", limit=200)
```

## 8. Recovery after compaction

OpenCode sessions cannot resume from Hermes context compaction. Use a **ledger file** to track which tasks are complete:

```markdown
# Ledger — plan: .hermes/plans/YYYY-MM-DD-feature.md

- [x] Task 1: scaffold
- [ ] Task 2: implement catalog
  - fix round 1: address review feedback
- [ ] Task 3: SEO
```

Save the ledger beside the plan. After compaction, read the ledger and `git log` to reconstruct state.

## 9. Pitfalls from real sessions

- OpenCode may cancel `npm create vite` if the target directory already exists. Prepare the skeleton yourself, or ensure the directory does not exist before launch.
- Vite SSR requires two builds: `vite build` for the client and `vite build --ssr entry.tsx --outDir dist/server` for prerender. Do not put `build.ssr` in `vite.config.ts` or the client `index.html` will not be produced.
- OpenCode's todo tool may fail with schema errors; do not rely on it for progress tracking. Use a ledger file instead. Add `"Do not use todo or planning tools"` to the brief to avoid the schema error.
- OpenCode may attempt direct `cat`/`ls`/`cp` on files outside the project directory. This is blocked by the sandbox. Either disable MCP servers and inline context, or include the MCP instruction block and verify the smoke test.
- Large multi-file briefs via headless stdin may silently truncate. For 10+ files or a full landing page, prefer Hermes `delegate_task` subagents.
- Stale `opencode-ai` CLI / plugin versions can cause `todowrite` schema errors even with the prompt guard. Update both before headless runs.
