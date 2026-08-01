# Skill Library Audit Pitfalls

Real findings from auditing the local Hermes skill library for overlap, stale
references, and class-level structure.

## Stale `related_skills` are the first sign of drift

When `skills_list()` shows a skill that has been archived, any active skill that
still names it in `related_skills` is likely outdated. Patch the active skill
before adding new skills, or the library will keep pointing at ghosts.

Common stale references found and fixed:
- `hermes-software-development-workflow` → replace with `superpowers-workflow`
- `orchestrator-mode` → replace with `superpowers-workflow`
- `subagent-driven-development` (old global) → `superpowers-subagent-driven-development`
- `writing-plans` (old global) → `superpowers-writing-plans`
- `requesting-code-review` (archived, absorbed into `code-quality-gates`)
- `systematic-debugging` (old global) → `superpowers-systematic-debugging`

## Distinguish class-level umbrellas from session artifacts

Good skill names describe a class of work:
- `frontend-efficiency-audit` (class: React performance auditing)
- `code-quality-gates` (class: quality verification)
- `frontend-css-maintenance` (class: safe CSS refactoring)

Bad skill names describe a single incident or a project that is no longer relevant:
- `fix-silicone-modal-scroll` (too narrow)
- `debug-vite-ssr-2026-07-31` (date-specific)
- `pentajunior-seo-audit-round-3` (round-specific)
- `react-vite-tailwind-landing-pages` (narrow stack + page type, not a class)
- `expo-tanstack-backend` (project/stack-specific, not current)
- `legacy-php-modernization` (project gone)
- `zf1-isp-billing` (project gone)

Session artifacts and project-specific skills whose projects are gone belong
in Obsidian notes, the project's ledger, or the archive — not in the active
skill library. See `references/project-specific-vs-class-level-skills.md` for
keep/archive/delete decisions.

## Avoid duplicate quality/review umbrellas

The library should have ONE primary umbrella per responsibility:

| Responsibility | Primary umbrella | Deep-dive / optional |
|----------------|------------------|----------------------|
| Software workflow | `superpowers-workflow` | — |
| Quality gates | `code-quality-gates` | archived Superpowers references |
| Over-engineering lens | `ponytail` | `ponytail-review` |
| Parallel cleanup | `simplify-code` | — |
| Frontend performance | `frontend-efficiency-audit` | — |
| CSS maintenance | `frontend-css-maintenance` | — |

If two skills claim the same primary responsibility, merge them or archive
the weaker one.

## References to external harnesses are dead weight

Skills that say `<SUBAGENT-STOP>` or reference Codex / Pi / Antigravity tools
are usually imported wholesale from another harness and do not help Hermes.
Either adapt them to Hermes tools or archive them.

## Verify after a cleanup pass

1. `skills_list()` shows the expected active set.
2. `rg "hermes-software-development-workflow|orchestrator-mode|requesting-code-review" ~/.hermes/skills/software-development/*/SKILL.md` returns nothing unexpected.
3. Every active skill has a coherent `related_skills` list.
