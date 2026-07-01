# Two-Tier Memory Model: Agent + Obsidian

This is the convention used by natan's Hermes setup.

## Why two tiers?

Agent short-term memory is capped at ~2,200 characters. Obsidian vault is unlimited. The model splits storage by durability and access speed.

## Tier 1 — Agent Short-Term Memory (~2,200 chars)

**Stores:**
- MOC coordinates (canonical entry-point paths in the vault)
- Active project names and their vault MOC
- One-line reminders like "search vault before creating from scratch"
- Critical environment facts (IPs, service ports, known pitfalls)

**Rule:** Never store full knowledge bodies here. Only references and coordinates.

## Tier 2 — Obsidian Vault (unlimited)

**Stores:**
- Full documentation, runbooks, methodologies
- Project details, decision logs, architecture notes
- Cheat sheets, API references, research findings
- Session logs (Daily/)

## Workflow rule

```
BEFORE creating any note, methodology, or structure from scratch:
  1. Search the vault via MCP search_vault or search_files
  2. If found → reuse, reference, or update
  3. If not found → create, then register in the appropriate MOC
```

This prevents duplicate knowledge, contradicting records, and wasted context.

## MOC coordinates that must be in agent memory

- `Knowledge/MOC — Index.md` — master index
- `Projects/MOC — Projects.md` — project index
- `Operations/MOC — Operations.md` — infra runbooks
- `Knowledge/Technical/MOC — Technical.md` — technical cheat-sheets

## Convention: frontmatter

Every vault note uses YAML frontmatter:
```yaml
---
tags: [topic, status/active]
date: YYYY-MM-DD
lang: ru
---
```

Tags use hierarchy: `status/active`, `status/archived`, `project/name`.
