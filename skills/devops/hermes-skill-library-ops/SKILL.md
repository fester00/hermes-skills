---
name: hermes-skill-library-ops
description: Maintain, sync, document, and version-control the Hermes skill library across profiles and Obsidian.
version: 1.0.0
author: Master Ugwai
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, skills, library, ops, profiles, obsidian, git, sync]
    related_skills: [hermes-agent, hermes-software-development-workflow, knowledge-first-protocol]
---

# Hermes Skill Library Ops

Operate the Hermes skill library as a durable, reusable knowledge base shared
between the active Hermes profile, other profiles, and the Obsidian vault.

## When to use this skill

- User asks to add/update/delete a skill.
- User asks to copy skills to another Hermes profile (e.g. `maximus`).
- User asks to document skills in Obsidian.
- You finish a session with a non-trivial learning that belongs in a skill.
- You need to audit the skill library or keep it in sync with git.

## Where skills live

| Location | Purpose |
|---|---|
| `~/.hermes/skills/` | Active skills for the default profile |
| `~/.hermes/profiles/<name>/skills/` | Profile-specific skill overrides |
| `~/obsidian-memory/Operations/Skills/` | Human-readable skill documentation |
| `~/obsidian-memory/Operations/MOC — Skills.md` | Index of skills and runbooks |
| `~/.hermes/skills/.archive/` | Deprecated/archived skills |

## Principles

1. **Class-level umbrellas, not one-session skills.** A skill should cover a class of tasks (e.g. "design one-off HTML artifacts"), not a single PR or bug.
2. **Rich SKILL.md + references/.** Every umbrella skill should have:
   - `SKILL.md` with frontmatter, triggers, workflow, pitfalls, verification
   - `references/` for session-specific detail, API excerpts, analysis notes
   - `templates/` or `scripts/` when reusable files or probes are needed
3. **Sync skills to Obsidian.** New or updated skills should be mirrored in the vault so the knowledge base stays the source of truth.
4. **Sync across profiles when asked.** Use `rsync --delete` with backups.
5. **Git push the vault.** After vault changes, commit and push to `origin/main`.

## Workflow: update a skill from a session learning

1. Identify the signal:
   - user correction (style, tone, workflow)
   - new technique/fix/workaround
   - outdated/missing step in a loaded skill
2. Prefer updating a **currently loaded skill**.
3. If no loaded skill fits, find an **existing umbrella** via `skills_list()` + `skill_view()`.
4. If the learning is session-specific detail, add a **support file** under `references/`.
5. If no umbrella exists, create a new **class-level skill**.
6. Update `~/obsidian-memory/Operations/Skills/` and `MOC — Skills.md`.
7. Commit and push the vault.
8. If the user maintains multiple Hermes profiles, copy the updated skill to
   those profiles too.

## Workflow: copy skills to another profile

```bash
cd ~/.hermes/profiles/<target>/skills

# Backup existing copies
cp -r <skill> <skill>.bak

# Sync from default profile (or another source)
rsync -av --delete ~/.hermes/skills/<category>/<skill>/ <skill>/

# Verify
ls -la <skill>/
```

For multiple skills, repeat per skill or script it. Always verify hashes match
between source and destination. See `references/profile-sync-commands.md` for
copy-paste ready commands.

After copying to another profile, the new skill is available there immediately.
If the skill itself documents an Obsidian mirror, the target profile will use
the same documentation reference.

## Workflow: document a skill in Obsidian

Create/update `~/obsidian-memory/Operations/Skills/<skill-name>.md`:

- frontmatter: title, date, tags, category, lang
- summary of what the skill does
- key workflow / commands
- integration with related skills
- link to `[[MOC — Skills]]`

Then update `~/obsidian-memory/Operations/MOC — Skills.md`:

- add or refresh the skill row in the right section
- add cross-links to related runbooks

## Workflow: commit and push the vault

```bash
cd ~/obsidian-memory
git add -A
git status --short
git commit -m "docs(skills): <concise description>"
git push origin main
```

Use a conventional commit prefix:

- `docs(skills):` — documentation or skill registry updates
- `feat(skill):` — new skill card or reference
- `fix(skill):` — correction to an existing skill note

## MCP Obsidian fallback

If `mcp_obsidian_*` calls timeout or return `ClosedResourceError`, use terminal
fallback:

```bash
# Read
read_file ~/obsidian-memory/Operations/Skills/<skill>.md

# Write
write_file path=~/obsidian-memory/Operations/Skills/<skill>.md content="..."
```

Never skip the vault lookup because MCP failed.

## Protected skills

Do not edit bundled Hermes skills (e.g. `hermes-agent`) or hub-installed skills.
Patch only agent-created skills living in `~/.hermes/skills/`.

## Anti-patterns

- Creating a skill for a single PR/issue/feature codename.
- Mirroring upstream docs verbatim in `references/` — keep it concise and task-focused.
- Forgetting to update Obsidian after updating a skill.
- Pushing skills to another profile without backups.
- Saving transient environment errors as skill rules.

## Verification

- Skill file parses as valid YAML frontmatter + Markdown.
- Obsidian mirror file exists and cross-links to MOC.
- `git status` in vault is clean after push.

## Related

- `hermes-agent` — Hermes CLI operations
- `knowledge-first-protocol` — search order and Obsidian fallback
- `hermes-software-development-workflow` — build/verify conventions
- [[AGENTS.md]] — agent constitution in Obsidian
- [[Operations/MOC — Skills]] — Obsidian skill index
- [[Operations/Runbooks/Master Ugwai — Operating Instructions]] — agent working rules
