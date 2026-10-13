# OpenCode Briefing Pattern for Hermes

Canonical way to hand off large coding tasks to OpenCode from a Hermes session.

## 1. Smoke test (before writing the brief)

```bash
opencode --version
opencode auth list
opencode run 'List MCP servers you can access, then respond exactly: OPENCODE_SMOKE_OK'
```

Success means: CLI starts, model answers, and `obsidian`/`codebase-memory` MCP servers are reachable. If any step fails, stop and report to the user instead of launching OpenCode.

Also verify the CLI is up to date before a large headless run:

```bash
npm install -g @opencode/cli@latest --force   # v2 package; the v1 `opencode-ai` package is gone
opencode --version                            # expect v2.x
```

## 2. Brief delivery

Always pipe the brief via stdin:

```bash
cd /path/to/project
export OPENCODE_CONFIG=$HOME/.config/opencode/profiles/opencodeai.json
opencode run --auto --title 'brief task' < /tmp/brief.md
```

Run from the project directory — v2 has **no `--dir` and no `--attach`**; the cwd *is* the working
directory and the provider comes from the profile named by `OPENCODE_CONFIG`. Add `--server <url>` only to
talk to a persistent server, and `--standalone` only when no background service is listening
(`ss -tlnp | grep 49374`). Bad forms to avoid:

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

Include this block whenever the run uses a profile that declares MCP servers (v2 puts them in the profile
under `mcp.servers`). If the profile declares none and the context is inlined in the brief, it can go.

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
    command="cd /path/to/project && OPENCODE_CONFIG=$HOME/.config/opencode/profiles/opencodeai.json "
            "opencode run --auto --title 'task' < /tmp/brief.md",
    background=True,
    notify=True
)
```

Then poll it with the Hermes `process_manage` tool (actions `list` / `poll` / `log`).

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
- OpenCode may attempt direct `cat`/`ls`/`cp` outside the project directory. Reach for the MCP servers
  (vault, code graph) instead of shelling out, and prove they work in the smoke test before the real run.
- Large multi-file briefs via headless stdin may silently truncate: keep one brief to 1–3 files and split the
  rest into lanes. Which runtime executes those lanes is the user's standing engine preference — see
  `references/opencode-vs-subagents.md` rather than deciding here.
- A leftover v1 CLI on PATH causes schema errors and unknown-argument failures even with the prompt guard.
  Keep only `@opencode/cli` (v2) installed, and re-link its bins after any `npm uninstall -g`.
