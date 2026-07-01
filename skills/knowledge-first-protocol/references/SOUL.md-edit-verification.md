---
date: 2026-06-23
skill: knowledge-first-protocol
topic: SOUL.md-edit-verification
---

# Verifying a SOUL.md edit

When adding a new section (e.g. a protocol) to `~/.hermes/SOUL.md`, confirm the result with a quick read-back so the edit is not silently wrong.

## Steps

1. Edit `~/.hermes/SOUL.md` via `patch` or `write_file`.
2. Immediately run:
   ```bash
   sed -n '1,60p' ~/.hermes/SOUL.md
   ```
   or use `read_file(path="~/.hermes/SOUL.md", limit=60)`.
3. Verify:
   - The new section appears after the persona bullets.
   - No duplicate headers.
   - No stray comment markers breaking the markdown.
4. No restart is required — SOUL.md is re-read each message.

## Pitfall

Do not assume the patch landed correctly just because `patch` reported success. Hermes .md files have no linter, so a syntax check won't catch semantic placement errors. Always visually confirm the top of the file.
