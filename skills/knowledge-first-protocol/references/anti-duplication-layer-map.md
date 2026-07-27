# Anti-Duplication Layer Map

Where to put different kinds of agent rules so they don't duplicate each other.

## The four layers

| Layer | File | Lifetime | Scope | What belongs there |
|---|---|---|---|---|
| **System prompt / SOUL.md** | `~/.hermes/SOUL.md` | Per-session injection | Global behavior | Persona, tool availability, core philosophy, "load skills before acting" |
| **Hermes memory** | `~/.hermes/profiles/<profile>/memories/MEMORY.md` | Persistent, ~2,200 chars | This user/profile | Short triggers, MOC coordinates, critical facts. Pointers to Obsidian, not details. |
| **AGENTS.md** | `~/obsidian-memory/AGENTS.md` | Durable vault constitution | This vault | Scope, folder map, safety rules, working rules, task conventions. Read every session. |
| **tasks.md** | `~/obsidian-memory/tasks.md` | Active work tracker | This vault | Active work, blockers, next steps, handoff notes between sessions. |
| **Skills** | `~/.hermes/skills/<category>/<name>/SKILL.md` | Class-level procedure | Task domain | Step-by-step workflows, pitfalls, tool patterns, verification gates. |
| **Obsidian notes** | `~/obsidian-memory/**/*.md` | Detailed reference | Topic/project | Project facts, runbooks, research synthesis, indexes. |

## Common mistakes

| Mistake | Fix |
|---|---|
| Full workflow checklist in memory | Move to skill; memory stores only pointer |
| Runbook duplicated in memory | Keep runbook in Obsidian; memory references path |
| Skill list duplicated in system prompt | Keep system prompt as hint only; use `skills_list()` |
| `AGENTS.md` contains session log | Move session log to `tasks.md` |
| Memory and `AGENTS.md` say the same rule | Keep the durable version in `AGENTS.md`; memory gets a one-line pointer |

## Decision tree

```
Is it about who the agent is or what tools exist?  → SOUL.md / system prompt
Is it a short trigger for this specific user?        → Hermes memory
Is it durable and applies to every vault session?   → AGENTS.md
Is it active work that changes week to week?       → tasks.md
Is it a reusable procedure for a class of task?    → Skill
Is it detailed reference about a project/topic?     → Obsidian note
```

## Session example: "Use design skills first"

- Memory: "For visual work, load `ui-ux-pro-max`, `popular-web-designs`, or `claude-design` before coding."
- Skill `hermes-software-development-workflow`: full Phase 0 skill-discovery rules.
- `AGENTS.md`: working rule "Skills discovery is mandatory — `skills_list()` before `skill_view()`."
- Obsidian: `Operations/MOC — Skills.md` index of all design/dev skills.

No layer repeats the full checklist.
