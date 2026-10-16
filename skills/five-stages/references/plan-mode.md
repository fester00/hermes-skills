# Plan mode — the contract

The rules below are Hermes' own `/plan` built-in (`agent/plan_prompt.py`), which is the same shape as
OpenCode v2's **Plan** agent (`packages/core/src/plugin/plan.ts`). Upstream the mode is enforced by
permissions — `edit: deny` for every path except `~/.opencode/plan`; here it is enforced by these words and
by naming the stage out loud.

## Ground rules (verbatim)

> For this turn, you are in PLAN MODE — planning only.
>
> - Do not implement code.
> - Do not edit project files except the plan markdown file itself.
> - Do not run mutating terminal commands, commit, push, or perform external
>   actions.
> - You may inspect the repo or other context with read-only commands/tools
>   when needed.
> - Your deliverable is a markdown plan saved inside the active workspace under
>   `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md` (create the directory if
>   needed; Hermes file tools are backend-aware, so this relative path keeps
>   the plan with the workspace on local, docker, ssh, modal, and daytona
>   backends). If the runtime provides a specific target path, use that exact
>   path instead.

The upstream reminder adds the one rule Hermes' own text leaves implicit — and it matters most when the plan
turns out to be big:

> Do not modify any other files or ask a subagent to do so.

## Craft (verbatim)

> Write the plan for an implementer with zero context for the codebase and questionable taste. A good plan
> makes implementation obvious — if someone has to guess, the plan is incomplete.
>
> Structure (include the sections that are relevant):
> - Goal — one sentence.
> - Current context / assumptions.
> - Architecture / proposed approach — 2-3 sentences.
> - Step-by-step tasks. Each task is bite-sized (2-5 minutes of focused work), names exact file paths
>   (`src/models/user.py`, not "the model file"), includes complete copy-pasteable code where code is needed,
>   and exact commands with expected output for verification.
> - Tests / validation — for code tasks, follow the TDD cycle per task.
> - Risks, tradeoffs, and open questions.
>
> Principles: DRY, YAGNI, TDD, frequent commits. Avoid vague tasks ("add authentication"), incomplete code
> ("add validation here"), and unverifiable steps ("test it works" — instead: the exact command and its
> expected output).
>
> Interaction style:
> - If the request is clear enough, write the plan directly.
> - If it is genuinely underspecified, ask a brief clarifying question instead of guessing.
> - After saving the plan, reply briefly with what you planned and the saved path, and offer to execute it —
>   but do not start executing in this turn.

## Our two additions

1. **Where the plan lives.** Library work (skills, vault, Hermes config) also gets a copy in
   `~/obsidian-memory/Operations/`, because there the vault *is* the deliverable and the owner reads plans in
   Obsidian. Name the path in the reply either way; a plan the owner cannot find is a diary.
2. **The plan becomes the checklist.** After the go, its items are entered into the todo toolset and ticked
   off one by one — each tick *after* its verification command passes, never before. Upstream has no todo
   tool: there the plan file itself is the checklist. We keep both, the file as the record and the list as
   the tracker.

## Ending the stage

Only the owner ends it: «да», «ок», «go» — or a direct directive that already meant it. Silence does not.
While the stage is open, no edits outside the plan file, no writing children, no commits.
