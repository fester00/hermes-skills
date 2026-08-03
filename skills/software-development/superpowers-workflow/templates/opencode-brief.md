# OpenCode Brief Template

> Copy this template for every OpenCode execution brief. Save as a `.md` file and pipe it via `opencode run --auto --attach ... < brief.md`.

---

Do not use todo or planning tools.

## Task

<One-sentence summary of what the agent must do.>

## Project context

- Project directory: `/mnt/data/natan-storage/silicone-landing-v2`
- Stack: Vite + React + TypeScript + Tailwind CSS
- This is a dark B2B landing page for silicone materials.

## External context sources

Before editing, read this note via the obsidian MCP server and follow its principles:
- `~/obsidian-memory/Operations/Coding Principles.md`

Use the configured MCP servers for all research outside this project directory:
- **obsidian** — query the `obsidian-memory` vault for design references, project notes, templates, runbooks.
- **codebase-memory** — index and query relevant repositories for architecture, file structure, data paths, and reusable code.

Do NOT read, copy, or list files outside the current project directory via direct terminal commands. If MCP servers are unavailable, stop and report.

## Constraints

- Preserve the dark B2B theme.
- Do not switch to light/warm/cream style unless explicitly asked.
- Do not change data files (`src/data/site.ts`).
- Keep shared components consistent across card and modal.
- Use git: check `git status`, commit changes with a clear message when done.
- Clean up only orphans created by your changes.

## Files to modify

- `src/components/...`
- Optionally `src/sections/...`

## Verification

Run these commands inside the project directory and report exit codes:

```bash
npx tsc --noEmit
npm run lint
npm run build
```

For visual/UI changes, also capture screenshots via Playwright (desktop, mobile, modal) and describe the visible difference from the user's perspective.

## Report

Write a brief report to `task-report.md` with:
- Status: `DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`
- Files changed
- Design decisions made
- Verification results (exit codes + screenshot summary)
- Any concerns or blockers
