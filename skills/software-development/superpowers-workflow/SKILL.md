---
name: superpowers-workflow
description: |
  Primary umbrella workflow for Hermes. Adapts the upstream Superpowers
  methodology (brainstorm → plan → isolate → execute → verify → review → finish)
  to Hermes tools, MCP servers, OpenCode/delegate_task agents, and our
  project-specific skills. Use for every software build, refactor, or complex bugfix.
category: software-development
related_skills:
  - superpowers-brainstorming
  - superpowers-writing-plans
  - superpowers-using-git-worktrees
  - superpowers-subagent-driven-development
  - superpowers-executing-plans
  - superpowers-dispatching-parallel-agents
  - superpowers-finishing-a-development-branch
  - superpowers-writing-skills
  - code-quality-gates
  - ponytail
  - ponytail-review
  - codebase-memory-audit
  - react-premium-landing-effects
  - yandex-api
  - yandex-seo-optimization
  - obsidian
---

# Superpowers Workflow for Hermes

Adapt the upstream [Superpowers](https://github.com/obra/superpowers) software-development methodology to the Hermes agent environment.

**Core loop:**

```
Brainstorm → Plan → Isolate → Execute → Verify → Review → Finish
```

This is the **primary umbrella skill** for software work in Hermes. It tells you which focused skill to load at each stage and how to move between stages. It also wires in our Hermes-specific tools and external context sources.

---

## When to use

Use for:
- building a feature or component
- refactoring code
- fixing a complex bug
- adding or modifying software in any project

Do NOT use for:
- one-liner shell commands
- pure explanations or consultations
- tasks the user explicitly wants done without a plan

---

## Phase 0: Knowledge Discovery

Before any design, load the most relevant prior knowledge. Use these sources in order:

1. **`session_search`** — prior Hermes conversations about this project.
2. **`skills_list` + `skill_view`** — project-specific skills (e.g. `pentajunior-v2-seo`, `frontend-efficiency-audit`, `frontend-css-maintenance`).
3. **Obsidian vault** — project notes, MOCs, runbooks, design references, prior audits.
   - Key MOCs: `[[MOC — Index]]`, `[[MOC — Projects]]`, `[[MOC — Skills]]`, `[[MOC — Operations]]`, `[[MOC — Technical]]`.
   - Use the `obsidian` MCP server or terminal fallback.
   - **Pitfall:** If the user's primary vault path is already in memory (e.g. `~/obsidian-memory`), do not keep retrying `mcp_obsidian_list_available_vaults` when it times out. Use the known path via terminal fallback immediately and continue knowledge retrieval.
4. **Project files** — README, package.json, recent commits, directory structure.
   - **Pitfall (greenfield vN):** When the user asks for a new version of an existing project (e.g. `silicone-landing-v3` when `silicone-landing-v2` exists), inspect the latest prior version in the same parent directory first. Reuse data structures, copy, images, design tokens, and contact info unless the user explicitly wants a clean slate.
5. **`codebase-memory-audit`** — for projects with more than 5 files, architecture questions, or first exploration.
   - Index via the `codebase-memory` MCP server.
   - Query `get_architecture(aspects=['all'])` for hotspots, layers, boundaries, entry points.
   - Save summary to `~/obsidian-memory/Projects/<project>/codebase-memory-audit.md`.

### OpenCode preparation (if needed)

When the execution phase will use **OpenCode CLI**, run an MCP-aware smoke test before design/planning:

```bash
opencode --version
opencode auth list
opencode run 'List the MCP servers and tools you can access, then respond exactly: OPENCODE_SMOKE_OK'
```

The smoke test must confirm:
- CLI launches,
- model responds,
- MCP servers (`obsidian`, `codebase-memory`) are reachable.

If OpenCode or its MCP fail, stop and report. Do not silently fall back to reading files outside the project directory.

### External context via MCP

When briefing OpenCode, include an explicit **External context sources** block. Do not rely on OpenCode remembering its MCP servers or inferring external research. The block must be present in every brief:

```markdown
## External context sources

Use the configured MCP servers for all research outside this project directory:
- **obsidian** — query the `obsidian-memory` vault for design references, project notes, templates, runbooks.
- **codebase-memory** — index and query relevant repositories for architecture, file structure, data paths, and reusable code.

Do NOT read, copy, or list files outside the current project directory via direct terminal commands. If MCP servers are unavailable, stop and report.
```

### Karpathy lens

Apply these four principles from Andrej Karpathy's coding guidelines in every phase:

1. **Think Before Coding** — state assumptions explicitly, present multiple interpretations, surface tradeoffs, stop and ask when confused.
2. **Simplicity First** — minimum code that solves the problem; no speculative features, single-use abstractions, or unnecessary flexibility.
3. **Surgical Changes** — touch only what the request requires; clean up only the mess your changes create.
4. **Goal-Driven Execution** — every task must have verifiable success criteria before implementation begins.

### Ponytail lens

Apply the lazy senior developer ladder from `ponytail` during design and implementation:

1. **Does this need to exist at all?** (YAGNI)
2. **Already in the codebase?**
3. **Stdlib does it?**
4. **Native platform feature covers it?**
5. **Already-installed dependency solves it?**
6. **Can it be one line?**
7. **Only then:** minimum code that works.

Use `ponytail-review` as an optional Phase 6 pass to find over-engineering before merge.

---

## Phase 1: Brainstorm / Design

**Goal:** agree on *what* to build before writing code.

1. Load the most specific skill for the project (`skills_list` → `skill_view`).
2. Check memory and Obsidian for prior work.
3. State assumptions explicitly. If multiple interpretations exist, present them — don't pick silently.
4. Ask clarifying questions **one at a time**.
5. Propose 2–3 approaches with trade-offs.
6. For visual design questions, use `claude-design`, `sketch`, `popular-web-designs`, or `ui-ux-pro-max`.
7. Get explicit approval before any code.

**Hard gate:** no implementation until the user approves the design.

When the design is approved:
- Save the spec to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` or `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>-design.md`.
- Run a quick self-review for placeholders, contradictions, ambiguity, scope.
- Ask the user to review the written spec before proceeding to planning.

---

## Phase 2: Plan

**Goal:** produce a detailed, task-by-task implementation plan.

1. Load `superpowers-writing-plans`.
2. Save plan to `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md` or `docs/superpowers/plans/`.
3. Every task must be 2–5 minutes, with exact file paths and verification commands.
4. Include delivery steps if relevant: build, lint, screenshots, Yandex.Disk upload, Telegram notification.
5. End plan with hand-off marker:
   > "Use `superpowers-workflow` → `superpowers-subagent-driven-development` to implement task-by-task."

---

## Phase 3: Isolate

**Goal:** work in a safe, isolated workspace.

1. Load `superpowers-using-git-worktrees`.
2. Detect existing isolation first (`GIT_DIR` vs `GIT_COMMON`).
3. If not isolated, ask the user whether to create a worktree.
- For non-git projects (common in `/mnt/data/natan-storage/`), work in place but clearly state the base directory. Do not create phantom worktrees.
- **Hermes skill location note:** custom skills must live under `~/.hermes/skills/` (global) to be discovered by `skills_list`/`skill_view`. The profile-specific directory `~/.hermes/profiles/default/skills/` is not scanned by the skill loader. If you create or copy skills into a profile directory, move them to the global `~/.hermes/skills/<category>/` tree before relying on them.
5. Verify clean baseline: run tests, lint, build — confirm passing.

---

## Phase 4: Execute

Pick the execution strategy based on task shape.

**Default rule:** if the task originated from a user request that is large
enough to need a plan (Phase 2) or design (Phase 1), prefer subagent or
OpenCode execution. Inline single-session execution is only for genuinely
small changes that fit in one verification cycle.

**User preference:** when the user says to use OpenCode, always grant applicable permissions and proceed through the OpenCode path unless a runtime error makes it impossible; in that case, report the blocker and fall back to subagents or inline execution rather than silently stalling.

### 4A: Single session (small or tightly coupled)
- Load `superpowers-executing-plans`.
- Work through tasks in the main Hermes session.
- Run verifications exactly as written in the plan.
- Before editing a function, search its callers and nearby helpers. Prefer one shared update over parallel guards.
- Scan nearby code for duplication, dead code, generalizable helpers, stdlib/native alternatives.
- **Trap check:** if you notice you are writing more than ~3 files or
  making UI/UX decisions beyond the approved spec, pause and either (a)
  escalate to the user for design approval, or (b) fall back to Phase 1/2
  before continuing. Coding around missing design is the most common way
  single-session execution violates the umbrella.

### 4B: Subagent-driven (recommended for multi-task plans)
- Load `superpowers-subagent-driven-development`.
- Use `delegate_task` for each task. Fresh context per subagent.
- Two-stage review after each task:
  1. Spec compliance — did it match the plan?
  2. Code quality — is it well-built?
- Fix and re-review before moving on.
- Maintain a ledger file at `.hermes/plans/<slug>-ledger.md` to survive context compaction.

### 4C: OpenCode-driven (large greenfield projects)
- Use OpenCode CLI with a detailed brief **piped via stdin**: `opencode run < /tmp/brief.md`.
- Do NOT use `opencode run -f /tmp/brief.md 'prompt'` — the positional argument is unreliable.
- Run the OpenCode smoke test first:
  ```bash
  opencode --version
  opencode auth list
  opencode run 'List the MCP servers and tools you can access, then respond exactly: OPENCODE_SMOKE_OK'
  ```
- Include an explicit **External context sources** block in the brief so OpenCode uses `obsidian` and `codebase-memory` MCP servers for external research instead of direct filesystem access.
- **Headless limitation:** `opencode run < brief.md` frequently fails with an internal `todowrite` SchemaError, even with `--auto --dir` and `--pure`. When the user asks for scripted/parallel agent execution or writes outside OpenCode's default cwd, prefer Hermes `delegate_task` subagents and reference `references/opencode-headless-limitations.md`. That reference includes a configuration recipe (update `opencode-ai`, disable MCP servers in `~/.config/opencode/opencode.json`, prepend `"Do not use todo or planning tools"`, and verify immediately).
- **Fallback rule:** if the smoke test passes but OpenCode still cannot reach MCP servers during execution (logs show `obsidian_list-available-vaults Unknown`, `codebase-memory_list_projects Unknown`, or repeated MCP timeouts), do **not** keep retrying or leave OpenCode stalled. Stop the agents, report the failure to the user, and fall back to **inline execution** using `superpowers-executing-plans`. Do not let an MCP outage block delivery of an already-approved plan.
- If OpenCode's bundled `opencode` skill cannot be edited (it is protected), place additional OpenCode-specific workflow rules in this umbrella skill and in `references/opencode-mcp-pitfall.md`.
- Hermes retains ownership of planning, verification, and final review.

### 4D: Parallel dispatch (independent failures)
- Load `superpowers-dispatching-parallel-agents`.
- Dispatch up to 3 `delegate_task` subagents concurrently.
- After they return, integrate and run full suite.

**Constraints:**
- Max 3 concurrent `delegate_task` subagents.
- Max 2 concurrent heavy CLI agents (OpenCode / Claude Code / Codex).
- Do NOT delegate web search or browser navigation to subagents.

---

## Phase 5: Verify

**Goal:** evidence before claims.

1. Load `code-quality-gates` and run the relevant gate(s):
   - **Gate 1 (TDD)** for new features / bugfixes: write failing test (RED), make it pass (GREEN), clean up (REFACTOR).
   - **Gate 2 (Systematic Debugging)** for unexpected failures: root cause first, then fix.
   - **Gate 3 (Pre-Commit Verification)** before commit/merge: security scan, tests/lint, self-review, reviewer subagent.
   - **Gate 4 (Runtime Debugging)** when logs/tests are not enough.
2. Identify the command that proves the claim.
3. Run it fresh. Read the full output.
4. Only then claim success.

For deep reference on a specific gate, load the archived Superpowers skill:
- TDD deep-dive → `superpowers-test-driven-development` (archived reference)
- Debugging deep-dive → `superpowers-systematic-debugging` (archived reference)
- Verification deep-dive → `superpowers-verification-before-completion` (archived reference)

---

## Phase 6: Review

**Goal:** catch issues before they cascade.

1. Load `code-quality-gates` Gate 3 (Pre-Commit Verification) for the reviewer subagent template and security scan.
2. For subagent-driven tasks, also follow the two-stage review in `superpowers-subagent-driven-development`:
   1. Spec compliance — did it match the plan?
   2. Code quality — is it well-built?
3. Fix Critical issues immediately.
4. Fix Important issues before proceeding.
5. Note Minor issues for later.

Run `ponytail-review` as an optional over-engineering pass: it lists what to
delete, replace with stdlib/native, or shrink. Route correctness and security
findings to `code-quality-gates`.

For the original Superpowers review discipline as a reference, see `superpowers-requesting-code-review` (archived reference).

---

## Phase 7: Finish

**Goal:** integrate the work cleanly.

1. Load `superpowers-finishing-a-development-branch`.
2. Run full test suite / build / lint.
3. Detect workspace state (normal repo / worktree / detached HEAD / non-git directory).
4. Present options:
   - Merge locally
   - Push and create PR
   - Keep as-is
   - Discard
5. Execute chosen option.
6. For non-git projects, package deliverables and upload to Yandex.Disk if requested (use `yandex-api`).
7. Report final result with evidence: commands run, output, file paths, screenshots, public URLs.

---

## Quick reference

| Stage | Skill to load | Output |
|---|---|---|
| Knowledge Discovery | `obsidian`, `codebase-memory-audit`, `session_search` | context summary |
| Brainstorm / Design | project-specific skills + `superpowers-brainstorming` | approved spec |
| Plan | `superpowers-writing-plans` | plan file |
| Isolate | `superpowers-using-git-worktrees` (or stated base dir) | clean workspace |
| Execute | `superpowers-subagent-driven-development` / `superpowers-executing-plans` / OpenCode | implemented tasks |
| Verify | `code-quality-gates` (Gates 1–4 as needed) | fresh evidence |
| Review | `code-quality-gates` Gate 3 + `superpowers-subagent-driven-development` two-stage review + optional `ponytail-review` | reviewed code |
| Finish | `superpowers-finishing-a-development-branch` + `yandex-api` (optional) | delivered work |

---

### Anti-patterns

- Skipping design for "simple" changes.
- Writing code before a failing test.
- Claiming completion without running verification.
- Trusting subagent success reports blindly.
- Cleaning up a worktree the user needs for PR iteration.
- Delegating web search or browser navigation to subagents.
- Reading files outside the project directory without MCP.
- **Importing or keeping harness-only skills** like `using-superpowers` that are
  meant for Codex/Pi/Antigravity. In Hermes the umbrella skill already defines
  the workflow; extra harness-specific bootstrap skills create confusion and
  stale references.
- **Executing a multi-file build/refactor/UI task inline in the controller
  session without a written plan and explicit user approval.** This is the
  single most common umbrella violation. It skips Gate 0 knowledge discovery,
  bypasses subagent review, and produces code that the user did not approve in
  structure before implementation. If you catch yourself writing a page.tsx,
  component directory, or data model from scratch in the main session, stop,
  load `superpowers-writing-plans`, and ask for approval on the plan.
- **Forgetting to mark interactive Next.js App Router sections as Client Components.** In Next.js 15 App Router, any component that uses event handlers (`onClick`), `useState`, `useEffect`, or `document`/`window` must include `"use client"` at the top. Server Component pages can *import* Client Components, but passing `onClick` props to a Server Component will fail at build time with: `Error: Event handlers cannot be passed to Client Component props`. When converting a Vite/React SPA to Next.js, audit each component for interactivity and add `"use client"` where needed.
- **Using `JSX.Element` as an explicit return type in React 19 + TypeScript 5 strict projects.** React 19 removes the global `JSX` namespace. Replace `JSX.Element` with `React.JSX.Element` or rely on type inference. See `frontend-css-maintenance` → `references/nextjs15-react19-jsx-namespace.md`.
- **Framer Motion `initial={{ opacity: 0 }}` combined with `whileInView` on Next.js 15 App Router static pages.** The server-rendered output is invisible until the client intersection observer fires, so first paint and full-page screenshots look broken. Use `initial={{ opacity: 1, y: 20 }}` (or another transform-only visible state) and animate to the final position. See `references/framer-motion-ssr-initial-opacity.md`.

Load them only when the gate in `code-quality-gates` requires deeper detail than the compact checklist provides.

### Skill audit and merge methodology

When asked to audit, adopt, or consolidate skills, follow the method in `references/skill-audit-and-merge-methodology.md`:

1. Compare **method and result on the output**, not just coverage.
2. Choose the skill that gives the clearer, more actionable, more Hermes-native path.
3. Consolidate the best parts into one class-level skill rather than keeping two overlapping entries.
4. Preserve canonical umbrellas (`superpowers-workflow`, `code-quality-gates`) and project-specific skills the user explicitly wants to keep.
5. Update or remove stale `related_skills` after every archive/merge/delete.

Quality gate: after the audit, run a broken-reference check across the active skill tree. No active skill should reference a non-existent or archived skill in `related_skills` or in a directive context.

## References

- `superpowers-brainstorming` — Socratic design refinement
- `superpowers-writing-plans` — plan authorship
- `superpowers-using-git-worktrees` — workspace isolation
- `superpowers-subagent-driven-development` — task-by-task delegation
- `ponytail` — lazy senior developer lens (YAGNI, stdlib-first, minimum diff)
- `ponytail-review` — over-engineering review pass
- `code-quality-gates` — Hermes-specific quality gates: TDD, debugging, pre-commit verification, runtime debugging
- `superpowers-finishing-a-development-branch` — merge/PR/cleanup
- `superpowers-dispatching-parallel-agents` — parallel failure investigation
- `codebase-memory-audit` — codebase intelligence via MCP
- `obsidian` — vault access for project context
- `yandex-api` — file upload and public links
- `yandex-seo-optimization` — Yandex SEO workflow
- `react-premium-landing-effects` — polished dark landing-page motion effects (gradient meshes, glassmorphism, shimmer, staggered entrances).

### Archived Superpowers references (deep-dive only)

These skills were absorbed into `code-quality-gates` but remain in `.archive` for detailed reference:

- `superpowers-test-driven-development` — RED-GREEN-REFACTOR deep-dive
- `superpowers-systematic-debugging` — 4-phase debugging deep-dive
- `superpowers-verification-before-completion` — evidence-before-claims deep-dive
- `superpowers-requesting-code-review` — pre-merge review discipline
- `superpowers-receiving-code-review` — responding to feedback

- `references/skill-audit-and-merge-methodology.md` — how to audit external skill libraries and consolidate local duplicates without broken references
- `references/hermes-tool-mapping.md` — Superpowers actions → Hermes tools
- `references/opencode-mcp-pitfall.md` — OpenCode sandbox auto-reject, MCP Unknown, and fallback rules
- `references/opencode-sandbox-external-directory.md` — OpenCode auto-reject on writes outside its cwd and the delegate_task fallback
- `references/opencode-headless-limitations.md` — internal `todowrite` SchemaError in headless `opencode run < brief.md` and the delegate_task fallback
- `references/opencode-briefing-pattern.md` — canonical OpenCode brief and pitfalls
- `references/nextjs-app-router-spa-migration.md` — migrating React/Vite landing pages to Next.js 15 App Router; client-component boundaries, metadata/JSON-LD, font setup, image paths, and build verification.
- `references/ecc-portable-ideas.md` — portable ideas from ECC (affaan-m/ECC) without installing the npm package
- `references/framer-motion-ssr-initial-opacity.md` — Framer Motion `whileInView` animations that start at `opacity: 0` cause blank SSR/SSG first paint; use a visible opacity with a transform offset, especially for sticky-scrolling feature cards.
- `references/external-design-spec-adaptation.md` — applying an external design instruction/spec to an existing project while preserving content, SEO, semantics, and functionality.
- `references/design-adaptation-checklist.md` — older checklist variant (prefer `external-design-spec-adaptation.md`).
- `references/opencode-briefing-pattern.md` — canonical OpenCode brief and pitfalls
- `references/opencode-mcp-pitfall.md` — OpenCode sandbox auto-reject, MCP Unknown, and fallback rules
- `references/nextjs-app-router-spa-migration.md` — migrating React/Vite landing pages to Next.js 15 App Router; client-component boundaries, metadata/JSON-LD, font setup, image paths, and build verification.