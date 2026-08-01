# Skill Consolidation Workflow

Use when the user asks to audit, consolidate, or clean up the local Hermes skill
library so that overlapping skills do not fight each other and outdated skills
do not send agents to archived references.

## When to run

- User says "audit my skills", "remove duplicates", "what skills overlap?",
  "consolidate skills", or explicitly asks which skills to keep / archive /
  merge.
- Before adopting a large external skill collection (Superpowers, Stitch, etc.).
- After merging several external skills and needing to reconcile the result.

## Goal

Class-level umbrellas only. The library should not contain a long flat list of
narrow, one-session skills that duplicate each other or conflict with a primary
umbrella.

## Step-by-step

### 1. Inventory

```bash
find ~/.hermes/skills -mindepth 2 -maxdepth 3 -name "SKILL.md" | sed 's|/SKILL.md||' | sed 's|/home/natan/.hermes/skills/||' | sort
```

Also list archived skills:

```bash
find ~/.hermes/skills/.archive -name "SKILL.md" | sed 's|/SKILL.md||' | xargs -n1 basename | sort
```

### 2. Identify overlap

For each category, read `SKILL.md` frontmatter and the first body section of
every skill. Look for:

- Same trigger phrase ("use when building X", "audit this", etc.).
- Same core workflow with a different name.
- One skill that is a thin wrapper around another.
- External skills that duplicate a local umbrella.

Use `skills_list(category)` and `skill_view(name)` programmatically.

### 3. Compare by method and result

When two skills cover the same territory, choose the one to keep by evaluating:

1. **Hermes-specific tooling** — does it name actual Hermes tools (`delegate_task`,
   `read_file`, `terminal`, MCP servers) instead of abstract agent actions?
2. **Completeness of outcome** — does it produce a verifiable artifact (plan,
   build, diff, review report) or just advice?
3. **Hard gates** — does it enforce review, verification, or rollback, or does it
   trust the agent to "do the right thing"?
4. **Maintenance cost** — is it short enough to keep correct, or huge and stale?

Do not keep two skills that differ only in wording unless one is a dedicated
project-specific skill (e.g., `pentajunior-v2-seo` vs `yandex-seo-optimization`).

### 4. Consolidation options

| Situation | Action |
|---|---|
| One skill is strictly better | Keep it; archive the worse one |
| Both have unique, valuable parts | Merge them into the better one as a new section or reference |
| External skill has good ideas but wrong runtime | Adapt ideas into a local umbrella; archive the external one |
| Project-specific skill duplicates methodology | Keep it as project-specific, but point methodology to the umbrella |
| Skill is just a link dump or wrapper | Archive it |

### 5. Merge procedure

1. Read both `SKILL.md` files.
2. Decide which skill is the survivor (usually the umbrella or the more
   Hermes-specific one).
3. Move unique sections, pitfalls, references, and scripts from the victim to
   the survivor.
4. Update the survivor's `related_skills` to point to canonical names only.
5. Move the victim to `~/.hermes/skills/.archive/<category>/<skill>/`.
6. If the victim's name is referenced elsewhere, grep the library and update
   references.

### 6. Verify

After consolidation:

- `skills_list()` shows no duplicate names.
- `related_skills` of every active skill resolves to an active or archived skill.
- No active skill still references an archived skill by its old standalone name
  unless it explicitly says "archived reference".
- Run a test query: ask `skills_list(category)` for each affected category.

## Common stale-reference cleanup

After archiving, these names often still appear in active skills and must be
updated:

- `hermes-software-development-workflow` → `superpowers-workflow`
- `orchestrator-mode` → `superpowers-workflow`
- `subagent-driven-development` → `superpowers-subagent-driven-development`
- `writing-plans` → `superpowers-writing-plans`
- `test-driven-development` → `code-quality-gates` (or `superpowers-test-driven-development` as archived reference)
- `systematic-debugging` → `code-quality-gates` (or `superpowers-systematic-debugging` as archived reference)
- `requesting-code-review` → `code-quality-gates`
- `verification-before-completion` → `code-quality-gates`
- `plan` → `superpowers-writing-plans` or `superpowers-workflow` spike phase
- `spike` → `superpowers-workflow` Phase 0 / `superpowers-writing-plans`

Use `rg` or `grep` across `~/.hermes/skills` to find leftovers:

```bash
cd ~/.hermes/skills
grep -R -E "(hermes-software-development-workflow|orchestrator-mode|subagent-driven-development|writing-plans|test-driven-development|systematic-debugging|requesting-code-review|verification-before-completion|react-vite-tailwind-landing-pages|expo-tanstack-backend|legacy-php-modernization|zf1-isp-billing|plan|spike)" --include="SKILL.md" .
```

Note: `superpowers-*` upstream skills intentionally still use the canonical
short names in their body text; do not rewrite those. Only fix non-Superpowers
active skills and umbrella directives. Also remove references to deleted
project-specific skills such as `react-vite-tailwind-landing-pages`,
`expo-tanstack-backend`, `legacy-php-modernization`, and `zf1-isp-billing`.

## Pitfalls

- **Do not leave archived skills referenced as active dependencies.** An agent
  that loads `code-quality-gates` and sees `systematic-debugging` as a
  `related_skill` may try to invoke a missing skill.
- **Do not merge project-specific skills into generic umbrellas.**
  `pentajunior-v2-seo` should stay separate from `yandex-seo-optimization`.
- **Do not rename Superpowers upstream skills to long prefixed names in their
  body text.** The `name:` frontmatter stays canonical (e.g., `writing-plans`),
  but `related_skills` and directives in other skills should point to the
  prefixed umbrella where applicable.
- **Do not move skills into profile subdirs expecting Hermes to load them.**
  The runtime loader scans `~/.hermes/skills/`, not
  `~/.hermes/profiles/default/skills/`.

## Verification checklist

- [ ] Active skill count is known and no unintended skills disappeared.
- [ ] Archived skills are in `~/.hermes/skills/.archive/`.
- [ ] `skills_list(category)` works for affected categories.
- [ ] No broken `related_skills` in active skills.
- [ ] Superpowers upstream skills still load and their `name:` frontmatter is
      unchanged.
- [ ] The canonical umbrella for each class is clearly referenced.
