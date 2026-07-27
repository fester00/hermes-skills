---
name: hermes-skill-library
description: |
  Maintain, evaluate, sync, and publish the Hermes skill library. Covers
  deciding whether to adopt external skill collections, updating internal
  skills, copying skills across Hermes profiles, publishing skills to a
  standalone GitHub repository, and cross-linking skills with the Obsidian
  knowledge base.
version: 1.0.0
author: Master Ugwai
license: MIT
metadata:
  hermes:
    tags: [hermes, skills, library, maintenance, sync, github, obsidian, evaluation]
    related_skills: [hermes-agent-skill-authoring, hermes-agent, hermes-software-development-workflow, orchestrator-mode]
---

# Hermes Skill Library — Maintenance & Publication

Use this skill when the user asks about Hermes skills as a library: adding
new skills, evaluating external skill collections, keeping skills in sync
across profiles, or publishing skills to a GitHub repository so another agent
can consume them.

## When To Use

- User drops a link to an external skill repo and asks "should we use this?"
- User wants to copy updated skills to another Hermes profile.
- User wants to back up or publish `~/.hermes/skills/` to git.
- User wants to connect Hermes skills with the Obsidian knowledge base.
- A skill was patched this session and needs to be synced to other profiles
  or to a standalone repo.

## Related Skills

- `hermes-agent-skill-authoring` — how to write a single `SKILL.md` file
  correctly.
- `hermes-agent` — Hermes CLI, config, and built-in skill mechanics.
- `hermes-software-development-workflow` — build/verify/commit discipline.
- `orchestrator-mode` — when the task spans evaluation + multiple file edits
  + delegation.

## Workflow: Evaluate External Skill Library

1. **Read the source**
   - Load the linked repo's `README.md` and a few representative `SKILL.md`
     files.
   - Identify the target runtime: Hermes, Stitch MCP, Codex, Cursor,
     Claude Code, or another agent platform.

2. **Check prerequisites and lock-in**
   - Does it require an external MCP server? (e.g., Google Stitch)
   - Does it require a specific IDE/agent that the user does not use?
   - Does it duplicate skills already in the local library?

3. **Compare with local skills**
   - Use `skills_list()` and `skill_view(name)` to map overlapping territory.
   - Prefer keeping local skills if they already cover the functionality
     without external dependencies.

4. **Decide**

   | Situation | Action |
   |---|---|
   | Requires external MCP/service we do not have | **Ignore** |
   | Duplicate of existing local skills | **Ignore** unless it is materially better |
   | Good ideas but wrong runtime/format | **Adapt** the ideas into existing local skills |
   | Genuinely missing capability and compatible | **Adopt** selectively |

5. **If adapting**
   - Patch the relevant existing umbrella skill.
   - Do not add the external repo as a dependency.
   - Credit the source in the skill body or a reference note.

6. **If adopting**
   - Install only the specific skills needed, not the whole repo.
   - Verify they work in the current environment before relying on them.

## Workflow: Sync Skills Across Hermes Profiles

Hermes profiles live under `~/.hermes/profiles/<profile>/skills/`. Each profile
may have its own isolated skill library.

1. Identify the source-of-truth profile (usually `default`).
2. Preserve profile-only files. If the target profile already contains
   files that do NOT exist in the source skill (e.g. profile-specific
   `references/hermes-profile-isolation.md`), keep them after the sync.
3. For each updated skill, copy it to the target profile while keeping
   profile-only additions:

   ```bash
   # Backup target first
   cp -r ~/.hermes/profiles/<profile>/skills/<category>/<skill> \
         ~/.hermes/profiles/<profile>/skills/<category>/<skill>.bak

   # Copy source skill over target
   cp -r ~/.hermes/skills/<category>/<skill>/* \
         ~/.hermes/profiles/<profile>/skills/<category>/<skill>/

   # Restore profile-only files that the source does not have
   for f in $(find ~/.hermes/profiles/<profile>/skills/<category>/<skill>.bak -type f); do
     rel="${f#$HOME/.hermes/profiles/<profile>/skills/<category>/<skill>.bak/}"
     [ ! -e "$HOME/.hermes/profiles/<profile>/skills/<category>/<skill>/$rel" ] && \
       mkdir -p "$(dirname "$HOME/.hermes/profiles/<profile>/skills/<category>/<skill>/$rel")" && \
       cp "$f" "$HOME/.hermes/profiles/<profile>/skills/<category>/<skill>/$rel"
   done
   ```

   Alternatively, use `rsync --delete` and then manually restore any
   profile-only references.

4. Verify:
   - `SKILL.md` frontmatter parses.
   - Key sections and workflow numbering are intact.
   - Cross-references inside the skill still resolve.
   - Any profile-only files remain in place.

## Workflow: Publish Skill Library to GitHub

### Why

- Gives another agent a machine-readable copy of all skills.
- Decouples skill files from the Obsidian knowledge base.
- Enables version control and diff review for skill changes.

### Repository shape

```
hermes-skills/
├── README.md
└── skills/
    ├── <category>/
    │   └── <skill-name>/
    │       ├── SKILL.md
    │       ├── references/
    │       ├── scripts/
    │       ├── templates/
    │       └── examples/
```

### Steps

1. Create a public repo (e.g., `github.com/<user>/hermes-skills`).
2. Copy active skills from `~/.hermes/skills/`, excluding:
   - `.archive/`
   - `.curator_backups/`
   - `.hub/`
   - `.git/` inside any skill

3. Write `README.md` with:
   - purpose
   - structure
   - key skills table
   - install/use instructions
   - cross-link back to the Obsidian knowledge base
   - sync recipe

4. Commit and push to `main`.

### Sync recipe

```bash
cd ~/hermes-skills
rsync -av --delete \
  --exclude='.archive' \
  --exclude='.curator_backups' \
  --exclude='.hub' \
  ~/.hermes/skills/ skills/
git add -A
git commit -m "sync skills from ~/.hermes/skills"
git push origin main
```

## Workflow: Sync a Skill with Its Upstream Source Repo

When a skill is mirrored from an external repo (e.g., `ui-ux-pro-max` from
`nextlevelbuilder/ui-ux-pro-max-skill`, `popular-web-designs` from
`VoltAgent/awesome-design-md`) and the user asks to update it:

1. **Clone upstream with git** (avoids GitHub API rate limits):
   ```bash
   cd /tmp
   https_proxy=http://127.0.0.1:1081 git clone --depth 1 <repo-url>.git
   ```
2. **Compare version/counts** via `skill.json` or upstream `README.md`.
3. **Backup local skill:** `cp -r ~/.hermes/skills/<cat>/<skill> ~/.hermes/skills/<cat>/<skill>-backup-v<old>`.
4. **Sync data**
   - CSV-driven skills: replace `data/` (and `data/stacks/`) from upstream.
   - Template-driven skills: convert each upstream `DESIGN.md` to the local
     narrative template shape, delete obsolete templates, add new ones, and
     update the SKILL.md catalog.
5. **Update SKILL.md frontmatter** with new version, description, and counts.
6. **Clean stale references** across the library (deleted skills, dead tools like
   `generative-widgets`) using `rg`.
7. **Verify** with the skill's own scripts and with `rg` for dead references.
8. **Commit** Obsidian updates first, then the skill repo if tracked.

See `references/upstream-skill-sync-workflow.md` for the full recipe and
verification commands.

## Workflow: Cross-Link Skills with Obsidian

Obsidian should remain the human-readable knowledge base; the GitHub repo
should remain the machine-readable skill store.

1. In Obsidian, create or update:
   - `Operations/Skills/Hermes Skills Repository.md`
   - `Operations/MOC — Skills.md`
   - `Operations/Runbooks/Master Ugwai — Operating Instructions.md`

2. Add cross-links in both directions:
   - Obsidian notes point to `https://github.com/<user>/hermes-skills`
   - `hermes-skills/README.md` points to the Obsidian repo URL

3. Commit and push Obsidian changes.

## Workflow: Combined Obsidian + hermes-skills Maintenance Session

Use this workflow when the user asks to keep the Obsidian vault and the public
skill repository in sync, or when making a repository public.

1. **Inspect state** of both repos:
   - `git status --short`, `git log --oneline -5`, `git remote -v`
   - Check visibility with `gh repo view <repo> --json isPrivate,visibility`

2. **Sync skill files** to `~/hermes-skills` using the rsync recipe above and
   remove any runtime artefacts (e.g., `__pycache__`).

3. **Update `README.md`** in `~/hermes-skills` to match the actual tree:
   categories, active skill count, key skills, cross-links.

4. **Audit Obsidian skill indices** against the real `~/.hermes/skills/` tree:
   - `Operations/MOC — Skills.md`
   - `Operations/Skills/Hermes — Skills Registry.md`
   - `Operations/Skills/Hermes Skills Repository.md`
   - Fix stale links, missing categories, duplicate rows, and count mismatches.

5. **Commit and push** `hermes-skills`, then `obsidian-memory`.

6. **Change visibility** if requested:
   - `gh api repos/<owner>/<repo> -X PATCH -f visibility=public`
   - Verify with `gh repo view`.

See `references/obsidian-skills-repo-sync.md` for the full command-by-command
recipe and verification checklist.

## Pitfalls

- **Do not install skill collections that require external MCP servers**
  unless the user already has that MCP configured. They become dead weight.
- **Do not add narrow, one-session skills.** Class-level umbrella skills only.
- **Do not sync skills blindly across profiles.** Verify the target profile
  actually needs the update and that the skill still works there.
- **Do not commit sensitive files.** Exclude `.env`, secrets, private SSH
  keys, and local caches from the published repo.
- **Do not let the GitHub repo drift.** Run the sync recipe after any
  significant skill update session.

## Verification

Before declaring a sync or publish done:

- `find skills -name 'SKILL.md' | wc -l` matches the active skill count.
- `git status` in `~/hermes-skills` shows no unexpected untracked files.
- README cross-links open correctly in a browser.
- Obsidian notes render the new links.

## References

- `references/skill-sync-profile-only-files.md` — How to sync a skill into a
  Hermes profile without deleting profile-only files such as
  `references/hermes-profile-isolation.md`.
- `references/stitch-skills-evaluation.md` — worked example of evaluating an
  external skill library (Google Stitch) and adapting ideas instead of
  adopting dependencies.
- `references/superpowers-evaluation.md` — worked example of evaluating the
  `obra/superpowers` agentic methodology and converting it into a local
  umbrella skill (`superpowers-workflow`).
- `references/context7-evaluation.md` — evaluating a paid docs-as-a-service
  tool and choosing a local docs mirror instead.
- `references/graphify-evaluation.md` — evaluating a local code intelligence
  tool and wrapping it in a read-only audit skill.
- `references/obsidian-skills-repo-sync.md` — combined end-to-end sync of the
  Obsidian vault and the public `hermes-skills` GitHub repository with
  visibility changes and verification checklist.
- `references/converting-design-md-to-templates.md` — converting a batch of
  `DESIGN.md` teardowns (YAML+narrative or pure narrative) into the narrative
  Markdown templates used by the `popular-web-designs` skill, including font
  substitution mappings and verification steps.
- `references/upstream-skill-sync-workflow.md` — full recipe for syncing a
  user-local skill with its upstream source repository (version comparison,
  format drift, stale-reference cleanup, verification).
## License

MIT. Skills inside the library carry their own licenses in their frontmatter.
