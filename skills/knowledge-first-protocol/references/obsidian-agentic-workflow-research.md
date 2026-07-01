# Obsidian Agentic Workflow Research Notes

> Condensed findings from web research on Obsidian + AI agent workflows, system prompts, and skill grouping. Created 2026-06-29 during VIDVIS workflow analysis.

---

## Key Sources

1. [pbeens/obsidian-agents.md](https://github.com/pbeens/obsidian-agents.md) — `AGENTS.md` as durable agent constitution.
2. [coolgan/Obsidian-AI-Agent-workflow](https://github.com/coolgan/Obsidian-AI-Agent-workflow) — Obsidian as knowledge-base core, skills for repeated tasks.
3. [Jason-Cyr/ai-agent-workflow](https://github.com/Jason-Cyr/ai-agent-workflow) — Obsidian + Linear + Slack + OpenClaw persistent agent loop.
4. [vieiraae/obsidian-sidekick](https://github.com/vieiraae/obsidian-sidekick) — `agents/`, `skills/`, `tools/`, `prompts/`, `triggers/` scaffold.
5. [yanivy9h/ai-shipr](https://github.com/yanivy9h/ai-shipr) — folder-based persistent product memory.
6. [Trystan-SA/claude-design-system-prompt](https://github.com/Trystan-SA/claude-design-system-prompt) — system prompt + 14 invokable skills.
7. [Kimotep/skills](https://github.com/Kimotep/skills) — self-contained `SKILL.md` library.
8. [bolivian-peru/bolivian-peru-prompt-library](https://github.com/bolivian-peru/bolivian-peru-prompt-library) — Anthropic skill format with verification against real code.
9. [danielmiessler/fabric](https://github.com/danielmiessler/fabric) — prompts organized by real-world task.

---

## Core Principles

### Obsidian is the agent's brain

- Vault = canonical, durable, associative memory.
- Agent reads the vault **before** acting, not after being asked.
- Short-term agent memory stores **coordinates** (MOC paths, critical rules), vault stores **details**.

### AGENTS.md = durable constitution

- Put at vault root.
- Contains: scope, folder map, deliverables, working rules, safety rules.
- Not a session log; not `tasks.md`.
- Read by agent at the start of every session.

### Vault structure for agentic work

```
vault/
├── AGENTS.md          # durable rules
├── tasks.md           # active work, blockers, handoff
├── README.md          # entrypoint
├── _raw/              # staging inbox
├── people/            # canonical people pages
├── projects/          # canonical project pages
├── skills/            # vault-specific reusable workflows
├── scripts/           # deterministic utilities
└── MOCs/              # index notes
```

### Skills vs system prompt

- System prompt: persona, philosophy, constraints, tool availability.
- Skills: procedural knowledge invoked explicitly per task.
- Do not overload system prompt with detailed workflows.

### Skill grouping

- Group by domain: design, development, research, operations.
- Each skill = `SKILL.md` + optional `references/`, `templates/`, `scripts/`.
- Agent discovers via `skills_list()` then loads via `skill_view()`.
- Repeated workflows become skills; repeated mechanical transforms become scripts.

---

## Recommended Additions to Our Vault

| Item | Purpose | Priority |
|---|---|---|
| `AGENTS.md` | Durable agent constitution | High |
| `tasks.md` | Cross-session active work tracking | High |
| `People/` | Canonical people pages | Medium |
| `Scripts/` | Deterministic utilities | Medium |
| `Operations/Skills/` quick refs | Per-category skill lookup | Medium |

---

## Anti-patterns to Avoid

- Bulk-migrating or mass-renaming legacy notes without approval.
- Leaving raw imports as canonical records — promote from `_raw/`.
- Storing project/runbook details in agent memory instead of Obsidian.
- Relying on Obsidian skill registry as single source of truth — it can lag behind `~/.hermes/skills/`.
- Treating system prompt as a place for detailed procedures.

---

## How This Affects Our Workflow

For every software task:
1. `skills_list()` → discover most specific skill.
2. `skill_view(name)` → load it.
3. For 2+ file/stage tasks → load `writing-plans` and produce formal plan.
4. Check Obsidian `AGENTS.md` and `tasks.md` at session start.
5. Execute with verification gates.
6. Write learnings back to vault (skill or script) if workflow repeats.
