# Hermes Subagent Mechanics — What a Child Is, and How to Track It

Verified against the live `delegate_task` contract and observed runs (2026-10-13).

## What a Hermes child is

- A separate agent process with its **own conversation, terminal session and workspace**. It sees
  **nothing** of your conversation, memory, or the plan — only its `goal`, `context`, `images`, and the
  files it reads itself.
- Toolset: the parent's tools **minus** `delegate_task`, `clarify`, `memory`, `cronjob`. So: files, terminal,
  web, skills of the Hermes library, and the Hermes MCP servers — but no nested delegation and no questions.
- Model: set by the `delegation` block in `~/.hermes/config.yaml`, **not** inherited from the session when
  that block is present. Verified here: `model: kimi-k2.7-code:cloud`, `provider: ollama-launch`,
  `base_url: http://127.0.0.1:11434/v1`, `inherit_mcp_toolsets: true` — i.e. children run on a different
  model than the session and do receive the parent's MCP toolsets. Check the block before assuming either
  way: `grep -A6 '^delegation' ~/.hermes/config.yaml`.
- It **can** write files, run tests, commit, and call external tools. Give it a report-file path and it will
  maintain a durable record.
- Several children run in parallel: up to `delegation.max_concurrent_children` (4 here). Extra ones do not
  start — they do not queue.

## What you get back

- One final answer per child, delivered as a message **when it finishes** (background mode) or inside the
  `delegate_task` result (fan-out mode).
- With `output_schema` set, the answer must validate against it; the result carries `schema_valid`, and
  `schema_errors` when it fails. This is the mechanism that turns a child's prose into a status contract —
  use it for every implementer and reviewer dispatch.
- **A child's summary is a self-report, not a fact.** For anything with an external side effect (a file
  written, a commit made, a service restarted), verify by reading the artefact yourself.

## Liveness: is it working, stuck, or dead?

| Question | Tool | Notes |
|---|---|---|
| What are the running children? | `delegate_task(action='list')` | id, goal, status, transcript path |
| What is it doing right now? | `tail -f ~/.hermes/cache/delegation/live/<delegation_id>/task-N.log` | append-only human-readable trace of operations and tool results |
| I need to change its direction | `delegate_task(action='steer', subagent_id=…, message=…)` | the **only** mid-run channel; the text is queued into the child's next tool result |
| Stop it and keep what it produced | `delegate_task(action='stop', subagent_id=…)` | returns the child's partial result; the run is marked `interrupted` |
| Did anything actually land? | `git status`, `git log --oneline`, `git diff --stat` | the disk is the truth, not the report |

## Recovery recipe (child stalled, died, or was stopped)

1. `tail -n 120` the live transcript → find the **last completed operation**.
2. `git log --oneline BASE..HEAD` + `git status` → what actually landed.
3. Read the report file (`<workspace>/task-N-report.md`) → what the child believed, and where it stopped
   writing.
4. Write the ledger line for the failed attempt — never leave it implicit.
5. Dispatch a **fresh child** for the remainder only, with context phrased as: "Task N is partially done:
   A landed at commit `<sha>`, B did not; finish B only. Do not redo A."

There is **no resume**: state travels in files, not in the child. That is why the report file and the ledger
are not bureaucracy — they are the recovery mechanism.

## Limits worth remembering

- Children die with the session: `/stop`, `/new`, process exit kill the whole tree (each child returns an
  `interrupted` completion with partial output). Durable work belongs in
  `terminal(background=True, persist_on_release=True)` or a cron job.
- A child cannot ask a question and cannot be given new information except via `steer`. Anything it must
  know has to be in `context` up front — including "what to do instead of asking".
- No partial result until the child ends. A hung child is silent by design; the transcript is your only
  window.
- Long fan-outs are wasteful if children end up duplicating each other's reading. Prefer one child per
  disjoint deliverable, not one child per file.
