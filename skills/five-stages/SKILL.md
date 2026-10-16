---
name: five-stages
description: Use when starting a multi-step task. Run five stages.
version: 1.0.0
author: Hermes Agent + Natan
license: MIT
metadata:
  hermes:
    tags: [workflow, delegation, subagents, planning, verification, orchestration]
    related_skills: [knowledge-base-audit, hermes-agent, code-quality-gates]
---

# Five stages

Borrowed from OpenCode's agent split. OpenCode ships a planning agent (**Plan**) whose edits and bash are pinned to `ask`, an execution agent (**Build**, the default with every tool), built-in subagents (General, Explore, Scout), and Tab to move between them. Here the planning mode is **a plan file plus the owner's explicit go**, the execution mode is the ordinary turn, and subagents are `delegate_task`. Same shape, no mode switch.

The owner asked for exactly this loop: collect information → write the plan → split into subtasks → execute → verify every item → only then mark it complete.

## When to use

Any task that touches more than one file, changes live state, or needs more than two or three tool calls — and anything the owner calls big or asks for from scratch.

**Skip the stages for:** a single-line fix, a typo, one read-only question. Skipping is a decision, not an omission: say it in one line («правка в одном файле — делаю сразу») so the owner can overrule you. Nothing else may be skipped silently.

## Stage 1 — Gather

Collect facts before forming an opinion: read the real files, the vault note, the running process, the docs of the version actually installed. Never answer from memory what a command can print. If the path is unclear, ask one question instead of guessing.

## Stage 2 — Plan

Write the plan to a **file** (vault `Operations/`, project root, or scratch), never only into chat. Each step carries the **verification command** that will settle it, and a line saying what the step is *not* supposed to change. State the ceilings you will respect (concurrency, destructive scope, files out of bounds).

Then **show it and wait for an explicit go** — «да», «ок», «go». A clear directive from the owner («удали отовсюду») already is the go; ambiguity is not. Silence is not.

## Stage 3 — Split

Break the plan into items and track them (todo toolset). Classify each item:

- **Independent** → subagents, in one batch (up to 4 concurrent; extra children do not queue, so plan batches).
- **Dependent or destructive** → do it yourself, sequentially.

Split parallel work **by file**, never by feature: two children editing one file overwrite each other.

**Zero is a valid number of children.** When every item touches the same file or the same artifact, nothing is independent and doing it alone is compliance, not neglect — one voice also matters for the artifact's soul (a page's prose, a design's tone). Say «делить нечего: один файл» out loud so the owner sees the call was made.

## Stage 4 — Execute and verify each item

One item at a time, and after every item **verify with your own hands**: run the command, read the file, check the count, look at the live state. A child's report is a claim, not a result. «Готово» is written only after the check — for each item separately, not for the batch.

## Stage 5 — Report and close

The report says what was verified and with what («проверено: 460 файлов, 0 битых»), not what was attempted. A failure gets its root cause, not a patch on top. If your own check put a wrong fact into a note, correct the note.

## Delegation mechanics

**Brief** (context field) must carry, every time: what to produce, the acceptance criterion, the verification command, what must **not** count as a result, and the hard boundaries (files not to touch). Children know nothing of this conversation.

**Monitoring** is live: `delegate_task` accepts `action` = `list` (who is running), `steer` (course-correct a running child), `stop` (end it early; partial output still returns). Results arrive **between turns** — never poll a transcript or an artifact file, never sleep on a child: finish what does not depend on it, post the status, end the turn.

**Self-report discipline.** Children inflate counts — a child counting broken links, notes without frontmatter, or violations applies no exclusion classes, so its total lands two to three times the truth. Demand a breakdown by class, then re-derive the number with your own script before it reaches the owner.

**Lifetime.** Background processes belong to the agent that started them: closing a child kills its remaining processes, including work from earlier turns. A child must await its own builds and tests before finishing; a server that has to outlive it starts in the parent session.

**Engine facts** (Hermes): an empty `delegation.model` makes children inherit the parent's model; `delegate_task` has **no** per-task model parameter (the pin is global — per-task models exist only on the kanban board); children inherit MCP toolsets when `delegation.inherit_mcp_toolsets: true`; default ceilings `max_concurrent_children: 4`, `max_spawn_depth: 1`. **Prove which model a child actually ran on from its session row, not from the batch report** — that report prints `Model: ?` and the delegation manifest records only `null` for an inherited pin, so the evidence lives in `state.db`: `sqlite3 $HERMES_HOME/state.db "SELECT model FROM sessions WHERE source='subagent' ORDER BY rowid DESC LIMIT 1"` (a row whose title carries the child's goal).

**Out of scope for delegation:** web search, page extraction and browser work are done by the parent — the owner's standing rule.

## Pitfalls

- **A bulk pass without a plan is how the library gets broken.** A whole-tree rewrite launched straight from an off-hand instruction flattened the frontmatter and headings of ten files: a `re.sub(r"\s{2,}", " ", text)` applied to a whole document eats the newlines themselves. Mass passes go through the plan, run on one file first, and end with a structure check across the whole tree.
- **A guard that skips what it cannot parse reports success on exactly the damaged files.** If the frontmatter check is written as «if the pattern matches, parse it», a flattened file drops into the skipped set and the count of valid files never moves. Compare files seen against files validated and fail on the difference.
- **A pass that reports success is not a verified pass.** Read one changed file in full afterwards, not only the diff of the lines you meant to touch.
- **Don't confuse motion with progress.** A finished batch is not a finished task: the stages end when the checks pass, not when the children return.
- **Don't delegate what you cannot verify.** If the acceptance criterion cannot be checked with a command, a diff or a read-back, it is not ready to hand out.
- **Check the script for whole-file whitespace ops before running it.** Knowing the rule does not help: today's damage came from `re.sub(r'\s{2,}', ' ', text)` inside a script whose author believed it was line-scoped — it collapsed the indentation of 19 source files. Grep the script for `\s`, `'  +'`, `sed 's/  */ /g'` first; whitespace may be tidied only inside the line being edited. Same class: **treating a binary file as text** — read the first bytes (`DIRC`, `PK`, `\x89PNG`) before any text pass; a git index rewritten as text is recoverable only by rebuilding it from its commit (`GIT_INDEX_FILE=... git read-tree <ref>`).
- **In SQLite `LIKE` ignores case while `replace()` does not.** A scrub written as `UPDATE ... WHERE col LIKE '%word%'` counts rows as cleaned and leaves every capitalised variant in place. Read the rows and rewrite them in Python with a case-insensitive regex instead; then rebuild the search tables (`DELETE FROM <fts>_content; DELETE FROM <fts>; INSERT INTO <fts>(<fts>) VALUES('rebuild')`) and `VACUUM` — without the vacuum the word survives in the file's old pages.
- **Hand over a privileged or service-stopping step as a script you have already run on a copy.** A script that stops a live service cannot be tested in place; the copy test is what caught the case-sensitivity bug and proved the vacuum step (5 s on a 1 GB base). Say what you verified and on what — «проверено на копии 1 ГБ» beats «скрипт готов».
- **Rewriting history changes every hash.** After a history rewrite, commit hashes cited in notes go dead — remap them from `.git/filter-repo/commit-map`, or cite commit messages instead of hashes. A content scrub does **not** rename paths: files whose *names* carry the word need a separate pass (`--path-glob '*word*' --invert-paths`).

## Boundaries

- Stage 2 exists for the owner's benefit: a plan he never sees is a diary.
- A plan the owner rewrites is a plan that worked.
- Trivial work stays trivial — the stages are a spine, not a ceremony. But every skipped stage gets named out loud.
- **Name each skipped stage in the first reply, not in the post-mortem.** One line — «стадии 2 и 3 пропускаю: один файл, делить нечего» — buys the owner the freedom to overrule you. If he has to ask «а что говорит инструкция?», the naming was missing and the process looks forgotten.
