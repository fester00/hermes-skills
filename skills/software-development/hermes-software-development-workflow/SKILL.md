---
name: hermes-software-development-workflow
description: |
  Complete software-development lifecycle on Hermes: design &#8594; plan &#8594; delegate &#8594;
  execute &#8594; verify &#8594; finish. Covers brainstorming, writing plans, parallel subagent
  dispatch, git worktrees, execution with checkpoints, verification gates,
  branch completion, and code-review handling.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [software-development, workflow, planning, execution, git, subagents, verification, code-review]
    related_skills: [writing-plans, test-driven-development, requesting-code-review]
---

# Hermes Software Development Workflow

## Overview

This skill governs the full development lifecycle within Hermes: from initial design
through parallel execution, verification, and completion. Use it whenever building
or modifying software in a Hermes session.

**Core principle:** Design before code. Verify before claims. Delegate when parallel. Think before coding — state assumptions, present interpretations, surface tradeoffs.

---

## Phase 0: Load Skills First (User Requirement)

**Trigger:** User asks to build, refactor, or modify software.

**Hard rule for this user:** &gt; ALWAYS load relevant skills BEFORE acting. This user installed skills for a reason and expects them applied.

### Step 0a -- Skill Discovery

1. **ALWAYS start with `skills_list()`** (optionally filtered by category) to discover the most specific skill for the task. The system prompt skill list is a hint only; `skills_list()` is authoritative.
2. Load the most relevant skill(s) via `skill_view(name)` and follow their instructions.
3. **For visual / UI / design / front-end work, also load the relevant design skill(s) BEFORE coding.** Examples:
   - Industry-matched design brief → `ui-ux-pro-max`
   - Real-brand visual vocabulary → `popular-web-designs`
   - One-off HTML artifact → `claude-design`
   - Formal token spec → `design-md`
   - Quick throwaway variants → `sketch`
4. For software work in general, also load:
   - `writing-plans` when the task touches 2+ files or has 2+ stages
   - `code-quality-gates` for verification patterns
5. Only fall back to generic workflow when no skill matches.

**Pitfall (caught in session 2026-06-29):** Relying on the system prompt skill list or an Obsidian skill registry without calling `skills_list()` can miss newly added or profile-specific skills. Obsidian indexes are documentation; `~/.hermes/skills/` is the source of truth.

**Pitfall — Stale skill references (2026-07-27):** Deleted project-specific skills (`luxury-immersive-web`, `nextjs-luxury-landing-to-catalog`, `nextjs-product-catalog-admin`, `pentajunior-v2-nextjs-sqlite`) linger in `related_skills`, runbooks, and MOCs. After deleting a skill, always grep Hermes skills + Obsidian vault for the old name and remove broken references so other agents do not try to load a missing skill.

**Skill deletion + cleanup recipe:**
1. Delete the skill via `skill_manage(action='delete', name=...)` or remove its directory.
2. Search `~/.hermes/skills/`: `rg -n '<skill-name>' ~/.hermes/skills/`.
3. Search Obsidian vault: `rg -n '<skill-name>' ~/obsidian-memory/`.
4. Remove or replace every occurrence. For example references, substitute a current umbrella skill (`popular-web-designs`, `ui-ux-pro-max`, `react-vite-tailwind-landing-pages`).
5. Commit and push both the skills tree and Obsidian vault.

**Upstream skill synchronization:** Some skills mirror external repos (e.g., `popular-web-designs` tracks `VoltAgent/awesome-design-md`, `ui-ux-pro-max` tracks `nextlevelbuilder/ui-ux-pro-max-skill`). Refresh them periodically: check upstream version, backup local skill, update data/templates, update `version` frontmatter, test primary entry point. If upstream changes format significantly, decide whether to adapt the skill or convert upstream files into the existing format — do not blindly overwrite a working format.

### Step 0b -- Confirm the Exact Project Path
**Trigger:** User asks to study, explore, refactor, or modify an existing project.

1. Use the `[Workspace::v1: ...]` tag as the primary hint, **not** hardcoded paths from system prompt or memory.
2. If the user names the project explicitly (e.g. `"pentajunior-v2"`), verify that the directory you open matches that exact name.
3. When in doubt, ask: "Подтверди путь: работаем в <полный путь>?"

**Pitfall:** Opening a similarly-named sibling directory (`pentajunior` instead of `pentajunior-v2`) wastes a full exploration cycle and requires the user to correct you. Always match the exact project name + path.

### Step 0c -- Load Skills Before Acting (User Requirement)

This user expects skills to be loaded **before** implementation begins. After confirming the project path, scan `skills_list` for any skill covering the tech stack or task type (e.g. `react-vite-tailwind-landing-pages`, `expo-tanstack-backend`, `pentajunior-v2-seo`).

If a skill covers the territory:
1. Load it with `skill_view(name)`.
2. Follow its instructions and proven workflows.
3. Only fall back to generic workflow when no skill matches.

**Anti-pattern:** Jumping straight into design or code without checking whether a relevant skill exists. The user has explicitly signalled that skills should be applied first.

### Step 0d -- Optional codebase-memory-audit

After confirming the project path and loading relevant skills, consider a project audit:

- **Run if:** the user is asking about a project with **more than 5 files**,
  asks architecture/refactoring/dependency questions, or this is the first
  exploration of an unfamiliar codebase.
- **Skip if:** single file / one-liner, throwaway prototype.

**Workflow:**
1. Load `codebase-memory-audit`.
2. Ensure the project is indexed via the `codebase-memory` MCP server or CBM CLI
   (`codebase-memory-mcp cli index_repository --repo-path <project-root>`).
3. Call `get_architecture(aspects=['all'])` to get hotspots, layers, boundaries,
   clusters, and entry points.
4. Optionally run `trace_path`, `search_code`, or `query_graph` for specific questions.
5. Save summary to `~/obsidian-memory/Projects/<project>/codebase-memory-audit.md`.
6. Use findings in design and planning.

> **Why CBM:** codebase-memory-mcp is a single static binary, supports 158 languages,
> exposes 14 structural query tools, needs no LLM API key, and indexes projects in
> milliseconds to seconds. The index persists in `~/.cache/codebase-memory-mcp` and
> is refreshed incrementally.

### Step 0d' -- Lazy-review mode

If the user signals minimalism or over-engineering concerns ("be lazy", "shortest
path", "what can we delete?", "simplify", "ponytail"), keep Master Ugwai persona
unchanged and add a lazy lens rooted in the Karpathy principles:

- **Think Before Coding:** explicitly name assumptions and tradeoffs before choosing the minimal path.
- **Simplicity First:** design phase asks whether the change can be solved by deleting or reusing code; plan includes a deletion/simplification scan before adding files.
- **Surgical Changes:** when touching a file, check nearby code for duplication, dead code, or stdlib/native alternatives, but touch only what the request requires.
- **Goal-Driven Execution:** every simplification must still meet the success criteria defined for the task.

**Lazy-review boundaries:**
- Persona stays **Master Ugwai**. The lazy lens is a filter on solutions, not a second character.
- Never cut input validation at trust boundaries, error handling that prevents data loss, security, accessibility, or anything explicitly requested by the user.
- Never use laziness as a reason to skip design approval, verification, or TDD.
- A deliberate shortcut with a known ceiling must be marked with a `ponytail:` comment:
  `# ponytail: <ceiling>, <upgrade trigger>`.
- Non-trivial logic still gets proper tests; a single `assert`-based self-check is only an acceptable smoke test, not a replacement for TDD.

### Step 0e -- Memory Discovery
4. Check `session_search` for past conversations on this topic
5. Check `mcp_obsidian_search_vault` or `mcp_obsidian_list_vaults` for related notes
6. Only ask the user a question when internal knowledge is insufficient

**Anti-pattern:** Jumping straight into design without checking if a skill exists. The user explicitly said: "сперва применяй навыки"

## Phase 1: Design (Brainstorming)

## Phase 1: Design (Brainstorming)

**Trigger:** Any creative work -- creating features, building components, adding
functionality, or modifying behavior.

**Announce:** "I'm using the design phase to explore requirements before implementation."

### Step 0: Knowledge Discovery (ALWAYS FIRST)

Before asking questions or proposing solutions, check internal knowledge sources:

1. **Persistent memory** -- `session_search` for past conversations on this topic
2. **Obsidian vault** -- if available, search for related notes
3. **Existing skills** -- check if a skill covers this workflow or tech stack
4. **Project files** -- read relevant files, docs, recent commits

If internal knowledge is insufficient:
5. **Web search** -- use `web_search` or `browser` tools to gather missing context
6. **Deep research** -- use `browser` for documentation, examples, best practices

### Step 1: Ask Clarifying Questions

After gathering context, identify gaps in the user's request. Ask **one at a time**:
- State assumptions explicitly. If multiple interpretations exist, present them — don't pick silently.
- Purpose and success criteria
- Constraints (tech stack, time, budget)
- Style preferences (for UI: landing vs multi-page, design system)
- Edge cases and error handling expectations

Use **multiple choice preferred** -- easier to answer than open-ended.

#### Design-polish and bugfix requests need explicit framing

When the user asks to "improve the design", "fix bugs", "make scrolling smooth",
or "fix mobile" on an existing project, do not start editing files immediately.
The user often has an implicit workflow in mind. Surface it explicitly by
proposing a default sequence and asking for confirmation:

1. **Audit** — inspect current state and list concrete bugs / design gaps.
2. **Design contract** — agree on what will change and what will stay the same.
3. **Plan** — write implementation steps with verification commands.
4. **Execute** — make the changes in small, verifiable increments.
5. **Verify** — run build, lint, tests, and visual checks.
6. **Finish** — present evidence and next options.

If the user says "just do it" or "start with the audit", adapt, but never skip
the audit step: it prevents rework and gives both sides the same picture of the
starting point. For visual work, also load design skills (`ui-ux-pro-max`, `popular-web-designs`) before the audit so the recommendations
are grounded in a real design vocabulary.

See `references/vidvis-design-review-driven-refactor.md` for a worked example of
this workflow applied to a luxury landing-page refactor, including the corrected
sequence after the user intervened.

### Hard Gate
```
Do NOT invoke any implementation skill, write any code, scaffold any project,
or take any implementation action until you have presented a design and the
user has approved it.
```

### Key Principles
- **Knowledge first** -- always check memory/obsidian/skills before asking user
- **One question at a time** -- don't overwhelm
- **State assumptions explicitly** -- Karpathy principle; ambiguity hides rework
- **Multiple choice preferred** -- easier to answer than open-ended
- **YAGNI ruthlessly** -- remove unnecessary features
- **Explore alternatives** -- always propose 2-3 approaches
- **Incremental validation** -- present design, get approval before moving on
- **Design for isolation** -- smaller units with clear interfaces

### Anti-Pattern
"This is too simple to need a design." Every project goes through this process.
A todo list, a single-function utility, a config change -- all of them. The design
can be short (a few sentences for truly simple projects), but you MUST present it
and get approval.

### Concrete Example: Design-Heavy Tasks
When the user asks for visual expansion of an existing site -- new pages, new
sections, new components, style refresh -- do NOT start writing components
from intuition. Load the relevant design skills first (e.g. `ui-ux-pro-max` for
industry-matched design systems) and use their guidance before producing code. If the user later asks
"did you use design skills?" and the answer is no, stop, load them, and do a
design review before continuing.

### Checklist

1. **Step 0: Knowledge Discovery** -- memory &#8594; obsidian &#8594; skills &#8594; files &#8594; web &#8594; browser
2. **Step 1: Ask clarifying questions** -- one at a time; understand purpose, constraints,
   success criteria
3. **Propose 2-3 approaches** -- with trade-offs and your recommendation
4. **Present design** -- in sections scaled to complexity; get approval after each
5. **Write design doc** -- save to project-appropriate spec location and commit
6. **Spec self-review** -- check for placeholders, contradictions, ambiguity, scope
7. **User reviews written spec** -- ask user to review before proceeding
8. **Transition to planning** -- invoke `writing-plans` skill

---

## Phase 2: Planning (Writing Plans)

After design approval, write a detailed implementation plan. This is handled by
the `writing-plans` skill (separate, focused on plan authorship).

Plan output: bite-sized tasks, explicit file paths, verification commands per step.

---

## Phase 3: Workspace Isolation (Git Worktrees)

**Trigger:** Starting feature work that needs isolation from the current workspace,
or before executing an implementation plan.

**Announce:** "I'm setting up an isolated workspace."

### Step 0: Detect Existing Isolation

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
```

- If `GIT_DIR != GIT_COMMON` (and not a submodule): already in a linked worktree.
  Skip creation. Report branch state.
- If `GIT_DIR == GIT_COMMON`: normal repo. Ask user for worktree preference.

### Directory Priority
1. Declared user preference (always wins)
2. Existing `.worktrees/` or `worktrees/` directory
3. Default: `.worktrees/` at project root

**Critical:** Verify directory is ignored before creating:
```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```
If NOT ignored, add to `.gitignore`, commit, then proceed.

### Create Worktree
```bash
BRANCH_NAME="feature/$(date +%s)-${USER:-agent}"
git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

### Setup & Baseline
Auto-detect project type and install dependencies. Run tests to verify clean baseline.
If tests fail, report and ask whether to proceed.

### Common Pitfalls
- Creating a worktree when already isolated &#8594; nested worktrees
- Worktree not in `.gitignore` &#8594; tracked files polluting repo
- Proceeding with failing baseline tests &#8594; can't distinguish new bugs from old
- Running `git worktree remove` from inside the worktree &#8594; fails silently

---

## Phase 4: Execution Strategies

### 4A: Execute in Current Session (No Subagents)

**Trigger:** You have a written plan and are executing it in the current session.

**Announce:** "I'm using the execution phase to implement this plan."

#### Step 1: Load and Review Plan
- Read the plan file completely
- Review critically: unclear instructions, missing paths, ambiguous verifications
- If concerns exist, present to user before proceeding
- If no concerns, summarize goal, task count, key verifications

#### Step 2: Set Up Workspace
- Never start on `main`/`master` without explicit consent
- Confirm branch exists or create one
- Load `git-worktrees` skill if linked worktree needed

#### Step 3: Execute Tasks
For each task:
1. **Mark in progress:** "Starting Task N: [name]"
2. **Follow each step exactly** -- no scope creep
3. **Run verifications** -- tests, lint, build as specified
4. **Commit** after every task
5. **Human checkpoint** -- stop and report: what was done, verification results,
   any deviations or blockers. Ask whether to continue, stop, or revisit.

#### Step 4: Complete
After all tasks complete and verified:
1. Run full test suite
2. Invoke `finishing-a-development-branch` skill

**When to stop and ask:**
- Blocker (missing dependency, test fails, unclear instruction)
- Critical gaps preventing start
- Don't understand an instruction
- Verification fails after two attempts

#### Variation: Static Site Plans
For static HTML/CSS/JS (no build step):
- No git branch needed (often throwaway deliverables)
- Create `PROJECT_BRIEF.md` with design tokens, DOM contract, page inventory
- Phase 1 solo: base template
- Phase 2 parallel: HTML content + CSS/JS agents simultaneously
- Phase 3 solo: integrate, verify, archive to `.zip`

**Search in static sites** (common failure mode):
- `fetch()` with relative URLs fails when the site is opened via `file://` protocol (CORS blocks file-level fetch)
- **Fix:** inject `window.__SEARCH_DATA__` inline `<script>` into every HTML file, then have `app.js` fall back to it when `fetch()` fails
- **Search URL resolution:** compute from `location.pathname` depth (pop filename segment, then `../` &#215; depth), NOT from hardcoded paths like `app/assets/...`
- **Navigation from results:** use `new URL(m.href, location.href).href` so relative `href` values resolve correctly regardless of current page depth
- See `references/file-protocol-static-site-search.md` for full reproduction recipe

### 4B: Dispatch Parallel Agents

**Trigger:** 2+ independent tasks without shared state or sequential dependencies.

**Core principle:** One agent per independent problem domain. Let them work concurrently.

**Constraint:** `max_concurrent_children` defaults to 3. Do not exceed it. Check your `~/.hermes/config.yaml` for the current value (user's config: **3**).
## Routing guidance:
- User preference for this session: Skills first, agents second. 
Use `delegate_task` only when genuinely useful -- to parallelize independent work
or get a fresh context on a well-scoped sub-task. Do NOT delegate as a default.
Never delegate web search or browser tasks.

**Updated routing (OpenCode-first for heavy coding):**
- Quick question / one-liner → do directly
- 1–3 files, ≤15 min → `delegate_task` subagent
- 3–5 files, isolated → `delegate_task` subagent
- >5 files, refactoring, website/project from scratch → **OpenCode**
- Parallel independent heavy streams → **2 OpenCode agents in background**
- Web search / browser / SEO → always main Hermes session (never OpenCode)

**Why OpenCode for heavy tasks:** `delegate_task` has a hard 25-minute timeout per subagent and a practical limit of 2 concurrent heavy subagents. OpenCode runs in a background process without the 25-minute ceiling and survives Hermes session restarts, making it the right tool for multi-file refactoring or building a site from a plan.

**Concurrency limits on this setup (verified 2026-06-13):**
- Native Hermes `delegate_task` subagents: up to **3 in parallel**.
- Heavy standalone CLI agents (OpenCode, Codex, Claude Code): up to **2 in parallel**, launched via `terminal(background=true)` or `process` tools. They are NOT counted in the `delegate_task` pool.
- Mixed mode: keep total concurrent heavy agents at 2 to avoid model/credential pool exhaustion.

**Hard timeout:** `delegate_task` is capped at 1500 seconds (25 minutes) per subagent. External CLI agents have no hard Hermes timeout.

#### When to Use
- 3+ test files failing with different root causes
- Multiple subsystems broken independently
- Each problem can be understood without context from others

#### When NOT to Use
- Failures are related (fixing one may fix others)
- Need to understand full system state
- Agents would interfere (editing same files)
- Task involves web search or browser navigation (STRICT RULE)

#### Pattern

1. **Identify independent domains** -- group failures by what's broken
2. **Create focused tasks** -- specific scope, clear goal, constraints, expected output
3. **Dispatch:**
```python
result = delegate_task(tasks=[
    {"goal": "Fix X.test.ts failures", "context": "...", "toolsets": ["terminal", "file"]},
    {"goal": "Fix Y.test.ts failures", "context": "...", "toolsets": ["terminal", "file"]},
])
```
(With `max_concurrent_children=3` in your config, do not exceed 3 tasks in one batch.)
4. **Review and integrate** -- read each summary, check for conflicts, run full suite

#### Critical Pitfall: Shared Design Contract
When agents build interdependent outputs (e.g., CSS/JS + HTML), ALWAYS provide a
shared design contract BEFORE dispatching:
1. Write a single brief (design tokens, class names, DOM IDs, file paths)
2. Reference the brief in BOTH agent contexts
3. Give structural agent a head start when possible

#### Pitfall: Agent Timeout with Incomplete Work
If an agent times out after completing only part of its work:
1. Identify what was NOT done via `find` / file listing
2. Dispatch new agents for ONLY the missing pieces
3. Consider giving critical subset to Agent 1, rest to others

---

## Phase 5: Verification Gate

**Trigger:** About to claim work is complete, fixed, or passing.

**Iron Law:**
```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

### The Gate Function
1. **Identify** -- What command proves this claim?
2. **Transform** -- State the success criterion in the Karpathy form: "Write tests for invalid inputs, then make them pass" rather than "Add validation".
3. **Run** -- Execute the FULL command (fresh, complete)
4. **Read** -- Full output, check exit code, count failures
5. **Verify** -- Does output confirm the claim?
   - If NO: state actual status with evidence
   - If YES: state claim WITH evidence
6. **ONLY THEN** -- Make the claim

### Common Failures
- "Tests pass" -- requires output showing 0 failures
- "Linter clean" -- requires output showing 0 errors
- "Build succeeds" -- requires exit code 0
- "Bug fixed" -- requires test of original symptom passes
- "Regression test works" -- requires red-green cycle verified

### Red Flags -- STOP
- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!")
- About to commit/push/PR without verification
- Trusting agent success reports without independent check
- Thinking "just this once"

---

## Phase 6: Finishing (Branch Completion)

**Trigger:** Implementation complete, all tests pass, deciding how to integrate.

**Core principle:** Verify tests &#8594; Detect environment &#8594; Present options &#8594; Execute choice &#8594; Clean up.

### Step 1: Verify Tests
Run the full test suite. If tests fail, stop and fix before proceeding.

### Step 2: Detect Environment
```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
```

### Step 3: Present Options

**Normal repo / named-branch worktree -- 4 options:**
```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work
```

**Detached HEAD -- 3 options:**
```
Implementation complete. You're on a detached HEAD.

1. Push as new branch and create a Pull Request
2. Keep as-is (I'll handle it later)
3. Discard this work
```

### Step 4: Execute Choice

| Option | Merge | Push | Keep Worktree | Cleanup Branch |
|--------|-------|------|---------------|----------------|
| 1. Merge locally | yes | -- | -- | yes |
| 2. Create PR | -- | yes | yes | -- |
| 3. Keep as-is | -- | -- | yes | -- |
| 4. Discard | -- | -- | -- | yes (force) |

**Critical rules:**
- Merge first, verify success, THEN remove worktree and delete branch
- For Option 2/3, NEVER clean up worktree -- user needs it for PR iteration
- For Option 4, require typed "discard" confirmation before proceeding
- Only clean up worktrees under known managed directories (`.worktrees/`, `worktrees/`)
- Always `cd` to main repo root before `git worktree remove`
- Run `git worktree prune` after removal

---

## Phase 7: Receiving Code Review

**Trigger:** Receiving any code review feedback (GitHub PR comments, inline reviews,
self-review, suggestions from users).

**Core principle:** Verify before implementing. Ask before assuming. Technical
correctness over social comfort.

### Response Pattern: Triage &#8594; Plan &#8594; Implement &#8594; Verify

1. **TRIAGE** -- Read all feedback without reacting. Group into:
   - Quick wins (typos, style, imports)
   - Complex changes (logic, refactoring, API changes)
   - Blockers or points needing clarification
2. **PLAN** -- Restate unclear requirements. Ask for clarification if needed.
3. **IMPLEMENT** -- One item at a time, smallest first. No batching without testing.
4. **VERIFY** -- Check against codebase reality and existing tests after each fix.

### Forbidden Responses
- ❌ "You're absolutely right!" / "Great point!" / "Excellent feedback!" -- performative
- ❌ "Let me implement that now" -- before verification
- ✅ Restate the technical requirement
- ✅ Ask clarifying questions
- ✅ Push back with technical reasoning if wrong
- ✅ Just start working (actions > words)

### Handling Unclear Feedback
```
IF any item is unclear:
  STOP -- do not implement anything yet
  ASK for clarification on unclear items
```

### Pushing Back
Push back when:
- Suggestion breaks existing functionality
- Reviewer lacks full context
- Violates YAGNI (unused feature)
- Technically incorrect for this stack
- Conflicts with human partner's architectural decisions

**How:** Use technical reasoning, not defensiveness. Ask specific questions.
Reference working tests/code.

---

### Subagent Timeout Reality

`delegate_task` hard timeout = **1500 seconds (25 minutes)** per subagent.

There are **no artificial micro-limits** on files touched, tool calls, or context size.
Size tasks based on this real ceiling only.

If a task legitimately exceeds 25 minutes, split into smaller independent chunks
or run heavy work in the main session (no timeout ceiling).

### Subagent Provider Limits

`delegate_task` can fail before any work starts if the configured provider
(e.g. ollama-cloud) hits a weekly/daily request cap. Typical symptom:
`HTTP 429 from ollama.com — weekly usage limit`.

When this happens:
1. Do **not** keep retrying subagents — the pool is exhausted.
2. Switch to **manual execution waves in the main session**.
3. Use a `todo` list to track plan tasks.
4. Run the same verification gates after each task.
5. Commit after every task.

See `references/subagent-api-fallback.md` for the full fallback workflow.

---

### Integration with Other Skills

| Skill | Role in lifecycle |
|-------|-------------------|
| `writing-plans` | Creates the plan that execution phases consume |
| `test-driven-development` | Follow TDD within each task when specified |
| `requesting-code-review` | Pre-commit review before finishing |
| `subagent-driven-development` | Execute parallel tasks via delegate_task (Phase 4B), persona-free routing |

---

## Appendix A: Planning Modes

The workflow uses two planning skills depending on depth needed.

### A.1 -- Lightweight Planning (`plan` skill)
Use when the user wants a plan but **not** execution.

- Restrict agent to read-only inspection
- Produce a concrete markdown plan saved under `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md`
- No code, no file edits, no commits
- Include: goal, context, approach, steps, files likely to change, risks/tradeoffs

**Do NOT use for:** implementation-ready plans with code, tests, or subagent handoff.
**Do use for:** early exploration, architecture discussions, user review before committing to build.

### A.2 -- Implementation Planning (`writing-plans` skill)
Use after design approval to write a detailed, copy-pasteable implementation plan.

- Bite-sized tasks (one action per step: write test &#8594; run test &#8594; implement &#8594; verify &#8594; commit)
- Exact file paths, complete code blocks, exact commands, verification steps per task
- Required header: goal, architecture (2--3 sentences), tech stack
- Emphasize DRY, YAGNI, TDD, frequent commits
- Static-site extra rules: design contract first (DOM IDs, class names, tokens), integration checklist
- Save the plan to `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md` or `docs/plans/` before executing
- Handoff pattern: end plan with `"For Hermes: Use subagent-driven-development skill to implement this plan task-by-task."`

**When to use:** any software task touching 2+ files or having 2+ logical stages.

**Do NOT use for:** quick brainstorming or when the user explicitly wants "just a plan, no code."

---

## Appendix B: Spike / Feasibility Prototyping

Before committing to a full build, validate uncertainty with disposable spikes.

**Trigger:** "let me try this", "is this even possible?", "compare A vs B", "quick prototype"

**Core loop:** decompose &#8594; research &#8594; build &#8594; verdict &#8594; iterate

1. **Decompose** into 2--5 independent feasibility questions. Order by risk (hardest first).
2. **Align** with user: present spike table, ask whether to build all, drop, or reorder.
3. **Research** competing approaches (2--3 sentences per spike, approach comparison table, pick one).
4. **Build** one directory per spike (`spikes/NNN-name/`). Standalone, no shared state.
5. **Verdict** per spike: VALIDATED / PARTIAL / INVALIDATED. Include: what worked, what didn't, next step recommendation.

**Comparison spikes:** same question, different approaches &#8594; shared number with letter suffix (`002a`, `002b`). Dispatch in parallel when independent.

**Frontier mode:** When the user isn't sure what to spike next, generate a frontier table of open questions and recommend the highest-risk spike to run first.

**When NOT to spike:** answer is knowable from docs, work is production path, idea is already validated.

---

## Appendix C: Subagent-Driven Execution

Use when you have an implementation plan and want fresh-context agents per task with automated two-stage review.

**Core principle:** Fresh subagent per task + two-stage review (spec compliance first, then code quality) = high quality, fast iteration.

### C.1 -- Read and Parse Plan
Read the plan ONCE. Extract all tasks. Create a todo list. Do NOT make subagents re-read the plan file -- inline the full task text in each `delegate_task` context.

### C.2 -- Per-Task Workflow
For each task:

1. **Dispatch implementer subagent** with:
   - Complete task text from the plan (files to create/modify, code requirements)
   - Relevant project context (not a wall-of-text dump)
   - Reference to TDD skill if tests are required
   - `toolsets` appropriate to the task

2. **Stage-1 review (spec compliance)** -- check:
   - Did the agent implement ALL requirements?
   - Are the specified files created/modified?
   - Did it skip any steps?

3. **Stage-2 review (code quality)** -- check:
   - Does it compile / pass tests?
   - Are there security issues?
   - Is the code idiomatic and maintainable?
   - Are there unintended side effects?

4. **Integrate or reject:**
   - If both stages pass &#8594; integrate and commit
   - If Stage 1 fails &#8594; reject, provide specific feedback, re-dispatch
   - If Stage 2 only fails &#8594; allow the agent to auto-fix and resubmit

### C.3 -- Sizing and Limits
- **Hard timeout:** 25 minutes per subagent. Size tasks accordingly.
- **Context budget:** include only what's needed. Sequential batches of related files beat touching the whole codebase at once.
- **Ollama pool exhaustion:** with ollama-cloud provider, safe limit is **2 concurrent subagents max** for heavy tasks. Use sequential 2-agent waves for larger batches.
- **If agent times out with incomplete work:** run the remaining work in the main session (no timeout ceiling), or split into smaller independent sub-tasks.

### C.4 -- Static Site Batching Strategy
When building static HTML/CSS/JS sites with subagents:
- Phase 1 (solo): base template + design tokens + shared CSS
- Phase 2 (parallel): content agents + styling agents simultaneously, sharing the design contract
- Phase 3 (solo): integrate, verify, archive to `.zip`

---

## Appendix D: External Coding Agent Delegation

When you need heavy lifting (large refactoring, deep codebase audits, or fresh-context code review), delegate to external autonomous coding agent CLIs instead of Hermes `delegate_task`.

| Agent | Install | Best For |
|-------|---------|----------|
| **Claude Code** | `npm install -g @anthropic-ai/claude-code` | Long-running interactive sessions, complex refactoring |
| **OpenAI Codex** | `npm install -g @openai/codex` | One-shot commands, OpenAI ecosystem |
| **OpenCode** | `npm i -g opencode-ai@latest` | Provider-agnostic, open-source, background batch jobs |

### Decision Tree — What to Use When

```
IF task involves web search OR browser navigation:
    -> ALWAYS do it yourself. Never delegate.

ELIF task is small (1-3 files, <10 min):
    -> Do it directly (faster than context setup)

ELIF task is medium (3-5 files, 10-20 min), well-defined, and self-contained:
    -> Use delegate_task (1 subagent, clean and fast)

ELIF task is large refactoring spanning >25 files OR needs >25 min:
    -> Use OpenCode in background (no hard timeout, survives session restarts)

ELIF 3+ independent subsystems broken (different test files, different root causes):
    -> Use 2 OpenCode agents in parallel (true parallelism without delegate queue)

ELIF code review of an entire branch before PR:
    -> Use OpenCode or Claude Code for fresh-context deep review

ELIF task is truly huge (audit codebase, migrate architecture):
    -> Sequential batches: Phase 1 solo plan -> Phase 2 parallel OC agents -> Phase 3 solo integrate
```

### Verified Limits (stress-tested)
- **2 OpenCode agents max** for true parallelism
- **2 `delegate_task` subagents max** when not using OpenCode
- **Mixed mode (2 OC + 2 del)**: delegates queue behind OpenCode (~99s delay)
- **Safe cap: 2 concurrent heavy agents** regardless of mix

### OpenCode `run` Mode Pitfall (Discovered 2026-05-31, Verified Twice)

**Symptom:** `opencode run --model <provider/model> --dir <path> "<prompt>"` runs for 4+ minutes streaming `message.part.delta` events but **never writes files to disk**. Exit code 0 or 143 (SIGTERM). The agent "thinks" in chat output only, producing zero file changes.

**Root cause:** OpenCode `run` mode is optimized for one-shot Q&A / reasoning, not multi-file code generation. It treats the prompt as a chat message to respond to, not a directive to create files. No filesystem MCP tools are activated in `run` mode.

**Evidence:** Two independent attempts (qwen3 → ProviderModelNotFoundError; kimi-k2.6:cloud → 4+ min of deltas, `git status` showed only `.hermes/admin-tz.md` which was pre-created by Hermes, zero files from agent).

**Fix — use one of these alternatives for multi-file code generation:**

| Approach | Command | Reliability | When |
|----------|---------|-------------|------|
| **Claude Code** | `claude -p "<detailed prompt>"` | ✅ High | Best for file creation, works headless |
| **OpenCode interactive** | `opencode <dir>` (TUI) | ⚠️ Medium | Needs human to start and type prompt |
| **OpenCode serve** | `opencode serve` + HTTP attach | ⚠️ Medium | Programmatic but complex setup |
| **Hermes delegate_task** | `delegate_task(tasks=[...])` | ✅ High | Up to 2 parallel, but interrupted by Telegram |
| **Hermes direct** | Do it yourself | ✅ Highest | For 6-12 files, often faster than agent setup |

**Decision rule:** For admin panels, CRUD, or any 6+ file task, if you have full project context, **doing it yourself in Hermes is faster than debugging why the agent didn't create files**. Reserve agents for truly independent parallel workstreams where you can't context-switch efficiently.

**Verification after ANY agent dispatch:** Check `git status --short` within 60 seconds. If no new files → kill the process (`pkill -f "opencode run"`) and switch approach immediately. Do not wait for the full timeout.

### Key Rules
- Never exceed 2 concurrent heavy agents to avoid credential pool exhaustion
- OpenCode agents run in background processes and survive Hermes session restarts
- `delegate_task` has a 25-minute hard timeout; OpenCode does not
- Always use isolated worktrees for parallel agents to prevent file conflicts

### User Preference: Persona-Free Routing
This user explicitly removed ALL role-based personas. When delegating, use direct routing ("Dispatching coder subagent for X") — never character names or role-play. Speak in a friendly but laconic style.

**See `references/coding-agents/kung-fu-delegation.md` for full slot architecture, stress test data, and worktree isolation recipes.**

---

## Common Pitfalls

- **Skipping design for "simple" changes** -- unexamined assumptions cause waste
- **Creating worktree without checking existing isolation** → nested worktrees
- **Dispatching without shared contract** → CSS/JS/HTML agents produce mismatched output
- **Claiming completion without verification** -- breaks trust, ships bugs
- **Merging before verifying on merged result** -- introduces conflicts silently
- **Cleaning up worktree for PR option** -- user loses iteration workspace
- **Performative agreement on code review** -- skip to action or technical acknowledgment
- **Blind implementation of review feedback** -- verify against codebase first
- **Jumping to execution before loading skills** -- user explicitly expects skills to be applied first. For design-heavy work, this includes `ui-ux-pro-max`, `popular-web-designs`, `claude-design`, or domain-specific skills such as `react-vite-tailwind-landing-pages`.
- **Delegating web search / browsing to subagents** -- STRICT RULE for this user
- **Relying on Obsidian skill registry as the single source of truth** -- Obsidian notes are documentation; the authoritative skill list is `skills_list()` plus `~/.hermes/skills/`. Obsidian registries may lag behind newly added skills.
- **Redundant `patch` calls** -- after a file was already put into the desired state by `write_file` or a previous `patch`, do not issue another `patch` with identical `old_string` and `new_string`. It will trigger a `File-mutation verifier: ... old_string and new_string are identical` warning. See `references/patch-old-string-new-string-identical.md`.
- **After any `patch` that changes Markdown structure, re-read the affected section** to confirm headings and paragraphs did not collapse or duplicate. Markdown patches can silently merge a new heading into the previous paragraph if the match boundary is off by one line.
- **Forcing a subagent strategy when the provider is exhausted** -- if `delegate_task` fails with a 429/usage-limit error, switch to manual execution waves in the main session. See `references/subagent-api-fallback.md`.
- **Trusting `read_file` immediately after heavy edits** -- the tool can return stale cached content after rapid `write_file`/`patch` bursts. Use `terminal` (`cat`/`grep`) or Python direct reads for ground truth. See `references/hermes-read-file-caching-pitfall.md`.

## References

- `references/coding-agents/` — External coding agent delegation: Claude Code, Codex, OpenCode, multi-agent orchestration patterns, stress-tested concurrency limits
- `references/dark-terminal-theme-tokens.md` -- Design tokens for dark terminal themes
- `references/file-protocol-static-site-search.md` -- Full reproduction recipe for static site search on file:// protocol
- `references/file-protocol-debug-log.md` -- Debug logging for file:// protocol issues
- `references/nextjs-sqlite-admin-panel.md` -- Next.js + better-sqlite3 admin panel recipe: middleware, API routes, upload, auth, Bootstrap UI
- `references/nextjs-sqlite-category-templates.md` -- Dynamic per-category product templates in admin panel: field definitions, auto-form generation, template assignment in categories UI
- `references/nextjs-sqlite-static-generation.md` -- SSG build performance and data sourcing patterns
- `references/patch-old-string-new-string-identical.md` -- Why `patch` may warn that old_string and new_string are identical and how to avoid it
- `references/project-context-retention.md` -- How to remember a project's exact name, path, and explored structure across Hermes sessions; avoid opening the wrong similarly-named directory
- `references/subagent-task-to-skill-mapping.md` -- Validated task-to-skill routing map for subagent dispatch decisions
- `references/vidvis-design-review-driven-refactor.md` -- **NEW** VIDVIS session: user corrected agent for not loading design skills first; corrected workflow for luxury/design-heavy tasks, preloader scoping, homepage section links, accessibility refactor
- `references/evaluating-integrating-external-methodologies.md` — How to evaluate third-party agent skills/methodologies (Ponytail, Superpowers, Graphify, CBM, etc.) and integrate them safely as additive lenses
- `references/karpathy-integration-example.md` — Worked example of option-B integration (Karpathy guidelines)
- `references/yandex-quick-links-seo-audit.md` -- SEO audit for Yandex quick links («быстрые ссылки»): navigation ↔ URL mapping, sitemap, JSON-LD, BreadcrumbList, timeline expectations
- `references/subagent-api-fallback.md` -- What to do when `delegate_task` fails due to provider request limits (e.g. ollama-cloud weekly cap)
- `references/hermes-read-file-caching-pitfall.md` -- Why `read_file` can return stale content after rapid edits and how to verify with `terminal` or Python
- `references/nextjs-google-fonts-build-flakiness.md` -- Handling `next/font/google` / `fonts.gstatic.com` build failures: wait/retry vs self-host vs temporary disable
- `scripts/verify-static-site.py` -- Python script to verify static sites
- `scripts/inline-assets.py` -- Script to inline assets into HTML
- `scripts/verify-static-site.sh` -- Shell script to verify static sites