# Karpathy Guidelines Integration Example

Session: 2026-07-14
Project: multica-ai/andrej-karpathy-skills
Decision: integrate as additive lens into existing skills, not as a standalone skill.

## Why this project was not adopted as a standalone skill

- Four principles overlap with existing Hermes skills (TDD, verification, lazy-review, planning).
- No new tool or workflow phase is required.
- The value is in sharper wording, not in new mechanics.

## What got patched

| Skill | Change |
|---|---|
| `superpowers-workflow/SKILL.md` | Added Karpathy lens to Phase 0; design phase now requires stating assumptions; verify phase requires success criteria before execution. |
| `hermes-software-development-workflow/SKILL.md` | Core principle updated; lazy-review mode reframed through Karpathy principles; verification gate includes transforming imperative tasks into verifiable goals. |
| `requesting-code-review/SKILL.md` | Self-review checklist checks all four Karpathy principles; review tags include `assume:` for hidden assumptions. |
| `writing-plans/SKILL.md` | Self-review checklist includes assumption scan. |

## What was deliberately left alone

- `systematic-debugging` — already systematic.
- `test-driven-development` — goal-driven execution already equals RED-GREEN-REFACTOR.
- `code-quality-gates` — coverage lives in child skills.

## Conflict-resolution rule used

If a new principle duplicates an existing rule, replace the old wording with the
new principle rather than keeping both. If it conflicts with TDD, verification,
approval gates, or Master Ugwai persona, reject it. If it fills a blind spot,
add the minimum subsection needed.
