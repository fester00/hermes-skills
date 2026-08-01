---
name: hermes-agent-skill-authoring
description: "Author in-repo SKILL.md: frontmatter, validator, structure."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, authoring, hermes-agent, conventions, skill-md]
    related_skills: [superpowers-writing-plans, code-quality-gates, superpowers-workflow]
---

# Authoring Hermes-Agent Skills (in-repo)

## Overview

There are two places a SKILL.md can live:

1. **User-local:** `~/.hermes/skills/<maybe-category>/<name>/SKILL.md` — personal, not shared. Created via `skill_manage(action='create')`.
2. **In-repo (this skill is about this case):** `/home/bb/hermes-agent/skills/<category>/<name>/SKILL.md` — committed, shipped with the package. Use `write_file` + `git add`. `skill_manage(action='create')` does NOT target this tree.

## When to Use

- User asks you to add a skill "in this branch / repo / commit"
- You're committing a reusable workflow that should ship with hermes-agent
- You're editing an existing skill under `/home/bb/hermes-agent/skills/` (use `patch` for small edits, `write_file` for rewrites; `skill_manage` still works for patch on in-repo skills, but not for `create`)

## Required Frontmatter

Source of truth: `tools/skill_manager_tool.py::_validate_frontmatter`. Hard requirements:

- Starts with `---` as the first bytes (no leading blank line).
- Closes with `\n---\n` before the body.
- Parses as a YAML mapping.
- `name` field present.
- `description` field present, ≤ **1024 chars** (`MAX_DESCRIPTION_LENGTH`).
- Non-empty body after the closing `---`.

Peer-matched shape used by every skill under `skills/software-development/`:

```yaml
---
name: my-skill-name               # lowercase, hyphens, ≤64 chars (MAX_NAME_LENGTH)
description: Use when <trigger>. <one-line behavior>.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [short, descriptive, tags]
    related_skills: [other-skill, another-skill]
---
```

`version` / `author` / `license` / `metadata` are NOT enforced by the validator, but every peer has them — omit and your skill sticks out.

## Size Limits

- Description: ≤ 1024 chars (enforced).
- Full SKILL.md: ≤ 100,000 chars (enforced as `MAX_SKILL_CONTENT_CHARS`, ~36k tokens).
- Peer skills in `software-development/` sit at **8-14k chars**. Aim for that range. If you're pushing past 20k, split into `references/*.md` and reference them from SKILL.md.

## Peer-Matched Structure

Every in-repo skill follows roughly:

```
# <Title>

## Overview
One or two paragraphs: what and why.

## When to Use
- Bulleted triggers
- "Don't use for:" counter-triggers

## <Topic sections specific to the skill>
- Quick-reference tables are common
- Code blocks with exact commands
- Hermes-specific recipes (tests via scripts/run_tests.sh, ui-tui paths, etc.)

## Common Pitfalls
Numbered list of mistakes and their fixes.

## Verification Checklist
- [ ] Checkbox list of post-action verifications

## One-Shot Recipes (optional)
Named scenarios → concrete command sequences.
```

Not every section is mandatory, but `Overview` + `When to Use` + actionable body + pitfalls are the minimum for the skill to feel like a peer.

## Directory Placement

```
skills/<category>/<skill-name>/SKILL.md
```

Categories currently in repo (confirm with `ls skills/`): `autonomous-ai-agents`, `creative`, `data-science`, `devops`, `dogfood`, `email`, `gaming`, `github`, `leisure`, `mcp`, `media`, `mlops/*`, `note-taking`, `productivity`, `red-teaming`, `research`, `smart-home`, `social-media`, `software-development`.

Pick the closest existing category. Don't invent new top-level categories casually.

## Workflow

1. **Survey peers** in the target category:
   ```
   ls skills/<category>/
   ```
   Read 2-3 peer SKILL.md files to match tone and structure.
2. **Check validator constraints** in `tools/skill_manager_tool.py` if unsure.
3. **Draft** with `write_file` to `skills/<category>/<name>/SKILL.md`.
4. **Validate locally**:
   ```python
   import yaml, re, pathlib
   content = pathlib.Path("skills/<category>/<name>/SKILL.md").read_text()
   assert content.startswith("---")
   m = re.search(r'\n---\s*\n', content[3:])
   fm = yaml.safe_load(content[3:m.start()+3])
   assert "name" in fm and "description" in fm
   assert len(fm["description"]) <= 1024
   assert len(content) <= 100_000
   ```
5. **Git add + commit** on the active branch.
6. **Note:** the CURRENT session's skill loader is cached — `skill_view` / `skills_list` will not see the new skill until a new session. This is expected, not a bug.

## Cross-Referencing Other Skills

`metadata.hermes.related_skills` unions both trees (`skills/` in-repo and `~/.hermes/skills/`) at load time. You CAN reference a user-local skill from an in-repo skill, but it won't resolve for other users who clone the repo fresh. Prefer referencing only in-repo skills from in-repo skills. If a frequently-referenced skill lives only in `~/.hermes/skills/`, consider promoting it to the repo.

## Editing Existing In-Repo Skills

- **Small fix (typo, added pitfall, tightened trigger):** `skill_manage(action='patch', name=..., old_string=..., new_string=...)` works fine on in-repo skills.
- **Major rewrite:** `write_file` the whole SKILL.md. `skill_manage(action='edit')` also works but requires supplying the full new content.
- **Adding supporting files:** `write_file` to `skills/<category>/<name>/references/<file>.md`, `templates/<file>`, or `scripts/<file>`. `skill_manage(action='write_file')` also works and enforces the references/templates/scripts/assets subdir allowlist.
- **Always commit** the edit — in-repo skills are source, not runtime state.

---

## Adapting External Skills into the Library

When a user shares an external skill repo (obra/superpowers, Anthropic, Cursor rules, Google Stitch Skills, etc.), evaluate, adapt, and migrate useful workflows into Hermes. **Core principle:** Evaluate before adapting. Adapt before migrating. Verify after migrating. Don't create duplicates. Don't import lock-in.

### Workflow
1. **Duplicate check** — `hermes skills list | grep -iE "<keyword>"`
2. **Clone & inventory** — `git clone --depth 1 <repo>`; count SKILL.md files
3. **Assess each skill** — P0 (new + critical), P1 (new + useful), P2 (nice-to-have), skip (duplicate)
4. **Check for lock-in** — Does the skill require a proprietary MCP server, hosted service, paid API, or harness-only runtime? If yes, see "Extracting Portable Ideas" below instead of importing wholesale.
5. **Adaptation rules** — Remove harness-specific refs ("Claude Code", "Codex", "Cursor", "Stitch MCP"), universalize paths, preserve hard-gates, convert tables to bullet lists for Telegram safety
6. **Migrate** — Direct `write_file` for simple skills; `delegate_task` for batches (max 3 concurrent)
7. **Verify** — `hermes skills list | grep <name>`; `hermes skills view <name>`

### Pitfalls
- **Subagent timeout** — Pre-read source files yourself before delegating; pass content in `context`
- **Duplicate creation** — Always run Step 0 before any work
- **Harness commands left behind** — Strip `/plugin install`, harness-specific setup sections
- **Path dependence** — Replace `docs/superpowers/specs/` with project-agnostic paths
- **Importing lock-in** — Don't add skills that require a proprietary server/service unless the user already uses that infrastructure

**See `references/superpowers-mapping.md` for a full obra/superpowers → Hermes mapping and detailed adaptation recipes.**
**See `references/stitch-skills-evaluation.md` for a worked example of rejecting an external library due to MCP lock-in and extracting its portable ideas into existing skills.**

---

## Extracting Portable Ideas from External Skill Libraries

Sometimes the best thing to do with an external library is **not** to install it. Many upstream skill repos are tightly coupled to a proprietary runtime (MCP server, hosted agent, IDE plugin, or cloud service). Importing them as-is adds dependencies that break in our environment.

In those cases, extract the *ideas* and patch them into existing umbrellas.

### When to extract instead of migrate

- The external library requires a proprietary MCP server or hosted service you don't have.
- The library is mostly wrappers around a single external tool/API.
- Existing Hermes skills already cover the same territory; the external repo just phrases it better.
- The user asked "should we use this?" rather than "install this."

### Workflow

1. **Read the README and prerequisites.** Check for required servers, credentials, or harness runtimes. If any are present, flag lock-in.
2. **Inventory the external skills.** Map each skill to your existing library:
   - exact duplicate → note and skip
   - partial overlap → extract the missing technique and patch the existing skill
   - genuinely new class → consider creating a new umbrella (only if no lock-in)
3. **Identify portable techniques.** Look for:
   - prompt templates or enhancement pipelines
   - checklists or anti-pattern lists
   - terminology maps (vague → professional)
   - verification steps
   - workflow ordering patterns
4. **Patch existing umbrellas.** Add the technique as a subsection, pitfall, or workflow step. Don't create a new skill for a borrowed idea.
5. **Add support files if needed.** If the evaluation itself is reusable, save it as `references/<external-name>-evaluation.md` under the governing skill.
6. **Verify cross-skill consistency.**
   - No contradictory workflow steps between patched skills.
   - No duplicate vague-term maps that would fight each other.
   - Repo/brand context always wins over generic data-driven defaults.

### Conflict-check recipe

After patching multiple skills:

```bash
# 1. Re-read the patched skills
skill_view(name="claude-design")
skill_view(name="ui-ux-pro-max")
skill_view(name="popular-web-designs")

# 2. Search for the same vague-term maps across skills
rg -n "modern|premium|make it pop" ~/.hermes/skills/creative/*/SKILL.md

# 3. Verify workflow numbering and cross-references
python3 - <<'PY'
import yaml, re
from pathlib import Path
for p in Path.home().glob('.hermes/skills/creative/*/SKILL.md'):
    text = p.read_text()
    fm = yaml.safe_load(text.split('---', 2)[1])
    print(f'{fm["name"]}: {len(text)} chars')
PY
```

### Pitfalls
- **Creating a new skill for every borrowed idea.** This produces a long flat list of narrow skills. Prefer adding subsections to existing umbrellas.
- **Importing the external library anyway.** If the user says "this looks useful," default to extracting ideas, not installing dependencies.
- **Ignoring cross-skill conflicts.** Two skills can now both define "how to handle vague prompts." Make their roles explicit: one owns the process, the other owns the data hand-off.

---

## Common Pitfalls

1. **Using `skill_manage(action='create')` for an in-repo skill.** It writes to `~/.hermes/skills/`, not the repo tree. Use `write_file` for in-repo creation.

2. **Leading whitespace before `---`.** The validator checks `content.startswith("---")`; any leading blank line or BOM fails validation.

3. **Description too generic.** Peer descriptions start with "Use when ..." and describe the *trigger class*, not the one task. "Use when debugging X" > "Debug X".

4. **Forgetting the author/license/metadata block.** Not validator-enforced, but every peer has it; omitting makes the skill look half-finished.

5. **Writing a skill that duplicates a peer.** Before creating, `ls skills/<category>/` and open 2-3 peers. Prefer extending an existing skill to creating a narrow sibling.

6. **Expecting the current session to see the new skill.** It won't. The skill loader is initialized at session start. Verify in a fresh session or via `skill_view` using the exact path.

7. **Linking to skills that don't exist in-repo.** `related_skills: [some-user-local-skill]` works for you but breaks for other clones. Prefer only in-repo links.

## Verification Checklist

- [ ] File is at `skills/<category>/<name>/SKILL.md` (not in `~/.hermes/skills/`)
- [ ] Frontmatter starts at byte 0 with `---`, closes with `\n---\n`
- [ ] `name`, `description`, `version`, `author`, `license`, `metadata.hermes.{tags, related_skills}` all present
- [ ] Name ≤ 64 chars, lowercase + hyphens
- [ ] Description ≤ 1024 chars and starts with "Use when ..."
- [ ] Total file ≤ 100,000 chars (aim for 8-15k)
- [ ] Structure: `# Title` → `## Overview` → `## When to Use` → body → `## Common Pitfalls` → `## Verification Checklist`
- [ ] `related_skills` references resolve in-repo (or are explicitly OK to be user-local)
- [ ] `git add skills/<category>/<name>/ && git commit` completed on the intended branch
- [ ] When adapting external skills: duplicate check run, harness refs stripped, verified via `skills list`
