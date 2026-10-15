# Orchestration with OpenCode agents: plan → subagent → helpers

The shape the user asked for on their work setup: the agent writes a plan first, the user approves it, the
execution goes to a subagent, and that subagent may call at most two helpers. All of it is configuration — no
plugin, no external orchestrator. Verified on `opencode v2.0.28` with live runs (`debug agents` listing the
agents with their modes, and an implementer actually invoking a helper).

## The three levers

| Lever | What it gives | Where |
|---|---|---|
| `default_agent` | every new session starts in a chosen agent (e.g. a read-only planner) | `opencode.json` |
| agent `mode` | `primary` leads the conversation, `subagent` is callable via the `task` tool or `@`, `all` = both | agent frontmatter or the `agent` block |
| `permission.task` | **which** subagents an agent may call (glob patterns); `deny` removes the subagent from the task tool's description entirely, so the model never even tries | agent frontmatter or the `agent` block |

Also useful: `steps: N` bounds an agent's iterations (the old `maxSteps` name is dead), and a slash command
with `agent: <subagent>` + `subtask: true` forces the command to run in a subagent session even when the
named agent's `mode` is `primary` — that is the "hand this to the implementer" button.

## Files

```
opencode.json                        # default_agent, commands, top-level permissions
.opencode/agents/orchestrator.md     # mode: primary
.opencode/agents/implementer.md      # mode: subagent
.opencode/agents/helper-a.md         # mode: subagent, read-only research
.opencode/agents/helper-b.md         # mode: subagent, runs tests, no edits
.opencode/agents/reviewer.md         # mode: subagent, read-only review (optional)
```

Names come from the file names. Project agents override global ones with the same name.

## The permission matrix that produces "at most two helpers"

```jsonc
{
  "agent": {
    "orchestrator": { "mode": "primary",
      "permission": { "bash": "ask", "task": { "*": "deny", "implementer": "allow", "reviewer": "allow" } } },
    "implementer":  { "mode": "subagent",
      "permission": { "edit": "allow", "bash": "allow",
                      "task": { "*": "deny", "helper-a": "allow", "helper-b": "allow" } } },
    "helper-a":     { "mode": "subagent", "permission": { "edit": "deny", "bash": "deny",  "task": { "*": "deny" } } },
    "helper-b":     { "mode": "subagent", "permission": { "edit": "deny", "bash": "allow", "task": { "*": "deny" } } },
    "reviewer":     { "mode": "subagent", "permission": { "edit": "deny", "bash": "deny",  "task": { "*": "deny" } } }
  }
}
```

Rules that follow from the semantics, and are worth stating to the user:

- `"*": "deny"` on the helpers is what stops the chain from growing: nested subagent calls are allowed in
  OpenCode, so an unrestricted helper could spawn its own helpers and the depth would be unbounded.
- `permission.task` limits **which** subagents may be called, never **how many times**. "At most two helper
  calls total" is not expressible in config. Counters need plugin hooks — absent in 2.0.28 (see the SKILL.md
  section on plugin hooks) — so express the budget as two allowed helpers plus a `steps` ceiling, and state
  the intent in the implementer's prompt as a requirement rather than a guarantee.
- The user can always call any subagent by hand with `@` in the TUI; permissions do not restrict the human.

## Prompts that keep the roles apart

- **Orchestrator**: read the project, ask the user, write the plan to a file (`plans/<slug>.md`: goal, files,
  2–5 minute steps, verification commands), then **wait for an explicit approval**, then dispatch.
- **Implementer**: the plan file is the single source of requirements; implement, tests first if the plan
  says so, commit, write a report file, answer with a status
  (`DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`). It has no channel to ask questions — tell it
  to stop and report instead of guessing.
- **Helpers**: narrow and read-mostly. A researcher that never edits, a verifier that runs tests and shows raw
  output and never fixes. Their value is context isolation, so give each one job, not a toolset to explore with.
- **Reviewer**: reads the plan and the diff and returns two separate verdicts — spec compliance and code
  quality — with `file:line` evidence. Keep it read-only, and tell it the implementer's report is a claim.

## Delivery note

A Telegram-side bridge is not part of OpenCode: the docs ship no messenger integration (the ecosystem has a
Discord bot built on the SDK). Whatever bridge the user runs only opens/continues a session and relays text —
the orchestration above lives entirely inside the OpenCode config, so it survives a bridge change.
