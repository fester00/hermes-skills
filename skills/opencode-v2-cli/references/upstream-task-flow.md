# The upstream task flow — as the OpenCode v2 repository defines it

The flow below is quoted from the repository itself (`github.com/anomalyco/opencode`, branch `v2`), not from
the documentation site. The site mirror under `/mnt/data/natan-storage/docs/opencode-v2/` can lag the code;
when the two disagree the repository wins, and `opencode debug agents` shows what the installed binary
really has.

Where the claims live:

- user documentation — `services/www/src/docs/content/*.mdx` (62 pages: `agents.mdx`, `permissions.mdx`,
  `tools.mdx`, `commands.mdx`, `instructions.mdx`, `skills.mdx`). Note that a top-level `docs/` directory does
  **not** exist in this repository.
- implementation — `packages/core/src/plugin/plan.ts` (the plan mode), shipped slash-command prompts in
  `packages/core/src/plugin/command/*.txt` (e.g. `review.txt`).

## The flow, stage by stage

1. **Plan** — built-in primary agent `plan`: "explores and plans without editing normal project files. It may
   write OpenCode plan files when asked". `permissions.mdx` states the mechanism plainly: *allows questions;
   denies edits except files under `~/.opencode/plan`*. The plugin implements it as `question: allow`,
   `edit: deny` with that one directory exempt, rewrites a blocked call into "Cannot use <tool> to modify
   files outside the Plan directory", and injects a reminder that is re-appended on every request so it
   survives compaction: discuss the plan in the conversation; do not create plan files unless asked; **do not
   modify any other files or ask a subagent to do so**; remain in Plan mode until the user switches agents —
   and if the user asks for implementation, refuse and tell them to switch.
   *The planning stage is a permission, not a promise; the plan is a file in a dedicated directory; only the
   owner's action ends the stage.*
2. **Checklist** — there is no todo/checklist tool in v2. The complete tool list is Read, Glob, Grep, Edit,
   Write, Patch, Shell, Webfetch, Websearch, Question, Skill, Subagent, Execute, Sessions, Worktrees. The
   markdown plan file in the plan directory **is** the checklist.
3. **Build** — the default primary agent, all tools allowed; only this stage may implement.
4. **Subagents** — the `subagent` tool opens a child session (fresh context, foreground or background) and
   returns its id so the same child conversation can be continued. The parent's `subagent` permissions decide
   which agents it may launch (deny `*`, allow one reviewer). Built-ins are **General** (research and
   multi-step work; cannot launch further subagents) and **Explore** (searches and reads, never edits).
   "A subagent uses its configured model, or inherits the parent session's model when none is configured."
5. **Review** — an agent of its own, read-only (`mode: subagent`, edit deny, shell deny), prompt: "Review the
   current changes. List findings in severity order with file and line references." The `/review` command
   prompt (`command/review.txt`) sets the boundaries, and they are the durable part:
   - be certain — call something a bug only when you are confident it is one;
   - review the changes only, never pre-existing code that was not modified;
   - unsure? investigate before flagging;
   - do not invent hypothetical problems — if an edge case matters, name the realistic scenario;
   - not a style zealot: verify the violation is real, and accept a "violation" that is the simplest option.
6. **Instructions and skills** — project rules live in `AGENTS.md` (with scope, discovery order and update
   semantics; deleting the file tells the session the old rules no longer apply). A skill is a `SKILL.md`
   under `.opencode/skills/<id>` whose description says *when* to use it; the text is loaded on demand by the
   `Skill` tool, scripts and references sit beside it.

## The Hermes side of the map (verified in this install)

| Upstream mechanic | Ours | Where it lives |
|---|---|---|
| Plan agent, `edit: deny` except `~/.opencode/plan` | `/plan [task]` — plan-mode prompt, plan file, no execution | `agent/plan_prompt.py`; `hermes_cli/commands.py:164`; plan path `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md` |
| Build agent (default, all tools) | the ordinary turn after the owner's go | — |
| `subagent` tool | `delegate_task` | batches ≤4, `max_spawn_depth: 1`, inherits the parent model when `delegation.model` is empty |
| Reviewer agent (read-only, `file:line`) | `/review [instructions]` — independent, full-privilege background subagent | `agent/review_engine.py`; `hermes_cli/commands.py:158` |
| `AGENTS.md` project instructions | `AGENTS.md` too — `/init` generates or updates it | `hermes_cli/init_command.py` |
| Skills, `SKILL.md` + description says *when* | identical | `.hermes/skills/<id>/SKILL.md` |
| Checklist inside the plan file | plan file **plus** a tracked todo list | todo toolset |
| Compaction re-injects the plan-mode reminder | session compression keeps the plan file on disk, which survives any compaction | — |

## Deltas from our own five stages

Adopted on 2026-10-16 — the port lives in the `five-stages` skill (`references/plan-mode.md`,
`references/review.md`): the plan stage now has the plan-file mechanic and its rules, the checklist is the plan
file plus a tracked todo list, and the review boundaries below are written down and handed to every reviewer.

Still unmatched:

1. the plan stage as an **enforced** restriction — upstream a permission, here a promise, so it is named out
   loud in the first line of the reply and no writing child is dispatched while it is open;
2. resumable children — an upstream child keeps its id and can be continued, a Hermes `delegate_task` child is
   one-shot (a live one can only be steered);
3. a per-child permission matrix — upstream the parent's `subagent` action decides which agents it may
   launch; here a read-only child is read-only because the brief says so and because the parent reads the diff
   afterwards.

Not missing: their "a subagent cannot spawn further subagents" is our `max_spawn_depth: 1`, and their
"a subagent inherits the parent's model when none is configured" is our empty `delegation.model` — both
verified in this install.

## Research recipe — read a large upstream repository without cloning it

```bash
curl -s "https://api.github.com/repos/<owner>/<repo>/git/trees/<branch>?recursive=1" -o tree.json
# filter the path list in Python — thousands of entries, never print it whole
curl -s "https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>" -o local-file
```

- Locate the documentation first by filtering the tree for `\.mdx?$`; do not assume `docs/` exists.
- For "how does this mode really behave", read the implementation (`plugin/plan.ts`) and the shipped prompt
  files (`plugin/command/*.txt`) — the prose page describes intent, the plugin describes enforcement.
- Grep the tree for the feature name (`todo`, `checklist`) before claiming it exists. Finding *no* hit is a
  result: it is how you learn the checklist is the plan file.
- Print a directory listing in slices (head -30) — dumping 60+ paths into context crowds out the pages that
  matter.
- **Before porting a mechanic, grep our own registry for a native that already exists.** The order is: search
  `hermes_cli/commands.py` for the surface (`grep -n '"plan"\|"review"'`), then read the prompt module behind it
  (`agent/plan_prompt.py`, `agent/review_engine.py`, `hermes_cli/init_command.py`), and only then write anything.
  In this install both the plan mode and the reviewer were already there — `/plan` and `/review` — so the port
  became a matter of wiring our order to them instead of inventing an equivalent. A feature that "we should have"
  is often a feature we have and do not call.
