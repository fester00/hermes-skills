---
name: autonomous-coding-agents
description: Use when delegating coding to an autonomous agent. Pick the right agent, write a clear brief, and recover from failures.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata: hermes: tags: [agents, coding-agents, opencode, subagents, delegation, orchestration] related_skills: [claude-code, codex, code-quality-gates]
--- # Autonomous Coding Agents Use this skill when you need to delegate implementation work to an autonomous coding agent and want to pick the right tool, write a bulletproof brief, and recover gracefully when the agent fails. ## When to use which agent Present the user with the available options and a recommendation when a task can be delegated. Current agents: | Agent | Model / environment | Best for |
|---|---|---|
| Hermes `delegate_task` (subagent) | Same model as orchestrator; inherits no Hermes skills/memory unless passed in context | Complex multi-step work where the orchestrator must keep control, iterate with the user, or apply Hermes-specific tooling (browser, web search, custom skills) |
| OpenCode Ollama | Local `ollama/kimi-k2.7-code:cloud` | Private / offline tasks, small code changes, no API spend |
| Codex / Claude Code | User-requested only | When the user explicitly names the tool | | Situation | Preferred agent |
|---|---|
| User explicitly asked for OpenCode | OpenCode Go |
| User explicitly asked for Codex / Claude Code | That tool |
| 1–3 files, ≤15 min, needs orchestrator context | Hermes `delegate_task` |
| 3–5 files, isolated coding | Hermes `delegate_task` or OpenCode Go |
| >5 files, refactoring, site/project from scratch, planning/review/audit | OpenCode Go |
| OpenCode fails on `todowrite` or permissions | Hermes `delegate_task` |
| Need iteration and user feedback | Interactive TUI (OpenCode / Claude Code) or Hermes | ## Brief template Every autonomous agent brief must include: 1. **Goal** — one sentence.
2. **Project path** — absolute path.
3. **Files to create/modify** — exact list.
4. **Files NOT to touch** — guardrails.
5. **Tech stack & constraints** — versions, lint rules, semantic HTML, etc.
6. **Design tokens / colors / fonts** — if UI work.
7. **Tooling and environment** — exact interpreter, installed packages, templates, or scaffolding the agent must use. If the task needs a local library (e.g. `python-docx`), point the agent to the prepared virtualenv or paste a working install command.
8. **Verification commands** — `npx tsc --noEmit`, `npm run build`, test command, or a programmatic check of the generated artifact. When the task implements a **wire protocol, API contract, or external file format** (an assistant skill envelope, a webhook payload, a signed token format), paste the authoritative doc reference into the brief and say the contract comes from it. An implementer reproduces the brief verbatim: a wrong field name or envelope in the brief becomes wrong code, and a test written to agree with the brief hides it. Require one call against the **real** service, not only mocked tests.
9. **Expected output format** — file list + verification results.
10. **Skill / memory are not inherited** — remind the agent that it does not have access to the orchestrator's Hermes skills, memory, or prior conversation context. All required background, constraints, and examples must be explicit in the brief. ## OpenCode CLI version selection OpenCode has two incompatible CLI generations. Use the right one before dispatching: | Generation | Package | `--version` output | Use case |
|---|---|---|---|
| V1 | `opencode-ai` | `1.18.x` | Legacy profiles; avoid for new work |
| V2 | `@opencode/cli` | `opencode v2.x.x` | Cloud providers (`opencode-go`, `opencode-zen`) and current config schema | When installing or switching to V2, both packages share the `opencode` binary name, so use `--force`: ```bash
npm install -g @opencode/cli@latest --force
opencode --version # expect "opencode v2.x.x"
``` Running V2 config under V1 CLI produces `Omitted native setting that cannot be represented in V1` or `ProviderModelNotFoundError`. If that appears, reinstall V2 with `--force`. **For headless one-shot tasks, always run V2 with `--standalone`**, otherwise it connects to a background service that may default to the deprecated `exo-free` provider and fail. See `references/opencode-provider-config.md` for the full endpoint, model, MCP and error-decoding guide. ## OpenCode headless pitfalls See `references/opencode-headless-failure-fallback.md` for the full
investigation and reproduction. ### `todowrite` schema error **Symptom:**
```
✗ Todos failed
Error: The todowrite tool was called with invalid arguments:
SchemaError(Missing key at ["todos"][0]["content"])
``` **Cause:** OpenCode's built-in todo tool breaks in headless `opencode run < brief.md` mode on multi-step tasks. **Fix:** Add an anti-todo instruction at the top of the brief:
```markdown
Do not use todo, planning, or task-tracking tools. Do not call todowrite
or similar tools. Execute the work directly.
```
If it still fails after a retry, **immediately switch to Hermes `delegate_task`**. ### External directory permission denied **Symptom:** `permission requested: external_directory` → auto-reject. **Fix:** Use `--auto --dir /absolute/path/to/project`. If still rejected, use `delegate_task`. ### Partial files / empty directory **Symptom:** Agent reports success but directory is empty or only config files exist. **Fix:** Agent crashed silently or the prompt was too large. Read full log, reduce scope to 1–3 files per dispatch, or switch to `delegate_task`. ## V2 command-line syntax V2 `run` syntax is positional, not flag-based: ```bash
opencode run --auto /absolute/path/to/project "Do the task"
``` The V1-style `--dir` flag does not exist in V2. Passing it produces `Unrecognized flag: --dir`. Override the active config file with `OPENCODE_CONFIG`: ```bash
OPENCODE_CONFIG=/home/natan/.config/opencode/profiles/opencodeai.json \
opencode run --auto /absolute/path/to/project "Do the task"
``` Keep profile configs under `~/.config/opencode/profiles/<name>.json`; leave the default at `~/.config/opencode/opencode.json`. For a pre-written brief in a file, **pipe it via stdin** with `-f`: ```bash
OPENCODE_CONFIG=/home/natan/.config/opencode/profiles/opencodeai.json \
opencode run --standalone --auto /absolute/path/to/project -f /tmp/brief.md
``` Do not pass the brief path as a positional prompt (`opencode run 'read /tmp/brief.md'`) — the agent may misinterpret it as the task text rather than as its instructions. ## Hermes subagent best practices - Use `role="leaf"` for implementation workers.
- Pass absolute project path and exact file list in `context`.
- Do NOT assume subagents can read your conversation history.
- Run `npx tsc --noEmit` inside each subagent task when possible.
- For parallel tasks, ensure they don't edit the same files.
- **Tell children not to run `git` at all.** Several children sharing one repo race on the index and sweep each other's half-written files into a commit. Let them leave their work in the tree and have the orchestrator commit after review with an **explicit file list** — never `git add -A` while a sibling is still running.
- **A child will sometimes touch files outside its brief** — a build config, a shared module, a package manifest. Read its diff (`git status`, `git diff`) before believing the scope was respected; a benign extra edit still belongs in the review, not in a silent commit.
- **One steer, then take it back.** When a child starts reverse-engineering a library's private internals or writing ad-hoc introspection harnesses to force a test green, it has lost the thread: send a short directive ("stop; do exactly these N steps; if it still fails, report honestly") once. If it drifts again, finish the task in the controller — a child's call budget is not a substitute for your judgment.
- **The executor the user names wins over this skill's table.** If they ask for subagents, run `delegate_task` waves even where another skill prefers OpenCode (a user-owned umbrella may state that preference); say in one line that you are following the user's choice. Silently substituting the "recommended" tool is a workflow violation, not a judgement call.
- **Never put a privileged step in a child brief** — `sudo`, `systemctl`, nginx, firewall, package installs. A child cannot ask for confirmation, so it either fails loudly or invents a workaround that changes system state. Let it create the artifacts and stop; the controller runs them together with the user.
- **A child cannot ask questions, so pre-decide every branch in the brief.** Give the fallback explicitly ("if X is unavailable, do Y; if Y also fails, report honestly and stop") — otherwise the child guesses, and a guess arrives disguised as a completed task. ## Post-agent verification (mandatory) After any agent reports completion: 1. Inspect file tree: `find. -maxdepth 3 -type f | sort`
2. Check for duplicates / wrong locations.
3. Run TypeScript check: `npx tsc --noEmit`
4. Run build: `npm run build`
5. Start production server and smoke test: - `npm run start` (or `npm run start:standalone` if configured) - `curl -s http://localhost:PORT | grep -E "<title|<h1"`
6. If using `output: 'standalone'` in Next.js: - Verify `.next/static/` is copied to `.next/standalone/.next/static/`, otherwise production will 404 on JS chunks. - Safer default: use `next start` without standalone unless you explicitly need Docker.
7. Run Playwright / e2e smoke if available.
8. Manually review screenshots if visual work.
9. **Verify against the authoritative spec, not only against the tests.** A child can bend the implementation to satisfy a test whose expectation was wrong (or harden the test to match a wrong implementation). When the two disagree, open the upstream documentation and fix whichever is actually wrong — green tests prove consistency, not correctness. ## Recovery decision tree ```
Agent failed?
├── OpenCode todowrite error
│ └── Switch to Hermes delegate_task
├── OpenCode permission denied
│ └── Try --auto --dir (V1) or --auto <path> (V2), else delegate_task
├── OpenCode: "Unrecognized flag: --dir"
│ └── Switch to V2 syntax: opencode run --auto <path> "prompt"
├── OpenCode: "Omitted native setting that cannot be represented in V1"
│ └── Reinstall V2 CLI with --force
├── OpenCode: "ProviderModelNotFoundError" / "Model is unavailable"
│ └── List provider models and pick an existing model ID
├── Agent created wrong structure
│ └── Take over directly; don't redispatch blindly
├── Build / tsc fails after agent
│ └── Fix manually or redispatch with exact error
└── Tests / e2e fail └── Redispatch with failing command and expected behavior
``` ## Rules 1. Never trust an agent's self-report of success without fresh verification.
2. If OpenCode headless fails twice with the same error, stop retrying and switch tool.
3. Always scope agents to a single workdir; never share directories across parallel agents unless designed for it.
4. Capture agent failures in the appropriate skill or support file, not just memory.
5. After visual/UI agent work, always inspect screenshots. ## Verification Smoke test any agent setup before heavy tasks: ```bash
# V1 syntax (legacy)
opencode run --auto --dir /tmp/agent-smoke 'Create a file /tmp/agent-smoke/hello.txt with text OPENCODE_SMOKE_OK' # V2 syntax (current)
opencode run --auto /tmp/agent-smoke 'Create a file /tmp/agent-smoke/hello.txt with text OPENCODE_SMOKE_OK'
``` ```python
delegate_task( goal="Create /tmp/hermes-smoke/hello.txt containing HERMES_SMOKE_OK", context="Project path: /tmp/hermes-smoke. Only create hello.txt.", role="leaf"
)
``` Both should result in the expected file and content. ## See also - `references/opencode-todowrite-fallback.md`
- `references/opencode-headless-failure-fallback.md`
- `references/opencode-provider-config.md`
- `references/opencode-mcp-obsidian-codebase.md`
- `references/opencode-skill-environment.md`
- `opencode` skill for OpenCode-specific commands
- `opencode-v2-cli` skill for V2 profile configuration
- for project lifecycle
- parallel subagents for parallel workstreams
