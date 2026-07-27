# Skill Curation: Deleting Overly Project-Specific Skills

## Context

2026-07-27: user deleted the `luxury-immersive-web` skill because it had grown
into a VIDVIS/silicone-landing project notebook rather than a class-level
umbrella. Several other skills still referenced it, causing stale pointers.

## Decision rule

| Keep | Delete / Merge |
|---|---|
| Class-level pattern that applies to ≥2 projects | Skill that only makes sense for one past project |
| Technique reusable across stacks (e.g. modal scroll-lock, SEO template) | Collection of project-specific tokens, file paths, and session refs |
| Name describes a capability, not a project | Name is a project codename or derived from one client's build |

## When a skill is deleted

1. Remove the skill via `skill_manage(action='delete', name='...')`.
2. Search the whole skill library for references: `rg -l "skill-name" ~/.hermes/skills`.
3. Patch every remaining skill that mentions the deleted one, replacing the
   pointer with the appropriate class-level umbrella(s).
4. Update Obsidian MOCs, registries, and project notes to remove broken links.
5. Move any genuinely reusable snippets into the surviving umbrella skill's
   `references/` or `templates/` directories, stripping project-specific names.

## What survives from `luxury-immersive-web`

The following patterns were generic enough to keep, now referenced within
`react-vite-tailwind-landing-pages` and `frontend-efficiency-audit`:

- Multi-layer parallax with GSAP ScrollTrigger
- CSS 3D perspective scene without Three.js
- 3D tilt cards with shine gradient
- Preloader with AnimatePresence
- Lenis + GSAP integration
- Magnetic cursor
- Grain overlay
- Split-text entrance

What was removed:

- `--vidvis-*` color tokens
- VIDVIS-specific session references and file paths
- Silicone-landing production examples
- HLS video background scaffolding (too narrow; can be recreated per project)

## Lesson

Build class-level umbrellas. Extract session-specific detail into `references/`
under those umbrellas. A skill whose name only makes sense for yesterday's
project is technical debt, not an asset.