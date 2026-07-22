---
title: "Profile-Isolated Skill Handling"
date: 2026-07-11
tags: [hermes, skills, profiles, shifu, education, socratic-course-architect]
---

# Profile-Isolated Skill Handling

Some skills live in only one Hermes profile. The canonical example in this environment is
`socratic-course-architect` in `~/.hermes/profiles/shifu/skills/education/`, tied to the
Master Shifu persona and used for Russian-language interactive courses.

## How to handle requests that need an isolated skill

1. **Check the active profile.** If the current session is not in the profile that owns the skill,
   tell the user the skill is available in the other profile.
2. **Offer two options:**
   - Switch to the owning profile (e.g. `hermes --profile shifu`).
   - Copy the skill into the current profile via `rsync --delete`.
3. **Never silently emulate the skill** from a different profile — the persona, memory, and reference
   files may differ.

## Copy example

```bash
# From default profile into maximus
rsync -av --delete \
  ~/.hermes/profiles/shifu/skills/education/socratic-course-architect/ \
  ~/.hermes/profiles/maximus/skills/education/socratic-course-architect/
```

## Obsidian mirror

If the skill is copied to another profile, also consider mirroring a human-readable note in
`~/obsidian-memory/Operations/Skills/` and linking it from `Operations/MOC — Skills.md`.

## Related

- [[socratic-course-architect]] — if copied into the active profile
- [[hermes-skill-library-ops]] — general sync workflow
