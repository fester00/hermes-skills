# OpenCode vs Hermes `delegate_task` — Decision Guide

Session-specific context: `silicone-landing-v2` polish, 2026-08-01.

## Rule of thumb

- **User says "OpenCode" / "opencode агенты" / "не субагенты"** → use OpenCode headless (`opencode run --auto --dir <project> < brief.md`). Do not continue dispatching `delegate_task`.
- **User says "делегируй" / "субагенты" / "проверяй результат"** → use Hermes `delegate_task` via `superpowers-subagent-driven-development`.
- **No explicit preference, multi-file UI/design work** → default to subagents for complex Hermes-native workflows; OpenCode for greenfield scaffolding.

## When OpenCode headless works

After the 2026-08 OpenCode upgrade (CLI + plugin 1.18.10) and MCP servers disabled:

- Smoke test passes: `opencode --version`, `opencode auth list`, `opencode run` with a simple command.
- Anti-todo prefix in every brief prevents the internal `todowrite` SchemaError:
  ```markdown
  Do not use todo or planning tools. Just execute the steps below.
  ```
- `--auto --dir <project-root>` grants write permissions inside the project directory.
- Tasks with 1–3 files and clear specs work reliably.

## When OpenCode headless struggles

- Complex briefs with 10+ files may be partially executed or skipped. In that case, either split the brief into smaller lanes or fall back to `delegate_task`.
- If the user explicitly rejects subagents, stay on OpenCode and split the work into smaller, verifiable briefs rather than silently falling back.

## Recommended OpenCode brief shape

```markdown
Do not use todo or planning tools. Just execute the steps below.

## Goal
One sentence.

## Files to modify
- `src/components/X.tsx`
- `src/sections/Y.tsx`

## Exact requirements
...

## Verification
After changes run:
```bash
npx tsc --noEmit
npm run build
```
Expected: exit 0.

## Report
Write a short report to `<project>/.superpowers/opencode-<lane>-report.md`.
```

## Lane split pattern

For a landing-page polish, split by visual subsystem:
- **Lane A:** cards + modal (shared component logic).
- **Lane B:** hero + sections + forms.
- **Lane C:** verification + screenshots (run by the controller, not OpenCode).

## Key pitfall

Do not mix execution models in the same plan mid-stream unless the user approves. If OpenCode starts failing, ask before switching back to subagents. If the user demands OpenCode, do not use subagents as a quiet fallback.
