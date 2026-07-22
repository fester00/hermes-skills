# Evaluating and Integrating External Agent Methodologies

Use this reference when a user asks you to study a third-party agent skill or
methodology (e.g. Ponytail, Superpowers, Graphify, codebase-memory-mcp, Context7,
mcp-sequential-thinking) and decide whether/how to integrate it into the Hermes
workflow.

## Core principle

Integrate the best practices, not the brand. Preserve Master Ugwai persona,
approval-controlled workflow, TDD, verification gates, and existing skill
boundaries.

---

## Evaluation checklist

Before recommending integration, answer these questions:

1. **What problem does it solve?**
   - Code analysis? (Graphify, CBM)
   - Code generation philosophy? (Ponytail, Caveman)
   - Planning methodology? (obra/superpowers)
   - Sequential thinking / memory? (mcp-sequential-thinking)

2. **Does it conflict with existing skills?**
   - Check `skills_list()` for overlapping Hermes skills.
   - Look for conflicts with TDD, verification, approval gates, persona.

3. **Is there a native Hermes equivalent?**
   - `todo`, `writing-plans`, `orchestrator-mode`, `subagent-driven-development`,
     `session_search`, `codebase-memory-audit`, `requesting-code-review`

4. **Can it be expressed as a lens/filter rather than a persona/plugin?**
   - If yes → integrate as additive skill sections.
   - If no → usually reject or limit to reference file.

5. **Does it require new dependencies/API keys?**
   - Prefer tools that work locally without keys.

6. **Does the user want the whole plugin or just the ideas?**
   - Default assumption: additive ideas, not plugin installation.

---

## Decision matrix

| Pattern | Action | Example |
|---|---|---|
| Structural code intelligence, local, no key | Integrate as skill + MCP server | codebase-memory-mcp replacing graphify |
| Planning methodology with compatible phases | Umbrella skill adaptation | superpowers-workflow |
| Code-generation philosophy / persona | Extract principles as lens, reject persona | Ponytail → lazy-review lens |
| Duplicates native Hermes tools | Reject integration, document why | mcp-sequential-thinking |
| Paid/cloud-only with no local alternative | Defer, propose local mirror | Context7 → Obsidian Docs Mirror (deferred) |
| Adds a new character/persona | Reject persona, extract rules if useful | Ponytail "lazy senior dev" |

---

## Integration workflow

1. **Clone and read** the project: README, skill files, architecture docs.
2. **Compare** with existing Hermes skills via `skill_view()`.
3. **Analyze conflicts** with subagent or self (logic/algorithm professor role).
4. **Propose options** to the user: integrate as lens / install plugin / reject / defer.
5. **Patch existing skills** rather than creating standalone copies.
6. **Add reference files** under the umbrella skill (`references/<topic>.md`).
7. **Sync to `maximus` profile** same session.
8. **Test** with controlled examples and guardrail checks.

---

## Sequential skill-analysis pattern

When the user chooses **option B** (integrate as additive lens into existing skills),
analyze each affected skill individually before patching anything. Do not batch the
analysis; do not ask permission to move from one skill to the next once the overall
variant is approved.

### Order

1. Load the umbrella skill first (`superpowers-workflow` or `hermes-software-development-workflow`).
2. Then load each affected child skill in dependency order:
   - planning skills (`writing-plans`)
   - execution skills (`subagent-driven-development`)
   - verification skills (`test-driven-development`, `requesting-code-review`, `systematic-debugging`)
   - quality-gate umbrella (`code-quality-gates`) only if children do not already cover the change
3. For each skill, check:
   - **Conflicts:** does the new methodology contradict an existing hard rule (TDD, verification, approval gates, persona)?
   - **Duplication:** does the new principle already exist under different wording?
   - **Gap:** does the new principle fill a real blind spot?
4. Synthesize the smallest change set: replace duplicated wording with the new principle,
   add missing subsections, but do not add new workflow phases.
5. Patch and sync.

### Autonomy expectation

Once the user has approved the integration variant (e.g. "Вариант Б"), proceed through
the skill-by-skill analysis and patching without asking "shall I continue?" or "should I
start skill N?". Report progress concisely; surface blockers immediately; otherwise keep
moving.

---

## Anti-patterns

- Installing a plugin that introduces a second persona.
- Replacing TDD with "one assert" or skipping verification.
- Creating standalone duplicate skills (e.g. `ponytail-review` next to `requesting-code-review`).
- Weakening approval gates because the methodology encourages "challenge requirements".
- Capturing a transient tool error as a permanent refusal.

---

## Related skills

- `superpowers-workflow` — umbrella for methodology adaptation
- `writing-plans` — plan authorship with lazy lens
- `requesting-code-review` — review with lazy-review checklist
- `codebase-memory-audit` — structural code intelligence
- `knowledge-first-protocol` — how to research before acting
