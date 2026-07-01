---
title: "Hermes Admin & Skill Maintenance — Runbook"
version: 1.0.0
author: Master Ugwai
updated: 2026-05-08
tags: [hermes, maintenance, skills, audit, subagent]
---

# Hermes Admin & Skill Maintenance

## max_concurrent_children vs Provider Limits

- `max_concurrent_children` in `~/.hermes/config.yaml` controls how many **subagent processes** Hermes spawns concurrently.
- Each subagent is an **independent AIAgent** with its own API calls — NOT a shared session.
- **Cloud models** (e.g. `kimi-k2.6:cloud` via `ollama-cloud`): cap is governed by `max_concurrent_children` AND provider's concurrent model limit. Ollama Pro = 3 concurrent cloud models total (parent + children). See `references/ollama-pro-concurrent-limits.md` in `kung-fu-delegation` skill for empirical test results.
- **Local Ollama**: `num_parallel` controls concurrent model requests. Never set `max_concurrent_children` higher than `(ollama_num_parallel - 1)`.
- When patching skills that mention `max_concurrent_children`, always add: "Check your `~/.hermes/config.yaml` for the current value." Examples in skills must never show more parallel tasks than the user's configured cap.
- User's current config: **3**.

## Ghost Reference Cleanup Pattern

When auditing skills, watch for references to non-existent files/skills. Common sources:
1. **Ghost `linked_files`** — SKILL.md lists `references/foo.md` that does not exist on disk.
2. **Ghost skill cross-references** — SKILL.md mentions `some-other-skill` that is not in `skills_list`.
3. **Ghost memory references** — MEMORY.md or USER.md claim a skill exists at `~/.hermes/skills/X/SKILL.md` but the directory is absent.

**Fix**: Either create the missing artifact, or remove the reference. Do NOT leave dangling links that mislead future sessions.

## Skill Audit Checklist (use delegate_task with 2 parallel agents)

Agent A — Skill integrity:
- Load each skill with `skill_view`
- Check `linked_files` exist
- Cross-reference `related_skills` against `skills_list`
- Verify `delegate_task` examples respect `max_concurrent_children`

Agent B — Memory/Obsidian integrity:
- Read `~/.hermes/memories/MEMORY.md` and `USER.md`
- Search `~/obsidian-memory` for matching topics
- Flag duplicates, stale timestamps, ghost references

## Persistent Memory Restructuring Rules

- MEMORY.md = **operational facts** (infra recipes, project context, tool quirks)
- USER.md = **identity and preferences** (contact, style, workflow expectations)
- Obsidian = **detailed runbooks, incident reports, deep documentation**
- Never duplicate full runbooks into MEMORY.md — keep a short reference + link to Obsidian
- Use `#last-verified: YYYY-MM-DD` for volatile technical snippets
- Use YAML frontmatter (`updated`, `tags`) for stale-data detection
- Replace `§` separators with Markdown `##` sections

## Subagent Sizing for Audits

When running `delegate_task` for audits:
- Agent A (skills): `toolsets=["skills", "file"]` — reads skill files, lists skills
- Agent B (memory): `toolsets=["file"]` — reads memory files, searches Obsidian
- Both need high context — split the skill list evenly if >10 skills
- With `max_concurrent_children=3`, never dispatch >3 agents in one batch
