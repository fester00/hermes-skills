# Skill Placement and Quality Umbrella Decisions

## Where Hermes discovers skills

Hermes resolves `HERMES_HOME` to `~/.hermes` by default. The skill scanner reads
from `get_hermes_home() / "skills"`, i.e. `~/.hermes/skills/<category>/<skill>/SKILL.md`.

**Do NOT place skills under `~/.hermes/profiles/default/skills/` and expect them
to be discovered.** That directory is not scanned unless it is added to
`skills.external_dirs` in `config.yaml` or symlinked into the global tree. If you
create or copy skills into a profile folder, move or symlink them under
`~/.hermes/skills/<category>/` before relying on them.

Discovered: 2026-07-31 while installing fresh Superpowers skills under the
default profile and finding `skills_list` did not return them.

## Quality umbrella: `code-quality-gates` over Superpowers quality skills

We evaluated the upstream Superpowers quality skills
(`superpowers-test-driven-development`, `superpowers-systematic-debugging`,
`superpowers-requesting-code-review`, `superpowers-receiving-code-review`,
`superpowers-verification-before-completion`) against our internal
`code-quality-gates`.

`code-quality-gates` is more useful in Hermes because it already includes:
- concrete `delegate_task` / `read_file` / `search_files` / `terminal` mappings,
- grep-based security scan patterns,
- baseline-aware test/lint verification,
- language auto-detection table,
- auto-fix loop ≤ 2 cycles,
- Hermes-specific debugging sections (TUI, React/TS animations).

Therefore these Superpowers quality skills were archived to
`~/.hermes/skills/.archive/software-development/` and `superpowers-workflow`
now routes Verify/Review phases through `code-quality-gates`. The archived
Superpowers skills remain available as deep-dive references when the compact
Hermes checklist is not enough.

## `simplify-code` source and scope

`simplify-code` performs parallel 3-agent cleanup (reuse, quality, efficiency).
It is inspired by Claude Code `/simplify`, not by the Ponytail project. It was
briefly archived during consolidation but restored because no other skill
provides parallel cleanup review.

## External reference sources

- Upstream Superpowers: https://github.com/obra/superpowers
- Karpathy guidelines: https://github.com/multica-ai/andrej-karpathy-skills
- Ponytail methodology: https://github.com/DietrichGebert/ponytail
