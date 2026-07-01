---
date: 2026-06-23
skill: knowledge-first-protocol
topic: SOUL.md-knowledge-first-block
---

# SOUL.md Knowledge-First Protocol block

Use this reference when the user asks to embed a protocol or instruction into the Hermes system prompt.

## Target file

`~/.hermes/SOUL.md` — the primary persona/identity file loaded into the system prompt every turn.

## Where to place the block

Insert after the persona bullet list (after `Your responses are concise but complete...`). Add a markdown section header so it is distinct from the persona prose.

## Suggested block

```markdown
## Knowledge-First Protocol

Before answering or acting on any user request, follow this retrieval hierarchy:

1. Clarify — ask questions if the request is ambiguous.
2. session_search — check whether this was discussed before in Hermes conversation history.
3. Skills — for typical tasks (coding, deploy, debug, design, etc.):
   - Always call `skills_list()` first; the system prompt skill list is a hint, not an authoritative catalog.
   - Then load the matching skill with `skill_view(name)`.
   - For software work, also load `hermes-software-development-workflow`, `writing-plans` (2+ files/stages), `code-quality-gates`, and domain-specific skills.
4. Obsidian Vault — the primary knowledge base at ~/obsidian-memory/.
   - Check `AGENTS.md` (durable agent constitution) and `tasks.md` (active work) at the vault root first.
   - Use mcp_obsidian_search_vault and mcp_obsidian_read_note to find relevant MOCs, runbooks, and project notes.
   - Key MOCs: [[Knowledge/MOC — Index]], [[Projects/MOC — Projects]], [[Operations/MOC — Skills]], [[Operations/MOC — Operations]], [[Knowledge/Technical/MOC — Technical]].
   - If MCP tools time out or return ClosedResourceError, immediately fall back to reading vault files via read_file/search_files.
5. Project files — when the request is about a specific project, inspect real files with read_file and search_files.
6. Web search — only if internal sources are insufficient.

Do not skip Obsidian lookup because of MCP failure. Project and procedural details live in the vault, not in memory.
```

## Verification

After editing:
1. Save the file.
2. Immediately verify the edit with `read_file(path="~/.hermes/SOUL.md", limit=80)` or `sed -n '1,80p' ~/.hermes/SOUL.md`. Confirm the new block appears after the persona bullets, has no duplicate headers, and is not nested inside an HTML comment.
3. No restart is required — SOUL.md is re-read each message.
4. Confirm the next assistant turn begins following the protocol explicitly (search skills, search Obsidian before web).

Full verification recipe: `references/SOUL.md-edit-verification.md`

## Pitfalls

- Do not create a separate `persona.md` or other file. Hermes specifically loads `~/.hermes/SOUL.md` as the identity slot.
- Keep the block stable; frequent edits invalidate the upstream prefix cache.
- Use declarative instructions, not imperative self-directives (e.g. "Obsidian is the primary knowledge base" not "Always check Obsidian").
- Do not overload SOUL.md with detailed workflows. Keep it as philosophy + retrieval hierarchy; details belong in skills and Obsidian (`AGENTS.md`, `Operations/Runbooks/Hermes — Knowledge Retrieval Protocol.md`).
