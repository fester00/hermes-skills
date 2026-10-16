---
name: five-stages
description: Use when starting a multi-step task. Run five stages.
version: 1.1.0
author: Hermes Agent + Natan
license: MIT
metadata:
  hermes:
    tags: [workflow, delegation, subagents, planning, verification, orchestration]
    related_skills: [knowledge-base-audit, hermes-agent, code-quality-gates, opencode-v2-cli]
---

# Five stages

The working order borrowed from OpenCode's agent split and ported onto Hermes' own mechanics. Upstream,
**Plan** is a primary agent that is read-only *by permission* (edits denied everywhere except its own plan
directory), **Build** is the default executor, subagents get fresh context and inherit the parent model, and
review is an agent of its own, read-only, citing `file:line`.

Hermes ships the same shape natively, so the port is a matter of using what is there:

- **`/plan [task]`** — the owner's command. It feeds the plan-mode prompt to the live agent, which inspects
the workspace read-only and saves a markdown plan to `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md`. No execution,
no project edits, no mutating commands. Rules and craft: `references/plan-mode.md`.
- **`/review [instructions]`** — spawns an independent, full-privilege background reviewer subagent over the
recent conversation; its verdict re-enters the session as an async completion. Brief and boundaries:
`references/review.md`.
- **`delegate_task`** — the subagent rail: fresh context, a batch ceiling, `max_spawn_depth: 1`, children
inherit the parent's model when `delegation.model` is empty.

Upstream quotes with their repository paths: `opencode-v2-cli` → `references/upstream-task-flow.md`.

The owner asked for exactly this loop: collect information → write the plan → split into subtasks → execute →
verify every item → only then mark it complete.

## When to use

Any task that touches more than one file, changes live state, or needs more than two or three tool calls —
and anything the owner calls big or asks for from scratch.

**Skip the stages for:** a single-line fix, a typo, one read-only question. Skipping is a decision, not an
omission: say it in one line («правка в одном файле — делаю сразу») so the owner can overrule you. Nothing
else may be skipped silently.

## Stage 1 — Gather

Collect facts before forming an opinion: read the real files, the vault note, the running process, the docs
of the version actually installed. Never answer from memory what a command can print. If the path is unclear,
ask one question instead of guessing. Gathering is **read-only** — upstream the planning agent cannot write
at all, and in a `/plan` turn the same holds here.

For an existing project, gathering has an order: check the codebase-memory index first (`list_projects`), and
ask the graph the structural questions — where a component is used, what a route renders, what a change would
touch. File searches come after, for content. A codebase already indexed in an earlier session costs nothing
to query; a project never indexed is worth indexing in the first minutes. Recursion in a 1.9 GB repository is
the expensive path, and it is the one that also floods the context.

## Stage 2 — Plan

The deliverable is a **file**, not a chat message. Mechanic: the owner's `/plan` (or the same rules when he
asks for a plan in words) — plan saved to `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md`, and for library work a
copy in the vault `Operations/`. Say the path in the reply.

Every step carries the **verification command with its expected output** that will settle it, plus a line
saying what the step is *not* supposed to change. Steps stay bite-sized (2–5 minutes), name exact file paths,
and carry copy-pasteable code where code is needed. State the ceilings you will respect (concurrency,
destructive scope, files out of bounds).

While planning: no implementation, no project edits except the plan file, no mutating commands, no commits,
no external actions — and **do not ask a subagent to modify files**. Then **show it and wait for an explicit
go** — «да», «ок», «go». A clear directive from the owner («удали отовсюду») already is the go; ambiguity is
not. Silence is not. After the go, the plan's items become the tracked checklist: enter them into the todo
toolset and tick them off one by one, each tick *after* its verification passes.

## Stage 3 — Split

Break the plan into items and track them (todo toolset). Classify each item:

- **Independent** → subagents, in one batch (this install runs 4 concurrent children — the built-in default is
  10; extra children do not queue, so plan batches).
- **Dependent or destructive** → do it yourself, sequentially.

Split parallel work **by file**, never by feature: two children editing one file overwrite each other.
Upstream a child's write access is a permission; here it is a sentence in the brief — a reviewer stays
read-only only because the brief says so and because the parent checks the diff afterwards.

**Shared layers are written and frozen by the parent.** When several children build on one foundation — a token
file, a base stylesheet, header/footer fragments, an exported data file — the parent makes that foundation first
and declares it read-only; each child adds only its own page, with page-scoped styles, so two of them cannot
disagree about a shared class. Handing one foundation to two children without freezing it is the same collision
as two children editing one file. Make the partition **physical before dispatching**: create the empty per-part
files (one stylesheet per page group, say) and wire their imports yourself, so each child owns a real file rather
than a verbal share of a busy one. And the **build belongs to the parent**: children iterate against a running
dev view, the parent rebuilds once per wave and restarts the server before measuring — several children
rebuilding one output directory while a dev view runs produces failures that belong to nobody.

**Zero is a valid number of children.** When every item touches the same file or the same artifact, nothing
is independent and doing it alone is compliance, not neglect — one voice also matters for the artifact's soul
(a page's prose, a design's tone). Say «делить нечего: один файл» out loud so the owner sees the call was made.

## Stage 4 — Execute and verify each item

One item at a time, and after every item **verify with your own hands**: run the command, read the file,
check the count, look at the live state. A child's report is a claim, not a result. «Готово» is written only
after the check — for each item separately, not for the batch — and only then does the item get ticked off.

## Stage 5 — Review and report

Run the review stage with `/review`, or hand a child the brief from `references/review.md`. That file is the
primary source for the review boundaries — do not restate them here or in a third place, or every future fix
gets to be made three times.

A review is evidence, not a verdict to paste: reproduce each finding, keep what survives, name what you could
not reproduce. The report says what was verified and with what («проверено: 460 файлов, 0 битых»), not what
was attempted. A failure gets its root cause, not a patch on top. If your own check put a wrong fact into a
note, correct the note.

## Delegation mechanics

**Brief** (context field) must carry, every time: what to produce, the acceptance criterion, the verification
command, what must **not** count as a result, the hard boundaries (files not to touch, and «read-only: report
instead of editing» when the child must not write), and the language of the answer. Children know nothing of
this conversation.

**Long briefs go into a file, not into the call.** Write the brief as markdown in the scratch directory and
pass its path in `context`. A multi-paragraph brief full of quotation marks and Cyrillic inside a JSON string
is one escaping slip away from `tasks must be a JSON array … could not be parsed as JSON`, and the file also
leaves the child a stable, re-readable statement of the boundaries instead of one it only saw in a prompt.

**Monitoring** is live: `delegate_task` accepts `action` = `list` (who is running), `steer` (course-correct a
running child), `stop` (end it early; partial output still returns). Results arrive **between turns** — never
poll a transcript or an artifact file, never sleep on a child: finish what does not depend on it, post the
status, end the turn.

**Self-report discipline.** Children inflate counts — a child counting broken links, notes without frontmatter,
or violations applies no exclusion classes, so its total lands two to three times the truth. Demand a
breakdown by class, then re-derive the number with your own script before it reaches the owner.

**Lifetime.** Background processes belong to the agent that started them: closing a child kills its remaining
processes, including work from earlier turns. A child must await its own builds and tests before finishing; a
server that has to outlive it starts in the parent session.

**Engine facts** (Hermes): an empty `delegation.model` makes children inherit the parent's model; `delegate_task`
has **no** per-task model parameter (the pin is global — per-task models exist only on the kanban board);
children inherit MCP toolsets when `delegation.inherit_mcp_toolsets: true`; ceilings — `max_spawn_depth: 1` is the
built-in value (`hermes_cli/config_defaults.py:1381`), while `max_concurrent_children` is **10 by default and 4
in this install** (the override sits in `config.yaml`) — quote both numbers or neither. Upstream a child keeps its session id and can be resumed;
a Hermes child is one-shot — only a live one can be steered. **Prove which model a child actually ran on from
its session row, not from the batch report** — that report prints `Model: ?` and the delegation manifest
records only `null` for an inherited pin, so the evidence lives in `state.db`:
`sqlite3 $HERMES_HOME/state.db "SELECT model FROM sessions WHERE source='subagent' ORDER BY rowid DESC LIMIT 1"`
(a row whose title carries the child's goal).

**Out of scope for delegation:** web search, page extraction and browser work are done by the parent — the
owner's standing rule.

## Pitfalls

- **A bulk pass without a plan is how the library gets broken.** A whole-tree rewrite launched straight from
  an off-hand instruction flattened the frontmatter and headings of ten files: a `re.sub(r"\s{2,}", " ", text)`
  applied to a whole document eats the newlines themselves. Mass passes go through the plan, run on one file
  first, and end with a structure check across the whole tree.
- **A guard that skips what it cannot parse reports success on exactly the damaged files.** If the frontmatter
  check is written as «if the pattern matches, parse it», a flattened file drops into the skipped set and the
  count of valid files never moves. Compare files seen against files validated and fail on the difference.
- **A negative finding is only as good as the method that could have shown the opposite.** Before reporting a
  defect — and before contradicting a child's claim — re-run the check in a way that *forces* the behaviour to
  happen: scroll the document, wait for completion, re-render the state you say is missing. Every instrument has
  a blind spot, and an instrument reports its blind spot as a defect in the work: a capture of a tall page draws
  unrendered images as empty frames, a counter skips what it cannot parse, a query ignores case. The specific
  traps and the tools that avoid them live with the page-measuring skills; the rule is that «X is broken»
  requires a method that could have shown X working. Re-measuring costs a minute — a false alarm sends a child
  back to redo work that was already correct and tells the owner about a defect that does not exist. When your
  check disagrees with the worker's own evidence, **print the concrete difference — the two values, the two
  blocks — before ordering any rework**: a bare «mismatch» is usually a comparator that was never written to
  agree, not work that is wrong. Three «divergences» in one afternoon were the checker's own fault — an
  unfollowed redirect, a set compared as an ordered list, and a normalisation regex that matched nothing because
  re-serialised JSON carries a space after the colon — and each was one print away from being obvious. A
  normaliser that matches nothing is indistinguishable from a clean file: before believing «расходится», print
  the two values and confirm the normalisation actually fired.
- **A pass that reports success is not a verified pass.** Read one changed file in full afterwards, not only
  the diff of the lines you meant to touch.
- **Pin the version you measured.** A child re-saves its artifact after your pass, and the numbers you reported
then describe a file that no longer exists. Record `md5sum` and `date -r` at measurement time, compare them with
the child's own reported hash when it gives one, and re-measure as soon as either moved — «перепроверил текущую
версию» is a claim you can make only with a fresh measurement.
- **An export you hand the children becomes a source of truth, so it must not be lossy.** A content dump with long
fields sliced to a column width (`text[:220]`) looks harmless and silently drops the tail of every long
description; children then either invent, or quietly refetch from the original source, and the divergence surfaces
only in the delivered pages. Normalise whitespace if you must, but keep whole fields, and compare lengths against
the origin before shipping the file.
- **Don't confuse motion with progress.** A finished batch is not a finished task: the stages end when the
  checks pass, not when the children return.
- **Don't delegate what you cannot verify.** If the acceptance criterion cannot be checked with a command, a
  diff or a read-back, it is not ready to hand out.
- **Check the script for whole-file whitespace ops before running it.** Knowing the rule does not help: today's
  damage came from `re.sub(r'\s{2,}', ' ', text)` inside a script whose author believed it was line-scoped — it
  collapsed the indentation of 19 source files. Grep the script for `\s`, `'  +'`, `sed 's/  */ /g'` first;
  whitespace may be tidied only inside the line being edited. Same class: **treating a binary file as text** —
  read the first bytes (`DIRC`, `PK`, `\x89PNG`) before any text pass; a git index rewritten as text is
  recoverable only by rebuilding it from its commit (`GIT_INDEX_FILE=... git read-tree <ref>`).
- **In SQLite `LIKE` ignores case while `replace()` does not.** A scrub written as
  `UPDATE ... WHERE col LIKE '%word%'` counts rows as cleaned and leaves every capitalised variant in place.
  Read the rows and rewrite them in Python with a case-insensitive regex instead; then rebuild the search
  tables (`DELETE FROM <fts>_content; DELETE FROM <fts>; INSERT INTO <fts>(<fts>) VALUES('rebuild')`) and
  `VACUUM` — without the vacuum the word survives in the file's old pages.
- **Hand over a privileged or service-stopping step as a script you have already run on a copy.** A script that
  stops a live service cannot be tested in place; the copy test is what caught the case-sensitivity bug and
  proved the vacuum step (5 s on a 1 GB base). Say what you verified and on what — «проверено на копии 1 ГБ»
  beats «скрипт готов».
- **A quote marked «verbatim» is a claim, and it is checked character by character.** Re-wrapped line breaks, a
  « — » where the source had « - », a dropped clause inside an otherwise exact quotation — each makes the word
  false. Either copy the block byte-for-byte and prove it with a script (compare normalised lines against the
  source file), or mark the elisions with `[…]`. A reviewer found three such silent edits in one afternoon's
  work; none of them changed the meaning, all of them made the reference untrustworthy.
- **Quote the built-in default and the local override as two numbers.** `max_concurrent_children` is **10** by
  default (`hermes_cli/config_defaults.py:1376`) and **4** in this install (`config.yaml`); «default ceilings:
  4» is a false statement that travels to every other machine. Same class: anything read from our own config is
  a local fact, not an upstream one — name which of the two you mean.
- **Rewriting history changes every hash.** After a history rewrite, commit hashes cited in notes go dead —
  remap them from `.git/filter-repo/commit-map`, or cite commit messages instead of hashes. A content scrub
  does **not** rename paths: files whose *names* carry the word need a separate pass
  (`--path-glob '*word*' --invert-paths`).

## Boundaries

- Stage 2 exists for the owner's benefit: a plan he never sees is a diary.
- A plan the owner rewrites is a plan that worked.
- Upstream the plan stage is a **permission**; here it is a promise — which is exactly why the stage is named
  out loud in the first line of the reply («стадия: план, правок не делаю»), and why no writing child is
  dispatched while it is open.
- Trivial work stays trivial — the stages are a spine, not a ceremony. But every skipped stage gets named out
  loud.
- **Name each skipped stage in the first reply, not in the post-mortem.** One line — «стадии 2 и 3 пропускаю:
  один файл, делить нечего» — buys the owner the freedom to overrule you. If he has to ask «а что говорит
  инструкция?», the naming was missing and the process looks forgotten.
