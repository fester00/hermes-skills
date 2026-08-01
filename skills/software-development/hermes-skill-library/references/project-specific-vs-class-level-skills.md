# Project-Specific vs Class-Level Skills

Use this reference when deciding whether a skill should stay in the active
library, be archived, or be deleted entirely.

## Rule of thumb

| Keep | Archive | Delete |
|---|---|---|
| Class-level methodology that applies to many projects | Project-specific skill for a project that is no longer active | Project-specific skill whose project/context is gone |
| Hermes-native tooling and reusable workflow | Good skill but superseded by a better umbrella | Duplicate of another skill |
| Deep domain reference that speeds up future work | Historical migration/audit notes | One-session artifact |

## Class-level skill names

Good names describe a **class of work**:

- `frontend-efficiency-audit` — React performance auditing methodology
- `frontend-css-maintenance` — safe CSS refactoring methodology
- `pentajunior-v2-seo` — project-specific implementation of a generic class (kept because active)
- `code-quality-gates` — quality verification umbrella
- `superpowers-workflow` — software development workflow umbrella

## Session-artifact / project-gone skill names

Bad names describe a single incident or a project that is no longer relevant:

- `fix-silicone-modal-scroll` — one bug, one fix
- `debug-vite-ssr-2026-07-31` — date-bound
- `react-vite-tailwind-landing-pages` — narrow stack + project type, not a class
- `expo-tanstack-backend` — project/stack-specific, not current
- `legacy-php-modernization` — project gone
- `zf1-isp-billing` — project gone

## How to decide

Ask three questions:

1. **Will this skill be useful on a different project next year?** If no → archive/delete.
2. **Does it describe a method, or does it describe a project?** Project → archive/delete.
3. **Does a broader umbrella already cover this?** If yes → archive/delete and merge any unique parts.

## Real decisions from the library rebuild

| Skill | Decision | Reason |
|---|---|---|
| `react-vite-tailwind-landing-pages` | Delete | Narrow stack + page type, not a class; methodology moved to `frontend-efficiency-audit` and `frontend-css-maintenance` |
| `expo-tanstack-backend` | Delete | Project-specific, not current stack |
| `legacy-php-modernization` | Delete | Project gone |
| `zf1-isp-billing` | Delete | Project gone |
| `yandex-seo-optimization` | Keep | Generic methodology, actively used |
| `pentajunior-v2-seo` | Keep | Project-specific but project is active |
| `code-quality-gates` | Keep | Class-level quality umbrella |
| `superpowers-workflow` | Keep | Class-level software workflow umbrella |
| `simplify-code` | Keep | Class-level parallel cleanup/review |
| `ponytail` / `ponytail-review` | Keep | Class-level over-engineering lens |

## When a resource does not become a skill

External resources (e.g., `https://ui.shadcn.com/`) do not automatically become
skills. If the user says "do not create a skill, just remember the resource",
record the resource in Obsidian or in a reference file under an existing
umbrella, but do not add a new skill entry.

## Related

- `references/skill-consolidation-workflow.md` — how to merge overlapping skills.
- `references/skill-audit-pitfalls.md` — stale references and duplicate umbrellas.
