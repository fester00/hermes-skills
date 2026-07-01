# VIDVIS Session — Skill-Discovery Correction

**Date:** 2026-06-29
**Project:** VIDVIS (`/home/natan/vidvis`)
**What happened:** Agent started implementing a Next.js landing-to-catalog extension without first calling `skills_list()`. The user later asked whether design/flow skills had been used and corrected the workflow.

**Lesson:** For software tasks, especially design-heavy Next.js work, the agent must call `skills_list()` **before** `skill_view()` and **before** proposing architecture. The system prompt skill list is not exhaustive, and Obsidian skill registries may lag behind `~/.hermes/skills/`.

**Correct workflow for VIDVIS-class tasks:**
1. `skills_list()` → discover `nextjs-luxury-landing-to-catalog`, `luxury-immersive-web`, `ui-ux-pro-max`, `hermes-software-development-workflow`, `writing-plans`, `code-quality-gates`
2. `skill_view()` on the most specific skills
3. Explore codebase
4. Propose architecture and get approval
5. Use `writing-plans` to produce a formal implementation plan
6. Execute with verification gates (`tsc`, `build`, browser on port 3001)
7. Commit/push

**User preferences confirmed:**
- Preloader animation only on `/`
- Homepage section/category cards link to real routes
- Verify in browser on `localhost:3001`
- Use design skills before visual work
