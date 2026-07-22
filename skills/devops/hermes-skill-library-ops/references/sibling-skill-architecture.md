# Sibling skills vs widening an umbrella

When a user asks an umbrella skill to cover a new task class, compare the two architectures before editing.

| Criterion | One umbrella | Sibling skills |
|---|---|---|
| Output format | Same | Different |
| Target sites/tools | Same family | Different families |
| Failure domains | Same triggers | Different triggers |
| User mental model | "One button" | "Pick the right tool" |

If the goals, selectors/output schema, or site families differ, prefer sibling skills under a shared infrastructure note. Add `related_skills` cross-links in frontmatter so each skill points to the other. Then:

1. Create or update the sibling SKILL.md.
2. Add its Obsidian mirror note under `Operations/Skills/`.
3. Update `Operations/MOC — Skills.md` in the right category section.
4. Add a `## ⚠️ Legacy notice` to any outdated Obsidian notes that now conflict, pointing to the new skills.
5. Keep the shared stack (venv, Chrome profile, Xvfb, base script) documented in both skills with identical paths.

Example: `playwright-web-search` (research) and `playwright-marketplace-search` (shopping) share the same Playwright + Chrome profile + Xvfb stack, but one extracts search snippets and the other product cards.
